"""Product schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    brand: Optional[str]
    color: Optional[str]

    class Config:
        from_attributes = True


class ProductUpdateRequest(BaseModel):
    """Request schema for updating product information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=50)
    features: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Premium Running Shoes",
                "description": "High-performance running shoes with advanced cushioning",
                "price": 129.99,
                "category": "Footwear",
                "brand": "Nike",
                "color": "Black",
                "size": "US 10",
                "features": "Breathable mesh, Responsive cushioning"
            }
        }
