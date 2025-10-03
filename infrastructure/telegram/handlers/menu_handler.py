"""Menu handler for Telegram bot."""

from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.menu_keyboard import MenuKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.menu_service import MenuService
from app.dependencies import get_menu_service


class MenuHandler(BaseHandler):
    """Handler for menu operations."""
    
    def _register_handlers(self) -> None:
        """Register menu handlers."""
        # Message handlers
        self.router.message.register(
            self.handle_menu_command,
            F.text == "📖 Меню"
        )
        
        # Callback handlers
        self.router.callback_query.register(
            self.handle_menu_callback,
            F.data == "menu"
        )
        
        self.router.callback_query.register(
            self.handle_category_callback,
            F.data.startswith("category")
        )
        
        self.router.callback_query.register(
            self.handle_item_callback,
            F.data.startswith("item")
        )
    
    async def handle_menu_command(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle menu command."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)
        
        # Get menu service
        menu_service = await get_menu_service(data)
        
        # Get categories
        categories = await menu_service.get_categories(active_only=True)
        
        if not categories:
            await message.answer("📖 Меню временно недоступно")
            return
        
        # Create categories keyboard
        keyboard = MenuKeyboard.get_categories_keyboard(categories)
        
        await message.answer(
            text="📖 <b>Наше меню</b>\n\nВыберите категорию:",
            reply_markup=keyboard
        )
        
        self.logger.info(
            "Menu command handled",
            user_id=user_id,
            categories_count=len(categories)
        )
    
    async def handle_menu_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle menu callback."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        if callback_data == "menu":
            # Show categories
            if session is None:
                menu_service = await get_menu_service(data)
            else:
                from app.dependencies import container
                menu_service = container.get_menu_service(session)
            categories = await menu_service.get_categories(active_only=True)
            
            if not categories:
                await self.replace_with_text_message(callback.message, "📖 Меню временно недоступно")
                return
            
            keyboard = MenuKeyboard.get_categories_keyboard(categories)
            
            await self.replace_with_text_message(
                callback.message,
                text="📖 <b>Наше меню</b>\n\nВыберите категорию:",
                reply_markup=keyboard
            )
        
        await callback.answer()
    
    async def handle_category_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle category callback."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse category ID from callback data
        category_id = CallbackParser.get_category_id(callback_data)
        
        if not category_id:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        # Get menu service
        if session is None:
            menu_service = await get_menu_service(data)
        else:
            from app.dependencies import container
            menu_service = container.get_menu_service(session)
        
        # Get category
        category = await menu_service.get_category(category_id)
        if not category:
            await callback.answer("❌ Категория не найдена")
            return
        
        # Get menu items for category
        menu_items = await menu_service.get_menu_items(category_id, active_only=True)
        
        if not menu_items:
            await self.replace_with_text_message(
                callback.message,
                text=f"📖 <b>{category.name}</b>\n\nВ этой категории пока нет блюд",
                reply_markup=MenuKeyboard.get_back_to_categories_keyboard()
            )
            return
        
        # Create menu items keyboard
        keyboard = MenuKeyboard.get_menu_items_keyboard(menu_items, category_id)
        
        await self.replace_with_text_message(
            callback.message,
            text=f"📖 <b>{category.name}</b>\n\nВыберите блюдо:",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
        self.logger.info(
            "Category callback handled",
            user_id=user_id,
            category_id=category_id,
            items_count=len(menu_items)
        )
    
    async def handle_item_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle menu item callback."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse item ID from callback data
        item_id = CallbackParser.get_item_id(callback_data)
        
        if not item_id:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        # Get menu service
        if session is None:
            menu_service = await get_menu_service(data)
        else:
            from app.dependencies import container
            menu_service = container.get_menu_service(session)
        
        # Get menu item
        menu_item = await menu_service.get_menu_item(item_id)
        if not menu_item:
            await callback.answer("❌ Блюдо не найдено")
            return
        
        # Format menu item message
        item_text = MessageFormatter.format_menu_item(menu_item)
        
        # Create keyboard for item actions (plus-only; quantity updated in cart flow)
        keyboard = MenuKeyboard.get_menu_item_keyboard(menu_item)
        
        # Send photo if available
        if menu_item.image_url:
            try:
                await callback.message.delete()
                await callback.message.answer_photo(
                    photo=menu_item.image_url,
                    caption=item_text,
                    reply_markup=keyboard
                )
            except Exception as e:
                self.logger.error(f"Failed to send photo: {e}")
                await self.safe_edit_message(
                    callback.message,
                    text=item_text,
                    reply_markup=keyboard
                )
        else:
            await self.safe_edit_message(
                callback.message,
                text=item_text,
                reply_markup=keyboard
            )
        
        await callback.answer()
        
        self.logger.info(
            "Item callback handled",
            user_id=user_id,
            item_id=item_id
        )