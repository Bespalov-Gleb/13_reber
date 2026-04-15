"""Promotion repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.promotion import Promotion, PromotionUsage


class PromotionRepository(ABC):
    """Promotion repository interface."""
    
    @abstractmethod
    async def create_promotion(self, promotion: Promotion) -> Promotion:
        """Create promotion."""
        pass
    
    @abstractmethod
    async def get_promotion_by_id(self, promotion_id: str) -> Optional[Promotion]:
        """Get promotion by ID."""
        pass
    
    @abstractmethod
    async def get_promotion_by_code(self, code: str) -> Optional[Promotion]:
        """Get promotion by code."""
        pass
    
    @abstractmethod
    async def update_promotion(self, promotion: Promotion) -> Promotion:
        """Update promotion."""
        pass
    
    @abstractmethod
    async def delete_promotion(self, promotion_id: str) -> bool:
        """Delete promotion."""
        pass
    
    @abstractmethod
    async def list_promotions(self, active_only: bool = True) -> List[Promotion]:
        """List promotions."""
        pass
    
    @abstractmethod
    async def create_promotion_usage(self, usage: PromotionUsage) -> PromotionUsage:
        """Create promotion usage."""
        pass
    
    @abstractmethod
    async def get_promotion_usage_by_order(self, order_id: str) -> Optional[PromotionUsage]:
        """Get promotion usage by order ID."""
        pass
    
    @abstractmethod
    async def get_user_promotion_usages(self, user_id: str, promotion_id: str) -> List[PromotionUsage]:
        """Get user's usages of specific promotion."""
        pass
