"""Review repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.review import Review


class ReviewRepository(ABC):
    """Review repository interface."""
    
    @abstractmethod
    async def create_review(self, review: Review) -> Review:
        """Create review."""
        pass
    
    @abstractmethod
    async def get_review_by_id(self, review_id: str) -> Optional[Review]:
        """Get review by ID."""
        pass
    
    @abstractmethod
    async def update_review(self, review: Review) -> Review:
        """Update review."""
        pass
    
    @abstractmethod
    async def delete_review(self, review_id: str) -> bool:
        """Delete review."""
        pass
    
    @abstractmethod
    async def get_reviews_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by user ID."""
        pass
    
    @abstractmethod
    async def get_reviews_by_order(self, order_id: str) -> List[Review]:
        """Get reviews by order ID."""
        pass
    
    @abstractmethod
    async def get_reviews_by_menu_item(self, menu_item_id: str, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by menu item ID."""
        pass
    
    @abstractmethod
    async def get_recent_reviews(self, limit: int = 20, offset: int = 0) -> List[Review]:
        """Get recent reviews."""
        pass
    
    @abstractmethod
    async def get_reviews_by_rating(self, rating: int, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by rating."""
        pass
    
    @abstractmethod
    async def get_average_rating_by_menu_item(self, menu_item_id: str) -> Optional[float]:
        """Get average rating for menu item."""
        pass
    
    @abstractmethod
    async def get_review_count_by_user(self, user_id: str) -> int:
        """Get review count by user."""
        pass
    
    @abstractmethod
    async def get_review_count_by_menu_item(self, menu_item_id: str) -> int:
        """Get review count by menu item."""
        pass
