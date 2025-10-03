"""Order entity."""

from datetime import datetime
from typing import Dict, List, Optional

from shared.constants.order_constants import OrderStatus, OrderType, PaymentMethod, PaymentStatus
from shared.types.order_types import DeliveryInfo, OrderItem, OrderSummary, OrderTimeline, PickupInfo


class Order:
    """Order domain entity."""
    
    def __init__(
        self,
        order_id: str,
        user_id: str,
        items: List[OrderItem],
        order_type: OrderType,
        status: OrderStatus = OrderStatus.PENDING,
        payment_method: PaymentMethod = PaymentMethod.CASH,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
        subtotal: int = 0,  # Subtotal in kopecks
        delivery_fee: int = 0,  # Delivery fee in kopecks
        discount: int = 0,  # Discount in kopecks
        total: int = 0,  # Total amount in kopecks
        delivery_info: Optional[DeliveryInfo] = None,
        pickup_info: Optional[PickupInfo] = None,
        comment: Optional[str] = None,
        timeline: Optional[OrderTimeline] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.order_type = order_type
        self.status = status
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.subtotal = subtotal
        self.delivery_fee = delivery_fee
        self.discount = discount
        self.total = total
        self.delivery_info = delivery_info
        self.pickup_info = pickup_info
        self.comment = comment
        self.timeline = timeline or OrderTimeline(created_at=created_at or datetime.now())
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def calculate_total(self) -> int:
        """Calculate total order amount."""
        self.total = self.subtotal + self.delivery_fee - self.discount
        return self.total
    
    def update_status(self, status: OrderStatus) -> None:
        """Update order status."""
        self.status = status
        self.updated_at = datetime.now()
        
        # Update timeline
        if status == OrderStatus.CONFIRMED:
            self.timeline.confirmed_at = datetime.now()
        elif status == OrderStatus.PREPARING:
            self.timeline.preparing_at = datetime.now()
        elif status == OrderStatus.READY:
            self.timeline.ready_at = datetime.now()
        elif status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP]:
            self.timeline.delivered_at = datetime.now()
        elif status == OrderStatus.CANCELLED:
            self.timeline.cancelled_at = datetime.now()
    
    def update_payment_status(self, payment_status: PaymentStatus) -> None:
        """Update payment status."""
        self.payment_status = payment_status
        self.updated_at = datetime.now()
    
    def update_payment_method(self, payment_method: PaymentMethod) -> None:
        """Update payment method."""
        self.payment_method = payment_method
        self.updated_at = datetime.now()
    
    def add_discount(self, discount: int) -> None:
        """Add discount to order."""
        self.discount = discount
        self.calculate_total()
        self.updated_at = datetime.now()
    
    def update_delivery_info(self, delivery_info: DeliveryInfo) -> None:
        """Update delivery information."""
        self.delivery_info = delivery_info
        self.updated_at = datetime.now()
    
    def update_pickup_info(self, pickup_info: PickupInfo) -> None:
        """Update pickup information."""
        self.pickup_info = pickup_info
        self.updated_at = datetime.now()
    
    def update_comment(self, comment: Optional[str]) -> None:
        """Update order comment."""
        self.comment = comment
        self.updated_at = datetime.now()
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    def can_be_modified(self) -> bool:
        """Check if order can be modified."""
        return self.status == OrderStatus.PENDING
    
    def is_delivery(self) -> bool:
        """Check if order is for delivery."""
        return self.order_type == OrderType.DELIVERY
    
    def is_pickup(self) -> bool:
        """Check if order is for pickup."""
        return self.order_type == OrderType.PICKUP
    
    def get_contact_phone(self) -> Optional[str]:
        """Get contact phone for order."""
        if self.delivery_info:
            return self.delivery_info.phone
        elif self.pickup_info:
            return self.pickup_info.phone
        return None
    
    def get_delivery_address(self) -> Optional[str]:
        """Get delivery address."""
        if self.delivery_info:
            return self.delivery_info.address
        return None
    
    def get_summary(self) -> OrderSummary:
        """Get order summary."""
        return OrderSummary(
            items=self.items,
            subtotal=self.subtotal,
            delivery_fee=self.delivery_fee,
            discount=self.discount,
            total=self.total
        )
    
    def __str__(self) -> str:
        return f"Order(id={self.order_id}, user_id={self.user_id}, type={self.order_type}, status={self.status}, total={self.total})"
    
    def __repr__(self) -> str:
        return self.__str__()