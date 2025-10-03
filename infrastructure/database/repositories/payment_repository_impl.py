"""Payment repository implementation."""

from datetime import datetime
from typing import List, Optional

from domain.entities.payment import Payment
from domain.repositories.payment_repository import PaymentRepository
from infrastructure.database.models.payment_model import PaymentModel
from shared.constants.order_constants import PaymentMethod
from shared.constants.payment_constants import PaymentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_


class PaymentRepositoryImpl(PaymentRepository):
    """Payment repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, payment: Payment) -> Payment:
        """Create new payment."""
        db_payment = PaymentModel(
            id=payment.payment_id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            payment_method=payment.payment_method,
            payment_url=payment.payment_url,
            external_payment_id=payment.external_payment_id,
            payment_metadata=payment.payment_metadata,
            created_at=payment.created_at or datetime.now(),
            updated_at=payment.updated_at or datetime.now()
        )
        
        self.session.add(db_payment)
        await self.session.flush()
        await self.session.refresh(db_payment)
        
        return self._model_to_entity(db_payment)
    
    async def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        db_payment = result.scalar_one_or_none()
        
        if db_payment:
            return self._model_to_entity(db_payment)
        return None
    
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Get payment by order ID."""
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.order_id == order_id)
        )
        db_payment = result.scalar_one_or_none()
        
        if db_payment:
            return self._model_to_entity(db_payment)
        return None
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID."""
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.external_payment_id == transaction_id)
        )
        db_payment = result.scalar_one_or_none()
        
        if db_payment:
            return self._model_to_entity(db_payment)
        return None
    
    async def update(self, payment: Payment) -> Payment:
        """Update payment."""
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment.payment_id)
        )
        db_payment = result.scalar_one_or_none()
        
        if not db_payment:
            raise ValueError(f"Payment with id {payment.payment_id} not found")
        
        db_payment.amount = payment.amount
        db_payment.currency = payment.currency
        db_payment.status = payment.status
        db_payment.payment_method = payment.payment_method
        db_payment.payment_url = payment.payment_url
        db_payment.external_payment_id = payment.external_payment_id
        db_payment.payment_metadata = payment.payment_metadata
        db_payment.updated_at = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(db_payment)
        
        return self._model_to_entity(db_payment)
    
    async def delete(self, payment_id: str) -> bool:
        """Delete payment."""
        result = await self.session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        db_payment = result.scalar_one_or_none()
        
        if not db_payment:
            return False
        
        await self.session.delete(db_payment)
        await self.session.flush()
        return True
    
    async def list_payments(self, limit: int = 100, offset: int = 0) -> List[Payment]:
        """List payments."""
        result = await self.session.execute(
            select(PaymentModel)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_payments = result.scalars().all()
        
        return [self._model_to_entity(payment) for payment in db_payments]
    
    async def get_payments_by_status(self, status: PaymentStatus, limit: int = 100, offset: int = 0) -> List[Payment]:
        """Get payments by status."""
        result = await self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.status == status.value)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_payments = result.scalars().all()
        
        return [self._model_to_entity(payment) for payment in db_payments]
    
    async def get_payments_by_method(self, method: PaymentMethod, limit: int = 100, offset: int = 0) -> List[Payment]:
        """Get payments by method."""
        result = await self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.payment_method == method.value)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_payments = result.scalars().all()
        
        return [self._model_to_entity(payment) for payment in db_payments]
    
    async def get_payments_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Payment]:
        """Get payments by date range."""
        result = await self.session.execute(
            select(PaymentModel)
            .where(
                and_(
                    PaymentModel.created_at >= start_date,
                    PaymentModel.created_at <= end_date
                )
            )
            .order_by(PaymentModel.created_at.desc())
        )
        db_payments = result.scalars().all()
        
        return [self._model_to_entity(payment) for payment in db_payments]
    
    async def count_payments(self) -> int:
        """Get total payment count."""
        result = await self.session.execute(
            select(func.count(PaymentModel.id))
        )
        return result.scalar() or 0
    
    async def get_user_payment_count(self, user_id: str) -> int:
        """Get user's payment count."""
        result = await self.session.execute(
            select(func.count(PaymentModel.id)).where(PaymentModel.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def get_user_total_paid(self, user_id: str) -> int:
        """Get user's total paid amount."""
        result = await self.session.execute(
            select(func.sum(PaymentModel.amount))
            .where(
                and_(
                    PaymentModel.user_id == user_id,
                    PaymentModel.status == PaymentStatus.SUCCEEDED.value
                )
            )
        )
        return result.scalar() or 0
    
    async def get_successful_payments(self, limit: int = 100, offset: int = 0) -> List[Payment]:
        """Get successful payments."""
        result = await self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.status == PaymentStatus.SUCCEEDED.value)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_payments = result.scalars().all()
        
        return [self._model_to_entity(payment) for payment in db_payments]
    
    async def get_failed_payments(self, limit: int = 100, offset: int = 0) -> List[Payment]:
        """Get failed payments."""
        result = await self.session.execute(
            select(PaymentModel)
            .where(PaymentModel.status == PaymentStatus.FAILED.value)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_payments = result.scalars().all()
        
        return [self._model_to_entity(payment) for payment in db_payments]
    
    def _model_to_entity(self, db_payment: PaymentModel) -> Payment:
        """Convert PaymentModel to Payment entity."""
        return Payment(
            payment_id=db_payment.id,
            order_id=db_payment.order_id,
            user_id=db_payment.user_id,
            amount=db_payment.amount,
            currency=db_payment.currency,
            status=db_payment.status,
            payment_method=db_payment.payment_method,
            payment_url=db_payment.payment_url,
            external_payment_id=db_payment.external_payment_id,
            payment_metadata=db_payment.payment_metadata,
            created_at=db_payment.created_at,
            updated_at=db_payment.updated_at
        )