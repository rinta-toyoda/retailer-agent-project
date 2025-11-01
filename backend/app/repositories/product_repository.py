"""
Product Repository - Data Access Layer
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.product import Product


class ProductRepository:
    """Repository for Product entity operations."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, product_id: int) -> Optional[Product]:
        """Find product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def find_by_sku(self, sku: str) -> Optional[Product]:
        """Find product by SKU."""
        return self.db.query(Product).filter(Product.sku == sku).first()

    def find_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all active products."""
        return self.db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Product]:
        """Search products by name or description."""
        search = f"%{query}%"
        return (
            self.db.query(Product)
            .filter(
                Product.is_active == True,
                (Product.name.ilike(search) | Product.description.ilike(search))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def find_by_category(self, category: str) -> List[Product]:
        """Find products by category."""
        return self.db.query(Product).filter(Product.category == category, Product.is_active == True).all()

    def create(self, product: Product) -> Product:
        """Create new product."""
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        """Update product."""
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> bool:
        """Soft delete product (set is_active = False)."""
        product = self.find_by_id(product_id)
        if product:
            product.is_active = False
            self.db.commit()
            return True
        return False
