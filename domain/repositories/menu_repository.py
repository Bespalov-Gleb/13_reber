"""Menu repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.category import Category
from domain.entities.menu_item import MenuItem


class MenuRepository(ABC):
    """Menu repository interface."""
    
    # Category methods
    @abstractmethod
    async def create_category(self, category: Category) -> Category:
        """Create new category."""
        pass
    
    @abstractmethod
    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        pass
    
    @abstractmethod
    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        pass
    
    @abstractmethod
    async def list_categories(self, active_only: bool = True) -> List[Category]:
        """List all categories."""
        pass
    
    @abstractmethod
    async def update_category(self, category: Category) -> Category:
        """Update category."""
        pass
    
    @abstractmethod
    async def delete_category(self, category_id: str) -> bool:
        """Delete category."""
        pass
    
    # Menu item methods
    @abstractmethod
    async def create_menu_item(self, menu_item: MenuItem) -> MenuItem:
        """Create new menu item."""
        pass
    
    @abstractmethod
    async def get_menu_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """Get menu item by ID."""
        pass
    
    @abstractmethod
    async def get_menu_items_by_category(self, category_id: str, active_only: bool = True) -> List[MenuItem]:
        """Get menu items by category."""
        pass
    
    @abstractmethod
    async def list_menu_items(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[MenuItem]:
        """List all menu items."""
        pass
    
    @abstractmethod
    async def search_menu_items(self, query: str, active_only: bool = True) -> List[MenuItem]:
        """Search menu items by name or description."""
        pass
    
    @abstractmethod
    async def update_menu_item(self, menu_item: MenuItem) -> MenuItem:
        """Update menu item."""
        pass
    
    @abstractmethod
    async def delete_menu_item(self, item_id: str) -> bool:
        """Delete menu item."""
        pass
    
    @abstractmethod
    async def count_menu_items(self, category_id: Optional[str] = None) -> int:
        """Count menu items."""
        pass
    
    @abstractmethod
    async def list_categories(self) -> List[Category]:
        """List all categories without filters."""
        pass
    
    @abstractmethod
    async def list_menu_items(self) -> List[MenuItem]:
        """List all menu items without filters."""
        pass