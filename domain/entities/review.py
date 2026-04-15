"""Review domain entity."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Review:
    """Review domain entity."""
    
    review_id: str
    user_id: str
    order_id: Optional[str] = None
    menu_item_id: Optional[str] = None
    
    # Review content
    rating: int = 1  # 1-5 stars
    comment: Optional[str] = None
    
    # Review status
    is_visible: bool = True
    is_answered: bool = False
    admin_response: Optional[str] = None
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def is_valid_rating(self) -> bool:
        """Check if rating is valid (1-5)."""
        return 1 <= self.rating <= 5
    
    def get_rating_stars(self) -> str:
        """Get rating as star emoji string."""
        return "⭐" * self.rating
    
    def get_rating_text(self) -> str:
        """Get rating as text description."""
        rating_texts = {
            1: "Очень плохо",
            2: "Плохо", 
            3: "Удовлетворительно",
            4: "Хорошо",
            5: "Отлично"
        }
        return rating_texts.get(self.rating, "Неизвестно")
    
    def is_recent(self, days: int = 30) -> bool:
        """Check if review is recent (within specified days)."""
        if self.created_at is None:
            return False
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.created_at >= cutoff_date
