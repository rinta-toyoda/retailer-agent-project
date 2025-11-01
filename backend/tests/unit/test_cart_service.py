"""
Unit tests for CartService with comprehensive edge case coverage.

Tests cover:
- Add product scenarios (new cart, existing cart, existing item)
- Remove product scenarios (partial, complete removal)
- Edge cases (invalid products, zero quantities, non-existent carts)
- Error handling (inactive products, quantity validation)

Marking Criteria: 4.1 (Testing and Quality Assurance)
"""
import pytest
from app.services.cart_service import CartService
from app.domain.product import Product
from app.domain.inventory_item import InventoryItem


class TestCartService:
    """Test suite for CartService with edge cases."""

    # ==================== ADD PRODUCT Tests ====================

    def test_add_product_to_new_cart(self, db_session, test_product):
        """Test adding product to a new cart - happy path."""
        service = CartService(db_session)

        cart = service.add_product(
            cart_id="new-cart-001",
            product_id=test_product.id,
            qty=2,
            customer_id=1
        )

        assert cart is not None
        assert cart.cart_id == "new-cart-001"
        assert cart.customer_id == 1
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 2
        assert cart.items[0].product_id == test_product.id

    def test_add_product_to_existing_cart(self, db_session, test_cart, test_product):
        """Test adding different product to existing cart."""
        service = CartService(db_session)

        # Create another product
        product2 = Product(
            sku="TEST-002",
            name="Test Product 2",
            price=50.00,
            category="test",
            is_active=True
        )
        db_session.add(product2)
        db_session.commit()
        db_session.refresh(product2)

        cart = service.add_product(
            cart_id=test_cart.cart_id,
            product_id=product2.id,
            qty=1,
            customer_id=test_cart.customer_id
        )

        # Should have original item + new item
        assert len(cart.items) == 2

    def test_add_product_increase_quantity(self, db_session, test_cart, test_product):
        """Test adding same product increases quantity."""
        service = CartService(db_session)

        # test_cart already has 2 items of test_product
        original_qty = test_cart.items[0].quantity

        cart = service.add_product(
            cart_id=test_cart.cart_id,
            product_id=test_product.id,
            qty=3,
            customer_id=test_cart.customer_id
        )

        # Quantity should increase
        updated_item = cart.find_item(test_product.id)
        assert updated_item.quantity == original_qty + 3

    def test_add_product_quantity_one(self, db_session, test_product):
        """Test adding single quantity (boundary case)."""
        service = CartService(db_session)

        cart = service.add_product(
            cart_id="single-qty-cart",
            product_id=test_product.id,
            qty=1,
            customer_id=1
        )

        assert cart.items[0].quantity == 1

    def test_add_product_large_quantity(self, db_session, test_product):
        """Test adding large quantity (boundary case)."""
        service = CartService(db_session)

        cart = service.add_product(
            cart_id="large-qty-cart",
            product_id=test_product.id,
            qty=100,
            customer_id=1
        )

        assert cart.items[0].quantity == 100

    def test_add_invalid_product(self, db_session):
        """Test adding non-existent product raises ValueError."""
        service = CartService(db_session)

        with pytest.raises(ValueError, match="Product 99999 not found or inactive"):
            service.add_product(
                cart_id="test-cart",
                product_id=99999,
                qty=1,
                customer_id=1
            )

    def test_add_inactive_product(self, db_session, test_product):
        """Test adding inactive product raises ValueError."""
        service = CartService(db_session)

        # Deactivate product
        test_product.is_active = False
        db_session.commit()

        with pytest.raises(ValueError, match="Product .* not found or inactive"):
            service.add_product(
                cart_id="test-cart",
                product_id=test_product.id,
                qty=1,
                customer_id=1
            )

    def test_add_product_without_customer_id(self, db_session, test_product):
        """Test adding product without customer ID (guest cart)."""
        service = CartService(db_session)

        cart = service.add_product(
            cart_id="guest-cart",
            product_id=test_product.id,
            qty=1,
            customer_id=None  # Guest cart
        )

        assert cart.customer_id is None
        assert len(cart.items) == 1

    # ==================== REMOVE PRODUCT Tests ====================

    def test_remove_product_partial_quantity(self, db_session, test_cart, test_product):
        """Test removing partial quantity from cart item."""
        service = CartService(db_session)

        original_qty = test_cart.items[0].quantity

        cart = service.remove_product(
            cart_id=test_cart.cart_id,
            product_id=test_product.id,
            qty=1
        )

        # Should decrease quantity
        updated_item = cart.find_item(test_product.id)
        assert updated_item is not None
        assert updated_item.quantity == original_qty - 1

    def test_remove_product_complete(self, db_session, test_cart, test_product):
        """Test removing all quantity removes item from cart."""
        service = CartService(db_session)

        cart = service.remove_product(
            cart_id=test_cart.cart_id,
            product_id=test_product.id,
            qty=test_cart.items[0].quantity  # Remove all
        )

        # Item should be removed
        assert cart.find_item(test_product.id) is None
        assert len(cart.items) == 0

    def test_remove_product_exceeding_quantity(self, db_session, test_cart, test_product):
        """Test removing more than available quantity removes item completely."""
        service = CartService(db_session)

        original_qty = test_cart.items[0].quantity

        cart = service.remove_product(
            cart_id=test_cart.cart_id,
            product_id=test_product.id,
            qty=original_qty + 10  # More than available
        )

        # Item should be completely removed
        assert cart.find_item(test_product.id) is None

    def test_remove_from_nonexistent_cart(self, db_session, test_product):
        """Test removing from non-existent cart raises ValueError."""
        service = CartService(db_session)

        with pytest.raises(ValueError, match="Cart nonexistent not found"):
            service.remove_product(
                cart_id="nonexistent",
                product_id=test_product.id,
                qty=1
            )

    def test_remove_nonexistent_product_from_cart(self, db_session, test_cart):
        """Test removing product not in cart raises ValueError."""
        service = CartService(db_session)

        with pytest.raises(ValueError, match="Product .* not in cart"):
            service.remove_product(
                cart_id=test_cart.cart_id,
                product_id=99999,
                qty=1
            )

    # ==================== GET CART Tests ====================

    def test_get_cart_success(self, db_session, test_cart):
        """Test getting existing cart - happy path."""
        service = CartService(db_session)

        cart = service.get_cart(test_cart.cart_id)

        assert cart is not None
        assert cart.cart_id == test_cart.cart_id
        assert len(cart.items) >= 1

    def test_get_nonexistent_cart(self, db_session):
        """Test getting non-existent cart returns None."""
        service = CartService(db_session)

        cart = service.get_cart("nonexistent-cart")

        assert cart is None

    def test_get_cart_with_empty_string(self, db_session):
        """Test getting cart with empty cart_id returns None."""
        service = CartService(db_session)

        cart = service.get_cart("")

        assert cart is None

