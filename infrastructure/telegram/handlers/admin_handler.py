"""Admin handler for Telegram bot."""

from typing import Any, Dict

from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.admin_keyboard import AdminKeyboard
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.admin_state_service import admin_state_service
from shared.types.admin_states import AdminState
from app.dependencies import get_menu_service, get_order_service


class AdminHandler(BaseHandler):
    """Handler for admin operations."""
    
    def __init__(self):
        # Инициализируем extensions и callbacks перед super().__init__()
        from infrastructure.telegram.handlers.admin_handler_extensions import AdminHandlerExtensions
        from infrastructure.telegram.handlers.admin_handler_callbacks import AdminHandlerCallbacks
        self.extensions = AdminHandlerExtensions(self)
        self.callbacks = AdminHandlerCallbacks(self)
        super().__init__()
        # Инициализируем logger в extensions и callbacks
        self.extensions.logger = self.logger
        self.callbacks.logger = self.logger
    
    def _register_handlers(self) -> None:
        """Register admin handlers."""
        # Message handlers
        self.router.message.register(
            self.handle_admin_command,
            F.text == "👨‍💼 Админ-панель"
        )
        # Also allow /admin command
        self.router.message.register(
            self.handle_admin_command,
            Command("admin")
        )
        
        # Photo handler first (explicit content filter)
        from aiogram import F as _F
        self.router.message.register(
            self.extensions.handle_admin_photo,
            _F.photo,
            lambda message: admin_state_service.is_admin_editing(message.from_user.id)
        )
        
        # Text message handler (explicit content filter)
        self.router.message.register(
            self.extensions.handle_admin_text_message,
            _F.text,
            lambda message: admin_state_service.is_admin_editing(message.from_user.id)
        )
        
        # Callback handlers
        # Explicit admin entry from main menu
        self.router.callback_query.register(
            self.handle_admin_open_callback,
            F.data == "admin"
        )
        self.router.callback_query.register(
            self.handle_admin_callback,
            F.data.startswith("admin")
        )
        
        self.router.callback_query.register(
            self.handle_menu_edit_callback,
            (F.data.startswith("menu_edit:"))
        )
        
        self.router.callback_query.register(
            self.handle_category_edit_callback,
            F.data.startswith("category_edit")
        )
        
        self.router.callback_query.register(
            self.handle_item_edit_callback,
            F.data.startswith("item_edit")
        )
        
        # Additional callback handlers for editing
        self.router.callback_query.register(
            self.callbacks.handle_edit_category_callback,
            F.data.startswith("edit_category")
        )
        
        self.router.callback_query.register(
            self.callbacks.handle_edit_item_callback,
            F.data.startswith("edit_item")
        )
        
        self.router.callback_query.register(
            self.callbacks.handle_add_category_callback,
            F.data.startswith("add_category")
        )
        
        self.router.callback_query.register(
            self.callbacks.handle_add_item_callback,
            F.data.startswith("add_item")
        )
        
        self.router.callback_query.register(
            self.callbacks.handle_select_category_callback,
            F.data.startswith("select_category")
        )
        
        self.router.callback_query.register(
            self.callbacks.handle_cancel_editing_callback,
            F.data.startswith("cancel_editing")
        )

    
    async def handle_admin_command(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle admin command."""
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
        
        if not is_admin:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        # Get admin keyboard
        keyboard = AdminKeyboard.get_admin_menu()
        
        await message.answer(
            text="👨‍💼 <b>Админ-панель</b>\n\nВыберите действие:",
            reply_markup=keyboard
        )
        
        self.logger.info(
            "Admin command handled",
            user_id=user_id,
            is_admin=is_admin
        )
    
    async def handle_admin_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle admin callback."""
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
        callback_data = callback.data
        
        if not is_admin:
            await callback.answer("❌ У вас нет прав администратора")
            return
        
        # Parse callback data (robust parsing for prefixes like 'admin:menu')
        if callback_data.startswith("admin:"):
            action = callback_data.split(":", 1)[1]
        else:
            action = CallbackParser.get_action(callback_data)
        
        if not action:
            # Treat bare 'admin' as open admin menu
            if callback_data == "admin":
                await self.handle_admin_open_callback(callback, data=data)
                return
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        if action == "menu":
            # Show menu management
            await self._show_menu_management(callback)
        elif action == "orders":
            # Show orders management
            await self._show_orders_management(callback)
        elif action == "stats":
            # Show statistics
            await self._show_statistics(callback)
        elif action == "back":
            # Go back to admin main menu
            await self.safe_edit_message(
                callback.message,
                text="👨‍💼 <b>Админ-панель</b>\n\nВыберите действие:",
                reply_markup=AdminKeyboard.get_admin_menu()
            )
        
        await callback.answer()
        
        self.logger.info(
            "Admin callback handled",
            user_id=user_id,
            action=action
        )

    async def handle_admin_open_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Open admin panel from main menu button."""
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
        if not is_admin:
            await callback.answer("❌ У вас нет прав администратора")
            return
        keyboard = AdminKeyboard.get_admin_menu()
        await self.replace_with_text_message(
            callback.message,
            text="👨‍💼 <b>Админ-панель</b>\n\nВыберите действие:",
            reply_markup=keyboard
        )
        await callback.answer()
    
    async def handle_menu_edit_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle menu editing callback."""
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
        callback_data = callback.data
        
        if not is_admin:
            await callback.answer("❌ У вас нет прав администратора")
            return
        
        # Parse callback data strictly for 'menu_edit:*'
        if callback_data.startswith("menu_edit:"):
            action = callback_data.split(":", 1)[1]
        else:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        if action == "categories":
            # Show categories management
            await self._show_categories_management(callback, data)
        elif action == "items":
            # Show items management
            await self._show_items_management(callback, data)
        elif action == "add_category":
            # Add new category
            await self._add_category(callback)
        elif action == "add_item":
            # Add new item
            await self._add_item(callback)
        elif action == "back":
            # Go back to admin menu
            await self.safe_edit_message(
                callback.message,
                text="👨‍💼 <b>Админ-панель</b>\n\nВыберите действие:",
                reply_markup=AdminKeyboard.get_admin_menu()
            )
        
        await callback.answer()
    
    async def handle_category_edit_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle category editing callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)
        callback_data = callback.data
        
        if not is_admin:
            await callback.answer("❌ У вас нет прав администратора")
            return
        
        # Parse callback data
        action = CallbackParser.get_action(callback_data)
        category_id = CallbackParser.get_value(callback_data, "id")
        
        if action == "edit":
            # Edit category
            await self._edit_category(callback, category_id)
        elif action == "delete":
            # Delete category
            await self._delete_category(callback, category_id)
        elif action == "toggle":
            # Toggle category status
            await self._toggle_category_status(callback, category_id)
        
        await callback.answer()
    
    async def handle_item_edit_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle item editing callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)
        callback_data = callback.data
        
        if not is_admin:
            await callback.answer("❌ У вас нет прав администратора")
            return
        
        # Parse callback data
        action = CallbackParser.get_action(callback_data)
        item_id = CallbackParser.get_value(callback_data, "id")
        
        if action == "edit":
            # Edit item
            await self._edit_item(callback, item_id)
        elif action == "delete":
            # Delete item
            await self._delete_item(callback, item_id)
        elif action == "toggle":
            # Toggle item status
            await self._toggle_item_status(callback, item_id)
        
        await callback.answer()
    
    async def _show_menu_management(self, callback: CallbackQuery) -> None:
        """Show menu management interface."""
        keyboard = AdminKeyboard.get_menu_management_keyboard()
        await self.safe_edit_message(
            callback.message,
            text="🍽️ <b>Управление меню</b>\n\nВыберите действие:",
            reply_markup=keyboard
        )
    
    async def _show_orders_management(self, callback: CallbackQuery) -> None:
        """Show orders management interface."""
        order_service = await get_order_service()
        
        # Get pending orders
        pending_orders = await order_service.get_orders_requiring_attention()
        
        if not pending_orders:
            text = "📋 <b>Управление заказами</b>\n\nНет заказов, требующих внимания"
        else:
            text = f"📋 <b>Управление заказами</b>\n\nЗаказов требующих внимания: {len(pending_orders)}"
        
        keyboard = AdminKeyboard.get_orders_management_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_statistics(self, callback: CallbackQuery) -> None:
        """Show statistics."""
        # TODO: Implement statistics
        await callback.message.edit_text(
            text="📊 <b>Статистика</b>\n\nФункция в разработке",
            reply_markup=AdminKeyboard.get_back_to_admin_keyboard()
        )
    
    async def _show_categories_management(self, callback: CallbackQuery, data: Dict[str, Any] | None = None) -> None:
        """Show categories management."""
        data = data or {}
        session = data.get("session")
        if session is None:
            menu_service = await get_menu_service(data)
        else:
            from app.dependencies import container
            menu_service = container.get_menu_service(session)
        categories = await menu_service.get_categories(active_only=False)
        
        if not categories:
            text = "📁 <b>Управление категориями</b>\n\nКатегории не найдены"
            keyboard = AdminKeyboard.get_empty_categories_keyboard()
        else:
            text = f"📁 <b>Управление категориями</b>\n\nНайдено категорий: {len(categories)}"
            keyboard = AdminKeyboard.get_categories_management_keyboard(categories)
        
        await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
    
    async def _show_items_management(self, callback: CallbackQuery, data: Dict[str, Any] | None = None) -> None:
        """Show items management."""
        data = data or {}
        session = data.get("session")
        if session is None:
            menu_service = await get_menu_service(data)
        else:
            from app.dependencies import container
            menu_service = container.get_menu_service(session)
        items = await menu_service.get_menu_items(active_only=False)
        
        if not items:
            text = "🍽️ <b>Управление блюдами</b>\n\nБлюда не найдены"
            keyboard = AdminKeyboard.get_empty_items_keyboard()
        else:
            text = f"🍽️ <b>Управление блюдами</b>\n\nНайдено блюд: {len(items)}"
            keyboard = AdminKeyboard.get_items_management_keyboard(items)
        
        await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
    
    async def _add_category(self, callback: CallbackQuery) -> None:
        """Add new category."""
        user_id = callback.from_user.id
        admin_state_service.set_admin_state(user_id, AdminState.ADDING_CATEGORY_NAME)
        await callback.message.edit_text(
            text="📝 <b>Добавление категории</b>\n\nВведите название новой категории:",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )
    
    async def _add_item(self, callback: CallbackQuery) -> None:
        """Add new item."""
        user_id = callback.from_user.id
        admin_state_service.set_admin_state(user_id, AdminState.ADDING_ITEM_NAME)
        await callback.message.edit_text(
            text="📝 <b>Добавление блюда</b>\n\nВведите название нового блюда:",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )
    
    async def _edit_category(self, callback: CallbackQuery, category_id: str) -> None:
        """Edit category."""
        await self.safe_edit_message(
            callback.message,
            text="📁 <b>Редактировать категорию</b>\n\nВыберите действие:",
            reply_markup=AdminKeyboard.get_category_actions_keyboard(category_id)
        )
    
    async def _delete_category(self, callback: CallbackQuery, category_id: str) -> None:
        """Delete category."""
        menu_service = await get_menu_service()
        
        try:
            success = await menu_service.delete_category(category_id)
            if success:
                await callback.message.edit_text(
                    text="✅ <b>Категория удалена</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
            else:
                await callback.message.edit_text(
                    text="❌ <b>Не удалось удалить категорию</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
            )
    
    async def _toggle_category_status(self, callback: CallbackQuery, category_id: str) -> None:
        """Toggle category status."""
        menu_service = await get_menu_service()
        
        try:
            category = await menu_service.get_category(category_id)
            if category:
                category.is_active = not category.is_active
                await menu_service.update_category(category)
                
                status = "активна" if category.is_active else "неактивна"
                await callback.message.edit_text(
                    text=f"✅ <b>Категория {status}</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
            else:
                await callback.message.edit_text(
                    text="❌ <b>Категория не найдена</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
            )
    
    async def _edit_item(self, callback: CallbackQuery, item_id: str) -> None:
        """Edit item."""
        user_id = callback.from_user.id
        admin_state_service.set_editing_id(user_id, item_id)
        
        await self.safe_edit_message(
            callback.message,
            text="🍽️ <b>Редактировать блюдо</b>\n\nВыберите действие:",
            reply_markup=AdminKeyboard.get_item_actions_keyboard(item_id)
        )
    
    async def _delete_item(self, callback: CallbackQuery, item_id: str) -> None:
        """Delete item."""
        menu_service = await get_menu_service()
        
        try:
            success = await menu_service.delete_menu_item(item_id)
            if success:
                await callback.message.edit_text(
                    text="✅ <b>Блюдо удалено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await callback.message.edit_text(
                    text="❌ <b>Не удалось удалить блюдо</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )
    
    async def _toggle_item_status(self, callback: CallbackQuery, item_id: str) -> None:
        """Toggle item status."""
        menu_service = await get_menu_service()
        
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.is_available = not item.is_available
                await menu_service.update_menu_item(item)
                
                status = "доступно" if item.is_available else "недоступно"
                await callback.message.edit_text(
                    text=f"✅ <b>Блюдо {status}</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await callback.message.edit_text(
                    text="❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )