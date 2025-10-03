"""Menu item entity."""

from datetime import datetime
from typing import Optional


class MenuItem:
    """Menu item domain entity."""
    
    def __init__(
        self,
        item_id: str,
        category_id: str,
        name: str,
        price: int,  # Price in kopecks
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        ingredients: Optional[str] = None,
        allergens: Optional[str] = None,
        weight: Optional[str] = None,
        calories: Optional[int] = None,
        is_available: bool = True,
        is_popular: bool = False,
        sort_order: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.item_id = item_id
        self.category_id = category_id
        self.name = name
        self.price = price
        self.description = description
        self.image_url = image_url
        self.ingredients = ingredients
        self.allergens = allergens
        self.weight = weight
        self.calories = calories
        self.is_available = is_available
        self.is_popular = is_popular
        self.sort_order = sort_order
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def update_name(self, name: str) -> None:
        """Update menu item name."""
        self.name = name
        self.updated_at = datetime.now()
    
    def update_description(self, description: Optional[str]) -> None:
        """Update menu item description."""
        self.description = description
        self.updated_at = datetime.now()
    
    def update_price(self, price: int) -> None:
        """Update menu item price."""
        self.price = price
        self.updated_at = datetime.now()
    
    def update_image(self, image_url: Optional[str]) -> None:
        """Update menu item image."""
        self.image_url = image_url
        self.updated_at = datetime.now()
    
    def update_ingredients(self, ingredients: Optional[str]) -> None:
        """Update menu item ingredients."""
        self.ingredients = ingredients
        self.updated_at = datetime.now()
    
    def update_allergens(self, allergens: Optional[str]) -> None:
        """Update menu item allergens."""
        self.allergens = allergens
        self.updated_at = datetime.now()
    
    def update_nutrition(self, weight: Optional[str] = None, calories: Optional[int] = None) -> None:
        """Update menu item nutrition info."""
        if weight is not None:
            self.weight = weight
        if calories is not None:
            self.calories = calories
        self.updated_at = datetime.now()
    
    def change_availability(self, is_available: bool) -> None:
        """Change menu item availability."""
        self.is_available = is_available
        self.updated_at = datetime.now()
    
    def mark_popular(self, is_popular: bool) -> None:
        """Mark menu item as popular."""
        self.is_popular = is_popular
        self.updated_at = datetime.now()
    
    def change_sort_order(self, sort_order: int) -> None:
        """Change menu item sort order."""
        self.sort_order = sort_order
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"MenuItem(id={self.item_id}, name={self.name}, price={self.price}, available={self.is_available})"
    
    def __repr__(self) -> str:
        return self.__str__()