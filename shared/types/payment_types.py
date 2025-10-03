"""Payment-related types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from shared.constants.payment_constants import PaymentCurrency, PaymentProvider, PaymentStatus


@dataclass
class PaymentRequest:
    """Payment request data class."""
    
    amount: int  # Amount in kopecks
    currency: PaymentCurrency
    order_id: str
    description: str
    provider: PaymentProvider
    return_url: Optional[str] = None
    payment_metadata: Optional[dict] = None


@dataclass
class PaymentResponse:
    """Payment response data class."""
    
    payment_id: str
    status: PaymentStatus
    payment_url: Optional[str] = None
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class PaymentWebhook:
    """Payment webhook data class."""
    
    payment_id: str
    transaction_id: str
    status: PaymentStatus
    amount: int  # Amount in kopecks
    currency: PaymentCurrency
    provider: PaymentProvider
    signature: str
    timestamp: datetime
    payment_metadata: Optional[dict] = None


@dataclass
class RefundRequest:
    """Refund request data class."""
    
    payment_id: str
    amount: int  # Amount in kopecks
    reason: str
    provider: PaymentProvider
    payment_metadata: Optional[dict] = None


@dataclass
class RefundResponse:
    """Refund response data class."""
    
    refund_id: str
    status: PaymentStatus
    amount: int  # Amount in kopecks
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class PaymentAnalytics:
    """Payment analytics data class."""
    
    total_payments: int
    successful_payments: int
    failed_payments: int
    total_revenue: int  # Total revenue in kopecks
    average_payment_amount: int  # Average payment amount in kopecks
    payments_by_provider: dict[PaymentProvider, int]
    payments_by_currency: dict[PaymentCurrency, int]
    payments_by_status: dict[PaymentStatus, int]
    conversion_rate: float  # Success rate (0.0 to 1.0)
    refund_rate: float  # Refund rate (0.0 to 1.0)


@dataclass
class PaymentLimits:
    """Payment limits data class."""
    
    min_amount: int  # Minimum amount in kopecks
    max_amount: int  # Maximum amount in kopecks
    daily_limit: int  # Daily limit in kopecks
    monthly_limit: int  # Monthly limit in kopecks
    max_transactions_per_day: int
    max_transactions_per_month: int