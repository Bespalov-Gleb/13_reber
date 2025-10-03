"""Order-related types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from shared.constants.order_constants import OrderStatus, OrderType, PaymentMethod, PaymentStatus


@dataclass
class OrderItem:
    """Order item data class."""
    
    menu_item_id: str
    name: str
    price: int  # Price in kopecks
    quantity: int
    comment: Optional[str] = None


@dataclass
class DeliveryInfo:
    """Delivery information data class."""
    
    address: str
    phone: str
    comment: Optional[str] = None
    delivery_time: Optional[datetime] = None


@dataclass
class PickupInfo:
    """Pickup information data class."""
    
    phone: str
    pickup_time: Optional[datetime] = None
    comment: Optional[str] = None


@dataclass
class OrderSummary:
    """Order summary data class."""
    
    items: list[OrderItem]
    subtotal: int  # Subtotal in kopecks
    delivery_fee: int = 0  # Delivery fee in kopecks
    discount: int = 0  # Discount in kopecks
    total: int = 0  # Total amount in kopecks
    
    def __post_init__(self):
        """Calculate total after initialization."""
        self.total = self.subtotal + self.delivery_fee - self.discount


@dataclass
class OrderTimeline:
    """Order timeline data class."""
    
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    preparing_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


@dataclass
class OrderFilters:
    """Order filters for queries."""
    
    status: Optional[OrderStatus] = None
    order_type: Optional[OrderType] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[str] = None
    limit: int = 50
    offset: int = 0


@dataclass
class OrderAnalytics:
    """Order analytics data class."""
    
    total_orders: int
    total_revenue: int  # Total revenue in kopecks
    average_order_value: int  # Average order value in kopecks
    orders_by_status: dict[OrderStatus, int]
    orders_by_type: dict[OrderType, int]
    orders_by_payment_method: dict[PaymentMethod, int]
    top_items: list[tuple[str, int]]  # (item_name, quantity)
    orders_by_hour: dict[int, int]  # Hour -> count
    orders_by_day: dict[str, int]  # Day -> count