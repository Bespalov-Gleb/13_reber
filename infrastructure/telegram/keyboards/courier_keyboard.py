"""Courier keyboard for Telegram bot."""

from typing import List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
from domain.entities.order import Order


class CourierKeyboard(BaseKeyboard):
    """Courier keyboard for the bot."""
    
    @staticmethod
    def get_courier_main_menu() -> InlineKeyboardMarkup:
        """Get courier main menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🚚 Активные доставки", callback_data="courier:active_deliveries"),
                InlineKeyboardButton(text="📋 История доставок", callback_data="courier:delivery_history"),
            ],
            [
                InlineKeyboardButton(text="👤 Профиль", callback_data="courier:profile"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="courier:statistics"),
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_active_deliveries_keyboard(orders: List[Order]) -> InlineKeyboardMarkup:
        """Get active deliveries keyboard."""
        buttons = []
        
        for order in orders:
            # Format order button text
            order_text = f"📦 #{order.order_id[:8]} - {order.total // 100}₽"
            if order.delivery_info and order.delivery_info.address:
                # Truncate address if too long
                address = order.delivery_info.address
                if len(address) > 30:
                    address = address[:27] + "..."
                order_text += f"\n📍 {address}"
            
            buttons.append([
                InlineKeyboardButton(
                    text=order_text,
                    callback_data=f"courier:order:{order.order_id}"
                )
            ])
        
        if not orders:
            buttons.append([
                InlineKeyboardButton(
                    text="📭 Нет активных доставок",
                    callback_data="courier:no_deliveries"
                )
            ])
        
        # Add back button
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="courier:main_menu")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_order_management_keyboard(order: Order) -> InlineKeyboardMarkup:
        """Get order management keyboard for courier."""
        buttons = []
        
        # Status-specific actions
        if order.status.value == "ready":
            buttons.append([
                InlineKeyboardButton(
                    text="🚚 Начать доставку",
                    callback_data=f"courier:start_delivery:{order.order_id}"
                )
            ])
        elif order.status.value == "delivery":
            buttons.append([
                InlineKeyboardButton(
                    text="✅ Доставлен",
                    callback_data=f"courier:delivered:{order.order_id}"
                )
            ])
            buttons.append([
                InlineKeyboardButton(
                    text="❌ Проблема с доставкой",
                    callback_data=f"courier:delivery_problem:{order.order_id}"
                )
            ])
        
        # Common actions
        if order.delivery_info and order.delivery_info.phone:
            buttons.append([
                InlineKeyboardButton(
                    text="📞 Позвонить клиенту",
                    callback_data=f"courier:call:{order.order_id}"
                )
            ])
        
        if order.delivery_info and order.delivery_info.address:
            buttons.append([
                InlineKeyboardButton(
                    text="🗺️ Открыть в картах",
                    callback_data=f"courier:maps:{order.order_id}"
                )
            ])
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 К активным доставкам", callback_data="courier:active_deliveries")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_delivery_problem_keyboard(order_id: str) -> InlineKeyboardMarkup:
        """Get delivery problem keyboard."""
        buttons = [
            [
                InlineKeyboardButton(
                    text="🏠 Клиент не отвечает",
                    callback_data=f"courier:problem:no_answer:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Неверный адрес",
                    callback_data=f"courier:problem:wrong_address:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Отказ от заказа",
                    callback_data=f"courier:problem:refused:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Другая проблема",
                    callback_data=f"courier:problem:other:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data=f"courier:order:{order_id}")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_delivery_history_keyboard(orders: List[Order], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
        """Get delivery history keyboard with pagination."""
        buttons = []
        start_idx = page * per_page
        end_idx = start_idx + per_page
        
        for order in orders[start_idx:end_idx]:
            status_emoji = {
                "delivered": "✅",
                "cancelled": "❌",
                "refunded": "💰"
            }.get(order.status.value, "❓")
            
            order_text = f"{status_emoji} #{order.order_id[:8]} - {order.total // 100}₽"
            if order.delivery_info and order.delivery_info.address:
                address = order.delivery_info.address
                if len(address) > 25:
                    address = address[:22] + "..."
                order_text += f"\n📍 {address}"
            
            buttons.append([
                InlineKeyboardButton(
                    text=order_text,
                    callback_data=f"courier:history_order:{order.order_id}"
                )
            ])
        
        # Pagination
        if len(orders) > per_page:
            pagination_buttons = []
            
            if page > 0:
                pagination_buttons.append(
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=f"courier:history_page:{page-1}"
                    )
                )
            
            if end_idx < len(orders):
                pagination_buttons.append(
                    InlineKeyboardButton(
                        text="➡️",
                        callback_data=f"courier:history_page:{page+1}"
                    )
                )
            
            if pagination_buttons:
                buttons.append(pagination_buttons)
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="courier:main_menu")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_courier_profile_keyboard() -> InlineKeyboardMarkup:
        """Get courier profile keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📞 Изменить телефон", callback_data="courier:edit_phone"),
                InlineKeyboardButton(text="👤 Изменить имя", callback_data="courier:edit_name"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="courier:main_menu")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_confirmation_keyboard(action: str, order_id: str) -> InlineKeyboardMarkup:
        """Get confirmation keyboard for courier actions."""
        buttons = [
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data=f"courier:confirm_{action}:{order_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"courier:order:{order_id}"
                )
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
