"""CloudPayments payment integration."""

import asyncio
import aiohttp
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime

from .base_payment import BasePaymentIntegration, PaymentRequest, PaymentResponse, PaymentStatus


class CloudPaymentsPaymentIntegration(BasePaymentIntegration):
    """CloudPayments payment integration."""
    
    def __init__(self, public_id: str, api_secret: str, test_mode: bool = True):
        self.public_id = public_id
        self.api_secret = api_secret
        self.test_mode = test_mode
        self.base_url = "https://api.cloudpayments.ru"
    
    def _generate_signature(self, data: str) -> str:
        """Generate HMAC signature for CloudPayments."""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Create payment using CloudPayments."""
        payment_data = {
            "PublicId": self.public_id,
            "Amount": request.amount / 100,  # Convert kopecks to rubles
            "Currency": "RUB",
            "InvoiceId": request.order_id,
            "Description": request.description,
            "TestMode": self.test_mode,
            "ReturnUrl": request.return_url or "https://t.me/your_bot",
            "Data": request.payment_metadata or {}
        }
        
        # Generate signature
        data_string = f"{payment_data['Amount']}{payment_data['Currency']}{payment_data['PublicId']}{payment_data['InvoiceId']}"
        signature = self._generate_signature(data_string)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/payments/cards/charge",
                json=payment_data,
                headers={
                    "Content-Type": "application/json",
                    "X-CP-Signature": signature
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Success"):
                        return PaymentResponse(
                            payment_id=data["Model"]["TransactionId"],
                            payment_url=data["Model"].get("AcsUrl", ""),
                            status="pending",
                            amount=request.amount,
                            currency="RUB"
                        )
                    else:
                        raise Exception(f"CloudPayments error: {data.get('Message', 'Unknown error')}")
                else:
                    error_text = await response.text()
                    raise Exception(f"CloudPayments API error: {response.status} - {error_text}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Get payment status from CloudPayments."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/payments/get",
                params={"TransactionId": payment_id},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {self._encode_auth()}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("Success"):
                        model = data["Model"]
                        return PaymentStatus(
                            payment_id=model["TransactionId"],
                            status=self._map_status(model["Status"]),
                            amount=int(model["Amount"] * 100),  # Convert rubles to kopecks
                            currency=model["Currency"],
                            payment_metadata=model.get("Data")
                        )
                    else:
                        raise Exception(f"CloudPayments error: {data.get('Message', 'Unknown error')}")
                else:
                    error_text = await response.text()
                    raise Exception(f"CloudPayments API error: {response.status} - {error_text}")
    
    def _encode_auth(self) -> str:
        """Encode authentication credentials for CloudPayments."""
        import base64
        credentials = f"{self.public_id}:{self.api_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _map_status(self, cloudpayments_status: str) -> str:
        """Map CloudPayments status to our status."""
        status_mapping = {
            "Completed": "succeeded",
            "Authorized": "pending",
            "Cancelled": "cancelled",
            "Declined": "failed"
        }
        return status_mapping.get(cloudpayments_status, "pending")
    
    async def cancel_payment(self, payment_id: str) -> bool:
        """Cancel payment in CloudPayments."""
        cancel_data = {
            "TransactionId": payment_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/payments/cancel",
                json=cancel_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {self._encode_auth()}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("Success", False)
                return False
    
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> bool:
        """Refund payment in CloudPayments."""
        refund_data = {
            "TransactionId": payment_id,
            "Amount": (amount or 0) / 100  # Convert kopecks to rubles
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/payments/refund",
                json=refund_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {self._encode_auth()}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("Success", False)
                return False
