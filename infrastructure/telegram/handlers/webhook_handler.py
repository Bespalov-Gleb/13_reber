"""Webhook handler for external services."""

import json
import hashlib
import hmac
from typing import Dict, Any

from aiohttp import web
from aiohttp.web import Request, Response

from app.config import get_settings


class WebhookHandler:
    """Handler for webhook requests from external services."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def get_routes(self):
        """Get webhook routes."""
        return [
            web.post("/webhook/yookassa", self.handle_yookassa_webhook),
            web.post("/webhook/cloudpayments", self.handle_cloudpayments_webhook)
        ]
    
    async def handle_yookassa_webhook(self, request: Request) -> Response:
        """Handle YooKassa webhook."""
        try:
            # Get request body
            body = await request.read()
            data = json.loads(body.decode())
            
            # Verify webhook signature (if configured)
            if self.settings.webhook_secret:
                signature = request.headers.get("X-YooMoney-Signature")
                if not self._verify_yookassa_signature(body, signature):
                    return web.json_response({"error": "Invalid signature"}, status=400)
            
            # Process payment notification
            event = data.get("event")
            payment_data = data.get("object", {})
            
            if event == "payment.succeeded":
                await self._process_payment_success(payment_data)
            elif event == "payment.canceled":
                await self._process_payment_canceled(payment_data)
            elif event == "payment.waiting_for_capture":
                await self._process_payment_waiting(payment_data)
            
            return web.json_response({"status": "ok"})
            
        except Exception as e:
            print(f"❌ YooKassa webhook error: {e}")
            return web.json_response({"error": "Internal server error"}, status=500)
    
    async def handle_cloudpayments_webhook(self, request: Request) -> Response:
        """Handle CloudPayments webhook."""
        try:
            # Get request body
            body = await request.read()
            data = json.loads(body.decode())
            
            # Verify webhook signature
            signature = request.headers.get("Content-HMAC")
            if not self._verify_cloudpayments_signature(body, signature):
                return web.json_response({"error": "Invalid signature"}, status=400)
            
            # Process payment notification
            event = data.get("Event")
            payment_data = data.get("Data", {})
            
            if event == "PaymentSucceeded":
                await self._process_cloudpayments_success(payment_data)
            elif event == "PaymentFailed":
                await self._process_cloudpayments_failed(payment_data)
            
            return web.json_response({"code": 0})
            
        except Exception as e:
            print(f"❌ CloudPayments webhook error: {e}")
            return web.json_response({"error": "Internal server error"}, status=500)
    
    def _verify_yookassa_signature(self, body: bytes, signature: str) -> bool:
        """Verify YooKassa webhook signature."""
        if not signature:
            return False
        
        # YooKassa uses HMAC-SHA256
        expected_signature = hmac.new(
            self.settings.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _verify_cloudpayments_signature(self, body: bytes, signature: str) -> bool:
        """Verify CloudPayments webhook signature."""
        if not signature:
            return False
        
        # CloudPayments uses HMAC-SHA256
        expected_signature = hmac.new(
            self.settings.cloudpayments_api_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def _process_payment_success(self, payment_data: Dict[str, Any]):
        """Process successful payment from YooKassa."""
        try:
            payment_id = payment_data.get("id")
            order_id = payment_data.get("metadata", {}).get("order_id")
            
            if not payment_id or not order_id:
                print(f"⚠️ Missing payment_id or order_id in YooKassa webhook: {payment_data}")
                return
            
            # Get services
            from app.dependencies import container
            from infrastructure.database.session import get_current_session
            
            async with get_current_session() as session:
                payment_service = container.get_payment_service(session)
                order_service = container.get_order_service(session)
                
                # Update payment status
                await payment_service.update_payment_status(payment_id, "succeeded")
                
                # Update order status
                from shared.constants.order_constants import OrderStatus
                await order_service.update_order_status(order_id, OrderStatus.CONFIRMED)
                
                # Send notifications
                from app.dependencies import get_notification_service
                notification_service = await get_notification_service()
                
                order = await order_service.get_order(order_id)
                if order:
                    user = await order_service.get_user_by_id(order.user_id)
                    if user:
                        await notification_service.send_order_status_notification(order, user)
            
            print(f"✅ Payment {payment_id} for order {order_id} processed successfully")
            
        except Exception as e:
            print(f"❌ Error processing YooKassa payment success: {e}")
    
    async def _process_payment_canceled(self, payment_data: Dict[str, Any]):
        """Process canceled payment from YooKassa."""
        try:
            payment_id = payment_data.get("id")
            order_id = payment_data.get("metadata", {}).get("order_id")
            
            if not payment_id or not order_id:
                print(f"⚠️ Missing payment_id or order_id in YooKassa webhook: {payment_data}")
                return
            
            # Get services
            from app.dependencies import container
            from infrastructure.database.session import get_current_session
            
            async with get_current_session() as session:
                payment_service = container.get_payment_service(session)
                order_service = container.get_order_service(session)
                
                # Update payment status
                await payment_service.update_payment_status(payment_id, "canceled")
                
                # Update order status
                from shared.constants.order_constants import OrderStatus
                await order_service.update_order_status(order_id, OrderStatus.CANCELLED)
            
            print(f"❌ Payment {payment_id} for order {order_id} was canceled")
            
        except Exception as e:
            print(f"❌ Error processing YooKassa payment cancel: {e}")
    
    async def _process_payment_waiting(self, payment_data: Dict[str, Any]):
        """Process waiting payment from YooKassa."""
        try:
            payment_id = payment_data.get("id")
            order_id = payment_data.get("metadata", {}).get("order_id")
            
            if not payment_id or not order_id:
                print(f"⚠️ Missing payment_id or order_id in YooKassa webhook: {payment_data}")
                return
            
            # Get services
            from app.dependencies import container
            from infrastructure.database.session import get_current_session
            
            async with get_current_session() as session:
                payment_service = container.get_payment_service(session)
                
                # Update payment status
                await payment_service.update_payment_status(payment_id, "waiting_for_capture")
            
            print(f"⏳ Payment {payment_id} for order {order_id} is waiting for capture")
            
        except Exception as e:
            print(f"❌ Error processing YooKassa payment waiting: {e}")
    
    async def _process_cloudpayments_success(self, payment_data: Dict[str, Any]):
        """Process successful payment from CloudPayments."""
        try:
            payment_id = payment_data.get("TransactionId")
            order_id = payment_data.get("OrderId")
            
            if not payment_id or not order_id:
                print(f"⚠️ Missing TransactionId or OrderId in CloudPayments webhook: {payment_data}")
                return
            
            # Get services
            from app.dependencies import container
            from infrastructure.database.session import get_current_session
            
            async with get_current_session() as session:
                payment_service = container.get_payment_service(session)
                order_service = container.get_order_service(session)
                
                # Update payment status
                await payment_service.update_payment_status(payment_id, "succeeded")
                
                # Update order status
                from shared.constants.order_constants import OrderStatus
                await order_service.update_order_status(order_id, OrderStatus.CONFIRMED)
                
                # Send notifications
                from app.dependencies import get_notification_service
                notification_service = await get_notification_service()
                
                order = await order_service.get_order(order_id)
                if order:
                    user = await order_service.get_user_by_id(order.user_id)
                    if user:
                        await notification_service.send_order_status_notification(order, user)
            
            print(f"✅ CloudPayments payment {payment_id} for order {order_id} processed successfully")
            
        except Exception as e:
            print(f"❌ Error processing CloudPayments payment success: {e}")
    
    async def _process_cloudpayments_failed(self, payment_data: Dict[str, Any]):
        """Process failed payment from CloudPayments."""
        try:
            payment_id = payment_data.get("TransactionId")
            order_id = payment_data.get("OrderId")
            
            if not payment_id or not order_id:
                print(f"⚠️ Missing TransactionId or OrderId in CloudPayments webhook: {payment_data}")
                return
            
            # Get services
            from app.dependencies import container
            from infrastructure.database.session import get_current_session
            
            async with get_current_session() as session:
                payment_service = container.get_payment_service(session)
                order_service = container.get_order_service(session)
                
                # Update payment status
                await payment_service.update_payment_status(payment_id, "failed")
                
                # Update order status
                from shared.constants.order_constants import OrderStatus
                await order_service.update_order_status(order_id, OrderStatus.CANCELLED)
            
            print(f"❌ CloudPayments payment {payment_id} for order {order_id} failed")
            
        except Exception as e:
            print(f"❌ Error processing CloudPayments payment failure: {e}")


# Create global instance
webhook_handler = WebhookHandler()
