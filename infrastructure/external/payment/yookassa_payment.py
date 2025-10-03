"""YooKassa payment integration."""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

from .base_payment import BasePaymentIntegration, PaymentRequest, PaymentResponse, PaymentStatus


class YooKassaPaymentIntegration(BasePaymentIntegration):
    """YooKassa payment integration."""
    
    def __init__(self, shop_id: str, secret_key: str, test_mode: bool = True):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.base_url = "https://api.yookassa.ru/v3" if not test_mode else "https://api.yookassa.ru/v3"
        self.auth_header = f"Basic {self._encode_auth()}"
    
    def _encode_auth(self) -> str:
        """Encode authentication credentials."""
        import base64
        credentials = f"{self.shop_id}:{self.secret_key}"
        return base64.b64encode(credentials.encode()).decode()
    
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Create payment using YooKassa."""
        payment_data = {
            "amount": {
                "value": f"{request.amount / 100:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.return_url or "https://t.me/your_bot"
            },
            "description": request.description,
            "metadata": {
                "order_id": request.order_id,
                **(request.payment_metadata or {})
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/payments",
                json=payment_data,
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json",
                    "Idempotence-Key": f"{request.order_id}_{int(datetime.now().timestamp())}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return PaymentResponse(
                        payment_id=data["id"],
                        payment_url=data["confirmation"]["confirmation_url"],
                        status=data["status"],
                        amount=request.amount,
                        currency="RUB"
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"YooKassa API error: {response.status} - {error_text}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get payment status from YooKassa."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/payments/{payment_id}",
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return PaymentStatus(
                        payment_id=data["id"],
                        status=data["status"],
                        amount=int(float(data["amount"]["value"]) * 100),
                        currency=data["amount"]["currency"],
                        payment_metadata=data.get("metadata")
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"YooKassa API error: {response.status} - {error_text}")
    
    async def cancel_payment(self, payment_id: str) -> bool:
        """Cancel payment in YooKassa."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/payments/{payment_id}/cancel",
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json",
                    "Idempotence-Key": f"cancel_{payment_id}_{int(datetime.now().timestamp())}"
                }
            ) as response:
                return response.status == 200
    
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> bool:
        """Refund payment in YooKassa."""
        refund_data = {
            "payment_id": payment_id,
            "amount": {
                "value": f"{(amount or 0) / 100:.2f}",
                "currency": "RUB"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/refunds",
                json=refund_data,
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json",
                    "Idempotence-Key": f"refund_{payment_id}_{int(datetime.now().timestamp())}"
                }
            ) as response:
                return response.status == 200