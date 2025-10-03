"""Cart repository implementation."""

from typing import List, Optional
from datetime import datetime

from domain.entities.cart import Cart, CartItem
from domain.entities.menu_item import MenuItem
from domain.repositories.cart_repository import CartRepository
from infrastructure.database.models.cart_model import CartModel, CartItemModel
from infrastructure.database.models.menu_item_model import MenuItemModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload


class CartRepositoryImpl(CartRepository):
    """Cart repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, cart: Cart) -> Cart:
        """Create new cart."""
        db_cart = CartModel(
            id=cart.cart_id,
            user_id=cart.user_id,
            created_at=cart.created_at or datetime.now(),
            updated_at=cart.updated_at or datetime.now()
        )
        
        self.session.add(db_cart)
        await self.session.flush()
        await self.session.refresh(db_cart)
        
        return self._model_to_entity(db_cart)
    
    async def get_by_id(self, cart_id: str) -> Optional[Cart]:
        """Get cart by ID."""
        result = await self.session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items).selectinload(CartItemModel.menu_item))
            .where(CartModel.id == cart_id)
        )
        db_cart = result.scalar_one_or_none()
        
        if db_cart:
            return self._model_to_entity(db_cart)
        return None
    
    async def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        """Get cart by user ID."""
        result = await self.session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items).selectinload(CartItemModel.menu_item))
            .where(CartModel.user_id == user_id)
        )
        db_cart = result.scalar_one_or_none()
        
        if db_cart:
            return self._model_to_entity(db_cart)
        return None
    
    async def update(self, cart: Cart) -> Cart:
        """Update cart."""
        result = await self.session.execute(
            select(CartModel).where(CartModel.id == cart.cart_id)
        )
        db_cart = result.scalar_one_or_none()
        
        if not db_cart:
            raise ValueError(f"Cart with id {cart.cart_id} not found")
        
        db_cart.updated_at = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(db_cart)
        
        return self._model_to_entity(db_cart)
    
    async def delete(self, cart_id: str) -> bool:
        """Delete cart."""
        result = await self.session.execute(
            select(CartModel).where(CartModel.id == cart_id)
        )
        db_cart = result.scalar_one_or_none()
        
        if not db_cart:
            return False
        
        await self.session.delete(db_cart)
        await self.session.flush()
        return True
    
    async def clear_user_cart(self, user_id: str) -> bool:
        """Clear user's cart."""
        # Delete all cart items for user
        result = await self.session.execute(
            select(CartModel).where(CartModel.user_id == user_id)
        )
        db_cart = result.scalar_one_or_none()
        
        if not db_cart:
            return False
        
        # Delete cart items
        await self.session.execute(
            delete(CartItemModel).where(CartItemModel.cart_id == db_cart.id)
        )
        
        # Delete cart
        await self.session.delete(db_cart)
        await self.session.flush()
        return True
    
    async def add_item(self, cart_id: str, item_id: str, quantity: int, comment: Optional[str] = None) -> bool:
        """Add item to cart."""
        # Check if item already exists in cart
        result = await self.session.execute(
            select(CartItemModel).where(
                CartItemModel.cart_id == cart_id,
                CartItemModel.menu_item_id == item_id
            )
        )
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            existing_item.updated_at = datetime.now()
            if comment:
                existing_item.comment = comment
        else:
            # Create new cart item
            cart_item = CartItemModel(
                id=f"{cart_id}_{item_id}_{int(datetime.now().timestamp())}",
                cart_id=cart_id,
                menu_item_id=item_id,
                quantity=quantity,
                comment=comment,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.session.add(cart_item)
        
        await self.session.flush()
        return True
    
    async def remove_item(self, cart_id: str, item_id: str) -> bool:
        """Remove item from cart."""
        result = await self.session.execute(
            select(CartItemModel).where(
                CartItemModel.cart_id == cart_id,
                CartItemModel.menu_item_id == item_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            return False
        
        await self.session.delete(cart_item)
        await self.session.flush()
        return True
    
    async def update_item_quantity(self, cart_id: str, item_id: str, quantity: int) -> bool:
        """Update item quantity in cart."""
        result = await self.session.execute(
            select(CartItemModel).where(
                CartItemModel.cart_id == cart_id,
                CartItemModel.menu_item_id == item_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            return False
        
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            await self.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
            cart_item.updated_at = datetime.now()
        
        await self.session.flush()
        return True
    
    async def get_cart_total(self, cart_id: str) -> int:
        """Get cart total amount."""
        result = await self.session.execute(
            select(CartItemModel)
            .options(selectinload(CartItemModel.menu_item))
            .where(CartItemModel.cart_id == cart_id)
        )
        cart_items = result.scalars().all()
        
        total = 0
        for item in cart_items:
            total += item.menu_item.price * item.quantity
        
        return total
    
    def _model_to_entity(self, db_cart: CartModel) -> Cart:
        """Convert CartModel to domain Cart without triggering lazy loads."""
        items_dict: dict[str, CartItem] = {}
        items_rel = db_cart.__dict__.get("items", []) or []
        for db_item in items_rel:
            menu = getattr(db_item, "menu_item", None)
            if menu is None:
                continue
            domain_item = CartItem(
                item_id=menu.id,
                name=menu.name,
                price=menu.price,
                quantity=db_item.quantity,
                comment=db_item.comment,
            )
            items_dict[menu.id] = domain_item
        
        return Cart(
            cart_id=db_cart.id,
            user_id=db_cart.user_id,
            items=items_dict,
            created_at=db_cart.created_at,
            updated_at=db_cart.updated_at
        )
    
    def _menu_item_model_to_entity(self, db_item: MenuItemModel) -> MenuItem:
        """Convert MenuItemModel to MenuItem entity."""
        from domain.entities.menu_item import MenuItem
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
    
    async def count_items(self, cart_id: str) -> int:
        """Count items in cart."""
        result = await self.session.execute(
            select(func.count(CartItemModel.id)).where(CartItemModel.cart_id == cart_id)
        )
        return result.scalar() or 0
    
    async def list_user_carts(self, user_id: str) -> List[Cart]:
        """List all carts for user."""
        result = await self.session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items).selectinload(CartItemModel.menu_item))
            .where(CartModel.user_id == user_id)
            .order_by(CartModel.created_at.desc())
        )
        db_carts = result.scalars().all()
        
        return [self._model_to_entity(cart) for cart in db_carts]