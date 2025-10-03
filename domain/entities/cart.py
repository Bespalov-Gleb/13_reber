"""Cart entity."""

from datetime import datetime
from typing import Dict, List, Optional

from domain.entities.menu_item import MenuItem


class CartItem:
    """Cart item domain entity."""
    
    def __init__(
        self,
        item_id: str,
        name: str,
        price: int,  # Price in kopecks
        quantity: int,
        comment: Optional[str] = None,
    ):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.comment = comment
    
    @property
    def total_price(self) -> int:
        """Get total price for this cart item."""
        return self.price * self.quantity
    
    def update_quantity(self, quantity: int) -> None:
        """Update item quantity."""
        self.quantity = quantity
    
    def update_comment(self, comment: Optional[str]) -> None:
        """Update item comment."""
        self.comment = comment
    
    def __str__(self) -> str:
        return f"CartItem(item_id={self.item_id}, name={self.name}, quantity={self.quantity}, price={self.total_price})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Cart:
    """Cart domain entity."""
    
    def __init__(
        self,
        cart_id: str,
        user_id: str,
        items: Optional[Dict[str, CartItem]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.cart_id = cart_id
        self.user_id = user_id
        self.items = items or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def add_item(self, menu_item: MenuItem, quantity: int, comment: Optional[str] = None) -> None:
        """Add item to cart."""
        item_id = menu_item.item_id
        
        if item_id in self.items:
            # Update existing item
            existing_item = self.items[item_id]
            existing_item.update_quantity(existing_item.quantity + quantity)
            if comment:
                existing_item.update_comment(comment)
        else:
            # Add new item
            cart_item = CartItem(
                item_id=item_id,
                name=menu_item.name,
                price=menu_item.price,
                quantity=quantity,
                comment=comment,
            )
            self.items[item_id] = cart_item
        
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: str) -> None:
        """Remove item from cart."""
        if item_id in self.items:
            del self.items[item_id]
            self.updated_at = datetime.now()
    
    def update_item_quantity(self, item_id: str, quantity: int) -> None:
        """Update item quantity in cart."""
        if item_id in self.items:
            if quantity <= 0:
                self.remove_item(item_id)
            else:
                self.items[item_id].update_quantity(quantity)
                self.updated_at = datetime.now()
    
    def update_item_comment(self, item_id: str, comment: Optional[str]) -> None:
        """Update item comment in cart."""
        if item_id in self.items:
            self.items[item_id].update_comment(comment)
            self.updated_at = datetime.now()
    
    def clear(self) -> None:
        """Clear all items from cart."""
        self.items.clear()
        self.updated_at = datetime.now()
    
    @property
    def total_items(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.values())
    
    @property
    def total_price(self) -> int:
        """Get total price of cart in kopecks."""
        return sum(item.total_price for item in self.items.values())
    
    @property
    def item_count(self) -> int:
        """Get number of different items in cart."""
        return len(self.items)
    
    def get_items_list(self) -> List[CartItem]:
        """Get list of cart items."""
        return list(self.items.values())
    
    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return len(self.items) == 0
    
    def __str__(self) -> str:
        return f"Cart(id={self.cart_id}, user_id={self.user_id}, items={self.item_count}, total={self.total_price})"
    
    def __repr__(self) -> str:
        return self.__str__()