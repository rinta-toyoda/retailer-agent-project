"""
Checkout Service - Payment Flow
Implements Checkout prepare/finalize flows from sequence diagrams.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.order import Order, OrderItem
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.services.inventory_service import InventoryService
from app.services.transaction_validation_service import TransactionValidationService
from app.infra.stripe_client_dummy import stripe_client


class CheckoutService:
    """
    Checkout business logic implementing:
    - Checkout - /checkout/prepare (create session, reserve stock)
    - Checkout - /checkout/finalize (capture payment, commit stock, create order)
    """

    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.order_repo = OrderRepository(db)
        self.inventory_service = InventoryService(db)
        self.validation_service = TransactionValidationService(db)

    def create_session(self, cart_id: str) -> dict:
        """
        Prepare checkout (Checkout - /checkout/prepare sequence diagram).

        Flow:
        1. Validate cart and reserve stock
        2. Create Stripe session
        3. Return redirect URL

        Args:
            cart_id: Cart to checkout

        Returns:
            Session with redirect URL
        """
        # Step 1: Validate cart and create reservations
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty or not found")

        self.validation_service.validate_cart(cart_id)

        # Step 2: Create Stripe session
        session = stripe_client.create_session(
            cart_id=cart_id,
            amount=float(cart.total()),
            metadata={"customer_id": cart.customer_id}
        )

        return {
            "session_id": session["id"],
            "payment_intent_id": session["payment_intent_id"],
            "redirect_url": session["url"]
        }

    def finalize(self, payment_intent_id: str, cart_id: str, customer_id: int) -> Order:
        """
        Finalize checkout (Checkout - /checkout/finalize sequence diagram).

        Flow:
        1. Capture payment
        2. On success: commit reservations, create order
        3. On failure: release reservations, return error

        Args:
            payment_intent_id: Stripe payment intent
            cart_id: Cart identifier
            customer_id: Customer ID

        Returns:
            Created order

        Raises:
            ValueError: If payment fails
        """
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if not cart:
            raise ValueError("Cart not found")

        # Step 1: Capture payment
        receipt = stripe_client.capture(payment_intent_id)

        if receipt["status"] == "success":
            # Step 2a: Commit stock reservations
            for item in cart.items:
                self.inventory_service.commit(item.product.sku, item.quantity)

            # Step 2b: Create order
            order = Order(
                order_number=f"ORD-{uuid.uuid4().hex[:12].upper()}",
                customer_id=customer_id,
                cart_id=cart_id,
                payment_intent_id=payment_intent_id,
                payment_status="PAID",
                receipt_url=receipt.get("receipt"),
                subtotal=cart.total(),
                tax=Decimal("0"),
                total=cart.total(),
                status="PROCESSING",
                paid_at=datetime.utcnow()
            )
            order = self.order_repo.create(order)

            # Add order items
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    sku=cart_item.product.sku,
                    name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    subtotal=cart_item.subtotal()
                )
                self.order_repo.add_item(order_item)

            # Clear cart items and mark as checked out
            self.cart_repo.clear_cart(cart)
            cart.status = "checked_out"
            self.cart_repo.update(cart)

            return order
        else:
            # Step 3: Release reservations on payment failure
            for item in cart.items:
                self.inventory_service.release(item.product.sku, item.quantity)

            raise ValueError(f"Payment failed: {receipt.get('error_message', 'Unknown error')}")
