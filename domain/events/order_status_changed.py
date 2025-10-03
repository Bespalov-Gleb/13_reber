"""Order status changed domain event."""

from datetime import datetime
from typing import Any, Dict

from domain.entities.order import Order
from shared.constants.order_constants import OrderStatus


class OrderStatusChanged:
    """Domain event for order status change."""
    
    def __init__(
        self,
        order: Order,
        old_status: OrderStatus,
        new_status: OrderStatus,
        occurred_at: datetime | None = None,
    ):
        self.order = order
        self.old_status = old_status
        self.new_status = new_status
        self.occurred_at = occurred_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": "order_status_changed",
            "order_id": self.order.order_id,
            "user_id": self.order.user_id,
            "old_status": self.old_status.value,
            "new_status": self.new_status.value,
            "order_type": self.order.order_type.value,
            "total": self.order.total,
            "occurred_at": self.occurred_at.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"OrderStatusChanged(order_id={self.order.order_id}, {self.old_status.value} -> {self.new_status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()