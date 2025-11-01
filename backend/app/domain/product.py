"""
Product Domain Model
Represents products in the retailer catalog.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
import os

from app.infra.database import Base

FALLBACK_IMAGE_BASE = os.getenv("FALLBACK_PRODUCT_IMAGE_BASE", "/product-images")
FALLBACK_IMAGES = [f"{FALLBACK_IMAGE_BASE}/shoe-{i:02d}.png" for i in range(1, 11)]


class Product(Base):
    """
    Product entity representing items available for purchase.
    Maps to the Product concept in the provided sequence diagrams.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)  # Decimal for precision
    category = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True)

    # Product attributes for AI agent search
    color = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    features = Column(Text, nullable=True)  # JSON string of features

    # Image storage (S3 URL)
    image_url = Column(String(500), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}', price={self.price})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "category": self.category,
            "brand": self.brand,
            "color": self.color,
            "size": self.size,
            "features": self.features,
            "image_url": self.image_url or self._fallback_image_url(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def _fallback_image_url(self) -> str:
        if not FALLBACK_IMAGES:
            return ""
        index = (self.id or 0) % len(FALLBACK_IMAGES)
        return FALLBACK_IMAGES[index]
