"""
FastAPI Main Application Entry Point
Retailer AI Agent System - Backend API
Marking Criteria: 4.1, 4.2, 4.4 (Implementation, AI Agent, Advanced Technologies)
"""

from fastapi import FastAPI, Depends, HTTPException, File, Header, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from app.infra.database import get_db, init_db
from app.infra.s3_client import get_s3_client
from app.schemas.cart_schema import AddToCartRequest, RemoveFromCartRequest
from app.schemas.checkout_schema import CheckoutPrepareRequest, CheckoutFinalizeRequest
from app.schemas.product_schema import ProductUpdateRequest
from app.schemas.auth_schema import UserLogin, UserCreate, Token, UserResponse
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService
from app.services.agent_service import AgentService
from app.services.recommendation_service import RecommendationService
from app.services.admin_inventory_service import AdminInventoryService
from app.services.admin_product_service import AdminProductService
from app.services.auth_service import AuthService
from app.repositories.product_repository import ProductRepository
from app.middleware.jwt_middleware import get_current_user, get_current_active_user, get_current_superuser
from app.domain.user import User
from app.tools.seed_db import ensure_seed_data
from datetime import timedelta

# Initialize FastAPI app
app = FastAPI(
    title="Retailer AI Agent System",
    description="E-commerce platform with AI-powered search and recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    ensure_seed_data(force=False)
    print("Retailer AI Agent System started successfully")


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    - **username**: User's username
    - **password**: User's password

    Returns access token for subsequent API calls.
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(user_credentials.username, user_credentials.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only admins can create users
):
    """
    Register a new user (admin only).

    Requires superuser authentication.
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return current_user.to_dict()


# ============================================
# CART ENDPOINTS (Cart Controller)
# ============================================

@app.post("/cart/add")
def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db)):
    """Add product to cart (Cart - Add Product sequence diagram)."""
    try:
        cart_service = CartService(db)
        cart = cart_service.add_product(
            cart_id=request.cart_id,
            product_id=request.product_id,
            qty=request.quantity,
            customer_id=request.customer_id
        )
        return cart.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/cart/remove")
def remove_from_cart(request: RemoveFromCartRequest, db: Session = Depends(get_db)):
    """Remove product from cart (Cart - Remove Product sequence diagram)."""
    try:
        cart_service = CartService(db)
        cart = cart_service.remove_product(
            cart_id=request.cart_id,
            product_id=request.product_id,
            qty=request.quantity
        )
        return cart.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))


@app.get("/cart/{cart_id}")
def get_cart(cart_id: str, db: Session = Depends(get_db)):
    """Get cart by ID."""
    cart_service = CartService(db)
    cart = cart_service.get_cart(cart_id)
    if not cart:
        cart = cart_service.ensure_cart(cart_id)
    return cart.to_dict()


# ============================================
# CHECKOUT ENDPOINTS (Checkout Controller)
# ============================================

@app.post("/checkout/prepare")
def prepare_checkout(request: CheckoutPrepareRequest, db: Session = Depends(get_db)):
    """Prepare checkout session (Checkout - /checkout/prepare sequence diagram)."""
    try:
        checkout_service = CheckoutService(db)
        session = checkout_service.create_session(request.cart_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/checkout/finalize")
def finalize_checkout(request: CheckoutFinalizeRequest, db: Session = Depends(get_db)):
    """Finalize checkout (Checkout - /checkout/finalize sequence diagram)."""
    try:
        checkout_service = CheckoutService(db)
        order = checkout_service.finalize(request.payment_intent_id, request.cart_id, request.customer_id)
        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.payment_status,
            "total": float(order.total)
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ============================================
# SEARCH ENDPOINTS (Search Controller)
# ============================================

@app.get("/search")
def keyword_search(q: str, db: Session = Depends(get_db)):
    """Search endpoint now fully powered by the AI agent."""
    agent_service = AgentService(db)
    results = agent_service.search_nl(q)
    return {"query": q, "results": results.get("products", []), "agent": results}


@app.get("/search/nl")
def natural_language_search(q: str, db: Session = Depends(get_db)):
    """
    Natural language search with AI agent (Search - Agent NL sequence diagram).
    Demonstrates AI agent capabilities (Marking Criteria 4.2).
    """
    agent_service = AgentService(db)
    results = agent_service.search_nl(q)
    return results


# ============================================
# RECOMMENDATION ENDPOINTS (Recommendation Controller)
# ============================================

@app.get("/recommendations")
def get_recommendations(customer_id: int, limit: int = 4, db: Session = Depends(get_db)):
    """
    Get personalized recommendations (Recommendation sequence diagram).
    Always uses AI agent for recommendation reasoning (Marking Criteria 4.2).
    """
    agent_service = AgentService(db)
    recommendations = agent_service.recommend_for(customer_id, limit=limit)
    return {"customer_id": customer_id, "recommendations": recommendations}


# ============================================
# ADMIN ENDPOINTS (Admin Controller)
# ============================================

@app.post("/admin/stock")
def update_stock(sku: str, qty_delta: int, db: Session = Depends(get_db)):
    """Manual stock update (Admin - Manual Stock Update sequence diagram)."""
    try:
        admin_service = AdminInventoryService(db)
        result = admin_service.update_stock(sku, qty_delta)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/admin/stock/set")
def set_stock(sku: str, quantity: int, db: Session = Depends(get_db)):
    """Set absolute stock quantity (replaces increment/decrement)."""
    try:
        admin_service = AdminInventoryService(db)
        result = admin_service.set_stock(sku, quantity)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/admin/inventory")
def get_inventory(db: Session = Depends(get_db)):
    """Get all inventory items."""
    admin_service = AdminInventoryService(db)
    return {"inventory": admin_service.get_all_inventory()}


@app.get("/admin/products")
def admin_get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all products for admin (including inactive)."""
    admin_service = AdminProductService(db)
    products = admin_service.get_all_products(skip=skip, limit=limit)
    return {"products": products}


@app.get("/admin/products/{product_id}")
def admin_get_product(product_id: int, db: Session = Depends(get_db)):
    """Get single product for admin."""
    try:
        admin_service = AdminProductService(db)
        return admin_service.get_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/admin/products/{product_id}")
def admin_update_product(
    product_id: int,
    update_data: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update product information."""
    try:
        admin_service = AdminProductService(db)
        result = admin_service.update_product(product_id, update_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/admin/products/{product_id}/upload-image")
async def upload_product_image(
    product_id: int,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    """
    Upload product image to S3 and update product.
    Demonstrates cloud storage integration (Marking Criteria 4.4).
    """
    try:
        # Read file content
        file_content = await file.read()
        content_type = file.content_type or "image/jpeg"

        # Upload to S3
        s3_client = get_s3_client()
        image_url = s3_client.upload_image(file_content, content_type, file.filename)

        # Update product with image URL
        admin_service = AdminProductService(db)
        update_data = ProductUpdateRequest(image_url=image_url)
        result = admin_service.update_product(product_id, update_data)

        return {"image_url": image_url, "product": result}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


# ============================================
# PRODUCT ENDPOINTS
# ============================================

@app.get("/products")
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all products."""
    product_repo = ProductRepository(db)
    products = product_repo.find_all(skip=skip, limit=limit)
    return {"products": [p.to_dict() for p in products]}


@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID."""
    product_repo = ProductRepository(db)
    product = product_repo.find_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_dict()


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Retailer AI Agent System"}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Retailer AI Agent System API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "AI-powered natural language search",
            "Intelligent product recommendations",
            "Cart management",
            "Checkout with payment simulation",
            "Admin inventory management"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
