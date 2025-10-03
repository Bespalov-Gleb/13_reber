"""Order repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from domain.entities.order import Order
from shared.constants.order_constants import OrderStatus, OrderType, PaymentStatus
from shared.types.order_types import OrderFilters


class OrderRepository(ABC):
    """Order repository interface."""
    
    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Create new order."""
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """Get orders by user ID."""
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Update order."""
        pass
    
    @abstractmethod
    async def delete(self, order_id: str) -> bool:
        """Delete order."""
        pass
    
    @abstractmethod
    async def list_orders(self, filters: OrderFilters) -> List[Order]:
        """List orders with filters."""
        pass
    
    @abstractmethod
    async def get_orders_by_status(self, status: OrderStatus, limit: int = 100, offset: int = 0) -> List[Order]:
        """Get orders by status."""
        pass
    
    @abstractmethod
    async def get_orders_by_type(self, order_type: OrderType, limit: int = 100, offset: int = 0) -> List[Order]:
        """Get orders by type."""
        pass
    
    @abstractmethod
    async def get_orders_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Get orders by date range."""
        pass
    
    @abstractmethod
    async def get_orders_by_payment_status(self, payment_status: PaymentStatus) -> List[Order]:
        """Get orders by payment status."""
        pass
    
    @abstractmethod
    async def count_orders(self, filters: Optional[OrderFilters] = None) -> int:
        """Count orders with optional filters."""
        pass
    
    @abstractmethod
    async def get_user_order_count(self, user_id: str) -> int:
        """Get user's order count."""
        pass
    
    @abstractmethod
    async def get_user_total_spent(self, user_id: str) -> int:
        """Get user's total spent amount."""
        pass
    
    @abstractmethod
    async def get_orders_requiring_attention(self) -> List[Order]:
        """Get orders that require attention (pending, preparing, etc.)."""
        pass
    
    @abstractmethod
    async def get_delivery_orders(self) -> List[Order]:
        """Get orders for delivery."""
        pass
    
    @abstractmethod
    async def get_pickup_orders(self) -> List[Order]:
        """Get orders for pickup."""
        pass