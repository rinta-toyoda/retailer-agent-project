"""Cart schemas."""
from pydantic import BaseModel
from typing import List


class AddToCartRequest(BaseModel):
    cart_id: str
    product_id: int
    quantity: int
    customer_id: int | None = None


class RemoveFromCartRequest(BaseModel):
    cart_id: str
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    subtotal: float


class CartResponse(BaseModel):
    cart_id: str
    items: List[dict]
    total: float
    item_count: int
