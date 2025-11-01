"""Pytest configuration and shared fixtures."""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infra.database import Base, get_db
from app.domain.user import User
from app.domain.product import Product
from app.domain.cart import Cart, CartItem
from app.domain.order import Order, OrderItem
from app.domain.inventory_item import InventoryItem
from app.services.auth_service import AuthService


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with check_same_thread=False for SQLite
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=AuthService.get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session: Session) -> User:
    """Create a test admin user."""
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=AuthService.get_password_hash("admin123"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_product(db_session: Session) -> Product:
    """Create a test product."""
    product = Product(
        sku="TEST-001",
        name="Test Product",
        description="A test product for unit testing",
        price=99.99,
        category="test",
        brand="TestBrand",
        color="blue",
        features="test,feature",
        image_url="http://example.com/test.png",
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    # Create inventory for the product
    inventory = InventoryItem(
        sku=product.sku,
        product_id=product.id,
        quantity=100
    )
    db_session.add(inventory)
    db_session.commit()

    return product


@pytest.fixture
def test_products(db_session: Session) -> list[Product]:
    """Create multiple test products."""
    products = [
        Product(
            sku=f"TEST-{i:03d}",
            name=f"Test Product {i}",
            description=f"Description for test product {i}",
            price=50.0 + (i * 10),
            category="test" if i % 2 == 0 else "demo",
            brand="TestBrand" if i % 3 == 0 else "DemoBrand",
            color="red" if i % 2 == 0 else "blue",
            features="test,feature",
            image_url=f"http://example.com/test{i}.png",
            is_active=True
        )
        for i in range(1, 6)
    ]

    for product in products:
        db_session.add(product)
    db_session.commit()

    # Create inventory for all products
    for product in products:
        db_session.refresh(product)
        inventory = InventoryItem(sku=product.sku, product_id=product.id, quantity=50)
        db_session.add(inventory)
    db_session.commit()

    return products


@pytest.fixture
def test_cart(db_session: Session, test_user: User, test_product: Product) -> Cart:
    """Create a test cart with items."""
    cart = Cart(
        cart_id="test-cart-001",
        customer_id=test_user.id
    )
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)

    cart_item = CartItem(
        cart_id=cart.id,
        product_id=test_product.id,
        quantity=2,
        price=test_product.price
    )
    db_session.add(cart_item)
    db_session.commit()

    return cart


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client: TestClient, test_admin: User) -> dict:
    """Get authentication headers for admin user."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set mock environment variables for all tests."""
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://localhost:4566")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
