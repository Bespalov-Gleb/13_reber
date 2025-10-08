"""Additional callback handlers for AdminHandler."""

from typing import Any, Dict, TYPE_CHECKING

from aiogram.types import CallbackQuery

if TYPE_CHECKING:
    from infrastructure.telegram.handlers.admin_handler import AdminHandler
from infrastructure.telegram.keyboards.admin_keyboard import AdminKeyboard
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.admin_state_service import admin_state_service
from shared.types.admin_states import AdminState


class AdminHandlerCallbacks:
    """Additional callback handlers for AdminHandler."""
    
    def __init__(self, admin_handler: "AdminHandler"):
        self.admin_handler = admin_handler
        # Logger будет инициализирован после super().__init__()
        self.logger = None
    
    @staticmethod
    def _is_admin_from_data(data: Dict[str, Any], user_id: int) -> bool:
        is_admin = data.get("is_admin", False)
        if not is_admin:
            try:
                from app.config import get_settings
                if user_id in get_settings().admin_user_ids:
                    return True
            except Exception:
                return False
        return is_admin
    
    async def handle_edit_category_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle edit category callback."""
        data = kwargs.get("data", {})
        
        # Robust parsing: edit_category:<action>:id:<category_id>
        parts = callback.data.split(":")
        action = parts[1] if len(parts) > 1 else None
        category_id = parts[-1] if len(parts) >= 4 else None
        
        if action == "name":
            admin_state_service.set_editing_id(user_id, category_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_CATEGORY_NAME)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="📝 <b>Редактирование категории</b>\n\nВведите новое название:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "edit":
            # Open category edit actions
            await self.admin_handler._edit_category(callback, category_id)
        elif action == "description":
            admin_state_service.set_editing_id(user_id, category_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_CATEGORY_DESCRIPTION)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="📝 <b>Редактирование категории</b>\n\nВведите новое описание (или '-' для удаления):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "delete":
            # Ask for confirmation; show info about items
            from app.dependencies import get_menu_service
            menu_service = await get_menu_service()
            items_count = await menu_service.menu_repository.count_menu_items(category_id)  # type: ignore
            warning = "❗ В категории есть блюда, они будут удалены вместе с категорией." if items_count else ""
            await self.admin_handler.safe_edit_message(
                callback.message,
                text=f"🗑️ <b>Удаление категории</b>\n\n{warning}\n\nУдалить категорию?",
                reply_markup=AdminKeyboard.get_confirm_delete_category_keyboard(category_id, items_count)
            )
        elif action == "delete_confirm":
            # Cascade delete items then category
            from app.dependencies import get_menu_service
            menu_service = await get_menu_service()
            try:
                # Delete items of category
                items = await menu_service.get_menu_items(category_id, active_only=False)
                for it in items:
                    await menu_service.delete_menu_item(it.item_id)
                # Delete category
                success = await menu_service.delete_category(category_id)
                if success:
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text="✅ <b>Категория и её блюда удалены</b>",
                        reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                    )
                else:
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text="❌ <b>Не удалось удалить категорию</b>",
                        reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                    )
            except Exception as e:
                from html import escape
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=f"❌ <b>Ошибка:</b> {escape(str(e))}",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
        elif action == "image":
            admin_state_service.set_editing_id(user_id, category_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_CATEGORY_IMAGE)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="📷 <b>Редактирование категории</b>\n\nОтправьте новое фото:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        
        await callback.answer()
    
    async def handle_edit_item_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle edit item callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        # Robust parsing: edit_item:<action>:id:<item_id>
        parts = callback.data.split(":")
        action = parts[1] if len(parts) > 1 else None
        item_id = parts[-1] if len(parts) >= 4 else None
        
        if action == "name":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_NAME)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="📝 <b>Редактирование блюда</b>\n\nВведите новое название:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "edit":
            # Open item edit actions
            await self.admin_handler._edit_item(callback, item_id)
        elif action == "description":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_DESCRIPTION)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="📝 <b>Редактирование блюда</b>\n\nВведите новое описание (или '-' для удаления):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "price":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_PRICE)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="💰 <b>Редактирование блюда</b>\n\nВведите новую цену в рублях:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "ingredients":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_INGREDIENTS)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="🥘 <b>Редактирование блюда</b>\n\nВведите новый состав (или '-' для удаления):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "allergens":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_ALLERGENS)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="⚠️ <b>Редактирование блюда</b>\n\nВведите аллергены (или '-' для удаления):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "weight":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_WEIGHT)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="⚖️ <b>Редактирование блюда</b>\n\nВведите вес в граммах (или '-' для удаления):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "calories":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_CALORIES)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="🔥 <b>Редактирование блюда</b>\n\nВведите калории (или '-' для удаления):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "image":
            admin_state_service.set_editing_id(user_id, item_id)
            admin_state_service.set_admin_state(user_id, AdminState.EDITING_ITEM_IMAGE)
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="📷 <b>Редактирование блюда</b>\n\nОтправьте новое фото:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
        elif action == "delete":
            # Confirm item deletion
            await self.admin_handler.safe_edit_message(
                callback.message,
                text="🗑️ <b>Удаление блюда</b>\n\nУдалить блюдо?",
                reply_markup=AdminKeyboard.get_confirm_delete_item_keyboard(item_id)
            )
        elif action == "delete_confirm":
            from app.dependencies import get_menu_service
            menu_service = await get_menu_service()
            try:
                success = await menu_service.delete_menu_item(item_id)
                if success:
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text="✅ <b>Блюдо удалено</b>",
                        reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                    )
                else:
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text="❌ <b>Не удалось удалить блюдо</b>",
                        reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                    )
            except Exception as e:
                from html import escape
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=f"❌ <b>Ошибка:</b> {escape(str(e))}",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        
        await callback.answer()
    
    async def handle_add_category_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle add category callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        admin_state_service.set_admin_state(user_id, AdminState.ADDING_CATEGORY_NAME)
        await self.admin_handler.safe_edit_message(
            callback.message,
            text="📝 <b>Добавление категории</b>\n\nВведите название новой категории:",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )
        await callback.answer()
    
    async def handle_add_item_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle add item callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        admin_state_service.set_admin_state(user_id, AdminState.ADDING_ITEM_NAME)
        await self.admin_handler.safe_edit_message(
            callback.message,
            text="📝 <b>Добавление блюда</b>\n\nВведите название нового блюда:",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )
        await callback.answer()
    
    async def handle_select_category_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle select category callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        # Robust parsing: select_category:id:<category_id>
        parts = callback.data.split(":")
        category_id = parts[-1] if len(parts) >= 3 else None
        admin_state_service.set_temp_data(user_id, "category_id", category_id)
        admin_state_service.set_admin_state(user_id, AdminState.ADDING_ITEM_INGREDIENTS)
        
        await self.admin_handler.safe_edit_message(
            callback.message,
            text="🥘 <b>Добавление блюда</b>\n\nВведите состав блюда (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )
        await callback.answer()
    
    async def handle_cancel_editing_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle cancel editing callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        admin_state_service.reset_admin_context(user_id)
        
        await self.admin_handler.safe_edit_message(
            callback.message,
            text="❌ <b>Редактирование отменено</b>",
            reply_markup=AdminKeyboard.get_back_to_admin_menu()
        )
        await callback.answer()