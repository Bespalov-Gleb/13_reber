"""Cart keyboard for Telegram bot."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
from domain.entities.cart import Cart, CartItem


class CartKeyboard(BaseKeyboard):
    """Cart keyboard for the bot."""
    
    @staticmethod
    def get_cart_keyboard(cart: Cart) -> InlineKeyboardMarkup:
        """Get cart keyboard (generic actions only)."""
        buttons = []
        
        # Action buttons
        buttons.append([
            BaseKeyboard.create_callback_button(
                text="✏️ Редактировать",
                prefix="cart",
                action="edit"
            )
        ])

        buttons.append([
            BaseKeyboard.create_callback_button(
                text="🗑️ Очистить корзину",
                prefix="cart",
                action="clear"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(text="🚚 Оформить заказ", callback_data="order")
        ])
        
        # Navigation buttons
        buttons.append([
            InlineKeyboardButton(text="📖 Меню", callback_data="menu"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)

    @staticmethod
    def get_item_edit_keyboard(item_id: str, prev_item_id: str | None = None, next_item_id: str | None = None) -> InlineKeyboardMarkup:
        """Keyboard for editing a specific cart item quantity with optional navigation."""
        buttons = [
            [
                BaseKeyboard.create_callback_button(
                    text="➖",
                    prefix="cart",
                    action="update",
                    item_id=item_id,
                    op="dec",
                    ctx="cart"
                ),
                BaseKeyboard.create_callback_button(
                    text="➕",
                    prefix="cart",
                    action="update",
                    item_id=item_id,
                    op="inc",
                    ctx="cart"
                )
            ],
        ]

        # Navigation row
        nav_row = []
        if prev_item_id:
            nav_row.append(
                BaseKeyboard.create_callback_button(
                    text="⬅️ Пред.",
                    prefix="cart",
                    action="navigate",
                    item_id=prev_item_id
                )
            )
        if next_item_id:
            nav_row.append(
                BaseKeyboard.create_callback_button(
                    text="След. ➡️",
                    prefix="cart",
                    action="navigate",
                    item_id=next_item_id
                )
            )
        if nav_row:
            buttons.append(nav_row)
        buttons.extend([
            [
                BaseKeyboard.create_callback_button(
                    text="🗑️ Удалить",
                    prefix="cart",
                    action="remove",
                    item_id=item_id
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Корзина", callback_data="cart"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ])
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_empty_cart_keyboard() -> InlineKeyboardMarkup:
        """Get empty cart keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📖 Меню", callback_data="menu"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_quantity_keyboard(item_id: str, current_quantity: int = 1) -> InlineKeyboardMarkup:
        """Get quantity selection keyboard."""
        buttons = []
        
        # Control buttons (only +/-)
        control_row = []
        if current_quantity > 1:
            control_row.append(
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"quantity:{item_id}:{current_quantity - 1}"
                )
            )
        
        control_row.append(
            InlineKeyboardButton(
                text="➕",
                callback_data=f"quantity:{item_id}:{current_quantity + 1}"
            )
        )
        buttons.append(control_row)
        
        # Action buttons
        buttons.append([
            BaseKeyboard.create_callback_button(
                text="✅ Добавить в корзину",
                prefix="cart",
                action="add_confirm",
                item_id=item_id,
                quantity=current_quantity
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"item:id:{item_id}")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_comment_keyboard(item_id: str, quantity: int) -> InlineKeyboardMarkup:
        """Get comment keyboard."""
        buttons = [
            [
                BaseKeyboard.create_callback_button(
                    text="✅ Без комментария",
                    prefix="cart",
                    action="add_final",
                    item_id=item_id,
                    quantity=quantity
                )
            ],
            [
                BaseKeyboard.create_callback_button(
                    text="✏️ Добавить комментарий",
                    prefix="cart",
                    action="add_comment",
                    item_id=item_id,
                    quantity=quantity
                )
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"item:id:{item_id}")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_item_keyboard(item_id: str) -> InlineKeyboardMarkup:
        """Get back to item keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К блюду", callback_data=f"item:id:{item_id}"),
                InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")
            ],
            [
                InlineKeyboardButton(text="📖 Меню", callback_data="menu"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_cancel_keyboard() -> InlineKeyboardMarkup:
        """Get cancel keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_order_type_keyboard() -> InlineKeyboardMarkup:
        """Get order type selection keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🚚 Доставка", callback_data="order:type:delivery"),
                InlineKeyboardButton(text="🚶 Самовывоз", callback_data="order:type:pickup")
            ],
            [
                InlineKeyboardButton(text="🔙 Корзина", callback_data="cart")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_payment_method_keyboard() -> InlineKeyboardMarkup:
        """Get payment method selection keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="💵 Наличные", callback_data="order:payment:cash"),
                InlineKeyboardButton(text="💳 Карта при получении", callback_data="order:payment:card")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="order:back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="order:cancel")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_order_confirmation_keyboard() -> InlineKeyboardMarkup:
        """Get order confirmation keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="order:confirm"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="order:cancel")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)