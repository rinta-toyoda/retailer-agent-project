"""
Agent Service - AI Reasoning and Decision Making
Demonstrates AI agent capabilities: NL search, recommendations, reasoning.
Marking Criteria: 4.2 (Demonstrating AI Agent Capabilities)
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.infra.llm_client import llm_client
from app.tools.db_tool import DatabaseTool
from app.services.inventory_service import InventoryService
from app.repositories.product_repository import ProductRepository


class AgentService:
    """
    AI Agent demonstrating:
    - Natural language search with intent parsing
    - Confidence scoring and clarification
    - History-based recommendations with reasoning
    """

    def __init__(self, db: Session):
        self.db = db
        self.db_tool = DatabaseTool(db)
        self.inventory_service = InventoryService(db)
        self.product_repo = ProductRepository(db)
        self.llm = llm_client

    def _enrich_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich AI-returned product objects with full database records.

        AI returns: {sku, name, score, reason}
        This enriches to: {id, sku, name, description, price, category, brand, color, size, features, image_url, ...}

        Args:
            products: List of minimal product objects from AI

        Returns:
            List of enriched product objects with all fields
        """
        enriched = []
        for product in products:
            sku = product.get("sku")
            if not sku:
                continue

            # Fetch full product record from database
            full_product = self.product_repo.find_by_sku(sku)
            if full_product:
                # Merge AI metadata (score, reason) with full product data
                product_dict = full_product.to_dict()
                product_dict["score"] = product.get("score") or product.get("recommendation_score", 0.0)
                product_dict["reason"] = product.get("reason", "")
                enriched.append(product_dict)
            else:
                # Fallback: keep minimal data if product not found
                enriched.append(product)

        return enriched

    def search_nl(self, query: str) -> Dict[str, Any]:
        """
        Natural language search (Search - Agent NL sequence diagram).

        Flow:
        1. Parse intent from query using LLM
        2. Fetch related products from database
        3. Score confidence
        4. If confidence >= threshold: return results
        5. If confidence < threshold: ask for clarification

        Args:
            query: Natural language search query

        Returns:
            Search results with reasoning logs
        """
        response = self.llm.natural_language_search(query, self.db_tool)
        # Ensure reasoning logs are always attached for transparency
        response["reasoning_logs"] = self.llm.get_reasoning_logs()

        # Fallback: if no products were returned, run a fuzzy DB search
        if not response.get("products"):
            fallback_products = self.db_tool.search_products_by_text(query, limit=3)
            response["products"] = fallback_products
            if fallback_products:
                response["confidence"] = max(response.get("confidence", 0.0), 0.5)
                response.setdefault("intent", {}).setdefault("requires_clarification", False)

        # Enrich products with full database records (price, image_url, etc.)
        if response.get("products"):
            response["products"] = self._enrich_products(response["products"])

        return response

    def recommend_for(self, customer_id: int, limit: int = 5) -> List[Dict]:
        """
        Generate personalized recommendations (Recommendation - Agent-driven sequence diagram).

        Flow:
        1. Fetch customer order history directly (no AI)
        2. Pass history to LLM for analysis
        3. LLM analyzes preferences and searches for products using database tool
        4. Enrich with full product data
        5. Check availability
        6. Return ranked recommendations

        Args:
            customer_id: Customer identifier
            limit: Number of recommendations

        Returns:
            List of recommended products with scores
        """
        # Step 1: Fetch order history directly (like AI Chat fetches products)
        order_history = self.db_tool.fetch_orders_by_customer(customer_id, limit=50)
        
        # Step 2: Pass to AI for analysis and product search
        recommendations = self.llm.recommend_products(
            customer_id=customer_id,
            limit=limit,
            db_tool=self.db_tool,
            order_history=order_history
        )

        # Step 3: Enrich with full product data (price, image_url, etc.)
        recommendations = self._enrich_products(recommendations)

        # Step 4: Check availability
        for rec in recommendations:
            sku = rec.get("sku")
            if not sku:
                continue
            availability = self.inventory_service.get_availability(sku)
            rec["available_quantity"] = availability
            rec["in_stock"] = availability > 0

        return recommendations

    def get_reasoning_logs(self) -> List[Dict]:
        """Get LLM reasoning logs for transparency."""
        return self.llm.get_reasoning_logs()

    def clear_logs(self) -> None:
        """Clear reasoning logs."""
        self.llm.clear_logs()
