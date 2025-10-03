"""Category entity."""

from datetime import datetime
from typing import Optional


class Category:
    """Category domain entity."""
    
    def __init__(
        self,
        category_id: str,
        name: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        sort_order: int = 0,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.category_id = category_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.sort_order = sort_order
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def update_name(self, name: str) -> None:
        """Update category name."""
        self.name = name
        self.updated_at = datetime.now()
    
    def update_description(self, description: Optional[str]) -> None:
        """Update category description."""
        self.description = description
        self.updated_at = datetime.now()
    
    def update_image(self, image_url: Optional[str]) -> None:
        """Update category image."""
        self.image_url = image_url
        self.updated_at = datetime.now()
    
    def change_sort_order(self, sort_order: int) -> None:
        """Change category sort order."""
        self.sort_order = sort_order
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activate category."""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """Deactivate category."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"Category(id={self.category_id}, name={self.name}, active={self.is_active})"
    
    def __repr__(self) -> str:
        return self.__str__()