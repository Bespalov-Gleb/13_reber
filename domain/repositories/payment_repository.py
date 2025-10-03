"""Payment repository interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from domain.entities.payment import Payment
from shared.constants.payment_constants import PaymentProvider, PaymentStatus
from shared.types.payment_types import PaymentAnalytics


class PaymentRepository(ABC):
    """Payment repository interface."""
    
    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        """Create new payment."""
        pass
    
    @abstractmethod
    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID."""
        pass
    
    @abstractmethod
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Get payment by order ID."""
        pass
    
    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID."""
        pass
    
    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        """Update payment."""
        pass
    
    @abstractmethod
    async def delete(self, payment_id: str) -> bool:
        """Delete payment."""
        pass
    
    @abstractmethod
    async def list_payments(
        self,
        user_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        provider: Optional[PaymentProvider] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """List payments with filters."""
        pass
    
    @abstractmethod
    async def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Get payments by status."""
        pass
    
    @abstractmethod
    async def get_payments_by_provider(self, provider: PaymentProvider) -> List[Payment]:
        """Get payments by provider."""
        pass
    
    @abstractmethod
    async def get_payments_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Payment]:
        """Get payments by date range."""
        pass
    
    @abstractmethod
    async def get_user_payments(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Payment]:
        """Get user's payments."""
        pass
    
    @abstractmethod
    async def count_payments(
        self,
        user_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        provider: Optional[PaymentProvider] = None
    ) -> int:
        """Count payments with filters."""
        pass
    
    @abstractmethod
    async def get_payment_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PaymentAnalytics:
        """Get payment analytics."""
        pass
    
    @abstractmethod
    async def get_total_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Get total revenue in kopecks."""
        pass
    
    @abstractmethod
    async def get_pending_payments(self) -> List[Payment]:
        """Get pending payments."""
        pass
    
    @abstractmethod
    async def get_failed_payments(self) -> List[Payment]:
        """Get failed payments."""
        pass