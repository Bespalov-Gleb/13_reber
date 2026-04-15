"""Promotion domain entity."""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Promotion:
    """Promotion domain entity."""
    
    promotion_id: str
    code: str
    name: str
    description: Optional[str] = None
    
    # Promotion type: percentage, fixed_amount, free_delivery
    promotion_type: str = "percentage"
    discount_value: int = 0  # percentage or kopecks
    
    # Conditions
    min_order_amount: Optional[int] = None  # in kopecks
    max_discount_amount: Optional[int] = None  # in kopecks
    usage_limit: Optional[int] = None  # maximum usage count
    usage_count: int = 0  # current usage count
    
    # Validity
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def is_valid(self, current_time: Optional[datetime] = None) -> bool:
        """Check if promotion is valid at given time."""
        if not self.is_active:
            return False
        
        if current_time is None:
            current_time = datetime.now()
        
        if self.valid_from and current_time < self.valid_from:
            return False
        
        if self.valid_until and current_time > self.valid_until:
            return False
        
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return True
    
    def can_be_used(self, order_amount: int, current_time: Optional[datetime] = None) -> bool:
        """Check if promotion can be used for given order amount."""
        if not self.is_valid(current_time):
            return False
        
        if self.min_order_amount and order_amount < self.min_order_amount:
            return False
        
        return True
    
    def calculate_discount(self, order_amount: int) -> int:
        """Calculate discount amount for given order amount."""
        if not self.can_be_used(order_amount):
            return 0
        
        if self.promotion_type == "percentage":
            discount = int(order_amount * self.discount_value / 100)
        elif self.promotion_type == "fixed_amount":
            discount = self.discount_value
        elif self.promotion_type == "free_delivery":
            # This would be handled separately in delivery fee calculation
            discount = 0
        else:
            discount = 0
        
        # Apply maximum discount limit
        if self.max_discount_amount and discount > self.max_discount_amount:
            discount = self.max_discount_amount
        
        return discount


@dataclass
class PromotionUsage:
    """Promotion usage domain entity."""
    
    usage_id: str
    promotion_id: str
    user_id: str
    order_id: str
    discount_amount: int  # in kopecks
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
