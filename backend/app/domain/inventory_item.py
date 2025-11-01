"""
InventoryItem and StockReservation Domain Models
Implements inventory management from Admin and Checkout flows.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.infra.database import Base


class InventoryItem(Base):
    """
    InventoryItem entity tracking product stock levels.
    Used in:
    - Admin - Manual Stock Update (sequence diagram)
    - Checkout - /checkout/prepare (stock reservation)
    - Low Stock Monitor - Alert Flow
    """
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)

    # Low stock monitoring
    low_stock_threshold = Column(Integer, default=10)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservations = relationship("StockReservation", back_populates="inventory_item", cascade="all, delete-orphan")

    def available_quantity(self) -> int:
        """Calculate available (unreserved) stock."""
        return max(0, self.quantity - self.reserved_quantity)

    def increment(self, qty: int) -> None:
        """Increment stock (Admin flow)."""
        self.quantity += qty

    def decrement(self, qty: int) -> None:
        """Decrement stock (Admin flow)."""
        self.quantity = max(0, self.quantity - qty)

    def reserve(self, qty: int) -> bool:
        """
        Reserve stock for checkout (Checkout - /checkout/prepare).
        Returns True if reservation successful.
        """
        if self.available_quantity() >= qty:
            self.reserved_quantity += qty
            return True
        return False

    def commit(self, qty: int) -> None:
        """
        Commit reserved stock (payment success).
        Reduces both reserved and total quantity.
        """
        self.reserved_quantity = max(0, self.reserved_quantity - qty)
        self.quantity = max(0, self.quantity - qty)

    def release(self, qty: int) -> None:
        """
        Release reserved stock (payment failure).
        Only reduces reserved quantity.
        """
        self.reserved_quantity = max(0, self.reserved_quantity - qty)

    def is_low_stock(self) -> bool:
        """Check if stock is below threshold (Low Stock Monitor)."""
        return self.quantity < self.low_stock_threshold

    def __repr__(self) -> str:
        return f"<InventoryItem(sku='{self.sku}', qty={self.quantity}, reserved={self.reserved_quantity})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "sku": self.sku,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "reserved_quantity": self.reserved_quantity,
            "available_quantity": self.available_quantity(),
            "low_stock_threshold": self.low_stock_threshold,
            "is_low_stock": self.is_low_stock(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StockReservation(Base):
    """
    StockReservation entity tracking temporary stock holds during checkout.
    Created in /checkout/prepare, resolved in /checkout/finalize.
    """
    __tablename__ = "stock_reservations"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(String(100), unique=True, nullable=False, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    sku = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)

    # Checkout flow tracking
    cart_id = Column(String(100), nullable=True)
    payment_intent_id = Column(String(200), nullable=True)

    # Status
    status = Column(String(20), default="RESERVED")  # RESERVED, COMMITTED, RELEASED, EXPIRED
    is_active = Column(Boolean, default=True)

    # TTL for reservations (expire after 30 minutes)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=30))
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="reservations")

    def is_expired(self) -> bool:
        """Check if reservation has expired."""
        return datetime.utcnow() > self.expires_at and self.is_active

    def __repr__(self) -> str:
        return f"<StockReservation(id='{self.reservation_id}', sku='{self.sku}', qty={self.quantity}, status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "reservation_id": self.reservation_id,
            "sku": self.sku,
            "quantity": self.quantity,
            "status": self.status,
            "cart_id": self.cart_id,
            "payment_intent_id": self.payment_intent_id,
            "is_active": self.is_active,
            "is_expired": self.is_expired(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
