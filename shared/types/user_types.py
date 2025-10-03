"""User-related types."""

from enum import Enum
from typing import Literal


class UserRole(str, Enum):
    """User role enumeration."""
    
    CUSTOMER = "customer"      # Клиент
    ADMIN = "admin"           # Администратор
    COURIER = "courier"       # Курьер


class UserStatus(str, Enum):
    """User status enumeration."""
    
    ACTIVE = "active"         # Активный пользователь
    BLOCKED = "blocked"       # Заблокированный пользователь
    DELETED = "deleted"       # Удаленный пользователь


# User preferences
UserLanguage = Literal["ru", "en"]
UserTimezone = Literal["Europe/Moscow", "UTC"]

# User limits
MAX_USER_NAME_LENGTH = 100
MAX_USER_PHONE_LENGTH = 20
MAX_USER_ADDRESS_LENGTH = 500

# User session settings
USER_SESSION_TIMEOUT = 30 * 60  # 30 minutes
MAX_USER_SESSIONS = 5           # Maximum concurrent sessions per user

# User notification preferences
class NotificationType(str, Enum):
    """Notification type enumeration."""
    
    ORDER_STATUS = "order_status"      # Статус заказа
    PROMOTIONS = "promotions"         # Акции и скидки
    NEWS = "news"                     # Новости кафе
    REVIEWS = "reviews"              # Отзывы


# User statistics
class UserStats:
    """User statistics data class."""
    
    def __init__(
        self,
        total_orders: int = 0,
        total_spent: int = 0,
        favorite_items: list[str] = None,
        last_order_date: str | None = None,
        average_order_value: int = 0,
    ):
        self.total_orders = total_orders
        self.total_spent = total_spent
        self.favorite_items = favorite_items or []
        self.last_order_date = last_order_date
        self.average_order_value = average_order_value