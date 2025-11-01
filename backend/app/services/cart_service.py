"""
Cart Service - Business Logic Layer
Implements Cart Add/Remove Product flows from sequence diagrams.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.domain.cart import Cart, CartItem
from app.domain.product import Product
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository


class CartService:
    """
    Cart business logic implementing sequence diagram flows:
    - Cart - Add Product
    - Cart - Remove Product
    """

    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)

    def add_product(self, cart_id: str, product_id: int, qty: int, customer_id: int = None) -> Cart:
        """
        Add product to cart (Cart - Add Product sequence diagram).

        Flow:
        1. Load/create cart
        2. Load product
        3. Find existing item or create new
        4. Increase quantity or attach new item
        5. Recompute totals

        Args:
            cart_id: Cart identifier
            product_id: Product to add
            qty: Quantity to add
            customer_id: Optional customer ID

        Returns:
            Updated cart

        Raises:
            ValueError: If product not found or inactive
        """
        # Step 1: Get or create active cart
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if not cart:
            cart = Cart(
                cart_id=cart_id or str(uuid.uuid4()),
                customer_id=customer_id,
                status="active"
            )
            cart = self.cart_repo.create(cart)

        # Step 2: Load product
        product = self.product_repo.find_by_id(product_id)
        if not product or not product.is_active:
            raise ValueError(f"Product {product_id} not found or inactive")

        # Step 3: Find existing item in cart
        existing_item = cart.find_item(product_id)

        if existing_item:
            # Step 4a: Increase quantity of existing item
            existing_item.increase_qty(qty)
            self.cart_repo.update(cart)
        else:
            # Step 4b: Create new cart item
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=qty,
                price=product.price  # Snapshot price at add time
            )
            self.cart_repo.add_item(new_item)
            cart.items.append(new_item)

        # Step 5: Recompute totals (handled by cart.total() method)
        self.cart_repo.update(cart)

        return cart

    def remove_product(self, cart_id: str, product_id: int, qty: int) -> Cart:
        """
        Remove product from cart (Cart - Remove Product sequence diagram).

        Flow:
        1. Find cart
        2. Find item in cart
        3. Decrease quantity or detach item
        4. Recompute totals

        Args:
            cart_id: Cart identifier
            product_id: Product to remove
            qty: Quantity to remove

        Returns:
            Updated cart

        Raises:
            ValueError: If cart or item not found
        """
        # Step 1: Find cart
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")

        # Step 2: Find item in cart
        item = cart.find_item(product_id)
        if not item:
            raise ValueError(f"Product {product_id} not in cart")

        # Step 3: Decrease quantity or remove item
        if qty < item.quantity:
            # Decrease quantity
            item.decrease_qty(qty)
            self.cart_repo.update(cart)
        else:
            # Detach and delete item
            cart.items.remove(item)
            self.cart_repo.remove_item(item)

        # Step 4: Recompute totals
        self.cart_repo.update(cart)

        return cart

    def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Get cart by ID."""
        return self.cart_repo.find_by_cart_id(cart_id)

    def ensure_cart(self, cart_id: str, customer_id: Optional[int] = None) -> Cart:
        """Get or create a cart for the given ID."""
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if cart:
            return cart

        new_cart = Cart(
            cart_id=cart_id,
            customer_id=customer_id,
            status="active"
        )
        return self.cart_repo.create(new_cart)

    def clear_cart(self, cart_id: str) -> bool:
        """Clear all items from cart."""
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if cart:
            return self.cart_repo.clear_cart(cart)
        return False

    def get_cart_total(self, cart_id: str) -> Decimal:
        """Get cart total."""
        cart = self.cart_repo.find_by_cart_id(cart_id)
        return cart.total() if cart else Decimal("0")
