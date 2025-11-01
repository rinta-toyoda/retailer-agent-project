"""
Inventory Repository - Data Access Layer
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.inventory_item import InventoryItem, StockReservation


class InventoryRepository:
    """Repository for InventoryItem and StockReservation operations."""

    def __init__(self, db: Session):
        self.db = db

    def find_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Find inventory item by SKU."""
        return self.db.query(InventoryItem).filter(InventoryItem.sku == sku).first()

    def find_by_product_id(self, product_id: int) -> Optional[InventoryItem]:
        """Find inventory item by product ID."""
        return self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()

    def find_all(self) -> List[InventoryItem]:
        """Find all inventory items, ordered by SKU for consistent ordering."""
        return self.db.query(InventoryItem).order_by(InventoryItem.sku).all()

    def find_all_low_stock(self) -> List[InventoryItem]:
        """Find all items below low stock threshold."""
        return self.db.query(InventoryItem).filter(
            InventoryItem.quantity < InventoryItem.low_stock_threshold
        ).all()

    def create(self, inventory_item: InventoryItem) -> InventoryItem:
        """Create inventory item."""
        self.db.add(inventory_item)
        self.db.commit()
        self.db.refresh(inventory_item)
        return inventory_item

    def update(self, inventory_item: InventoryItem) -> InventoryItem:
        """Update inventory item."""
        self.db.commit()
        self.db.refresh(inventory_item)
        return inventory_item

    # Stock Reservation operations
    def create_reservation(self, reservation: StockReservation) -> StockReservation:
        """Create stock reservation."""
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def find_reservation(self, reservation_id: str) -> Optional[StockReservation]:
        """Find reservation by ID."""
        return self.db.query(StockReservation).filter(
            StockReservation.reservation_id == reservation_id
        ).first()

    def find_reservations_by_cart(self, cart_id: str) -> List[StockReservation]:
        """Find all active reservations for a cart."""
        return self.db.query(StockReservation).filter(
            StockReservation.cart_id == cart_id,
            StockReservation.is_active == True
        ).all()

    def update_reservation(self, reservation: StockReservation) -> StockReservation:
        """Update reservation."""
        self.db.commit()
        self.db.refresh(reservation)
        return reservation
