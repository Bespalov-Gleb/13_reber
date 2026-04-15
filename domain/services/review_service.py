"""Review service for business logic."""

from typing import List, Optional
from datetime import datetime

from domain.entities.review import Review
from domain.repositories.review_repository import ReviewRepository
from shared.utils.helpers import generate_id


class ReviewService:
    """Review service for business logic."""
    
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository
    
    async def create_review(
        self,
        user_id: str,
        rating: int,
        comment: Optional[str] = None,
        order_id: Optional[str] = None,
        menu_item_id: Optional[str] = None
    ) -> Review:
        """Create new review."""
        # Validate rating
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if user already reviewed this order/item
        if order_id:
            existing_reviews = await self.review_repository.get_reviews_by_order(order_id)
            for review in existing_reviews:
                if review.user_id == user_id:
                    raise ValueError("You have already reviewed this order")
        
        if menu_item_id:
            existing_reviews = await self.review_repository.get_reviews_by_menu_item(menu_item_id)
            for review in existing_reviews:
                if review.user_id == user_id:
                    raise ValueError("You have already reviewed this item")
        
        review = Review(
            review_id=generate_id(),
            user_id=user_id,
            order_id=order_id,
            menu_item_id=menu_item_id,
            rating=rating,
            comment=comment,
            is_visible=True,
            is_answered=False
        )
        
        return await self.review_repository.create_review(review)
    
    async def get_review_by_id(self, review_id: str) -> Optional[Review]:
        """Get review by ID."""
        return await self.review_repository.get_review_by_id(review_id)
    
    async def update_review(self, review: Review) -> Review:
        """Update review."""
        review.updated_at = datetime.now()
        return await self.review_repository.update_review(review)
    
    async def delete_review(self, review_id: str) -> bool:
        """Delete review."""
        return await self.review_repository.delete_review(review_id)
    
    async def get_user_reviews(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get user's reviews."""
        return await self.review_repository.get_reviews_by_user(user_id, limit, offset)
    
    async def get_order_reviews(self, order_id: str) -> List[Review]:
        """Get reviews for order."""
        return await self.review_repository.get_reviews_by_order(order_id)
    
    async def get_menu_item_reviews(self, menu_item_id: str, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews for menu item."""
        return await self.review_repository.get_reviews_by_menu_item(menu_item_id, limit, offset)
    
    async def get_recent_reviews(self, limit: int = 20, offset: int = 0) -> List[Review]:
        """Get recent reviews."""
        return await self.review_repository.get_recent_reviews(limit, offset)
    
    async def get_reviews_by_rating(self, rating: int, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by rating."""
        return await self.review_repository.get_reviews_by_rating(rating, limit, offset)
    
    async def get_menu_item_rating_stats(self, menu_item_id: str) -> dict:
        """Get rating statistics for menu item."""
        avg_rating = await self.review_repository.get_average_rating_by_menu_item(menu_item_id)
        review_count = await self.review_repository.get_review_count_by_menu_item(menu_item_id)
        
        # Get rating distribution
        rating_distribution = {}
        for rating in range(1, 6):
            reviews = await self.review_repository.get_reviews_by_rating(rating)
            rating_distribution[rating] = len([r for r in reviews if r.menu_item_id == menu_item_id])
        
        return {
            "average_rating": avg_rating,
            "review_count": review_count,
            "rating_distribution": rating_distribution
        }
    
    async def add_admin_response(self, review_id: str, admin_response: str) -> Review:
        """Add admin response to review."""
        review = await self.review_repository.get_review_by_id(review_id)
        if not review:
            raise ValueError(f"Review with id {review_id} not found")
        
        review.admin_response = admin_response
        review.is_answered = True
        review.updated_at = datetime.now()
        
        return await self.review_repository.update_review(review)
    
    async def hide_review(self, review_id: str) -> Review:
        """Hide review from public view."""
        review = await self.review_repository.get_review_by_id(review_id)
        if not review:
            raise ValueError(f"Review with id {review_id} not found")
        
        review.is_visible = False
        review.updated_at = datetime.now()
        
        return await self.review_repository.update_review(review)
    
    async def show_review(self, review_id: str) -> Review:
        """Show review in public view."""
        review = await self.review_repository.get_review_by_id(review_id)
        if not review:
            raise ValueError(f"Review with id {review_id} not found")
        
        review.is_visible = True
        review.updated_at = datetime.now()
        
        return await self.review_repository.update_review(review)
    
    def format_rating_display(self, rating: int) -> str:
        """Format rating for display."""
        stars = "⭐" * rating
        empty_stars = "☆" * (5 - rating)
        return f"{stars}{empty_stars} ({rating}/5)"
    
    def format_review_summary(self, review: Review) -> str:
        """Format review summary for display."""
        text = f"{review.get_rating_stars()} {review.get_rating_text()}\n"
        
        if review.comment:
            # Truncate long comments
            comment = review.comment
            if len(comment) > 100:
                comment = comment[:97] + "..."
            text += f"💬 {comment}\n"
        
        text += f"📅 {review.created_at.strftime('%d.%m.%Y')}"
        
        return text
