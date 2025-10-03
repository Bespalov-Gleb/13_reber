"""Order created domain event."""

from datetime import datetime
from typing import Any, Dict

from domain.entities.order import Order


class OrderCreated:
    """Domain event for order creation."""
    
    def __init__(self, order: Order, occurred_at: datetime | None = None):
        self.order = order
        self.occurred_at = occurred_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": "order_created",
            "order_id": self.order.order_id,
            "user_id": self.order.user_id,
            "order_type": self.order.order_type.value,
            "total": self.order.total,
            "payment_method": self.order.payment_method.value,
            "occurred_at": self.occurred_at.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"OrderCreated(order_id={self.order.order_id}, user_id={self.order.user_id}, total={self.order.total})"
    
    def __repr__(self) -> str:
        return self.__str__()