"""Order-related constants."""

from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    
    PENDING = "pending"           # Заказ создан, ожидает подтверждения
    CONFIRMED = "confirmed"       # Заказ подтвержден
    PREPARING = "preparing"       # Заказ готовится
    READY = "ready"              # Заказ готов
    OUT_FOR_DELIVERY = "delivery" # Заказ в доставке
    DELIVERED = "delivered"       # Заказ доставлен
    PICKED_UP = "picked_up"       # Заказ получен (самовывоз)
    CANCELLED = "cancelled"       # Заказ отменен
    REFUNDED = "refunded"         # Заказ возвращен


class OrderType(str, Enum):
    """Order type enumeration."""
    
    DELIVERY = "delivery"         # Доставка
    PICKUP = "pickup"            # Самовывоз


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    
    PENDING = "pending"          # Ожидает оплаты
    PROCESSING = "processing"    # Обрабатывается
    COMPLETED = "completed"      # Оплачен
    FAILED = "failed"           # Неуспешная оплата
    REFUNDED = "refunded"       # Возвращен
    CANCELLED = "cancelled"     # Отменен


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    
    ONLINE = "online"           # Онлайн оплата
    CASH = "cash"              # Наличные при получении
    CARD = "card"              # Карта при получении


# Order time options
ORDER_TIME_ASAP = "asap"        # Как можно скорее
ORDER_TIME_SCHEDULED = "scheduled"  # К определенному времени

# Order limits
MIN_ORDER_AMOUNT = 500          # Минимальная сумма заказа (в копейках)
MAX_ORDER_AMOUNT = 50000        # Максимальная сумма заказа (в копейках)
MAX_ORDER_ITEMS = 50            # Максимальное количество позиций в заказе

# Delivery settings
DEFAULT_DELIVERY_TIME_MINUTES = 60  # Время доставки по умолчанию
MAX_DELIVERY_TIME_MINUTES = 180     # Максимальное время доставки
DELIVERY_FEE = 200                  # Стоимость доставки (в копейках)
FREE_DELIVERY_THRESHOLD = 2000      # Порог бесплатной доставки (в копейках)

# Working hours
DEFAULT_WORKING_HOURS = "09:00-22:00"
WORKING_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Notification settings
NOTIFICATION_DELAYS = {
    OrderStatus.CONFIRMED: 0,      # Сразу после подтверждения
    OrderStatus.PREPARING: 5,      # Через 5 минут после начала приготовления
    OrderStatus.READY: 0,          # Сразу когда готов
    OrderStatus.OUT_FOR_DELIVERY: 0,  # Сразу когда отправлен на доставку
    OrderStatus.DELIVERED: 0,      # Сразу после доставки
}