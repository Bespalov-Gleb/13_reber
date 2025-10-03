"""Helper utilities."""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import re


def generate_id(length: int = 8) -> str:
    """Generate random ID."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_payment_id() -> str:
    """Generate unique payment ID."""
    timestamp = int(datetime.now().timestamp())
    random_part = secrets.token_hex(4)
    return f"pay_{timestamp}_{random_part}"


def generate_order_id() -> str:
    """Generate unique order ID."""
    timestamp = int(datetime.now().timestamp())
    random_part = secrets.token_hex(4)
    return f"ord_{timestamp}_{random_part}"


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    
    return password_hash.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against hash."""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash


def is_working_hours(working_hours: str, current_time: Optional[datetime] = None) -> bool:
    """Check if current time is within working hours."""
    if not working_hours:
        return True
    
    if current_time is None:
        current_time = datetime.now()
    
    try:
        # Parse working hours (format: "09:00-22:00")
        start_str, end_str = working_hours.split('-')
        start_time = datetime.strptime(start_str, '%H:%M').time()
        end_time = datetime.strptime(end_str, '%H:%M').time()
        current_time_only = current_time.time()
        
        return start_time <= current_time_only <= end_time
    except (ValueError, IndexError):
        return True  # If parsing fails, assume always open


def calculate_delivery_time(
    base_time_minutes: int = 60,
    distance_km: Optional[float] = None,
    traffic_factor: float = 1.0
) -> int:
    """Calculate delivery time in minutes."""
    delivery_time = base_time_minutes
    
    # Add time based on distance (1 minute per km)
    if distance_km:
        delivery_time += int(distance_km)
    
    # Apply traffic factor
    delivery_time = int(delivery_time * traffic_factor)
    
    # Minimum delivery time
    return max(delivery_time, 30)


def calculate_delivery_fee(
    order_amount: int,
    distance_km: Optional[float] = None,
    free_delivery_threshold: int = 2000,
    base_delivery_fee: int = 200
) -> int:
    """Calculate delivery fee in kopecks."""
    # Free delivery if order amount exceeds threshold
    if order_amount >= free_delivery_threshold:
        return 0
    
    # Base delivery fee
    fee = base_delivery_fee
    
    # Add extra fee for long distance (10 kopecks per km over 5km)
    if distance_km and distance_km > 5:
        extra_km = distance_km - 5
        fee += int(extra_km * 10)
    
    return fee


def parse_phone_number(phone: str) -> Optional[str]:
    """Parse and normalize phone number."""
    if not phone:
        return None
    
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if clean_phone.startswith('8') and len(clean_phone) == 11:
        # Russian format starting with 8
        clean_phone = '7' + clean_phone[1:]
    elif clean_phone.startswith('+7') and len(clean_phone) == 12:
        # International format
        clean_phone = clean_phone[1:]
    elif not clean_phone.startswith('7') and len(clean_phone) == 10:
        # Missing country code
        clean_phone = '7' + clean_phone
    
    # Validate final format
    if len(clean_phone) == 11 and clean_phone.startswith('7'):
        return clean_phone
    
    return None


def extract_callback_data(callback_data: str, prefix: str) -> Dict[str, str]:
    """Extract data from callback string."""
    if not callback_data.startswith(prefix):
        return {}
    
    # Remove prefix and split by separator
    data_part = callback_data[len(prefix):]
    # Normalize leading separator like "category:id:..." -> "id:..."
    if data_part.startswith(":"):
        data_part = data_part[1:]
    if not data_part:
        return {}
    
    # Split by separator and create key-value pairs
    parts = data_part.split(':')
    result = {}
    
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            key = parts[i]
            value = parts[i + 1]
            result[key] = value
    
    return result


def build_callback_data(prefix: str, **kwargs) -> str:
    """Build callback data string."""
    if not kwargs:
        return prefix
    
    # Convert all values to strings and join with separator
    parts = []
    for key, value in kwargs.items():
        parts.extend([str(key), str(value)])
    
    return f"{prefix}:{':'.join(parts)}"


def paginate_items(items: List[Any], page: int, per_page: int) -> Dict[str, Any]:
    """Paginate list of items."""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Validate page number
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get items for current page
    page_items = items[offset:offset + per_page]
    
    return {
        'items': page_items,
        'page': page,
        'per_page': per_page,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
    }


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested value from dictionary."""
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates_preserve_order(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order."""
    seen = set()
    result = []
    
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


def format_currency(amount: int, currency: str = "RUB") -> str:
    """Format currency amount."""
    if currency == "RUB":
        return format_price(amount, "₽")
    elif currency == "USD":
        return f"${amount / 100:.2f}"
    elif currency == "EUR":
        return f"€{amount / 100:.2f}"
    else:
        return f"{amount / 100:.2f} {currency}"