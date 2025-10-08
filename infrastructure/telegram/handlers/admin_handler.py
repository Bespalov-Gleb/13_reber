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
        from infrastructure.telegram.handlers.admin_management_handlers import AdminManagementHandlers
        self.extensions = AdminHandlerExtensions(self)
        self.callbacks = AdminHandlerCallbacks(self)
        self.management = AdminManagementHandlers()
        super().__init__()
        # Инициализируем logger в extensions, callbacks и management
        self.extensions.logger = self.logger
        self.callbacks.logger = self.logger
        self.management.logger = self.logger
    
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
        
        # Orders management callbacks
        self.router.callback_query.register(
            self.handle_orders_callback,
            F.data.startswith("orders:")
        )
        
        # Order detail and management callbacks
        self.router.callback_query.register(
            self.handle_order_detail_callback,
            F.data.startswith("order_detail:")
        )
        self.router.callback_query.register(
            self.handle_order_management_callback,
            F.data.startswith("order_")
        )
        
        # Statistics callbacks
        self.router.callback_query.register(
            self.handle_statistics_callback,
            F.data.startswith("stats:")
        )
        
        # Users management callbacks
        self.router.callback_query.register(
            self.management.handle_users_callback,
            F.data.startswith("users:")
        )
        self.router.callback_query.register(
            self.management.handle_user_detail_callback,
            F.data.startswith("user_detail:")
        )
        self.router.callback_query.register(
            self.management.handle_user_management_callback,
            F.data.startswith("user_")
        )
        
        # Payments management callbacks
        self.router.callback_query.register(
            self.management.handle_payments_callback,
            F.data.startswith("payments:")
        )
        self.router.callback_query.register(
            self.management.handle_payment_detail_callback,
            F.data.startswith("payment_detail:")
        )
        self.router.callback_query.register(
            self.management.handle_payment_management_callback,
            F.data.startswith("payment_")
        )
        
        # Notifications management callbacks
        self.router.callback_query.register(
            self.management.handle_notifications_callback,
            F.data.startswith("notify:")
        )
        self.router.callback_query.register(
            self.management.handle_notification_template_callback,
            F.data.startswith("notify_template:")
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
        # Role-based admin fallback
        if not is_admin:
            try:
                from app.dependencies import get_user_service
                user_service = await get_user_service(data)
                db_user = await user_service.get_user_by_telegram_id(user_id)
                if db_user and getattr(db_user, "is_admin", False):
                    is_admin = True
            except Exception:
                pass
        # Role-based admin as fallback
        if not is_admin:
            try:
                from app.dependencies import get_user_service
                user_service = await get_user_service(data)
                db_user = await user_service.get_user_by_telegram_id(user_id)
                if db_user and getattr(db_user, "is_admin", False):
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
        callback_data = callback.data
        # Admin rights are verified at panel entry; do not re-check here to avoid false negatives
        
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
        elif action == "users":
            # Show users management
            await self._show_users_management(callback)
        elif action == "payments":
            # Show payments management
            await self._show_payments_management(callback)
        elif action == "notifications":
            # Show notifications management
            await self._show_notifications_management(callback)
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
        callback_data = callback.data
        
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
        callback_data = callback.data
        
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
        callback_data = callback.data
        
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
        await self.safe_edit_message(
            callback.message,
            text="📊 <b>Статистика</b>\n\nВыберите тип статистики:",
            reply_markup=AdminKeyboard.get_statistics_keyboard()
        )
    
    async def _show_users_management(self, callback: CallbackQuery) -> None:
        """Show users management."""
        await self.safe_edit_message(
            callback.message,
            text="👥 <b>Управление пользователями</b>\n\nВыберите действие:",
            reply_markup=AdminKeyboard.get_users_management_keyboard()
        )
    
    async def _show_payments_management(self, callback: CallbackQuery) -> None:
        """Show payments management."""
        await self.safe_edit_message(
            callback.message,
            text="💰 <b>Управление платежами</b>\n\nВыберите действие:",
            reply_markup=AdminKeyboard.get_payments_management_keyboard()
        )
    
    async def _show_notifications_management(self, callback: CallbackQuery) -> None:
        """Show notifications management."""
        await self.safe_edit_message(
            callback.message,
            text="📢 <b>Управление уведомлениями</b>\n\nВыберите действие:",
            reply_markup=AdminKeyboard.get_notifications_management_keyboard()
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
    
    # Orders management handlers
    async def handle_orders_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle orders management callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)

        # Fallback admin check
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

        callback_data = callback.data

        # Parse orders action
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Ошибка: неверные данные")
            return

        action = parts[1]  # pending, preparing, ready, delivery

        # Get order service
        session = data.get("session")
        if session is None:
            order_service = await get_order_service(data)
        else:
            from app.dependencies import container
            order_service = container.get_order_service(session)

        try:
            if action == "pending":
                orders = await order_service.get_orders_by_status("pending")
                status_text = "⏳ Ожидающие заказы"
            elif action == "preparing":
                orders = await order_service.get_orders_by_status("preparing")
                status_text = "👨‍🍳 Заказы в приготовлении"
            elif action == "ready":
                orders = await order_service.get_orders_by_status("ready")
                status_text = "✅ Готовые заказы"
            elif action == "delivery":
                orders = await order_service.get_orders_by_status("delivery")
                status_text = "🚚 Заказы в доставке"
            else:
                await callback.answer("❌ Неизвестное действие")
                return

            if not orders:
                text = f"{status_text}\n\nЗаказы не найдены"
                keyboard = AdminKeyboard.get_back_to_admin_keyboard()
            else:
                text = f"{status_text}\n\nНайдено заказов: {len(orders)}\n\nВыберите заказ для управления:"
                keyboard = AdminKeyboard.get_orders_list_keyboard(orders[:10])  # Show first 10 orders

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Orders callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке заказов")
            return

        await callback.answer()

        self.logger.info(
            "Orders callback handled",
            user_id=user_id,
            action=action
        )

    async def handle_order_detail_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle order detail callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)

        # Fallback admin check
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

        callback_data = callback.data
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Ошибка: неверные данные")
            return

        order_id = parts[1]

        try:
            # Get order service
            session = data.get("session")
            if session is None:
                order_service = await get_order_service(data)
            else:
                from app.dependencies import container
                order_service = container.get_order_service(session)

            order = await order_service.get_order(order_id)
            if not order:
                await callback.answer("❌ Заказ не найден")
                return

            # Format order details
            from infrastructure.telegram.utils.message_formatter import MessageFormatter
            text = MessageFormatter.format_order_message(order)
            keyboard = AdminKeyboard.get_order_management_keyboard(order)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Order detail callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке заказа")
            return

        await callback.answer()

    async def handle_order_management_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle order management callbacks (accept, ready, delivery, etc.)."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)

        # Fallback admin check
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

        callback_data = callback.data
        parts = callback_data.split(":")
        if not parts:
            await callback.answer("❌ Ошибка: неверные данные")
            return

        # Expected formats: order_accept:{id}, order_ready:{id}, order_delivery:{id}, order_delivered:{id}, order_picked_up:{id}, order_cancel:{id}
        token = parts[0]
        action = token.split("_", 1)[1] if "_" in token else None
        order_id = parts[1] if len(parts) > 1 else None

        if not action or not order_id:
            await callback.answer("❌ Ошибка: неверные данные")
            return

        try:
            # Get order service
            session = data.get("session")
            if session is None:
                order_service = await get_order_service(data)
            else:
                from app.dependencies import container
                order_service = container.get_order_service(session)

            # Get order
            order = await order_service.get_order(order_id)
            if not order:
                await callback.answer("❌ Заказ не найден")
                return

            # Update order status
            from shared.constants.order_constants import OrderStatus
            
            if action == "accept":
                order.status = OrderStatus.PREPARING
                await order_service.update_order_status(order.order_id, OrderStatus.PREPARING)
                await callback.answer("✅ Заказ принят в работу")
                
            elif action == "ready":
                order.status = OrderStatus.READY
                await order_service.update_order_status(order.order_id, OrderStatus.READY)
                await callback.answer("✅ Заказ готов")
                
            elif action == "delivery":
                order.status = OrderStatus.OUT_FOR_DELIVERY
                await order_service.update_order_status(order.order_id, OrderStatus.OUT_FOR_DELIVERY)
                await callback.answer("✅ Заказ передан в доставку")
                
            elif action == "delivered":
                order.status = OrderStatus.DELIVERED
                await order_service.update_order_status(order.order_id, OrderStatus.DELIVERED)
                await callback.answer("✅ Заказ доставлен")
                
            elif action == "picked_up":
                order.status = OrderStatus.PICKED_UP
                await order_service.update_order_status(order.order_id, OrderStatus.PICKED_UP)
                await callback.answer("✅ Заказ выдан")
                
            elif action == "cancel":
                order.status = OrderStatus.CANCELLED
                await order_service.update_order_status(order.order_id, OrderStatus.CANCELLED)
                await callback.answer("❌ Заказ отменен")
                
            else:
                await callback.answer("❌ Неизвестное действие")
                return

            # Update the message with new order details
            from infrastructure.telegram.utils.message_formatter import MessageFormatter
            text = MessageFormatter.format_order_message(order)
            keyboard = AdminKeyboard.get_order_management_keyboard(order)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Order management callback error: {e}")
            await callback.answer("❌ Произошла ошибка при обновлении заказа")
            return

        await callback.answer()

    # Statistics handlers
    async def handle_statistics_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle statistics callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        is_admin = data.get("is_admin", False)

        # Fallback admin check
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

        callback_data = callback.data

        # Parse statistics action
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Ошибка: неверные данные")
            return

        action = parts[1]  # overview, sales, users, menu, today, week, month, year

        try:
            # Get statistics service
            session = data.get("session")
            if session is None:
                from app.dependencies import get_statistics_service
                statistics_service = await get_statistics_service(data)
            else:
                from app.dependencies import container
                statistics_service = container.get_statistics_service(session)

            # Handle different statistics types
            if action == "overview":
                await self._show_overview_statistics(callback, statistics_service)
            elif action == "sales":
                await self._show_sales_statistics(callback, statistics_service)
            elif action == "users":
                await self._show_user_statistics(callback, statistics_service)
            elif action == "menu":
                await self._show_menu_statistics(callback, statistics_service)
            elif action in ["today", "week", "month", "year"]:
                await self._show_period_statistics(callback, statistics_service, action)
            else:
                await callback.answer("❌ Неизвестный тип статистики")
                return

        except Exception as e:
            self.logger.error(f"Statistics callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке статистики")
            return

        await callback.answer()

        self.logger.info(
            "Statistics callback handled",
            user_id=user_id,
            action=action
        )

    async def _show_overview_statistics(self, callback: CallbackQuery, statistics_service) -> None:
        """Show overview statistics."""
        try:
            summary = await statistics_service.get_dashboard_summary()
            
            text = "📊 <b>Общая статистика</b>\n\n"
            text += f"📅 <b>Сегодня:</b>\n"
            text += f"• Заказов: {summary['today']['orders']}\n"
            text += f"• Выручка: {summary['today']['revenue'] // 100}₽\n"
            text += f"• Средний чек: {summary['today']['avg_order'] // 100}₽\n\n"
            
            text += f"📅 <b>Вчера:</b>\n"
            text += f"• Заказов: {summary['yesterday']['orders']}\n"
            text += f"• Выручка: {summary['yesterday']['revenue'] // 100}₽\n"
            text += f"• Средний чек: {summary['yesterday']['avg_order'] // 100}₽\n\n"
            
            text += f"👥 <b>Пользователи:</b>\n"
            text += f"• Всего: {summary['users']['total_users']}\n"
            text += f"• Новых сегодня: {summary['users']['new_users_today']}\n"
            text += f"• Активных сегодня: {summary['users']['active_users_today']}\n\n"
            
            text += f"🍽️ <b>Меню:</b>\n"
            text += f"• Категорий: {summary['menu']['total_categories']}\n"
            text += f"• Блюд: {summary['menu']['total_items']}"

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=AdminKeyboard.get_back_to_admin_keyboard()
            )

        except Exception as e:
            self.logger.error(f"Overview statistics error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке статистики")

    async def _show_sales_statistics(self, callback: CallbackQuery, statistics_service) -> None:
        """Show sales statistics."""
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            sales_stats = await statistics_service.get_sales_statistics(start_date, end_date)
            
            text = "📈 <b>Статистика продаж</b>\n\n"
            text += f"💰 Общая выручка: {sales_stats.total_sales // 100}₽\n\n"
            
            text += "📅 <b>Продажи по дням:</b>\n"
            for day, amount in sales_stats.sales_by_day[:7]:  # Last 7 days
                text += f"• {day}: {amount // 100}₽\n"
            
            text += "\n🕐 <b>Продажи по часам:</b>\n"
            for hour, amount in sales_stats.sales_by_hour[:5]:  # Top 5 hours
                text += f"• {hour}:00 - {amount // 100}₽\n"

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=AdminKeyboard.get_back_to_admin_keyboard()
            )

        except Exception as e:
            self.logger.error(f"Sales statistics error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке статистики")

    async def _show_user_statistics(self, callback: CallbackQuery, statistics_service) -> None:
        """Show user statistics."""
        try:
            user_stats = await statistics_service.get_user_statistics()
            
            text = "👥 <b>Статистика пользователей</b>\n\n"
            text += f"👤 Всего пользователей: {user_stats.total_users}\n"
            text += f"🆕 Новых сегодня: {user_stats.new_users_today}\n"
            text += f"🆕 Новых на этой неделе: {user_stats.new_users_this_week}\n"
            text += f"🆕 Новых в этом месяце: {user_stats.new_users_this_month}\n"
            text += f"🔥 Активных сегодня: {user_stats.active_users_today}\n"
            text += f"🔥 Активных на этой неделе: {user_stats.active_users_this_week}"

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=AdminKeyboard.get_back_to_admin_keyboard()
            )

        except Exception as e:
            self.logger.error(f"User statistics error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке статистики")

    async def _show_menu_statistics(self, callback: CallbackQuery, statistics_service) -> None:
        """Show menu statistics."""
        try:
            menu_stats = await statistics_service.get_menu_statistics()
            
            text = "🍽️ <b>Статистика меню</b>\n\n"
            text += f"📂 Всего категорий: {menu_stats.total_categories}\n"
            text += f"📂 Активных категорий: {menu_stats.active_categories}\n"
            text += f"🍽️ Всего блюд: {menu_stats.total_items}\n"
            text += f"🍽️ Активных блюд: {menu_stats.active_items}\n\n"
            
            text += "🏆 <b>Топ категории:</b>\n"
            for category, count in menu_stats.top_categories[:5]:
                text += f"• {category}: {count} блюд\n"
            
            text += "\n🏆 <b>Топ блюда:</b>\n"
            for item, count in menu_stats.top_items[:5]:
                text += f"• {item}: {count} заказов"

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=AdminKeyboard.get_back_to_admin_keyboard()
            )

        except Exception as e:
            self.logger.error(f"Menu statistics error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке статистики")

    async def _show_period_statistics(self, callback: CallbackQuery, statistics_service, period: str) -> None:
        """Show period-based statistics."""
        try:
            from datetime import datetime, timedelta
            
            now = datetime.now()
            if period == "today":
                start_date = datetime.combine(now.date(), datetime.min.time())
                end_date = datetime.combine(now.date(), datetime.max.time())
                period_text = "сегодня"
            elif period == "week":
                start_date = now - timedelta(days=7)
                end_date = now
                period_text = "за неделю"
            elif period == "month":
                start_date = now - timedelta(days=30)
                end_date = now
                period_text = "за месяц"
            elif period == "year":
                start_date = now - timedelta(days=365)
                end_date = now
                period_text = "за год"
            else:
                await callback.answer("❌ Неизвестный период")
                return
            
            order_stats = await statistics_service.get_order_statistics(start_date, end_date)
            
            text = f"📊 <b>Статистика {period_text}</b>\n\n"
            text += f"📦 Всего заказов: {order_stats.total_orders}\n"
            text += f"💰 Выручка: {order_stats.total_revenue // 100}₽\n"
            text += f"📈 Средний чек: {order_stats.average_order_value // 100}₽\n\n"
            
            text += "📊 <b>По статусам:</b>\n"
            for status, count in order_stats.orders_by_status.items():
                text += f"• {status}: {count}\n"
            
            text += "\n📊 <b>По типам:</b>\n"
            for order_type, count in order_stats.orders_by_type.items():
                text += f"• {order_type}: {count}\n"

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=AdminKeyboard.get_back_to_admin_keyboard()
            )

        except Exception as e:
            self.logger.error(f"Period statistics error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке статистики")