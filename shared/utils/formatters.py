"""Formatting utilities."""

from datetime import datetime, timedelta
from typing import Optional

from shared.constants.order_constants import OrderStatus, OrderType, PaymentMethod, PaymentStatus


def format_price(price_kopecks: int, currency: str = "₽") -> str:
    """Format price from kopecks to human-readable format."""
    rubles = price_kopecks // 100
    kopecks = price_kopecks % 100
    
    if kopecks == 0:
        return f"{rubles:,} {currency}".replace(",", " ")
    else:
        return f"{rubles:,}.{kopecks:02d} {currency}".replace(",", " ")


def format_phone(phone: str) -> str:
    """Format phone number to readable format."""
    if not phone:
        return ""
    
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Format as +7 (XXX) XXX-XX-XX
    if len(clean_phone) == 11 and clean_phone.startswith('7'):
        return f"+7 ({clean_phone[1:4]}) {clean_phone[4:7]}-{clean_phone[7:9]}-{clean_phone[9:11]}"
    
    return phone


def format_datetime(dt: datetime, format_type: str = "short") -> str:
    """Format datetime to human-readable format."""
    if not dt:
        return ""
    
    if format_type == "short":
        return dt.strftime("%d.%m.%Y %H:%M")
    elif format_type == "long":
        return dt.strftime("%d %B %Y, %H:%M")
    elif format_type == "time":
        return dt.strftime("%H:%M")
    elif format_type == "date":
        return dt.strftime("%d.%m.%Y")
    else:
        return dt.strftime("%d.%m.%Y %H:%M")


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable format."""
    if minutes < 60:
        return f"{minutes} мин"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours} ч"
    else:
        return f"{hours} ч {remaining_minutes} мин"


def format_order_status(status: OrderStatus) -> str:
    """Format order status to human-readable format."""
    status_map = {
        OrderStatus.PENDING: "⏳ Ожидает подтверждения",
        OrderStatus.CONFIRMED: "✅ Подтвержден",
        OrderStatus.PREPARING: "👨‍🍳 Готовится",
        OrderStatus.READY: "🍽️ Готов",
        OrderStatus.OUT_FOR_DELIVERY: "🚚 В доставке",
        OrderStatus.DELIVERED: "🎉 Доставлен",
        OrderStatus.PICKED_UP: "🎉 Получен",
        OrderStatus.CANCELLED: "❌ Отменен",
        OrderStatus.REFUNDED: "💰 Возвращен",
    }
    return status_map.get(status, status.value)


def format_payment_status(status: PaymentStatus) -> str:
    """Format payment status to human-readable format."""
    status_map = {
        PaymentStatus.PENDING: "⏳ Ожидает оплаты",
        PaymentStatus.PROCESSING: "🔄 Обрабатывается",
        PaymentStatus.COMPLETED: "✅ Оплачен",
        PaymentStatus.FAILED: "❌ Неуспешная оплата",
        PaymentStatus.REFUNDED: "💰 Возвращен",
        PaymentStatus.CANCELLED: "❌ Отменен",
    }
    return status_map.get(status, status.value)


def format_payment_method(method: PaymentMethod) -> str:
    """Format payment method to human-readable format."""
    method_map = {
        PaymentMethod.ONLINE: "💳 Онлайн оплата",
        PaymentMethod.CASH: "💵 Наличные",
        PaymentMethod.CARD: "💳 Карта при получении",
    }
    return method_map.get(method, method.value)


def format_order_type(order_type: OrderType) -> str:
    """Format order type to human-readable format."""
    type_map = {
        OrderType.DELIVERY: "🚚 Доставка",
        OrderType.PICKUP: "🚶 Самовывоз",
    }
    return type_map.get(order_type, order_type.value)


def format_quantity(quantity: int, item_name: str) -> str:
    """Format quantity with proper Russian pluralization."""
    if quantity == 1:
        return f"{quantity} {item_name}"
    elif 2 <= quantity <= 4:
        return f"{quantity} {item_name}а"
    else:
        return f"{quantity} {item_name}ов"


def format_address(address: str, max_length: int = 50) -> str:
    """Format address with length limit."""
    if not address:
        return ""
    
    if len(address) <= max_length:
        return address
    
    return address[:max_length-3] + "..."


def format_working_hours(hours: str) -> str:
    """Format working hours."""
    if not hours:
        return "Не указано"
    
    return f"🕐 {hours}"


def format_delivery_time(minutes: int) -> str:
    """Format delivery time."""
    if minutes <= 0:
        return "Как можно скорее"
    
    return f"Через {format_duration(minutes)}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage value."""
    return f"{value:.{decimals}f}%"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix