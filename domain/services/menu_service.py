"""Menu service for business logic."""

from typing import List, Optional

from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from domain.repositories.menu_repository import MenuRepository


class MenuService:
    """Menu service for business logic."""
    
    def __init__(self, menu_repository: MenuRepository):
        self.menu_repository = menu_repository
    
    async def get_categories(self, active_only: bool = True) -> List[Category]:
        """Get all categories."""
        return await self.menu_repository.list_categories(active_only=active_only)
    
    async def get_category(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        return await self.menu_repository.get_category_by_id(category_id)
    
    async def create_category(self, category: Category) -> Category:
        """Create new category."""
        # Validate category data
        if not await self.validate_category(category):
            raise ValueError("Invalid category data")
        
        return await self.menu_repository.create_category(category)
    
    async def update_category(self, category: Category) -> Category:
        """Update category."""
        # Validate category data
        if not await self.validate_category(category):
            raise ValueError("Invalid category data")
        
        return await self.menu_repository.update_category(category)
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete category."""
        # Check if category has menu items
        items_count = await self.menu_repository.count_menu_items(category_id)
        if items_count > 0:
            raise ValueError("Cannot delete category with menu items")
        
        return await self.menu_repository.delete_category(category_id)
    
    async def get_menu_items(self, category_id: Optional[str] = None, active_only: bool = True) -> List[MenuItem]:
        """Get menu items."""
        if category_id:
            return await self.menu_repository.get_menu_items_by_category(category_id, active_only)
        else:
            return await self.menu_repository.list_menu_items(active_only)
    
    async def get_menu_item(self, item_id: str) -> Optional[MenuItem]:
        """Get menu item by ID."""
        return await self.menu_repository.get_menu_item_by_id(item_id)
    
    async def create_menu_item(self, menu_item: MenuItem) -> MenuItem:
        """Create new menu item."""
        # Validate menu item data
        if not await self.validate_menu_item(menu_item):
            raise ValueError("Invalid menu item data")
        
        # Check if category exists
        category = await self.menu_repository.get_category_by_id(menu_item.category_id)
        if not category:
            raise ValueError(f"Category with id {menu_item.category_id} not found")
        
        return await self.menu_repository.create_menu_item(menu_item)
    
    async def update_menu_item(self, menu_item: MenuItem) -> MenuItem:
        """Update menu item."""
        # Validate menu item data
        if not await self.validate_menu_item(menu_item):
            raise ValueError("Invalid menu item data")
        
        # Check if category exists
        category = await self.menu_repository.get_category_by_id(menu_item.category_id)
        if not category:
            raise ValueError(f"Category with id {menu_item.category_id} not found")
        
        return await self.menu_repository.update_menu_item(menu_item)
    
    async def delete_menu_item(self, item_id: str) -> bool:
        """Delete menu item."""
        return await self.menu_repository.delete_menu_item(item_id)
    
    async def search_menu_items(self, query: str, active_only: bool = True) -> List[MenuItem]:
        """Search menu items."""
        if not query or len(query.strip()) < 2:
            return []
        
        return await self.menu_repository.search_menu_items(query.strip(), active_only)
    
    async def get_popular_items(self, limit: int = 10) -> List[MenuItem]:
        """Get popular menu items."""
        # Get all menu items and filter popular ones
        all_items = await self.menu_repository.list_menu_items(active_only=True)
        popular_items = [item for item in all_items if item.is_popular]
        
        # Sort by sort_order and limit
        popular_items.sort(key=lambda x: x.sort_order)
        return popular_items[:limit]
    
    async def validate_menu_item(self, menu_item: MenuItem) -> bool:
        """Validate menu item data."""
        if not menu_item.name or len(menu_item.name.strip()) < 2:
            return False
        
        if menu_item.price < 0:
            return False
        
        if menu_item.calories is not None and menu_item.calories < 0:
            return False
        
        return True
    
    async def validate_category(self, category: Category) -> bool:
        """Validate category data."""
        if not category.name or len(category.name.strip()) < 2:
            return False
        
        return True