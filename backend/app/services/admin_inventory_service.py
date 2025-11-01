"""
Admin Inventory Service
Manual stock adjustments for admin panel.
"""

from sqlalchemy.orm import Session
from app.repositories.inventory_repository import InventoryRepository


class AdminInventoryService:
    """Admin inventory management (manual stock updates)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def set_stock(self, sku: str, new_quantity: int) -> dict:
        """
        Set absolute stock quantity (replaces increment/decrement approach).

        Args:
            sku: Product SKU
            new_quantity: New absolute quantity to set

        Returns:
            Updated inventory info
        """
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        inventory_item = self.repo.find_by_sku(sku)
        if not inventory_item:
            raise ValueError(f"SKU {sku} not found")

        # Set the new quantity directly
        inventory_item.quantity = new_quantity
        self.repo.update(inventory_item)

        return inventory_item.to_dict()

    def update_stock(self, sku: str, qty_delta: int) -> dict:
        """
        Manual stock update (Admin - Manual Stock Update sequence diagram).

        Args:
            sku: Product SKU
            qty_delta: Quantity change (positive = add, negative = subtract)

        Returns:
            Updated inventory info
        """
        inventory_item = self.repo.find_by_sku(sku)
        if not inventory_item:
            raise ValueError(f"SKU {sku} not found")

        if qty_delta > 0:
            inventory_item.increment(qty_delta)
        else:
            inventory_item.decrement(abs(qty_delta))

        self.repo.update(inventory_item)

        return inventory_item.to_dict()

    def get_all_inventory(self) -> list:
        """Get all inventory items with product details."""
        from app.domain.product import Product
        
        items = self.repo.find_all()
        result = []
        
        for item in items:
            item_dict = item.to_dict()
            
            # Fetch product details
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                item_dict["product"] = {
                    "name": product.name,
                    "description": product.description,
                    "image_url": product.image_url,
                    "brand": product.brand,
                    "category": product.category,
                }
            
            result.append(item_dict)
        
        return result
