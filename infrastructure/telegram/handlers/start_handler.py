"""Start handler for Telegram bot."""

from typing import Any, Dict

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.main_keyboard import MainKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter


class StartHandler(BaseHandler):
    """Handler for /start command."""
    
    def _register_handlers(self) -> None:
        """Register start command handler."""
        self.router.message.register(
            self.handle_start_command,
            CommandStart()
        )
        # Navigation callbacks
        self.router.callback_query.register(
            self.handle_main_menu_callback,
            F.data == "main_menu"
        )
        self.router.callback_query.register(
            self.handle_back_callback,
            F.data == "back"
        )
        # Misc callbacks from main menu
        self.router.callback_query.register(
            self.handle_contacts_callback,
            F.data == "contacts"
        )
        self.router.callback_query.register(
            self.handle_support_callback,
            F.data == "support"
        )
    
    async def handle_start_command(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle /start command."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)
        is_admin = data.get("is_admin", False)
        if not is_admin:
            try:
                from app.config import get_settings
                if user_id in get_settings().admin_user_ids:
                    is_admin = True
            except Exception:
                pass
        
        # Get cafe information from settings
        cafe_name = "Кафе"  # TODO: Get from settings
        working_hours = "09:00-22:00"  # TODO: Get from settings
        
        # Format welcome message
        welcome_text = MessageFormatter.format_welcome_message(cafe_name, working_hours)
        
        # Get appropriate keyboard based on user role
        if is_admin:
            keyboard = MainKeyboard.get_main_menu_with_admin()
        else:
            keyboard = MainKeyboard.get_main_menu()
        
        await message.answer(
            text=welcome_text,
            reply_markup=keyboard
        )
        
        self.logger.info(
            "Start command handled",
            user_id=user_id,
            is_admin=is_admin
        )

    async def handle_main_menu_callback(self, callback, **kwargs) -> None:
        """Handle main menu callback from inline buttons."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)
        if not is_admin:
            try:
                from app.config import get_settings
                if user_id in get_settings().admin_user_ids:
                    is_admin = True
            except Exception:
                pass

        keyboard = MainKeyboard.get_main_menu_with_admin() if is_admin else MainKeyboard.get_main_menu()

        await self.replace_with_text_message(
            callback.message,
            text="🏠 <b>Главное меню</b>",
            reply_markup=keyboard
        )

        await callback.answer()

        self.logger.info(
            "Main menu callback handled",
            user_id=user_id,
            is_admin=is_admin
        )

    async def handle_back_callback(self, callback, **kwargs) -> None:
        """Treat generic back as navigation to main menu."""
        await self.handle_main_menu_callback(callback, **kwargs)

    async def handle_contacts_callback(self, callback, **kwargs) -> None:
        """Show contacts information."""
        text = (
            "📍 <b>Контакты</b>\n\n"
            "Адрес: ул. Примерная, 13\n"
            "Телефон: +7 (999) 123-45-67\n"
            "Часы работы: 09:00–22:00"
        )
        from aiogram.types import InlineKeyboardButton
        from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
        keyboard = BaseKeyboard.create_inline_keyboard([
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ])
        await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
        await callback.answer()

    async def handle_support_callback(self, callback, **kwargs) -> None:
        """Show support info."""
        text = (
            "☎️ <b>Поддержка</b>\n\n"
            "Напишите нам здесь: @your_support\n"
            "Или позвоните: +7 (999) 123-45-67"
        )
        from aiogram.types import InlineKeyboardButton
        from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
        keyboard = BaseKeyboard.create_inline_keyboard([
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ])
        await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
        await callback.answer()