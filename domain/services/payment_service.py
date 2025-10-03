"""Payment service for business logic."""

from typing import Optional, Dict, Any
from datetime import datetime

from domain.entities.payment import Payment
from domain.entities.order import Order
from domain.repositories.payment_repository import PaymentRepository
from domain.repositories.order_repository import OrderRepository
from infrastructure.external.payment.base_payment import BasePaymentIntegration, PaymentRequest, PaymentResponse


class PaymentService:
    """Payment service for business logic."""

    def __init__(
        self, 
        payment_repository: PaymentRepository,
        order_repository: OrderRepository,
        payment_integration: BasePaymentIntegration
    ):
        self.payment_repository = payment_repository
        self.order_repository = order_repository
        self.payment_integration = payment_integration

    async def create_payment(self, order: Order, return_url: Optional[str] = None) -> Payment:
        """Create payment for order."""
        # Check if payment already exists
        existing_payment = await self.payment_repository.get_payment_by_order_id(order.order_id)
        if existing_payment and existing_payment.status in ["pending", "processing"]:
            return existing_payment

        # Create payment request
        payment_request = PaymentRequest(
            order_id=order.order_id,
            amount=order.total,
            description=f"Оплата заказа #{order.order_id}",
            return_url=return_url,
            payment_metadata={
                "order_id": order.order_id,
                "user_id": order.user_id,
                "order_type": order.order_type.value
            }
        )

        # Create payment via integration
        payment_response = await self.payment_integration.create_payment(payment_request)

        # Create payment entity
        payment = Payment(
            payment_id=payment_response.payment_id,
            order_id=order.order_id,
            user_id=order.user_id,
            amount=payment_response.amount,
            currency=payment_response.currency,
            status=payment_response.status,
            payment_url=payment_response.payment_url,
            payment_method="online",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save payment
        return await self.payment_repository.create_payment(payment)

    async def get_payment_status(self, payment_id: str) -> Payment:
        """Get payment status."""
        payment = await self.payment_repository.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        # Get status from payment integration
        status_response = await self.payment_integration.get_payment_status(payment_id)

        # Update payment status
        payment.status = status_response.status
        payment.updated_at = datetime.now()

        return await self.payment_repository.update_payment(payment)

    async def process_payment_webhook(self, webhook_data: Dict[str, Any]) -> Payment:
        """Process payment webhook."""
        payment_id = webhook_data.get("object", {}).get("id")
        if not payment_id:
            raise ValueError("Payment ID not found in webhook data")

        # Get payment from database
        payment = await self.payment_repository.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        # Update payment status
        new_status = webhook_data.get("object", {}).get("status")
        if new_status:
            payment.status = new_status
            payment.updated_at = datetime.now()
            payment = await self.payment_repository.update_payment(payment)

        # Update order status if payment is successful
        if new_status == "succeeded":
            order = await self.order_repository.get_order_by_id(payment.order_id)
            if order:
                order.status = "confirmed"
                order.updated_at = datetime.now()
                await self.order_repository.update_order(order)

        return payment

    async def cancel_payment(self, payment_id: str) -> bool:
        """Cancel payment."""
        payment = await self.payment_repository.get_payment_by_id(payment_id)
        if not payment:
            return False

        if payment.status not in ["pending", "processing"]:
            return False

        # Cancel via payment integration
        success = await self.payment_integration.cancel_payment(payment_id)

        if success:
            payment.status = "cancelled"
            payment.updated_at = datetime.now()
            await self.payment_repository.update_payment(payment)

        return success

    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> bool:
        """Refund payment."""
        payment = await self.payment_repository.get_payment_by_id(payment_id)
        if not payment:
            return False

        if payment.status != "succeeded":
            return False

        # Refund via payment integration
        success = await self.payment_integration.refund_payment(payment_id, amount)

        if success:
            payment.status = "refunded"
            payment.updated_at = datetime.now()
            await self.payment_repository.update_payment(payment)

        return success

    async def get_payment_url(self, payment_id: str) -> Optional[str]:
        """Get payment URL."""
        payment = await self.payment_repository.get_payment_by_id(payment_id)
        return payment.payment_url if payment else None