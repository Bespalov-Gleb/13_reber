"""Cart repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.cart import Cart


class CartRepository(ABC):
    """Cart repository interface."""
    
    @abstractmethod
    async def create(self, cart: Cart) -> Cart:
        """Create new cart."""
        pass
    
    @abstractmethod
    async def get_by_id(self, cart_id: str) -> Optional[Cart]:
        """Get cart by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        """Get cart by user ID."""
        pass
    
    @abstractmethod
    async def update(self, cart: Cart) -> Cart:
        """Update cart."""
        pass
    
    @abstractmethod
    async def delete(self, cart_id: str) -> bool:
        """Delete cart."""
        pass
    
    @abstractmethod
    async def clear_user_cart(self, user_id: str) -> bool:
        """Clear user's cart."""
        pass
    
    @abstractmethod
    async def add_item(self, cart_id: str, item_id: str, quantity: int, comment: Optional[str] = None) -> bool:
        """Add item to cart."""
        pass
    
    @abstractmethod
    async def remove_item(self, cart_id: str, item_id: str) -> bool:
        """Remove item from cart."""
        pass
    
    @abstractmethod
    async def update_item_quantity(self, cart_id: str, item_id: str, quantity: int) -> bool:
        """Update item quantity in cart."""
        pass
    
    @abstractmethod
    async def get_cart_total(self, cart_id: str) -> int:
        """Get cart total amount in kopecks."""
        pass
    
    @abstractmethod
    async def count_items(self, cart_id: str) -> int:
        """Count items in cart."""
        pass
    
    @abstractmethod
    async def list_user_carts(self, user_id: str) -> List[Cart]:
        """List all carts for user."""
        pass