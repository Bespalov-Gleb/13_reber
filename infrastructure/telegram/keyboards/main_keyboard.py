"""Main keyboard for Telegram bot."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard


class MainKeyboard(BaseKeyboard):
    """Main keyboard for the bot."""
    
    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """Get main menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📖 Меню", callback_data="menu"),
                InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
            ],
            [
                InlineKeyboardButton(text="🚚 Оформить заказ", callback_data="order"),
                InlineKeyboardButton(text="📍 Контакты", callback_data="contacts"),
            ],
            [
                InlineKeyboardButton(text="☎️ Поддержка", callback_data="support"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_main_menu_with_admin() -> InlineKeyboardMarkup:
        """Get main menu keyboard with admin button."""
        buttons = [
            [
                InlineKeyboardButton(text="📖 Меню", callback_data="menu"),
                InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
            ],
            [
                InlineKeyboardButton(text="🚚 Оформить заказ", callback_data="order"),
                InlineKeyboardButton(text="📍 Контакты", callback_data="contacts"),
            ],
            [
                InlineKeyboardButton(text="☎️ Поддержка", callback_data="support"),
            ],
            [
                InlineKeyboardButton(text="👨‍💼 Админ-панель", callback_data="admin"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_admin_menu() -> InlineKeyboardMarkup:
        """Get admin menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                InlineKeyboardButton(text="📋 Заказы", callback_data="admin_orders"),
            ],
            [
                InlineKeyboardButton(text="🍽️ Меню", callback_data="admin_menu"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            ],
            [
                InlineKeyboardButton(text="💰 Платежи", callback_data="admin_payments"),
                InlineKeyboardButton(text="📢 Уведомления", callback_data="admin_notifications"),
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_courier_menu() -> InlineKeyboardMarkup:
        """Get courier menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🚚 Доставки", callback_data="courier_deliveries"),
                InlineKeyboardButton(text="📋 Мои заказы", callback_data="courier_orders"),
            ],
            [
                InlineKeyboardButton(text="📍 Маршрут", callback_data="courier_route"),
                InlineKeyboardButton(text="⏰ Время работы", callback_data="courier_schedule"),
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_main() -> InlineKeyboardMarkup:
        """Get back to main menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_help_menu() -> InlineKeyboardMarkup:
        """Get help menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="❓ Как сделать заказ", callback_data="help_order"),
                InlineKeyboardButton(text="💳 Способы оплаты", callback_data="help_payment"),
            ],
            [
                InlineKeyboardButton(text="🚚 Доставка", callback_data="help_delivery"),
                InlineKeyboardButton(text="🚶 Самовывоз", callback_data="help_pickup"),
            ],
            [
                InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact_us"),
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_contacts_menu() -> InlineKeyboardMarkup:
        """Get contacts menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📍 Адрес", callback_data="contact_address"),
                InlineKeyboardButton(text="📞 Телефон", callback_data="contact_phone"),
            ],
            [
                InlineKeyboardButton(text="🕐 Режим работы", callback_data="contact_hours"),
                InlineKeyboardButton(text="🗺️ Карта", callback_data="contact_map"),
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)