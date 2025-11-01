"""
Cart and CartItem Domain Models
Implements the Cart - Add/Remove Product flows from sequence diagrams.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.infra.database import Base


class Cart(Base):
    """
    Cart entity representing a user's shopping cart.
    Implements cart management from the provided sequence diagrams:
    - Cart - Add Product
    - Cart - Remove Product
    """
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, nullable=True)  # Optional for guest carts
    status = Column(String(20), default="active")  # active, checked_out, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def total(self) -> Decimal:
        """
        Recompute cart totals (as shown in sequence diagram).
        Returns total as Decimal for precision.
        """
        return sum((item.price * item.quantity for item in self.items), Decimal("0"))

    def find_item(self, product_id: int) -> Optional["CartItem"]:
        """Find cart item by product ID."""
        for item in self.items:
            if item.product_id == product_id:
                return item
        return None

    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, cart_id='{self.cart_id}', items={len(self.items)}, total={self.total()})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "customer_id": self.customer_id,
            "status": self.status,
            "items": [item.to_dict() for item in self.items],
            "total": float(self.total()),
            "item_count": len(self.items),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CartItem(Base):
    """
    CartItem entity representing individual products in a cart.
    Maps to CartItem in the sequence diagrams with quantity management.
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)  # Snapshot of price at add time
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    def increase_qty(self, qty: int) -> None:
        """Increase item quantity (from Add Product flow)."""
        self.quantity += qty

    def decrease_qty(self, qty: int) -> None:
        """Decrease item quantity (from Remove Product flow)."""
        self.quantity = max(0, self.quantity - qty)

    def subtotal(self) -> Decimal:
        """Calculate line item subtotal."""
        return self.price * self.quantity

    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, product_id={self.product_id}, qty={self.quantity}, price={self.price})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "product": self.product.to_dict() if self.product else None,
            "quantity": self.quantity,
            "price": float(self.price),
            "subtotal": float(self.subtotal()),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
