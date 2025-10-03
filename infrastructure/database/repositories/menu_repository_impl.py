"""Menu repository implementation."""

from typing import List, Optional

from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from domain.repositories.menu_repository import MenuRepository
from infrastructure.database.models.category_model import CategoryModel
from infrastructure.database.models.menu_item_model import MenuItemModel
from infrastructure.database.models.cart_model import CartItemModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.orm import selectinload


class MenuRepositoryImpl(MenuRepository):
    """Menu repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # Category methods
    async def create_category(self, category: Category) -> Category:
        """Create new category."""
        db_category = CategoryModel(
            id=category.category_id,
            name=category.name,
            description=category.description,
            image_url=category.image_url,
            sort_order=category.sort_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
        self.session.add(db_category)
        await self.session.flush()
        await self.session.refresh(db_category)
        
        return self._category_model_to_entity(db_category)
    
    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        db_category = result.scalar_one_or_none()
        
        if db_category:
            return self._category_model_to_entity(db_category)
        return None
    
    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.name == name)
        )
        db_category = result.scalar_one_or_none()
        
        if db_category:
            return self._category_model_to_entity(db_category)
        return None
    
    async def list_categories(self, active_only: bool = True) -> List[Category]:
        """List all categories."""
        query = select(CategoryModel).order_by(CategoryModel.sort_order, CategoryModel.name)
        
        if active_only:
            query = query.where(CategoryModel.is_active == True)
        
        result = await self.session.execute(query)
        db_categories = result.scalars().all()
        
        return [self._category_model_to_entity(cat) for cat in db_categories]
    
    async def update_category(self, category: Category) -> Category:
        """Update category."""
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == category.category_id)
        )
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            raise ValueError(f"Category with id {category.category_id} not found")
        
        db_category.name = category.name
        db_category.description = category.description
        db_category.image_url = category.image_url
        db_category.sort_order = category.sort_order
        db_category.is_active = category.is_active
        db_category.updated_at = category.updated_at
        
        await self.session.flush()
        await self.session.refresh(db_category)
        
        return self._category_model_to_entity(db_category)
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete category."""
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            return False
        
        await self.session.delete(db_category)
        await self.session.flush()
        return True
    
    # Menu item methods
    async def create_menu_item(self, menu_item: MenuItem) -> MenuItem:
        """Create new menu item."""
        db_item = MenuItemModel(
            id=menu_item.item_id,
            category_id=menu_item.category_id,
            name=menu_item.name,
            description=menu_item.description,
            price=menu_item.price,
            image_url=menu_item.image_url,
            ingredients=menu_item.ingredients,
            allergens=menu_item.allergens,
            weight=menu_item.weight,
            calories=menu_item.calories,
            is_available=menu_item.is_available,
            is_popular=menu_item.is_popular,
            sort_order=menu_item.sort_order,
            created_at=menu_item.created_at,
            updated_at=menu_item.updated_at
        )
        
        self.session.add(db_item)
        await self.session.flush()
        await self.session.refresh(db_item)
        
        return self._menu_item_model_to_entity(db_item)
    
    async def get_menu_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """Get menu item by ID."""
        result = await self.session.execute(
            select(MenuItemModel).where(MenuItemModel.id == item_id)
        )
        db_item = result.scalar_one_or_none()
        
        if db_item:
            return self._menu_item_model_to_entity(db_item)
        return None
    
    async def get_menu_items_by_category(self, category_id: str, active_only: bool = True) -> List[MenuItem]:
        """Get menu items by category."""
        query = select(MenuItemModel).where(MenuItemModel.category_id == category_id)
        
        if active_only:
            query = query.where(MenuItemModel.is_available == True)
        
        query = query.order_by(MenuItemModel.sort_order, MenuItemModel.name)
        
        result = await self.session.execute(query)
        db_items = result.scalars().all()
        
        return [self._menu_item_model_to_entity(item) for item in db_items]
    
    async def list_menu_items(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[MenuItem]:
        """List all menu items."""
        query = select(MenuItemModel).offset(offset).limit(limit)
        
        if active_only:
            query = query.where(MenuItemModel.is_available == True)
        
        query = query.order_by(MenuItemModel.sort_order, MenuItemModel.name)
        
        result = await self.session.execute(query)
        db_items = result.scalars().all()
        
        return [self._menu_item_model_to_entity(item) for item in db_items]
    
    async def search_menu_items(self, query: str, active_only: bool = True) -> List[MenuItem]:
        """Search menu items by name or description."""
        search_query = select(MenuItemModel).where(
            or_(
                MenuItemModel.name.ilike(f"%{query}%"),
                MenuItemModel.description.ilike(f"%{query}%")
            )
        )
        
        if active_only:
            search_query = search_query.where(MenuItemModel.is_available == True)
        
        search_query = search_query.order_by(MenuItemModel.sort_order, MenuItemModel.name)
        
        result = await self.session.execute(search_query)
        db_items = result.scalars().all()
        
        return [self._menu_item_model_to_entity(item) for item in db_items]
    
    async def update_menu_item(self, menu_item: MenuItem) -> MenuItem:
        """Update menu item."""
        result = await self.session.execute(
            select(MenuItemModel).where(MenuItemModel.id == menu_item.item_id)
        )
        db_item = result.scalar_one_or_none()
        
        if not db_item:
            raise ValueError(f"Menu item with id {menu_item.item_id} not found")
        
        db_item.category_id = menu_item.category_id
        db_item.name = menu_item.name
        db_item.description = menu_item.description
        db_item.price = menu_item.price
        db_item.image_url = menu_item.image_url
        db_item.ingredients = menu_item.ingredients
        db_item.allergens = menu_item.allergens
        db_item.weight = menu_item.weight
        db_item.calories = menu_item.calories
        db_item.is_available = menu_item.is_available
        db_item.is_popular = menu_item.is_popular
        db_item.sort_order = menu_item.sort_order
        db_item.updated_at = menu_item.updated_at
        
        await self.session.flush()
        await self.session.refresh(db_item)
        
        return self._menu_item_model_to_entity(db_item)
    
    async def delete_menu_item(self, item_id: str) -> bool:
        """Delete menu item."""
        result = await self.session.execute(
            select(MenuItemModel).where(MenuItemModel.id == item_id)
        )
        db_item = result.scalar_one_or_none()
        
        if not db_item:
            return False
        
        # Remove cart references first to satisfy FK constraints
        await self.session.execute(
            delete(CartItemModel).where(CartItemModel.menu_item_id == item_id)
        )
        await self.session.flush()
        # Now delete the menu item
        await self.session.delete(db_item)
        await self.session.flush()
        return True
    
    async def count_menu_items(self, category_id: Optional[str] = None) -> int:
        """Count menu items."""
        query = select(func.count(MenuItemModel.id))
        
        if category_id:
            query = query.where(MenuItemModel.category_id == category_id)
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    # Helper methods
    def _category_model_to_entity(self, db_category: CategoryModel) -> Category:
        """Convert CategoryModel to Category entity."""
        return Category(
            category_id=db_category.id,
            name=db_category.name,
            description=db_category.description,
            image_url=db_category.image_url,
            sort_order=db_category.sort_order,
            is_active=db_category.is_active,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at
        )
    
    def _menu_item_model_to_entity(self, db_item: MenuItemModel) -> MenuItem:
        """Convert MenuItemModel to MenuItem entity."""
        return MenuItem(
            item_id=db_item.id,
            category_id=db_item.category_id,
            name=db_item.name,
            description=db_item.description,
            price=db_item.price,
            image_url=db_item.image_url,
            ingredients=db_item.ingredients,
            allergens=db_item.allergens,
            weight=db_item.weight,
            calories=db_item.calories,
            is_available=db_item.is_available,
            is_popular=db_item.is_popular,
            sort_order=db_item.sort_order,
            created_at=db_item.created_at,
            updated_at=db_item.updated_at
        )