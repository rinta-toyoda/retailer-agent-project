"""
Order and OrderItem Domain Models
Implements the Checkout flow from sequence diagrams.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.infra.database import Base


class Order(Base):
    """
    Order entity representing completed purchases.
    Created in /checkout/finalize flow (sequence diagram).
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, nullable=True)
    cart_id = Column(String(100), nullable=True)  # Reference to original cart

    # Payment information
    payment_intent_id = Column(String(200), nullable=True)
    payment_status = Column(String(20), default="PENDING")  # PENDING, PAID, FAILED
    receipt_url = Column(String(500), nullable=True)

    # Order totals
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=Decimal("0"))
    total = Column(Numeric(10, 2), nullable=False)

    # Status tracking
    status = Column(String(20), default="PROCESSING")  # PROCESSING, SHIPPED, DELIVERED, CANCELLED
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}', total={self.total})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "payment_status": self.payment_status,
            "receipt_url": self.receipt_url,
            "subtotal": float(self.subtotal),
            "tax": float(self.tax),
            "total": float(self.total),
            "status": self.status,
            "items": [item.to_dict() for item in self.items],
            "item_count": len(self.items),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
        }


class OrderItem(Base):
    """
    OrderItem entity representing products in an order.
    Snapshot of cart items at checkout time.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku = Column(String(50), nullable=False)  # Snapshot for historical record
    name = Column(String(200), nullable=False)  # Snapshot
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Price at time of purchase
    subtotal = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, sku='{self.sku}', qty={self.quantity}, price={self.price})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "sku": self.sku,
            "name": self.name,
            "quantity": self.quantity,
            "price": float(self.price),
            "subtotal": float(self.subtotal),
        }
