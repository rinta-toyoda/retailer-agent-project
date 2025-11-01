"""
Dummy Stripe Client - Payment Gateway Simulation
Implements the mock payment gateway as specified in Instructions.md.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

import uuid
from typing import Dict, Any


class StripeClientDummy:
    """
    Mock Stripe client that simulates checkout sessions and payment capture.
    Used in Checkout flows (sequence diagrams: /checkout/prepare, /checkout/finalize).

    This is a dummy implementation that always succeeds, avoiding external dependencies.
    """

    def __init__(self, api_key: str = "dummy_stripe_key"):
        """
        Initialize dummy Stripe client.

        Args:
            api_key: Mock API key (not used in dummy implementation)
        """
        self.api_key = api_key
        self.sessions = {}  # In-memory session storage

    def create_session(self, cart_id: str, amount: float = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a dummy checkout session.
        Maps to CheckoutService.createSession() in sequence diagram.

        Args:
            cart_id: Unique cart identifier
            amount: Optional amount (for validation)
            metadata: Optional metadata to attach to session

        Returns:
            Dictionary with session id and redirect URL
        """
        session_id = f"dummy_session_{cart_id}_{uuid.uuid4().hex[:8]}"
        payment_intent_id = f"pi_{uuid.uuid4().hex}"

        session = {
            "id": session_id,
            "payment_intent_id": payment_intent_id,
            "url": f"/dummy/checkout/{cart_id}",
            "status": "open",
            "cart_id": cart_id,
            "amount": amount,
            "metadata": metadata or {},
        }

        # Store session for later retrieval
        self.sessions[session_id] = session
        self.sessions[payment_intent_id] = session  # Allow lookup by payment intent

        return {
            "id": session_id,
            "payment_intent_id": payment_intent_id,
            "url": session["url"],
        }

    def capture(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Capture a payment (finalize checkout).
        Maps to CheckoutService.finalize() → StripeClient.capture() in sequence diagram.

        Args:
            payment_intent_id: Payment intent ID from session

        Returns:
            Dictionary with payment status and receipt
        """
        # Simulate successful payment capture (90% success rate for realism)
        import random
        success = random.random() > 0.1  # 90% success rate

        if success:
            receipt_id = f"receipt_{uuid.uuid4().hex[:12]}"
            return {
                "status": "success",
                "payment_intent_id": payment_intent_id,
                "receipt": f"https://stripe.com/receipts/{receipt_id}",
                "receipt_id": receipt_id,
                "captured": True,
            }
        else:
            return {
                "status": "failed",
                "payment_intent_id": payment_intent_id,
                "error": "card_declined",
                "error_message": "Your card was declined. Please try another payment method.",
                "captured": False,
            }

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session or payment intent ID

        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)

    def refund(self, payment_intent_id: str, amount: float = None) -> Dict[str, Any]:
        """
        Process a refund (not required for Stage 1, but useful for completeness).

        Args:
            payment_intent_id: Payment intent to refund
            amount: Optional partial refund amount

        Returns:
            Refund status
        """
        refund_id = f"refund_{uuid.uuid4().hex[:12]}"
        return {
            "status": "success",
            "refund_id": refund_id,
            "payment_intent_id": payment_intent_id,
            "amount": amount,
        }


# Global instance
stripe_client = StripeClientDummy()
