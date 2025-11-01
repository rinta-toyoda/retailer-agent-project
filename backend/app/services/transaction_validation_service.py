"""
Transaction Validation Service
Validates cart before checkout and creates reservations.
"""

from sqlalchemy.orm import Session
from app.repositories.cart_repository import CartRepository
from app.services.inventory_service import InventoryService


class TransactionValidationService:
    """Validates transactions and creates stock reservations."""

    def __init__(self, db: Session):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.inventory_service = InventoryService(db)

    def validate_cart(self, cart_id: str) -> bool:
        """
        Validate cart and create stock reservations.
        Maps to TransactionValidationService in checkout/prepare flow.
        """
        cart = self.cart_repo.find_by_cart_id(cart_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty")

        # Create reservations for each cart item
        for item in cart.items:
            self.inventory_service.create_reservation(
                sku=item.product.sku,
                qty=item.quantity,
                cart_id=cart_id
            )

        return True
