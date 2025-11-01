"""
Cart Repository - Data Access Layer
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.domain.cart import Cart, CartItem


class CartRepository:
    """Repository for Cart entity operations."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_cart_id(self, cart_id: str) -> Optional[Cart]:
        """Find cart by cart_id."""
        return self.db.query(Cart).filter(Cart.cart_id == cart_id).first()

    def find_by_customer(self, customer_id: int) -> Optional[Cart]:
        """Find active cart for customer."""
        return (
            self.db.query(Cart)
            .filter(Cart.customer_id == customer_id, Cart.status == "active")
            .first()
        )

    def create(self, cart: Cart) -> Cart:
        """Create new cart."""
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def update(self, cart: Cart) -> Cart:
        """Update cart."""
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def add_item(self, cart_item: CartItem) -> CartItem:
        """Add item to cart."""
        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def remove_item(self, cart_item: CartItem) -> bool:
        """Remove item from cart."""
        self.db.delete(cart_item)
        self.db.commit()
        return True

    def clear_cart(self, cart: Cart) -> bool:
        """Clear all items from cart."""
        for item in cart.items:
            self.db.delete(item)
        self.db.commit()
        return True
