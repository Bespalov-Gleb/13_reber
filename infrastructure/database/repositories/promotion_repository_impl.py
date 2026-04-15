"""Promotion repository implementation."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from domain.entities.promotion import Promotion, PromotionUsage
from domain.repositories.promotion_repository import PromotionRepository
from infrastructure.database.models.promotion_model import PromotionModel, PromotionUsageModel


class PromotionRepositoryImpl(PromotionRepository):
    """Promotion repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_promotion(self, promotion: Promotion) -> Promotion:
        """Create promotion."""
        db_promotion = PromotionModel(
            id=promotion.promotion_id,
            code=promotion.code,
            name=promotion.name,
            description=promotion.description,
            promotion_type=promotion.promotion_type,
            discount_value=promotion.discount_value,
            min_order_amount=promotion.min_order_amount,
            max_discount_amount=promotion.max_discount_amount,
            usage_limit=promotion.usage_limit,
            usage_count=promotion.usage_count,
            is_active=promotion.is_active,
            valid_from=promotion.valid_from,
            valid_until=promotion.valid_until,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at
        )
        
        self.session.add(db_promotion)
        await self.session.flush()
        
        return self._model_to_entity(db_promotion)
    
    async def get_promotion_by_id(self, promotion_id: str) -> Optional[Promotion]:
        """Get promotion by ID."""
        result = await self.session.execute(
            select(PromotionModel).where(PromotionModel.id == promotion_id)
        )
        db_promotion = result.scalar_one_or_none()
        
        if db_promotion:
            return self._model_to_entity(db_promotion)
        return None
    
    async def get_promotion_by_code(self, code: str) -> Optional[Promotion]:
        """Get promotion by code."""
        result = await self.session.execute(
            select(PromotionModel).where(PromotionModel.code == code)
        )
        db_promotion = result.scalar_one_or_none()
        
        if db_promotion:
            return self._model_to_entity(db_promotion)
        return None
    
    async def update_promotion(self, promotion: Promotion) -> Promotion:
        """Update promotion."""
        result = await self.session.execute(
            select(PromotionModel).where(PromotionModel.id == promotion.promotion_id)
        )
        db_promotion = result.scalar_one_or_none()
        
        if not db_promotion:
            raise ValueError(f"Promotion with id {promotion.promotion_id} not found")
        
        # Update fields
        db_promotion.code = promotion.code
        db_promotion.name = promotion.name
        db_promotion.description = promotion.description
        db_promotion.promotion_type = promotion.promotion_type
        db_promotion.discount_value = promotion.discount_value
        db_promotion.min_order_amount = promotion.min_order_amount
        db_promotion.max_discount_amount = promotion.max_discount_amount
        db_promotion.usage_limit = promotion.usage_limit
        db_promotion.usage_count = promotion.usage_count
        db_promotion.is_active = promotion.is_active
        db_promotion.valid_from = promotion.valid_from
        db_promotion.valid_until = promotion.valid_until
        db_promotion.updated_at = promotion.updated_at
        
        await self.session.flush()
        
        return self._model_to_entity(db_promotion)
    
    async def delete_promotion(self, promotion_id: str) -> bool:
        """Delete promotion."""
        result = await self.session.execute(
            select(PromotionModel).where(PromotionModel.id == promotion_id)
        )
        db_promotion = result.scalar_one_or_none()
        
        if not db_promotion:
            return False
        
        await self.session.delete(db_promotion)
        await self.session.flush()
        
        return True
    
    async def list_promotions(self, active_only: bool = True) -> List[Promotion]:
        """List promotions."""
        query = select(PromotionModel)
        
        if active_only:
            query = query.where(PromotionModel.is_active == True)
        
        result = await self.session.execute(query)
        db_promotions = result.scalars().all()
        
        return [self._model_to_entity(db_promotion) for db_promotion in db_promotions]
    
    async def create_promotion_usage(self, usage: PromotionUsage) -> PromotionUsage:
        """Create promotion usage."""
        db_usage = PromotionUsageModel(
            id=usage.usage_id,
            promotion_id=usage.promotion_id,
            user_id=usage.user_id,
            order_id=usage.order_id,
            discount_amount=usage.discount_amount,
            created_at=usage.created_at
        )
        
        self.session.add(db_usage)
        await self.session.flush()
        
        return self._usage_model_to_entity(db_usage)
    
    async def get_promotion_usage_by_order(self, order_id: str) -> Optional[PromotionUsage]:
        """Get promotion usage by order ID."""
        result = await self.session.execute(
            select(PromotionUsageModel).where(PromotionUsageModel.order_id == order_id)
        )
        db_usage = result.scalar_one_or_none()
        
        if db_usage:
            return self._usage_model_to_entity(db_usage)
        return None
    
    async def get_user_promotion_usages(self, user_id: str, promotion_id: str) -> List[PromotionUsage]:
        """Get user's usages of specific promotion."""
        result = await self.session.execute(
            select(PromotionUsageModel).where(
                and_(
                    PromotionUsageModel.user_id == user_id,
                    PromotionUsageModel.promotion_id == promotion_id
                )
            )
        )
        db_usages = result.scalars().all()
        
        return [self._usage_model_to_entity(db_usage) for db_usage in db_usages]
    
    def _model_to_entity(self, db_promotion: PromotionModel) -> Promotion:
        """Convert database model to domain entity."""
        return Promotion(
            promotion_id=db_promotion.id,
            code=db_promotion.code,
            name=db_promotion.name,
            description=db_promotion.description,
            promotion_type=db_promotion.promotion_type,
            discount_value=db_promotion.discount_value,
            min_order_amount=db_promotion.min_order_amount,
            max_discount_amount=db_promotion.max_discount_amount,
            usage_limit=db_promotion.usage_limit,
            usage_count=db_promotion.usage_count,
            is_active=db_promotion.is_active,
            valid_from=db_promotion.valid_from,
            valid_until=db_promotion.valid_until,
            created_at=db_promotion.created_at,
            updated_at=db_promotion.updated_at
        )
    
    def _usage_model_to_entity(self, db_usage: PromotionUsageModel) -> PromotionUsage:
        """Convert usage database model to domain entity."""
        return PromotionUsage(
            usage_id=db_usage.id,
            promotion_id=db_usage.promotion_id,
            user_id=db_usage.user_id,
            order_id=db_usage.order_id,
            discount_amount=db_usage.discount_amount,
            created_at=db_usage.created_at
        )
