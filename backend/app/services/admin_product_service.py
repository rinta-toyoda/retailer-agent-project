"""
Admin Product Service
Product management operations for admin panel.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductUpdateRequest


class AdminProductService:
    """Admin product management (CRUD operations)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def update_product(self, product_id: int, update_data: ProductUpdateRequest) -> dict:
        """
        Update product information.

        Args:
            product_id: Product ID
            update_data: Fields to update (only provided fields will be updated)

        Returns:
            Updated product info

        Raises:
            ValueError: If product not found
        """
        product = self.repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(product, field, value)

        self.repo.update(product)
        return product.to_dict()

    def get_all_products(self, skip: int = 0, limit: int = 100) -> list:
        """Get all products (including inactive for admin view)."""
        from app.domain.product import Product
        all_products = self.db.query(Product).offset(skip).limit(limit).all()
        return [p.to_dict() for p in all_products]

    def get_product(self, product_id: int) -> dict:
        """Get single product by ID."""
        product = self.repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        return product.to_dict()
