"""Runtime notification templates storage."""

from __future__ import annotations

from typing import Dict


DEFAULT_NOTIFICATION_TEMPLATES: Dict[str, str] = {
    "welcome": (
        "👋 <b>Добро пожаловать, {first_name}!</b>\n\n"
        "Вы в {cafe_name}.\n"
        "🕒 Часы работы: {working_hours}\n\n"
        "Выберите действие в меню ниже."
    ),
    "order_ready": (
        "✅ <b>Заказ готов!</b>\n\n"
        "📦 Заказ #{order_id_short}\n"
        "💰 Сумма: {total_rub}₽\n"
        "🛍️ Формат: {order_type}"
    ),
    "order_delivery": (
        "🚚 <b>Заказ передан в доставку</b>\n\n"
        "📦 Заказ #{order_id_short}\n"
        "📍 Адрес: {address}\n"
        "Ожидайте курьера."
    ),
    "order_delivered": (
        "🎉 <b>Заказ завершен</b>\n\n"
        "📦 Заказ #{order_id_short}\n"
        "Приятного аппетита! 🍽️"
    ),
}


_notification_templates: Dict[str, str] = DEFAULT_NOTIFICATION_TEMPLATES.copy()


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def get_notification_template(template_key: str) -> str:
    """Return template text by key."""
    return _notification_templates.get(template_key, DEFAULT_NOTIFICATION_TEMPLATES.get(template_key, ""))


def set_notification_template(template_key: str, template_text: str) -> None:
    """Save template text by key."""
    if template_key not in DEFAULT_NOTIFICATION_TEMPLATES:
        raise ValueError("Unknown notification template key")
    _notification_templates[template_key] = template_text


def reset_notification_template(template_key: str) -> None:
    """Reset template to default value."""
    if template_key not in DEFAULT_NOTIFICATION_TEMPLATES:
        raise ValueError("Unknown notification template key")
    _notification_templates[template_key] = DEFAULT_NOTIFICATION_TEMPLATES[template_key]


def render_notification_template(template_key: str, values: Dict[str, str]) -> str:
    """Render template safely with placeholders."""
    template = get_notification_template(template_key)
    return template.format_map(_SafeDict(values))

