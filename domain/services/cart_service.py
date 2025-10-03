"""Cart service for business logic."""

from typing import Optional
from datetime import datetime

from domain.entities.cart import Cart
from domain.entities.user import User
from domain.entities.menu_item import MenuItem
from domain.repositories.cart_repository import CartRepository
from domain.repositories.menu_repository import MenuRepository
from domain.repositories.user_repository import UserRepository
from shared.types.user_types import UserRole, UserStatus
from shared.utils.helpers import generate_id


class CartService:
    """Cart service for business logic."""
    
    def __init__(
        self,
        cart_repository: CartRepository,
        menu_repository: MenuRepository,
        user_repository: UserRepository,
    ):
        self.cart_repository = cart_repository
        self.menu_repository = menu_repository
        self.user_repository = user_repository
    
    async def _ensure_user(self, telegram_id: int) -> User:
        """Get or create user by Telegram ID."""
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if user:
            return user
        user = User(
            user_id=generate_id(),
            telegram_id=telegram_id,
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return await self.user_repository.create(user)

    async def get_or_create_cart(self, user_id: str | int) -> Cart:
        """Get existing cart or create new one for user."""
        telegram_id = int(user_id)
        user = await self._ensure_user(telegram_id)
        cart = await self.cart_repository.get_by_user_id(user.user_id)
        
        if not cart:
            # Create new cart
            cart = Cart(
                cart_id=generate_id(),
                user_id=user.user_id,
                items=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            cart = await self.cart_repository.create(cart)
        
        return cart
    
    async def add_item_to_cart(
        self,
        user_id: str,
        item_id: str,
        quantity: int,
        comment: Optional[str] = None,
    ) -> Cart:
        """Add item to user's cart."""
        # Get or create cart
        cart = await self.get_or_create_cart(user_id)
        
        # Get menu item
        menu_item = await self.menu_repository.get_menu_item_by_id(item_id)
        if not menu_item:
            raise ValueError(f"Menu item with id {item_id} not found")
        
        # Add item to cart
        await self.cart_repository.add_item(cart.cart_id, item_id, quantity, comment)
        
        # Return updated cart
        return await self.cart_repository.get_by_id(cart.cart_id)
    
    async def remove_item_from_cart(self, user_id: str | int, item_id: str) -> Cart:
        """Remove item from user's cart."""
        telegram_id = int(user_id)
        user = await self._ensure_user(telegram_id)
        cart = await self.cart_repository.get_by_user_id(user.user_id)
        if not cart:
            raise ValueError("Cart not found")
        
        await self.cart_repository.remove_item(cart.cart_id, item_id)
        
        return await self.cart_repository.get_by_id(cart.cart_id)
    
    async def update_item_quantity(self, user_id: str | int, item_id: str, quantity: int) -> Cart:
        """Update item quantity in user's cart."""
        telegram_id = int(user_id)
        user = await self._ensure_user(telegram_id)
        cart = await self.cart_repository.get_by_user_id(user.user_id)
        if not cart:
            raise ValueError("Cart not found")
        
        await self.cart_repository.update_item_quantity(cart.cart_id, item_id, quantity)
        
        return await self.cart_repository.get_by_id(cart.cart_id)
    
    async def clear_cart(self, user_id: str | int) -> bool:
        """Clear user's cart."""
        telegram_id = int(user_id)
        user = await self._ensure_user(telegram_id)
        return await self.cart_repository.clear_user_cart(user.user_id)
    
    async def get_cart_total(self, user_id: str | int) -> int:
        """Get cart total amount."""
        telegram_id = int(user_id)
        user = await self._ensure_user(telegram_id)
        cart = await self.cart_repository.get_by_user_id(user.user_id)
        if not cart:
            return 0
        return await self.cart_repository.get_cart_total(cart.cart_id)
    
    async def validate_cart(self, user_id: str | int) -> bool:
        """Validate cart items availability and prices."""
        telegram_id = int(user_id)
        user = await self._ensure_user(telegram_id)
        cart = await self.cart_repository.get_by_user_id(user.user_id)
        if not cart or cart.is_empty():
            return False
        
        # Check if all items are available
        for item in cart.get_items_list():
            if not item.menu_item.is_available:
                return False
        
        return True