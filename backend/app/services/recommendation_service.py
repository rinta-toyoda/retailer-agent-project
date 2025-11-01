"""
Recommendation Service
Simple history-based recommendations without agent (fallback).
"""

from typing import List
from sqlalchemy.orm import Session
from app.repositories.order_history_repository import OrderHistoryRepository
from app.tools.db_tool import DatabaseTool


class RecommendationService:
    """Simple recommendation service based on order history."""

    def __init__(self, db: Session):
        self.db = db
        self.order_history_repo = OrderHistoryRepository(db)
        self.db_tool = DatabaseTool(db)

    def recommend_from_history(self, customer_id: int, limit: int = 5) -> List[dict]:
        """
        Generate recommendations from customer history.

        Args:
            customer_id: Customer ID
            limit: Number of recommendations

        Returns:
            List of recommended products
        """
        # Check if customer has orders
        has_orders = self.order_history_repo.has_past_orders(customer_id)

        if not has_orders:
            # Return popular products
            return self.db_tool.fetch_popular_products(limit=limit)

        # Get order history
        order_history = self.order_history_repo.find_by_customer(customer_id)

        # Extract categories from history
        categories = list(set(item["category"] for item in order_history if item.get("category")))

        # Fetch similar products from those categories
        recommendations = []
        for category in categories[:3]:  # Top 3 categories
            category_products = self.db_tool.search_products_by_attributes(
                category=category,
                limit=3
            )
            recommendations.extend(category_products)

        return recommendations[:limit]
