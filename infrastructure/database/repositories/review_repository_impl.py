"""Review repository implementation."""

from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc

from domain.entities.review import Review
from domain.repositories.review_repository import ReviewRepository
from infrastructure.database.models.review_model import ReviewModel


class ReviewRepositoryImpl(ReviewRepository):
    """Review repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_review(self, review: Review) -> Review:
        """Create review."""
        db_review = ReviewModel(
            id=review.review_id,
            user_id=review.user_id,
            order_id=review.order_id,
            menu_item_id=review.menu_item_id,
            rating=review.rating,
            comment=review.comment,
            is_visible=review.is_visible,
            is_answered=review.is_answered,
            admin_response=review.admin_response,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        
        self.session.add(db_review)
        await self.session.flush()
        
        return self._model_to_entity(db_review)
    
    async def get_review_by_id(self, review_id: str) -> Optional[Review]:
        """Get review by ID."""
        result = await self.session.execute(
            select(ReviewModel).where(ReviewModel.id == review_id)
        )
        db_review = result.scalar_one_or_none()
        
        if db_review:
            return self._model_to_entity(db_review)
        return None
    
    async def update_review(self, review: Review) -> Review:
        """Update review."""
        result = await self.session.execute(
            select(ReviewModel).where(ReviewModel.id == review.review_id)
        )
        db_review = result.scalar_one_or_none()
        
        if not db_review:
            raise ValueError(f"Review with id {review.review_id} not found")
        
        # Update fields
        db_review.rating = review.rating
        db_review.comment = review.comment
        db_review.is_visible = review.is_visible
        db_review.is_answered = review.is_answered
        db_review.admin_response = review.admin_response
        db_review.updated_at = review.updated_at
        
        await self.session.flush()
        
        return self._model_to_entity(db_review)
    
    async def delete_review(self, review_id: str) -> bool:
        """Delete review."""
        result = await self.session.execute(
            select(ReviewModel).where(ReviewModel.id == review_id)
        )
        db_review = result.scalar_one_or_none()
        
        if not db_review:
            return False
        
        await self.session.delete(db_review)
        await self.session.flush()
        
        return True
    
    async def get_reviews_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by user ID."""
        result = await self.session.execute(
            select(ReviewModel)
            .where(ReviewModel.user_id == user_id)
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        db_reviews = result.scalars().all()
        
        return [self._model_to_entity(db_review) for db_review in db_reviews]
    
    async def get_reviews_by_order(self, order_id: str) -> List[Review]:
        """Get reviews by order ID."""
        result = await self.session.execute(
            select(ReviewModel)
            .where(ReviewModel.order_id == order_id)
            .order_by(desc(ReviewModel.created_at))
        )
        db_reviews = result.scalars().all()
        
        return [self._model_to_entity(db_review) for db_review in db_reviews]
    
    async def get_reviews_by_menu_item(self, menu_item_id: str, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by menu item ID."""
        result = await self.session.execute(
            select(ReviewModel)
            .where(and_(
                ReviewModel.menu_item_id == menu_item_id,
                ReviewModel.is_visible == True
            ))
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        db_reviews = result.scalars().all()
        
        return [self._model_to_entity(db_review) for db_review in db_reviews]
    
    async def get_recent_reviews(self, limit: int = 20, offset: int = 0) -> List[Review]:
        """Get recent reviews."""
        result = await self.session.execute(
            select(ReviewModel)
            .where(ReviewModel.is_visible == True)
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        db_reviews = result.scalars().all()
        
        return [self._model_to_entity(db_review) for db_review in db_reviews]
    
    async def get_reviews_by_rating(self, rating: int, limit: int = 50, offset: int = 0) -> List[Review]:
        """Get reviews by rating."""
        result = await self.session.execute(
            select(ReviewModel)
            .where(and_(
                ReviewModel.rating == rating,
                ReviewModel.is_visible == True
            ))
            .order_by(desc(ReviewModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        db_reviews = result.scalars().all()
        
        return [self._model_to_entity(db_review) for db_review in db_reviews]
    
    async def get_average_rating_by_menu_item(self, menu_item_id: str) -> Optional[float]:
        """Get average rating for menu item."""
        result = await self.session.execute(
            select(func.avg(ReviewModel.rating))
            .where(and_(
                ReviewModel.menu_item_id == menu_item_id,
                ReviewModel.is_visible == True
            ))
        )
        avg_rating = result.scalar()
        
        return round(avg_rating, 2) if avg_rating is not None else None
    
    async def get_review_count_by_user(self, user_id: str) -> int:
        """Get review count by user."""
        result = await self.session.execute(
            select(func.count(ReviewModel.id))
            .where(ReviewModel.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def get_review_count_by_menu_item(self, menu_item_id: str) -> int:
        """Get review count by menu item."""
        result = await self.session.execute(
            select(func.count(ReviewModel.id))
            .where(and_(
                ReviewModel.menu_item_id == menu_item_id,
                ReviewModel.is_visible == True
            ))
        )
        return result.scalar() or 0
    
    def _model_to_entity(self, db_review: ReviewModel) -> Review:
        """Convert database model to domain entity."""
        return Review(
            review_id=db_review.id,
            user_id=db_review.user_id,
            order_id=db_review.order_id,
            menu_item_id=db_review.menu_item_id,
            rating=db_review.rating,
            comment=db_review.comment,
            is_visible=db_review.is_visible,
            is_answered=db_review.is_answered,
            admin_response=db_review.admin_response,
            created_at=db_review.created_at,
            updated_at=db_review.updated_at
        )
