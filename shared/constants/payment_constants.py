"""Payment-related constants."""

from enum import Enum


class PaymentProvider(str, Enum):
    """Payment provider enumeration."""
    
    YOOKASSA = "yookassa"
    CLOUDPAYMENTS = "cloudpayments"
    STRIPE = "stripe"


class PaymentCurrency(str, Enum):
    """Payment currency enumeration."""
    
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


# Payment provider settings
PAYMENT_PROVIDERS = {
    PaymentProvider.YOOKASSA: {
        "name": "ЮKassa",
        "supported_currencies": [PaymentCurrency.RUB],
        "webhook_timeout": 30,
        "retry_attempts": 3,
    },
    PaymentProvider.CLOUDPAYMENTS: {
        "name": "CloudPayments",
        "supported_currencies": [PaymentCurrency.RUB, PaymentCurrency.USD, PaymentCurrency.EUR],
        "webhook_timeout": 30,
        "retry_attempts": 3,
    },
    PaymentProvider.STRIPE: {
        "name": "Stripe",
        "supported_currencies": [PaymentCurrency.USD, PaymentCurrency.EUR],
        "webhook_timeout": 30,
        "retry_attempts": 3,
    },
}

# Payment limits
MIN_PAYMENT_AMOUNT = 100        # Минимальная сумма платежа (в копейках)
MAX_PAYMENT_AMOUNT = 100000     # Максимальная сумма платежа (в копейках)

# Payment timeouts
PAYMENT_TIMEOUT_MINUTES = 15    # Таймаут ожидания оплаты
PAYMENT_RETRY_DELAY_SECONDS = 5 # Задержка между попытками

# Webhook settings
WEBHOOK_TIMEOUT_SECONDS = 30
WEBHOOK_RETRY_ATTEMPTS = 3
WEBHOOK_RETRY_DELAY_SECONDS = 5

# Refund settings
MAX_REFUND_DAYS = 30           # Максимальное количество дней для возврата
REFUND_PROCESSING_DAYS = 3     # Время обработки возврата

# Security settings
WEBHOOK_SIGNATURE_HEADER = "X-Signature"
PAYMENT_ID_LENGTH = 32         # Длина ID платежа
TRANSACTION_ID_LENGTH = 64     # Длина ID транзакции

# Error codes
PAYMENT_ERROR_CODES = {
    "INSUFFICIENT_FUNDS": "Недостаточно средств",
    "CARD_DECLINED": "Карта отклонена",
    "EXPIRED_CARD": "Карта просрочена",
    "INVALID_CARD": "Неверные данные карты",
    "NETWORK_ERROR": "Ошибка сети",
    "TIMEOUT": "Превышено время ожидания",
    "UNKNOWN_ERROR": "Неизвестная ошибка",
}