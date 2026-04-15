"""Promotion service for business logic."""

from typing import List, Optional
from datetime import datetime

from domain.entities.promotion import Promotion, PromotionUsage
from domain.repositories.promotion_repository import PromotionRepository
from shared.utils.helpers import generate_id


class PromotionService:
    """Promotion service for business logic."""
    
    def __init__(self, promotion_repository: PromotionRepository):
        self.promotion_repository = promotion_repository
    
    async def create_promotion(
        self,
        code: str,
        name: str,
        promotion_type: str,
        discount_value: int,
        description: Optional[str] = None,
        min_order_amount: Optional[int] = None,
        max_discount_amount: Optional[int] = None,
        usage_limit: Optional[int] = None,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None
    ) -> Promotion:
        """Create new promotion."""
        # Check if code already exists
        existing = await self.promotion_repository.get_promotion_by_code(code)
        if existing:
            raise ValueError(f"Promotion with code '{code}' already exists")
        
        promotion = Promotion(
            promotion_id=generate_id(),
            code=code.upper().strip(),
            name=name,
            description=description,
            promotion_type=promotion_type,
            discount_value=discount_value,
            min_order_amount=min_order_amount,
            max_discount_amount=max_discount_amount,
            usage_limit=usage_limit,
            is_active=True,
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        return await self.promotion_repository.create_promotion(promotion)
    
    async def get_promotion_by_code(self, code: str) -> Optional[Promotion]:
        """Get promotion by code."""
        return await self.promotion_repository.get_promotion_by_code(code.upper().strip())
    
    async def validate_promotion_code(self, code: str, order_amount: int, user_id: str) -> tuple[bool, Optional[Promotion], str]:
        """Validate promotion code for given order and user."""
        promotion = await self.get_promotion_by_code(code)
        
        if not promotion:
            return False, None, "Промокод не найден"
        
        if not promotion.is_valid():
            return False, promotion, "Промокод неактивен или истек"
        
        if not promotion.can_be_used(order_amount):
            if promotion.min_order_amount and order_amount < promotion.min_order_amount:
                min_amount_rub = promotion.min_order_amount // 100
                return False, promotion, f"Минимальная сумма заказа для этого промокода: {min_amount_rub}₽"
            return False, promotion, "Промокод не может быть применен к данному заказу"
        
        # Check if user has already used this promotion (if there's a limit)
        if promotion.usage_limit:
            user_usages = await self.promotion_repository.get_user_promotion_usages(user_id, promotion.promotion_id)
            if len(user_usages) >= promotion.usage_limit:
                return False, promotion, "Вы уже использовали этот промокод максимальное количество раз"
        
        return True, promotion, "Промокод действителен"
    
    async def apply_promotion_to_order(self, promotion: Promotion, order_id: str, user_id: str, order_amount: int) -> tuple[int, PromotionUsage]:
        """Apply promotion to order and return discount amount."""
        discount_amount = promotion.calculate_discount(order_amount)
        
        if discount_amount <= 0:
            raise ValueError("Promotion cannot be applied to this order")
        
        # Create usage record
        usage = PromotionUsage(
            usage_id=generate_id(),
            promotion_id=promotion.promotion_id,
            user_id=user_id,
            order_id=order_id,
            discount_amount=discount_amount
        )
        
        # Save usage
        saved_usage = await self.promotion_repository.create_promotion_usage(usage)
        
        # Update promotion usage count
        promotion.usage_count += 1
        promotion.updated_at = datetime.now()
        await self.promotion_repository.update_promotion(promotion)
        
        return discount_amount, saved_usage
    
    async def get_promotion_usage_by_order(self, order_id: str) -> Optional[PromotionUsage]:
        """Get promotion usage by order ID."""
        return await self.promotion_repository.get_promotion_usage_by_order(order_id)
    
    async def list_promotions(self, active_only: bool = True) -> List[Promotion]:
        """List promotions."""
        return await self.promotion_repository.list_promotions(active_only)
    
    async def update_promotion(self, promotion: Promotion) -> Promotion:
        """Update promotion."""
        promotion.updated_at = datetime.now()
        return await self.promotion_repository.update_promotion(promotion)
    
    async def deactivate_promotion(self, promotion_id: str) -> bool:
        """Deactivate promotion."""
        promotion = await self.promotion_repository.get_promotion_by_id(promotion_id)
        if not promotion:
            return False
        
        promotion.is_active = False
        promotion.updated_at = datetime.now()
        await self.promotion_repository.update_promotion(promotion)
        
        return True
    
    async def delete_promotion(self, promotion_id: str) -> bool:
        """Delete promotion."""
        return await self.promotion_repository.delete_promotion(promotion_id)
    
    def format_discount_description(self, promotion: Promotion) -> str:
        """Format discount description for display."""
        if promotion.promotion_type == "percentage":
            return f"Скидка {promotion.discount_value}%"
        elif promotion.promotion_type == "fixed_amount":
            amount_rub = promotion.discount_value // 100
            return f"Скидка {amount_rub}₽"
        elif promotion.promotion_type == "free_delivery":
            return "Бесплатная доставка"
        else:
            return "Скидка"
    
    def format_promotion_conditions(self, promotion: Promotion) -> str:
        """Format promotion conditions for display."""
        conditions = []
        
        if promotion.min_order_amount:
            min_amount_rub = promotion.min_order_amount // 100
            conditions.append(f"Минимальная сумма: {min_amount_rub}₽")
        
        if promotion.max_discount_amount:
            max_discount_rub = promotion.max_discount_amount // 100
            conditions.append(f"Максимальная скидка: {max_discount_rub}₽")
        
        if promotion.usage_limit:
            conditions.append(f"Лимит использований: {promotion.usage_limit}")
        
        if promotion.valid_until:
            conditions.append(f"Действует до: {promotion.valid_until.strftime('%d.%m.%Y')}")
        
        return ", ".join(conditions) if conditions else "Без ограничений"
