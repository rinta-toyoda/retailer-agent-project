"""LLM client abstraction supporting both mock logic and OpenAI Agents."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from app.tools.db_tool import DatabaseTool

try:  # Optional dependency until OpenAI provider is enabled
    from openai import OpenAI
except Exception:  # pragma: no cover - handled at runtime if provider=openai
    OpenAI = None  # type: ignore


class BaseAgentLLM(ABC):
    """Common interface for running the agent in search/recommendation flows."""

    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.reasoning_logs: List[Dict[str, Any]] = []

    @abstractmethod
    def natural_language_search(self, query: str, db_tool: DatabaseTool) -> Dict[str, Any]:
        """Run the natural-language search agent."""

    @abstractmethod
    def recommend_products(self, customer_id: int, limit: int, db_tool: DatabaseTool) -> List[Dict[str, Any]]:
        """Run the recommendation agent."""

    # ------------------------------------------------------------------
    # Reasoning logs helpers
    # ------------------------------------------------------------------

    def get_reasoning_logs(self) -> List[Dict[str, Any]]:
        return self.reasoning_logs

    def clear_logs(self) -> None:
        self.reasoning_logs = []

    def _log_reasoning(self, step: str, message: str) -> None:
        if not self.enable_logging:
            return
        self.reasoning_logs.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "step": step,
                "message": message,
            }
        )


class MockLLMClient(BaseAgentLLM):
    """Original heuristic-based implementation retained for offline demos."""

    COLORS = [
        "red",
        "blue",
        "green",
        "black",
        "white",
        "yellow",
        "pink",
        "purple",
        "orange",
        "gray",
        "brown",
    ]

    CATEGORY_KEYWORDS = {
        "running shoes": ["running", "running shoes", "runners"],
        "sneakers": ["sneakers", "trainers"],
        "boots": ["boots"],
        "sandals": ["sandals"],
        "shirt": ["shirt", "t-shirt", "tee"],
        "pants": ["pants", "trousers", "jeans"],
        "jacket": ["jacket", "coat"],
    }

    FEATURE_KEYWORDS = {
        "breathable": ["breathable", "ventilated", "mesh"],
        "waterproof": ["waterproof", "water-resistant"],
        "lightweight": ["lightweight", "light"],
        "comfortable": ["comfortable", "comfy"],
        "durable": ["durable", "sturdy"],
        "stylish": ["stylish", "fashionable"],
    }

    def natural_language_search(self, query: str, db_tool: DatabaseTool) -> Dict[str, Any]:
        self.clear_logs()
        intent = self._parse_search_intent(query)
        attributes = intent["attributes"]

        products = db_tool.search_products_by_attributes(
            category=attributes.get("category"),
            color=attributes.get("color"),
            brand=attributes.get("brand"),
            features=attributes.get("features", [None])[0]
            if attributes.get("features")
            else None,
            limit=20,
        )

        if not products:
            products = db_tool.search_products_by_text(query, limit=20)
        if not products:
            products = db_tool.fetch_products(limit=20)

        ranked_products = self._rank_candidates(products, attributes, limit=3)

        response = {
            "query": query,
            "intent": intent,
            "products": ranked_products,
            "confidence": intent["confidence"],
            "requires_clarification": intent["requires_clarification"],
            "reasoning_logs": self.get_reasoning_logs(),
        }

        if intent["requires_clarification"]:
            response["clarification_message"] = (
                "I understood your query but need more details. "
                "Are you looking for specific features or brands?"
            )

        return response

    def recommend_products(self, customer_id: int, limit: int, db_tool: DatabaseTool, order_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mock recommendation using pre-fetched order history.
        
        Args:
            customer_id: Customer ID
            limit: Number of recommendations
            db_tool: Database tool for searching products
            order_history: Pre-fetched order history
        
        Returns:
            List of recommended products
        """
        self.clear_logs()

        if not order_history:
            self._log_reasoning(
                "COLD_START", "No history found, returning popular products"
            )
            return db_tool.fetch_popular_products(limit=limit)

        # Analyze purchase patterns and extract characteristics
        self._log_reasoning("ANALYZE_HISTORY", f"Analyzing {len(order_history)} past purchases")
        
        user_preferences = self._extract_user_preferences(order_history)
        self._log_reasoning("USER_PROFILE", f"Preferences: {user_preferences}")
        
        # Search for complementary products
        product_catalog = db_tool.fetch_products(limit=100)
        recommendations = self._generate_recommendations(
            user_history=order_history,
            product_catalog=product_catalog,
            limit=limit,
            user_preferences=user_preferences
        )
        
        return recommendations

    # ------------------------------------------------------------------
    # Helper implementations for mock reasoning
    # ------------------------------------------------------------------

    def _parse_search_intent(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower().strip()
        attributes: Dict[str, Any] = {}
        features: List[str] = []

        self._log_reasoning("INTENT_PARSING", f"Analyzing query: '{query}'")

        for color in self.COLORS:
            if color in query_lower:
                attributes["color"] = color
                self._log_reasoning("ATTRIBUTE", f"Detected color: {color}")
                break

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                attributes["category"] = category
                self._log_reasoning("ATTRIBUTE", f"Detected category: {category}")
                break

        for feature, keywords in self.FEATURE_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                features.append(feature)
                self._log_reasoning("ATTRIBUTE", f"Detected feature: {feature}")

        if features:
            attributes["features"] = features

        confidence = self._calculate_confidence(query, attributes)
        requires_clarification = confidence < 0.6
        self._log_reasoning(
            "CONFIDENCE", f"Calculated confidence: {confidence:.2f}"
        )

        return {
            "intent": "product_search",
            "query": query,
            "attributes": attributes,
            "confidence": confidence,
            "features": features,
            "requires_clarification": requires_clarification,
        }

    def _calculate_confidence(self, query: str, attributes: Dict[str, Any]) -> float:
        base_confidence = 0.4
        base_confidence += len(attributes) * 0.15
        if "category" in attributes:
            base_confidence += 0.2
        if "features" in attributes and attributes["features"]:
            base_confidence += 0.1
        if len(query.split()) >= 4:
            base_confidence += 0.1
        return min(0.95, base_confidence)

    def _rank_candidates(
        self, candidates: List[Dict[str, Any]], query_attributes: Dict[str, Any], limit: int = 10
    ) -> List[Dict[str, Any]]:
        scored_candidates = []
        for product in candidates:
            score = self._calculate_relevance_score(product, query_attributes)
            scored_candidates.append({**product, "relevance_score": score})
        ranked = sorted(scored_candidates, key=lambda x: x["relevance_score"], reverse=True)
        if ranked:
            self._log_reasoning(
                "CANDIDATE_RANKING",
                f"Top candidate: {ranked[0]['name']} (score: {ranked[0]['relevance_score']:.2f})",
            )
        return ranked[:limit]

    def _calculate_relevance_score(
        self, product: Dict[str, Any], query_attributes: Dict[str, Any]
    ) -> float:
        score = 0.0
        if "category" in query_attributes and product.get("category") == query_attributes["category"]:
            score += 0.5
        if "color" in query_attributes and product.get("color") == query_attributes["color"]:
            score += 0.3
        if "features" in query_attributes and product.get("features"):
            product_features = (
                product["features"].lower() if isinstance(product["features"], str) else ""
            )
            matching = sum(1 for feat in query_attributes["features"] if feat in product_features)
            if query_attributes["features"]:
                score += (matching / len(query_attributes["features"])) * 0.2
        return min(1.0, score)

    def _extract_user_preferences(self, user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze purchase history and extract user preferences.
        Returns a profile of preferred categories, brands, colors, and price range.
        """
        preferred_categories: Dict[str, int] = {}
        preferred_brands: Dict[str, int] = {}
        preferred_colors: Dict[str, int] = {}
        prices: List[float] = []

        for item in user_history:
            if item.get("category"):
                preferred_categories[item["category"]] = preferred_categories.get(item["category"], 0) + 1
            if item.get("brand"):
                preferred_brands[item["brand"]] = preferred_brands.get(item["brand"], 0) + 1
            if item.get("color"):
                preferred_colors[item["color"]] = preferred_colors.get(item["color"], 0) + 1
            if item.get("price"):
                prices.append(float(item["price"]))

        # Calculate price range
        avg_price = sum(prices) / len(prices) if prices else 0
        
        return {
            "categories": preferred_categories,
            "brands": preferred_brands,
            "colors": preferred_colors,
            "avg_price": avg_price,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0
        }

    def _generate_recommendations(
        self, 
        user_history: List[Dict[str, Any]], 
        product_catalog: List[Dict[str, Any]], 
        limit: int,
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on user preferences extracted from history.
        Scores products by matching category, brand, color, and price range.
        """
        self._log_reasoning(
            "RECOMMENDATION_GENERATION",
            f"Searching {len(product_catalog)} products for matches",
        )

        preferred_categories = user_preferences.get("categories", {})
        preferred_brands = user_preferences.get("brands", {})
        preferred_colors = user_preferences.get("colors", {})
        avg_price = user_preferences.get("avg_price", 0)

        scored_products: List[Dict[str, Any]] = []
        purchased_skus = {item.get("sku") for item in user_history}

        import random

        for product in product_catalog:
            # Skip already purchased products
            if product.get("sku") in purchased_skus:
                continue
                
            score = 0.0
            reason_parts = []
            
            # Category matching (40% weight)
            if product.get("category") in preferred_categories:
                category_score = preferred_categories[product["category"]] * 0.4
                score += category_score
                reason_parts.append(f"matches preferred category ({product['category']})")
            
            # Brand matching (30% weight)
            if product.get("brand") in preferred_brands:
                brand_score = preferred_brands[product["brand"]] * 0.3
                score += brand_score
                reason_parts.append(f"from favorite brand ({product['brand']})")
            
            # Color matching (20% weight)
            if product.get("color") in preferred_colors:
                color_score = preferred_colors[product["color"]] * 0.2
                score += color_score
                reason_parts.append(f"in preferred color ({product['color']})")
            
            # Price range matching (10% weight)
            if avg_price > 0 and product.get("price"):
                price_diff = abs(product["price"] - avg_price) / avg_price
                if price_diff < 0.3:  # Within 30% of average
                    score += 0.1
                    reason_parts.append("within your typical price range")
            
            # Add small randomness for variety
            score += random.random() * 0.05
            
            # Build recommendation reason
            reason = "Complements your style: " + ", ".join(reason_parts) if reason_parts else "Popular item"
            
            scored_products.append({
                **product, 
                "recommendation_score": score,
                "reason": reason
            })

        # Rank by score
        ranked = sorted(scored_products, key=lambda x: x["recommendation_score"], reverse=True)
        
        if ranked:
            self._log_reasoning(
                "RECOMMENDATION_RANKING",
                f"Top recommendation: {ranked[0]['name']} (score: {ranked[0]['recommendation_score']:.2f})",
            )
        
        return ranked[:limit]


class OpenAIChatLLMClient(BaseAgentLLM):
    """OpenAI-powered implementation that uses the DatabaseTool via function calling."""

    def __init__(self) -> None:
        super().__init__(enable_logging=True)
        if OpenAI is None:
            raise RuntimeError(
                "The 'openai' package is not installed. Install backend requirements before using OpenAI provider."
            )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
            )
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.max_tool_iterations = int(os.getenv("LLM_MAX_TOOL_CALLS", "4"))

    def natural_language_search(self, query: str, db_tool: DatabaseTool) -> Dict[str, Any]:
        self.clear_logs()
        instructions = (
            "You are the Retailer AI Search Agent with intelligent semantic matching capabilities. "
            "\n\nSEARCH STRATEGY:\n"
            "1. FIRST: Call get_product_categories to see all available product types\n"
            "2. ANALYZE: Determine which category best matches the user's intent:\n"
            "   - 'hiking boots' → running shoes, sneakers (footwear)\n"
            "   - 'waterproof jacket' → jacket\n"
            "   - 'athletic wear' → shirt, pants\n"
            "3. FETCH: Use fetch_products with the relevant category to get ALL products in that category\n"
            "4. SEMANTIC MATCH: Analyze each product's name, description, and features:\n"
            "   - Trail running shoes with 'waterproof' features match 'hiking boots'\n"
            "   - Running shoes with 'durable' features match 'outdoor footwear'\n"
            "   - Look for semantic similarity, not exact keyword matches\n"
            "5. SCORE: Assign relevance scores (0.0-1.0) based on semantic similarity\n"
            "6. RETURN: Top 3 most relevant products with reasoning\n\n"
            "IMPORTANT: Be creative with matching! 'hiking boots' can match trail running shoes, "
            "'rain jacket' can match waterproof jacket, 'gym clothes' can match athletic wear.\n\n"
            "Response Schema: {\"query\": str, \"intent_summary\": str, \"confidence\": float, "
            "\"requires_clarification\": bool, \"products\": ["
            "{\"sku\": str, \"name\": str, \"score\": float, \"reason\": str}], "
            "\"reasoning\": str}"
        )
        messages = [
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": (
                    "Customer query: '" + query + "'. Provide up to 3 relevant matches using the search strategy."
                ),
            },
        ]

        raw = self._run_agent(messages, db_tool)
        parsed = self._safe_json_parse(raw)
        parsed.setdefault("query", query)
        parsed.setdefault("products", [])
        parsed.setdefault("reasoning", raw)
        parsed["reasoning_logs"] = self.get_reasoning_logs()
        parsed["intent"] = {
            "intent": "product_search",
            "query": query,
            "attributes": parsed.get("attributes", {}),
            "confidence": parsed.get("confidence", 0.5),
            "requires_clarification": parsed.get("requires_clarification", False),
        }
        return parsed

    def recommend_products(self, customer_id: int, limit: int, db_tool: DatabaseTool, order_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recommend products for a customer by analyzing their purchase history.
        Includes fallback to Mock implementation if OpenAI fails or times out.
        
        Args:
            customer_id: Customer ID
            limit: Number of recommendations to return
            db_tool: Database tool for searching products
            order_history: Pre-fetched order history for the customer
        
        Returns:
            List of recommended products with scores and reasons
        """
        self.clear_logs()
        
        # If no order history, fallback to popular products immediately
        if not order_history:
            return db_tool.fetch_popular_products(limit=limit)
        
        # Format order history for AI analysis
        history_summary = self._format_order_history(order_history)
        
        instructions = (
            "You are the Retailer AI recommendation agent with deep expertise in personalized shopping.\\n\\n"
            "## Your Mission\\n"
            "Analyze the customer's purchase history and recommend products that match their preferences.\\n\\n"
            "## Process\\n"
            "1. ANALYZE HISTORY: Review the customer's past purchases to identify patterns\\n"
            "2. EXTRACT PREFERENCES: Determine preferred categories, brands, colors, price range, features\\n"
            "3. SEARCH INVENTORY: Use database_tool.search_products_by_attributes() to find matching products\\n"
            "   - **START SIMPLE**: First call with ONLY category parameter\\n"
            "   - Example: search_products_by_attributes(category='running shoes', limit=10)\\n"
            "   - If results found, select best matches and return\\n"
            "   - If no results, try related categories\\n"
            "4. SELECT BEST: Choose top products that complement past purchases\\n"
            "5. RETURN: Immediately return JSON with recommendations\\n\\n"
            "## Database Tool Usage\\n"
            "- search_products_by_attributes(category=None, color=None, brand=None, features=None, limit=20)\\n"
            "- **CRITICAL**: Use ONLY category parameter first\\n"
            "- Example: search_products_by_attributes(category='sneakers', limit=10)\\n"
            "- **NEVER** search with color+brand+category at once\\n"
            "- Try 2-3 categories max, then return results\\n\\n"
            "## Output Format\\n"
            "Return JSON immediately: {\\\"recommendations\\\": [{\\\"sku\\\": \\\"...\\\", \\\"name\\\": \\\"...\\\", \\\"score\\\": 0.95, \\\"reason\\\": \\\"...\\\"}]}\\n"
            "- score: confidence 0-1 (how well it matches user profile)\\n"
            "- reason: why this product fits the customer's preferences\\n"
        )
        
        messages = [
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": (
                    f"Customer id: {customer_id}\\n\\n"
                    f"Purchase History:\\n{history_summary}\\n\\n"
                    f"Provide exactly {limit} personalized recommendations. "
                    f"Search by category ONLY first, then select the best matches."
                ),
            },
        ]
        
        try:
            raw = self._run_agent(messages, db_tool)
            parsed = self._safe_json_parse(raw)
            recommendations = parsed.get("recommendations") or []
            
            result = []
            for rec in recommendations[:limit]:
                sku = rec.get("sku", "")
                name = rec.get("name", "")
                score = rec.get("score", 0.0)
                reason = rec.get("reason", "")
                if sku and name:
                    result.append({"sku": sku, "name": name, "score": score, "reason": reason})
            
            # If AI returned results, use them
            if result:
                return result
            
            # If AI returned nothing, fallback to Mock
            print("OpenAI returned no recommendations, falling back to Mock implementation")
            return self._fallback_recommendations(customer_id, limit, db_tool, order_history)
            
        except RuntimeError as e:
            # If OpenAI exceeded max iterations, fallback to Mock
            print(f"OpenAI agent failed: {e}, falling back to Mock implementation")
            return self._fallback_recommendations(customer_id, limit, db_tool, order_history)
    
    def _fallback_recommendations(self, customer_id: int, limit: int, db_tool: DatabaseTool, order_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback to Mock-style recommendations when OpenAI fails."""
        # Extract user preferences from order history
        preferred_categories: Dict[str, int] = {}
        preferred_brands: Dict[str, int] = {}
        preferred_colors: Dict[str, int] = {}
        
        for item in order_history:
            if item.get("category"):
                preferred_categories[item["category"]] = preferred_categories.get(item["category"], 0) + 1
            if item.get("brand"):
                preferred_brands[item["brand"]] = preferred_brands.get(item["brand"], 0) + 1
            if item.get("color"):
                preferred_colors[item["color"]] = preferred_colors.get(item["color"], 0) + 1
        
        # Get all products
        product_catalog = db_tool.fetch_products(limit=100)
        purchased_skus = {item.get("sku") for item in order_history}
        
        # Score products
        scored_products = []
        import random
        
        for product in product_catalog:
            if product.get("sku") in purchased_skus:
                continue
            
            score = 0.0
            reason_parts = []
            
            if product.get("category") in preferred_categories:
                score += preferred_categories[product["category"]] * 0.4
                reason_parts.append(f"matches your preferred {product['category']}")
            
            if product.get("brand") in preferred_brands:
                score += preferred_brands[product["brand"]] * 0.3
                reason_parts.append(f"from {product['brand']} brand you like")
            
            if product.get("color") in preferred_colors:
                score += preferred_colors[product["color"]] * 0.2
                reason_parts.append(f"in {product['color']} color")
            
            score += random.random() * 0.1
            
            reason = "Recommended: " + ", ".join(reason_parts) if reason_parts else "Popular choice"
            
            scored_products.append({
                "sku": product.get("sku"),
                "name": product.get("name"),
                "score": score,
                "reason": reason
            })
        
        # Sort and return top N
        ranked = sorted(scored_products, key=lambda x: x["score"], reverse=True)
        return ranked[:limit]
    
    def _format_order_history(self, order_history: List[Dict[str, Any]]) -> str:
        """Format order history for AI analysis."""
        if not order_history:
            return "No previous purchases"
        
        summary_lines = []
        for item in order_history:
            product_name = item.get("product_name", "Unknown")
            category = item.get("category", "Unknown")
            brand = item.get("brand", "")
            color = item.get("color", "")
            price = item.get("price", 0)
            
            line = f"- {product_name} ({category}"
            if brand:
                line += f", {brand}"
            if color:
                line += f", {color}"
            line += f", ${price:.2f})"
            summary_lines.append(line)
        
        return "\n".join(summary_lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_agent(self, messages: List[Dict[str, Any]], db_tool: DatabaseTool) -> str:
        conversation = list(messages)
        tools = [db_tool.tool_definition()]
        for iteration in range(self.max_tool_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=conversation,
                tools=tools,
                tool_choice="auto",
            )
            message = response.choices[0].message

            if message.tool_calls:
                conversation.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": message.tool_calls,
                    }
                )
                for call in message.tool_calls:
                    if call.function.name != db_tool.TOOL_NAME:
                        raise RuntimeError(f"Unknown tool call: {call.function.name}")
                    arguments = json.loads(call.function.arguments or "{}")
                    self._log_reasoning("TOOL_CALL", f"{call.function.name}({arguments})")
                    tool_result = db_tool.handle_tool_call(**arguments)
                    conversation.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": call.function.name,
                            "content": json.dumps(tool_result),
                        }
                    )
                continue

            if message.content:
                self._log_reasoning(
                    "ASSISTANT_RESPONSE",
                    message.content.strip()[:280],
                )
                return message.content

        raise RuntimeError("OpenAI agent exceeded maximum tool iterations without a response")

    def _safe_json_parse(self, content: str) -> Dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"raw_response": content}


def _build_llm_client() -> BaseAgentLLM:
    """Build LLM client based on provider configuration."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return OpenAIChatLLMClient()
    else:
        raise RuntimeError(
            f"LLM_PROVIDER must be set to 'openai'. Current value: '{provider}'"
        )


llm_client: BaseAgentLLM = _build_llm_client()
