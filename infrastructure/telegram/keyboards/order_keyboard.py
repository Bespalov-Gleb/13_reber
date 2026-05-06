"""Order keyboard for order creation flow."""

from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shared.types.order_states import OrderState


class OrderKeyboard:
    """Keyboard for order creation flow."""
    
    @staticmethod
    def create_inline_keyboard(buttons: List[List[Dict[str, Any]]]) -> InlineKeyboardMarkup:
        """Create inline keyboard from button configuration."""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button["text"],
                        callback_data=button["callback_data"]
                    )
                )
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_inline_button(text: str, callback_data: str) -> Dict[str, Any]:
        """Create inline button configuration."""
        return {"text": text, "callback_data": callback_data}
    
    @staticmethod
    def get_order_type_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for order type selection."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "🚚 Доставка",
                    "order:type:delivery"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "🏪 Самовывоз",
                    "order:type:pickup"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "❌ Отменить",
                    "order:cancel"
                )
            ]
        ])
    
    @staticmethod
    def get_payment_method_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for payment method selection."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "💵 Наличные",
                    "order:payment:cash"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "💳 Карта при получении",
                    "order:payment:card"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
    
    @staticmethod
    def get_address_suggestions_keyboard(suggestions: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        """Get keyboard with address suggestions."""
        buttons = []
        
        # Add suggestion buttons (max 5)
        for i, suggestion in enumerate(suggestions[:5]):
            buttons.append([
                OrderKeyboard.create_inline_button(
                    f"📍 {suggestion['title']}",
                    f"order:address:select:{i}"
                )
            ])
        
        # Add navigation buttons
        buttons.extend([
            [
                OrderKeyboard.create_inline_button(
                    "✏️ Ввести вручную",
                    "order:address:manual"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
        
        return OrderKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_delivery_phone_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for delivery phone input."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "📱 Использовать мой номер",
                    "order:phone:use_my"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "✏️ Ввести другой номер",
                    "order:phone:manual"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
    
    @staticmethod
    def get_order_time_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for order time selection."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "⚡ Как можно скорее",
                    "order:time:asap"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "🕐 К определенному времени",
                    "order:time:scheduled"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
    
    @staticmethod
    def get_comment_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for order comment."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "✏️ Добавить комментарий",
                    "order:comment:add"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⏭️ Пропустить",
                    "order:comment:skip"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
    
    @staticmethod
    def get_promo_code_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for promo code input."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "🎁 У меня есть промокод",
                    "order:promo:add"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⏭️ Пропустить",
                    "order:promo:skip"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
    
    @staticmethod
    def get_confirmation_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for order confirmation."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "✅ Подтвердить заказ",
                    "order:confirm"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "✏️ Изменить",
                    "order:edit"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "❌ Отменить",
                    "order:cancel"
                )
            ]
        ])
    
    @staticmethod
    def get_delivery_zone_error_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for delivery zone error."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "🏪 Переключить на самовывоз",
                    "order:type:pickup"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "✏️ Попробовать другой адрес",
                    "order:address:retry"
                )
            ],
            [
                OrderKeyboard.create_inline_button(
                    "❌ Отменить заказ",
                    "order:cancel"
                )
            ]
        ])
    
    @staticmethod
    def get_back_keyboard() -> InlineKeyboardMarkup:
        """Get simple back keyboard."""
        return OrderKeyboard.create_inline_keyboard([
            [
                OrderKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "order:back"
                )
            ]
        ])
