"""Base payment integration class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PaymentRequest:
    """Payment request data."""
    order_id: str
    amount: int  # Amount in kopecks
    description: str
    return_url: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaymentResponse:
    """Payment response data."""
    payment_id: str
    payment_url: str
    status: str
    amount: int
    currency: str = "RUB"


@dataclass
class PaymentStatus:
    """Payment status data."""
    payment_id: str
    status: str
    amount: int
    currency: str = "RUB"
    payment_metadata: Optional[Dict[str, Any]] = None


class BasePaymentIntegration(ABC):
    """Base class for payment integrations."""
    
    @abstractmethod
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Create payment."""
        pass
    
    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get payment status."""
        pass
    
    @abstractmethod
    async def cancel_payment(self, payment_id: str) -> bool:
        """Cancel payment."""
        pass
    
    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> bool:
        """Refund payment."""
        pass