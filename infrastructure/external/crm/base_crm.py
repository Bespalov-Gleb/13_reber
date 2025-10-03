"""Base CRM provider class."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.order import Order
from domain.entities.menu_item import MenuItem
from domain.entities.category import Category


class BaseCRMProvider(ABC):
    """Base class for CRM providers."""
    
    @abstractmethod
    async def create_order(self, order: Order) -> bool:
        """Create order in CRM system."""
        pass
    
    @abstractmethod
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in CRM system."""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Optional[str]:
        """Get order status from CRM system."""
        pass
    
    @abstractmethod
    async def sync_menu_items(self, items: List[MenuItem]) -> bool:
        """Sync menu items with CRM system."""
        pass
    
    @abstractmethod
    async def sync_categories(self, categories: List[Category]) -> bool:
        """Sync categories with CRM system."""
        pass
    
    @abstractmethod
    async def get_menu_items(self) -> List[MenuItem]:
        """Get menu items from CRM system."""
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[Category]:
        """Get categories from CRM system."""
        pass
    
    @abstractmethod
    async def update_menu_item(self, item: MenuItem) -> bool:
        """Update menu item in CRM system."""
        pass
    
    @abstractmethod
    async def update_category(self, category: Category) -> bool:
        """Update category in CRM system."""
        pass
    
    @abstractmethod
    async def delete_menu_item(self, item_id: str) -> bool:
        """Delete menu item from CRM system."""
        pass
    
    @abstractmethod
    async def delete_category(self, category_id: str) -> bool:
        """Delete category from CRM system."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to CRM system."""
        pass