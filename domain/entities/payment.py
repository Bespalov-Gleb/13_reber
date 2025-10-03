"""Payment entity."""

from datetime import datetime
from typing import Optional

from shared.constants.payment_constants import PaymentCurrency, PaymentProvider, PaymentStatus


class Payment:
    """Payment domain entity."""
    
    def __init__(
        self,
        payment_id: str,
        order_id: str,
        user_id: str,
        amount: int,  # Amount in kopecks
        currency: PaymentCurrency = PaymentCurrency.RUB,
        provider: PaymentProvider = PaymentProvider.YOOKASSA,
        status: PaymentStatus = PaymentStatus.PENDING,
        transaction_id: Optional[str] = None,
        payment_url: Optional[str] = None,
        error_message: Optional[str] = None,
        payment_metadata: Optional[dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.payment_id = payment_id
        self.order_id = order_id
        self.user_id = user_id
        self.amount = amount
        self.currency = currency
        self.provider = provider
        self.status = status
        self.transaction_id = transaction_id
        self.payment_url = payment_url
        self.error_message = error_message
        self.payment_metadata = payment_metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def update_status(self, status: PaymentStatus) -> None:
        """Update payment status."""
        self.status = status
        self.updated_at = datetime.now()
    
    def set_transaction_id(self, transaction_id: str) -> None:
        """Set transaction ID."""
        self.transaction_id = transaction_id
        self.updated_at = datetime.now()
    
    def set_payment_url(self, payment_url: str) -> None:
        """Set payment URL."""
        self.payment_url = payment_url
        self.updated_at = datetime.now()
    
    def set_error(self, error_message: str) -> None:
        """Set error message."""
        self.error_message = error_message
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.now()
    
    def clear_error(self) -> None:
        """Clear error message."""
        self.error_message = None
        self.updated_at = datetime.now()
    
    def add_metadata(self, key: str, value: any) -> None:
        """Add metadata."""
        self.payment_metadata[key] = value
        self.updated_at = datetime.now()
    
    def remove_metadata(self, key: str) -> None:
        """Remove metadata."""
        if key in self.payment_metadata:
            del self.payment_metadata[key]
            self.updated_at = datetime.now()
    
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == PaymentStatus.PENDING
    
    def is_processing(self) -> bool:
        """Check if payment is processing."""
        return self.status == PaymentStatus.PROCESSING
    
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == PaymentStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if payment is failed."""
        return self.status == PaymentStatus.FAILED
    
    def is_refunded(self) -> bool:
        """Check if payment is refunded."""
        return self.status == PaymentStatus.REFUNDED
    
    def is_cancelled(self) -> bool:
        """Check if payment is cancelled."""
        return self.status == PaymentStatus.CANCELLED
    
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded."""
        return self.status == PaymentStatus.COMPLETED
    
    def can_be_cancelled(self) -> bool:
        """Check if payment can be cancelled."""
        return self.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]
    
    def __str__(self) -> str:
        return f"Payment(id={self.payment_id}, order_id={self.order_id}, amount={self.amount}, status={self.status})"
    
    def __repr__(self) -> str:
        return self.__str__()