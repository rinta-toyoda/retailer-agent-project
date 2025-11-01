"""Checkout schemas."""
from pydantic import BaseModel


class CheckoutPrepareRequest(BaseModel):
    cart_id: str


class CheckoutPrepareResponse(BaseModel):
    session_id: str
    payment_intent_id: str
    redirect_url: str


class CheckoutFinalizeRequest(BaseModel):
    payment_intent_id: str
    cart_id: str
    customer_id: int


class OrderResponse(BaseModel):
    order_number: str
    status: str
    total: float
    payment_status: str
