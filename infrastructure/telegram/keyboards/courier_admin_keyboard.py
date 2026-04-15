"""Courier admin keyboard for Telegram bot."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
from domain.entities.user import User


class CourierAdminKeyboard(BaseKeyboard):
    """Courier admin keyboard for the bot."""
    
    @staticmethod
    def get_couriers_management_keyboard() -> InlineKeyboardMarkup:
        """Get couriers management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="👥 Все курьеры", callback_data="admin_couriers:list_all"),
                InlineKeyboardButton(text="🚚 Активные курьеры", callback_data="admin_couriers:active"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика курьеров", callback_data="admin_couriers:statistics"),
                InlineKeyboardButton(text="➕ Назначить курьера", callback_data="admin_couriers:assign"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_courier_list_keyboard(couriers: List[User], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
        """Get courier list keyboard with pagination."""
        buttons = []
        start_idx = page * per_page
        end_idx = start_idx + per_page
        
        for courier in couriers[start_idx:end_idx]:
            status_emoji = "🟢" if courier.is_active else "🔴"
            buttons.append([
                InlineKeyboardButton(
                    f"{status_emoji} {courier.full_name}",
                    callback_data=f"admin_couriers:view:{courier.user_id}"
                )
            ])
        
        # Pagination
        if len(couriers) > per_page:
            pagination_buttons = []
            
            if page > 0:
                pagination_buttons.append(
                    InlineKeyboardButton(
                        "⬅️",
                        callback_data=f"admin_couriers:page:{page-1}"
                    )
                )
            
            if end_idx < len(couriers):
                pagination_buttons.append(
                    InlineKeyboardButton(
                        "➡️",
                        callback_data=f"admin_couriers:page:{page+1}"
                    )
                )
            
            if pagination_buttons:
                buttons.append(pagination_buttons)
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_couriers:menu")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_courier_selection_keyboard(couriers: List[User], order_id: str) -> InlineKeyboardMarkup:
        """Get courier selection keyboard for order assignment."""
        buttons = []
        
        for courier in couriers:
            if courier.is_active:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"🚚 {courier.full_name}",
                        callback_data=f"admin_couriers:assign_to_order:{order_id}:{courier.user_id}"
                    )
                ])
        
        if not couriers:
            buttons.append([
                InlineKeyboardButton(
                    text="❌ Нет активных курьеров",
                    callback_data="admin_couriers:no_couriers"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data=f"order_detail:{order_id}")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_courier_management_keyboard(courier: User) -> InlineKeyboardMarkup:
        """Get courier management keyboard."""
        buttons = []
        
        if courier.is_active:
            buttons.append([
                InlineKeyboardButton(
                    text="🔴 Деактивировать",
                    callback_data=f"admin_couriers:deactivate:{courier.user_id}"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    text="🟢 Активировать",
                    callback_data=f"admin_couriers:activate:{courier.user_id}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data=f"admin_couriers:stats:{courier.user_id}"
            ),
            InlineKeyboardButton(
                text="📋 Заказы",
                callback_data=f"admin_couriers:orders:{courier.user_id}"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_couriers:list_all")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_assign_courier_keyboard(order_id: str, couriers: List[User]) -> InlineKeyboardMarkup:
        """Get assign courier keyboard for order."""
        buttons = []
        
        for courier in couriers:
            if courier.is_active:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"🚚 {courier.full_name}",
                        callback_data=f"admin_couriers:assign_to_order:{order_id}:{courier.user_id}"
                    )
                ])
        
        if not couriers:
            buttons.append([
                InlineKeyboardButton(
                    text="❌ Нет активных курьеров",
                    callback_data="admin_couriers:no_couriers"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin:order:{order_id}")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
