"""Payment completed domain event."""

from datetime import datetime
from typing import Any, Dict

from domain.entities.payment import Payment


class PaymentCompleted:
    """Domain event for payment completion."""
    
    def __init__(self, payment: Payment, occurred_at: datetime | None = None):
        self.payment = payment
        self.occurred_at = occurred_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": "payment_completed",
            "payment_id": self.payment.payment_id,
            "order_id": self.payment.order_id,
            "user_id": self.payment.user_id,
            "amount": self.payment.amount,
            "currency": self.payment.currency.value,
            "provider": self.payment.provider.value,
            "transaction_id": self.payment.transaction_id,
            "occurred_at": self.occurred_at.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"PaymentCompleted(payment_id={self.payment.payment_id}, order_id={self.payment.order_id}, amount={self.payment.amount})"
    
    def __repr__(self) -> str:
        return self.__str__()