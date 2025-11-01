"""Database tool exposed to the AI agent via OpenAI function-calling."""

from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class DatabaseTool:
    """Expose safe read-only SQL helpers both to Python and the OpenAI agent."""

    TOOL_NAME = "database_tool"

    def __init__(self, session: Session):
        self.session = session


    def _serialize_row(self, columns: List[str], row: Any) -> Dict[str, Any]:
        """Convert database row to JSON-serializable dict, handling Decimal and datetime types."""
        from decimal import Decimal
        from datetime import datetime, date
        result = {}
        for key, value in zip(columns, row):
            if isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, (datetime, date)):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

    def fetch_products(self, limit: int = 20, category: str = None) -> List[Dict[str, Any]]:
        """
        Fetch products from database for agent reasoning.
        Used in natural language search flow.

        Args:
            limit: Maximum number of products to fetch
            category: Optional category filter

        Returns:
            List of product dictionaries
        """
        query = "SELECT * FROM products WHERE is_active = true"
        params = {"limit": limit}

        if category:
            query += " AND category = :category"
            params["category"] = category

        query += " LIMIT :limit"

        result = self.session.execute(text(query), params)
        columns = result.keys()
        return [self._serialize_row(columns, row) for row in result.fetchall()]

    def fetch_orders_by_customer(self, customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch customer's order history for recommendation reasoning.
        Used in history-based recommendations.

        Args:
            customer_id: Customer identifier
            limit: Maximum number of orders to fetch

        Returns:
            List of order dictionaries with items
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
        ORDER BY o.created_at DESC
        LIMIT :limit
        """

        result = self.session.execute(
            text(query),
            {"customer_id": customer_id, "limit": limit}
        )
        columns = result.keys()
        return [self._serialize_row(columns, row) for row in result.fetchall()]

    def search_products_by_attributes(
        self,
        category: str = None,
        color: str = None,
        brand: str = None,
        features: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search products by attributes (for AI agent search).

        Args:
            category: Product category
            color: Product color
            brand: Product brand
            features: Product features (partial match)
            limit: Maximum results

        Returns:
            List of matching products
        """
        query = "SELECT * FROM products WHERE is_active = true"
        params = {"limit": limit}
        conditions = []

        if category:
            conditions.append("category = :category")
            params["category"] = category

        if color:
            conditions.append("color = :color")
            params["color"] = color

        if brand:
            conditions.append("brand = :brand")
            params["brand"] = brand

        if features:
            conditions.append("features LIKE :features")
            params["features"] = f"%{features}%"

        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += " LIMIT :limit"

        result = self.session.execute(text(query), params)
        columns = result.keys()
        return [self._serialize_row(columns, row) for row in result.fetchall()]

    def search_products_by_text(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Fuzzy search on name/description/brand/features."""
        if not query_text:
            return []

        like_param = f"%{query_text.lower()}%"
        query = text(
            """
            SELECT *
            FROM products
            WHERE is_active = true
              AND (
                LOWER(name) LIKE :term OR
                LOWER(description) LIKE :term OR
                LOWER(brand) LIKE :term OR
                LOWER(features) LIKE :term OR
                LOWER(category) LIKE :term
              )
            LIMIT :limit
            """
        )
        result = self.session.execute(query, {"term": like_param, "limit": limit})
        columns = result.keys()
        return [self._serialize_row(columns, row) for row in result.fetchall()]

    def get_product_categories(self) -> List[str]:
        """Get all distinct product categories in the catalog."""
        query = text(
            """
            SELECT DISTINCT category
            FROM products
            WHERE is_active = true AND category IS NOT NULL
            ORDER BY category
            """
        )
        result = self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    # ------------------------------------------------------------------
    # OpenAI tool adapter helpers
    # ------------------------------------------------------------------

    def tool_definition(self) -> Dict[str, Any]:
        """Return the function metadata passed to OpenAI for tool-calling."""

        return {
            "type": "function",
            "function": {
                "name": self.TOOL_NAME,
                "description": (
                    "Read-only access to the retailer database for AI reasoning. "
                    "Use the `action` argument to choose which dataset to query."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [
                                "fetch_products",
                                "fetch_popular_products",
                                "fetch_orders_by_customer",
                                "search_products_by_attributes",
                                "search_products_by_text",
                                "get_product_categories",
                            ],
                            "description": "Database query to run",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return",
                        },
                        "category": {"type": "string"},
                        "color": {"type": "string"},
                        "brand": {"type": "string"},
                        "features": {
                            "type": "string",
                            "description": "Single feature string (comma-separated for multiple)",
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Free-form text to match against product name/description",
                        },
                        "customer_id": {
                            "type": "integer",
                            "description": "Required when action is fetch_orders_by_customer",
                        },
                    },
                    "required": ["action"],
                },
            },
        }

    def handle_tool_call(
        self,
        action: str,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        color: Optional[str] = None,
        brand: Optional[str] = None,
        features: Optional[Any] = None,
        query_text: Optional[str] = None,
        customer_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute the corresponding helper and return JSON-serialisable payload."""

        if limit is None:
            limit = 20

        if isinstance(features, list):
            features_value = features[0] if features else None
        else:
            features_value = features

        if action == "fetch_products":
            data = self.fetch_products(limit=limit, category=category)
        elif action == "fetch_popular_products":
            data = self.fetch_popular_products(limit=limit)
        elif action == "fetch_orders_by_customer":
            if customer_id is None:
                raise ValueError("customer_id is required for fetch_orders_by_customer")
            data = self.fetch_orders_by_customer(customer_id=customer_id, limit=limit)
        elif action == "search_products_by_attributes":
            data = self.search_products_by_attributes(
                category=category,
                color=color,
                brand=brand,
                features=features_value,
                limit=limit,
            )
        elif action == "search_products_by_text":
            data = self.search_products_by_text(query_text=query_text or "", limit=limit)
        elif action == "get_product_categories":
            data = self.get_product_categories()
        else:
            raise ValueError(f"Unsupported database_tool action: {action}")

        return {
            "action": action,
            "limit": limit,
            "results": data,
        }

    def fetch_popular_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch popular products (based on order frequency).
        Used for cold-start recommendations.

        Args:
            limit: Number of products to fetch

        Returns:
            List of popular products
        """
        query = """
        SELECT
            p.*,
            COUNT(oi.id) as order_count
        FROM products p
        LEFT JOIN order_items oi ON oi.product_id = p.id
        WHERE p.is_active = true
        GROUP BY p.id
        ORDER BY order_count DESC
        LIMIT :limit
        """

        result = self.session.execute(text(query), {"limit": limit})
        columns = result.keys()
        return [self._serialize_row(columns, row) for row in result.fetchall()]
