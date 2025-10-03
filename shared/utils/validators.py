"""Validation utilities."""

import re
from typing import Any, Optional

from pydantic import BaseModel, ValidationError


class ValidationResult:
    """Validation result data class."""
    
    def __init__(self, is_valid: bool, error_message: Optional[str] = None):
        self.is_valid = is_valid
        self.error_message = error_message


def validate_phone(phone: str) -> ValidationResult:
    """Validate phone number."""
    if not phone:
        return ValidationResult(False, "Номер телефона не может быть пустым")
    
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Check if phone starts with 7 or 8 (Russian format)
    if clean_phone.startswith('8'):
        clean_phone = '7' + clean_phone[1:]
    
    # Check length (should be 11 digits for Russian number)
    if len(clean_phone) != 11:
        return ValidationResult(False, "Номер телефона должен содержать 11 цифр")
    
    # Check if starts with 7
    if not clean_phone.startswith('7'):
        return ValidationResult(False, "Номер телефона должен начинаться с 7")
    
    return ValidationResult(True)


def validate_email(email: str) -> ValidationResult:
    """Validate email address."""
    if not email:
        return ValidationResult(False, "Email не может быть пустым")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return ValidationResult(False, "Неверный формат email")
    
    return ValidationResult(True)


def validate_address(address: str) -> ValidationResult:
    """Validate delivery address."""
    if not address:
        return ValidationResult(False, "Адрес не может быть пустым")
    
    if len(address) < 10:
        return ValidationResult(False, "Адрес слишком короткий")
    
    if len(address) > 500:
        return ValidationResult(False, "Адрес слишком длинный")
    
    return ValidationResult(True)


def validate_quantity(quantity: int) -> ValidationResult:
    """Validate item quantity."""
    if quantity <= 0:
        return ValidationResult(False, "Количество должно быть больше 0")
    
    if quantity > 99:
        return ValidationResult(False, "Количество не может превышать 99")
    
    return ValidationResult(True)


def validate_price(price: int) -> ValidationResult:
    """Validate price in kopecks."""
    if price < 0:
        return ValidationResult(False, "Цена не может быть отрицательной")
    
    if price > 10000000:  # 100,000 rubles
        return ValidationResult(False, "Цена слишком высокая")
    
    return ValidationResult(True)


def validate_comment(comment: str) -> ValidationResult:
    """Validate comment text."""
    if not comment:
        return ValidationResult(True)  # Comment is optional
    
    if len(comment) > 500:
        return ValidationResult(False, "Комментарий слишком длинный")
    
    # Check for inappropriate content (basic check)
    inappropriate_words = ['спам', 'реклама', 'мошенничество']
    comment_lower = comment.lower()
    
    for word in inappropriate_words:
        if word in comment_lower:
            return ValidationResult(False, "Комментарий содержит недопустимое содержимое")
    
    return ValidationResult(True)


def validate_pydantic_model(model_class: type[BaseModel], data: dict[str, Any]) -> ValidationResult:
    """Validate data against Pydantic model."""
    try:
        model_class(**data)
        return ValidationResult(True)
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            message = error.get('msg', 'Validation error')
            error_messages.append(f"{field}: {message}")
        
        return ValidationResult(False, "; ".join(error_messages))


def sanitize_text(text: str) -> str:
    """Sanitize text input."""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_callback_data(callback_data: str, expected_prefix: str) -> ValidationResult:
    """Validate callback data format."""
    if not callback_data:
        return ValidationResult(False, "Callback data не может быть пустым")
    
    if not callback_data.startswith(expected_prefix):
        return ValidationResult(False, f"Неверный формат callback data. Ожидается префикс: {expected_prefix}")
    
    if len(callback_data) > 64:  # Telegram limit
        return ValidationResult(False, "Callback data слишком длинный")
    
    return ValidationResult(True)