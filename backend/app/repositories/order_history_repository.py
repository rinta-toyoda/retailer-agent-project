"""
Order History Repository - For Recommendation Service
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


class OrderHistoryRepository:
    """Repository for fetching customer order history for recommendations."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_customer(self, customer_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find customer's order history with product details.
        Used in Recommendation flow (sequence diagram).

        Args:
            customer_id: Customer identifier
            limit: Maximum orders to fetch

        Returns:
            List of order items with product details
        """
        query = """
        SELECT
            o.id as order_id,
            o.order_number,
            o.created_at as order_date,
            oi.product_id,
            oi.sku,
            oi.name as product_name,
            oi.quantity,
            oi.price,
            p.category,
            p.brand,
            p.color,
            p.features
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        LEFT JOIN products p ON p.id = oi.product_id
        WHERE o.customer_id = :customer_id
        AND o.payment_status = 'PAID'
        ORDER BY o.created_at DESC
        LIMIT :limit
        """

        result = self.db.execute(
            text(query),
            {"customer_id": customer_id, "limit": limit}
        )

        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def has_past_orders(self, customer_id: int) -> bool:
        """
        Check if customer has any past orders.

        Args:
            customer_id: Customer identifier

        Returns:
            True if customer has orders
        """
        query = """
        SELECT COUNT(*) as count
        FROM orders
        WHERE customer_id = :customer_id
        AND payment_status = 'PAID'
        """

        result = self.db.execute(text(query), {"customer_id": customer_id}).fetchone()
        return result[0] > 0 if result else False
