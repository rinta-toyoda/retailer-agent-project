"""
Order Repository - Data Access Layer
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.order import Order, OrderItem


class OrderRepository:
    """Repository for Order entity operations."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Find order by ID."""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def find_by_order_number(self, order_number: str) -> Optional[Order]:
        """Find order by order number."""
        return self.db.query(Order).filter(Order.order_number == order_number).first()

    def find_by_customer(self, customer_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
        """Find orders by customer."""
        return (
            self.db.query(Order)
            .filter(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, order: Order) -> Order:
        """Create new order."""
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order: Order) -> Order:
        """Update order."""
        self.db.commit()
        self.db.refresh(order)
        return order

    def add_item(self, order_item: OrderItem) -> OrderItem:
        """Add item to order."""
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        return order_item
