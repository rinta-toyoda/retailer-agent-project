"""
Inventory Service - Stock Management
Implements stock reservation/commit/release for checkout flow.
"""

import uuid
from sqlalchemy.orm import Session
from app.domain.inventory_item import StockReservation
from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    """Inventory management service."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def create_reservation(self, sku: str, qty: int, cart_id: str = None) -> str:
        """Reserve stock for checkout."""
        inventory_item = self.repo.find_by_sku(sku)
        if not inventory_item:
            raise ValueError(f"Inventory item {sku} not found")

        if not inventory_item.reserve(qty):
            raise ValueError(f"Insufficient stock for {sku}")

        reservation = StockReservation(
            reservation_id=str(uuid.uuid4()),
            inventory_item_id=inventory_item.id,
            sku=sku,
            quantity=qty,
            cart_id=cart_id,
            status="RESERVED"
        )
        self.repo.create_reservation(reservation)
        self.repo.update(inventory_item)

        return reservation.reservation_id

    def commit(self, sku: str, qty: int) -> None:
        """Commit reserved stock (after successful payment)."""
        inventory_item = self.repo.find_by_sku(sku)
        if inventory_item:
            inventory_item.commit(qty)
            self.repo.update(inventory_item)

    def release(self, sku: str, qty: int) -> None:
        """Release reserved stock (after payment failure)."""
        inventory_item = self.repo.find_by_sku(sku)
        if inventory_item:
            inventory_item.release(qty)
            self.repo.update(inventory_item)

    def get_availability(self, sku: str) -> int:
        """Get available stock for SKU."""
        inventory_item = self.repo.find_by_sku(sku)
        return inventory_item.available_quantity() if inventory_item else 0
