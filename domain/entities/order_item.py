"""Order item entity for the application."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from domain.entities.menu_item import MenuItem


@dataclass
class OrderItem:
    """Order item entity."""
    order_item_id: str
    order_id: str
    menu_item: Optional[MenuItem] = None
    item_id: Optional[str] = None
    name: Optional[str] = None
    quantity: int = 1
    price: int = 0
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def total_price(self) -> int:
        """Get total price for this item."""
        return self.price * self.quantity
    
    def get_display_name(self) -> str:
        """Get display name."""
        if self.name:
            return self.name
        return self.menu_item.name if self.menu_item else ""
    
    def get_price_display(self) -> str:
        """Get price display."""
        return f"{self.total_price // 100}₽"
    
    def get_quantity_display(self) -> str:
        """Get quantity display."""
        return f"{self.quantity} шт"
    
    def get_comment_display(self) -> str:
        """Get comment display."""
        return self.comment or "Без комментария"