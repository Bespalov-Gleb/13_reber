"""Order status value object."""

from enum import Enum
from typing import List


class OrderStatus(Enum):
    """Order status enumeration."""
    
    PENDING = "pending"           # Заказ создан, ожидает подтверждения
    CONFIRMED = "confirmed"       # Заказ подтвержден
    PREPARING = "preparing"       # Заказ готовится
    READY = "ready"              # Заказ готов
    OUT_FOR_DELIVERY = "delivery" # Заказ в доставке
    DELIVERED = "delivered"       # Заказ доставлен
    PICKED_UP = "picked_up"       # Заказ получен (самовывоз)
    CANCELLED = "cancelled"       # Заказ отменен
    REFUNDED = "refunded"         # Заказ возвращен
    
    @property
    def display_name(self) -> str:
        """Get display name for status."""
        status_names = {
            self.PENDING: "⏳ Ожидает подтверждения",
            self.CONFIRMED: "✅ Подтвержден",
            self.PREPARING: "👨‍🍳 Готовится",
            self.READY: "🍽️ Готов",
            self.OUT_FOR_DELIVERY: "🚚 В доставке",
            self.DELIVERED: "🎉 Доставлен",
            self.PICKED_UP: "🎉 Получен",
            self.CANCELLED: "❌ Отменен",
            self.REFUNDED: "💰 Возвращен",
        }
        return status_names.get(self, self.value)
    
    @property
    def is_active(self) -> bool:
        """Check if status is active (not final)."""
        return self in [
            self.PENDING,
            self.CONFIRMED,
            self.PREPARING,
            self.READY,
            self.OUT_FOR_DELIVERY,
        ]
    
    @property
    def is_final(self) -> bool:
        """Check if status is final."""
        return self in [
            self.DELIVERED,
            self.PICKED_UP,
            self.CANCELLED,
            self.REFUNDED,
        ]
    
    @property
    def is_successful(self) -> bool:
        """Check if status is successful."""
        return self in [
            self.DELIVERED,
            self.PICKED_UP,
        ]
    
    @property
    def is_failed(self) -> bool:
        """Check if status is failed."""
        return self in [
            self.CANCELLED,
            self.REFUNDED,
        ]
    
    @property
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled from this status."""
        return self in [
            self.PENDING,
            self.CONFIRMED,
        ]
    
    @property
    def can_be_modified(self) -> bool:
        """Check if order can be modified from this status."""
        return self == self.PENDING
    
    @property
    def requires_payment(self) -> bool:
        """Check if status requires payment."""
        return self in [
            self.PENDING,
            self.CONFIRMED,
        ]
    
    @property
    def is_ready_for_pickup(self) -> bool:
        """Check if order is ready for pickup."""
        return self == self.READY
    
    @property
    def is_ready_for_delivery(self) -> bool:
        """Check if order is ready for delivery."""
        return self == self.READY
    
    @classmethod
    def get_active_statuses(cls) -> List["OrderStatus"]:
        """Get all active statuses."""
        return [status for status in cls if status.is_active]
    
    @classmethod
    def get_final_statuses(cls) -> List["OrderStatus"]:
        """Get all final statuses."""
        return [status for status in cls if status.is_final]
    
    @classmethod
    def get_successful_statuses(cls) -> List["OrderStatus"]:
        """Get all successful statuses."""
        return [status for status in cls if status.is_successful]
    
    @classmethod
    def get_failed_statuses(cls) -> List["OrderStatus"]:
        """Get all failed statuses."""
        return [status for status in cls if status.is_failed]
    
    def __str__(self) -> str:
        return self.display_name
    
    def __repr__(self) -> str:
        return f"OrderStatus.{self.name}"