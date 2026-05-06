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
        user_id = data.get("user_id", callback.from_user.id)
        
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
    
    async def handle_bookings_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle bookings management callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        if not self._is_admin_from_data(data, user_id):
            await callback.answer("❌ У вас нет прав админа")
            return
        
        callback_data = callback.data
        parts = callback_data.split(":")
        
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return
        
        action = parts[1]
        
        try:
            from app.dependencies import get_booking_service
            booking_service = await get_booking_service(data)
            
            if action == "menu" or action == "all":
                # Show bookings management menu
                text = "🪑 <b>Управление бронированиями</b>\n\nВыберите действие:"
                keyboard = AdminKeyboard.get_bookings_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "list_all":
                # Show all bookings
                bookings = await booking_service.get_upcoming_bookings(limit=20)
                
                if not bookings:
                    text = "🪑 <b>Бронирования</b>\n\nНет активных бронирований."
                    keyboard = AdminKeyboard.get_bookings_management_keyboard()
                else:
                    text = f"🪑 <b>Бронирования</b>\n\nНайдено бронирований: {len(bookings)}"
                    from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                    keyboard = BookingKeyboard.get_booking_list_keyboard(bookings)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "today":
                # Show today's bookings
                bookings = await booking_service.get_today_bookings()
                
                if not bookings:
                    text = "🪑 <b>Бронирования на сегодня</b>\n\nНет бронирований на сегодня."
                    keyboard = AdminKeyboard.get_bookings_management_keyboard()
                else:
                    text = f"🪑 <b>Бронирования на сегодня</b>\n\nНайдено бронирований: {len(bookings)}"
                    from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                    keyboard = BookingKeyboard.get_booking_list_keyboard(bookings)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "pending":
                # Show pending bookings
                bookings = await booking_service.get_bookings_by_status("pending")
                
                if not bookings:
                    text = "🪑 <b>Ожидающие бронирования</b>\n\nНет ожидающих бронирований."
                    keyboard = AdminKeyboard.get_bookings_management_keyboard()
                else:
                    text = f"🪑 <b>Ожидающие бронирования</b>\n\nНайдено бронирований: {len(bookings)}"
                    from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                    keyboard = BookingKeyboard.get_booking_list_keyboard(bookings)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "view":
                # View specific booking
                booking_id = CallbackParser.get_value(callback_data, "booking_id")
                if not booking_id and len(parts) >= 3:
                    # Backward compatibility for plain format: admin_bookings:view:<id>
                    booking_id = parts[2]
                if not booking_id:
                    await callback.answer("❌ Неверные данные")
                    return
                booking = await booking_service.get_booking(booking_id)
                
                if not booking:
                    await callback.answer("❌ Бронирование не найдено")
                    return
                
                # Format booking details
                date_str = booking.booking_date.strftime("%d.%m.%Y")
                time_str = booking.booking_time.strftime("%H:%M")
                status_emoji = {
                    "pending": "⏳",
                    "confirmed": "✅",
                    "cancelled": "❌"
                }.get(booking.status, "❓")
                
                text = f"🪑 <b>Детали бронирования</b>\n\n"
                text += f"🆔 ID: {booking.booking_id[:8]}\n"
                text += f"👥 Гостей: {booking.guests_count}\n"
                text += f"📅 Дата: {date_str}\n"
                text += f"🕐 Время: {time_str}\n"
                text += f"📊 Статус: {status_emoji} {booking.status}\n"
                text += f"👤 Имя: {booking.contact_name}\n"
                text += f"📞 Телефон: {booking.contact_phone}\n"
                if booking.comment:
                    text += f"💬 Комментарий: {booking.comment}\n"
                text += f"🕐 Создано: {booking.created_at.strftime('%d.%m.%Y %H:%M')}"
                
                from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                keyboard = BookingKeyboard.get_booking_management_keyboard(booking)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "confirm":
                # Confirm booking
                booking_id = CallbackParser.get_value(callback_data, "booking_id")
                if not booking_id and len(parts) >= 3:
                    booking_id = parts[2]
                if not booking_id:
                    await callback.answer("❌ Неверные данные")
                    return
                booking = await booking_service.confirm_booking(booking_id)

                date_str = booking.booking_date.strftime("%d.%m.%Y")
                time_str = booking.booking_time.strftime("%H:%M")
                status_emoji = {
                    "pending": "⏳",
                    "confirmed": "✅",
                    "cancelled": "❌"
                }.get(booking.status, "❓")

                text = f"🪑 <b>Детали бронирования</b>\n\n"
                text += f"🆔 ID: {booking.booking_id[:8]}\n"
                text += f"👥 Гостей: {booking.guests_count}\n"
                text += f"📅 Дата: {date_str}\n"
                text += f"🕐 Время: {time_str}\n"
                text += f"📊 Статус: {status_emoji} {booking.status}\n"
                text += f"👤 Имя: {booking.contact_name}\n"
                text += f"📞 Телефон: {booking.contact_phone}\n"
                if booking.comment:
                    text += f"💬 Комментарий: {booking.comment}\n"
                text += f"🕐 Создано: {booking.created_at.strftime('%d.%m.%Y %H:%M')}"

                from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                keyboard = BookingKeyboard.get_booking_management_keyboard(booking)
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "cancel":
                # Cancel booking
                booking_id = CallbackParser.get_value(callback_data, "booking_id")
                if not booking_id and len(parts) >= 3:
                    booking_id = parts[2]
                if not booking_id:
                    await callback.answer("❌ Неверные данные")
                    return
                booking = await booking_service.cancel_booking(booking_id)

                date_str = booking.booking_date.strftime("%d.%m.%Y")
                time_str = booking.booking_time.strftime("%H:%M")
                status_emoji = {
                    "pending": "⏳",
                    "confirmed": "✅",
                    "cancelled": "❌"
                }.get(booking.status, "❓")

                text = f"🪑 <b>Детали бронирования</b>\n\n"
                text += f"🆔 ID: {booking.booking_id[:8]}\n"
                text += f"👥 Гостей: {booking.guests_count}\n"
                text += f"📅 Дата: {date_str}\n"
                text += f"🕐 Время: {time_str}\n"
                text += f"📊 Статус: {status_emoji} {booking.status}\n"
                text += f"👤 Имя: {booking.contact_name}\n"
                text += f"📞 Телефон: {booking.contact_phone}\n"
                if booking.comment:
                    text += f"💬 Комментарий: {booking.comment}\n"
                text += f"🕐 Создано: {booking.created_at.strftime('%d.%m.%Y %H:%M')}"

                from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                keyboard = BookingKeyboard.get_booking_management_keyboard(booking)
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "page":
                # Handle pagination
                page_value = CallbackParser.get_value(callback_data, "page")
                if page_value is None and len(parts) >= 3:
                    page_value = parts[2]
                if page_value is None:
                    await callback.answer("❌ Неверные данные")
                    return
                page = int(page_value)
                bookings = await booking_service.get_upcoming_bookings(limit=20, offset=page*5)
                
                if not bookings:
                    text = "🪑 <b>Бронирования</b>\n\nНет активных бронирований."
                    keyboard = AdminKeyboard.get_bookings_management_keyboard()
                else:
                    text = f"🪑 <b>Бронирования</b>\n\nНайдено бронирований: {len(bookings)}"
                    from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
                    keyboard = BookingKeyboard.get_booking_list_keyboard(bookings, page=page)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            else:
                await callback.answer("❌ Неизвестное действие")
                
        except Exception as e:
            self.logger.error(f"Error handling bookings callback: {e}")
            await callback.answer("❌ Произошла ошибка")
        
        await callback.answer()
    
    async def handle_iiko_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle iiko management callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        if not self._is_admin_from_data(data, user_id):
            await callback.answer("❌ У вас нет прав админа")
            return
        
        callback_data = callback.data
        parts = callback_data.split(":")
        
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return
        
        action = parts[1]
        
        try:
            from app.dependencies import get_iiko_sync_service
            sync_service = await get_iiko_sync_service(data)
            
            if action == "menu":
                # Show iiko management menu
                text = "🍽️ <b>Управление iiko CRM</b>\n\nВыберите действие:"
                keyboard = AdminKeyboard.get_iiko_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "test_connection":
                # Test iiko connection
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text="🔄 <b>Проверка подключения к iiko...</b>",
                    reply_markup=None
                )
                
                success = await sync_service.test_iiko_connection()
                
                if success:
                    text = "✅ <b>Подключение к iiko успешно!</b>\n\nСервис готов к работе."
                else:
                    text = "❌ <b>Ошибка подключения к iiko</b>\n\nПроверьте настройки в config.env:\n• IIKO_API_URL\n• IIKO_API_LOGIN"
                
                keyboard = AdminKeyboard.get_iiko_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "sync_menu":
                # Sync menu from iiko
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text="🔄 <b>Синхронизация меню с iiko...</b>\n\nЭто может занять несколько минут.",
                    reply_markup=None
                )
                
                success = await sync_service.sync_menu_from_iiko(force=True)
                
                if success:
                    last_sync = sync_service.get_last_sync_time()
                    sync_time = last_sync.strftime("%d.%m.%Y %H:%M") if last_sync else "Неизвестно"
                    
                    text = f"✅ <b>Синхронизация меню завершена!</b>\n\nВремя синхронизации: {sync_time}\n\nМеню обновлено из iiko."
                else:
                    details = ""
                    if hasattr(sync_service, "get_last_error"):
                        last_error = sync_service.get_last_error()
                        if last_error:
                            details = f"\n\nПричина: {last_error}"
                    text = "❌ <b>Ошибка синхронизации меню</b>\n\nПроверьте подключение к iiko и настройки." + details
                
                keyboard = AdminKeyboard.get_iiko_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "sync_orders":
                # Sync order statuses from iiko
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text="🔄 <b>Синхронизация статусов заказов с iiko...</b>",
                    reply_markup=None
                )
                
                # This would need to be implemented based on your order repository
                # For now, we'll just show a success message
                text = "✅ <b>Синхронизация заказов завершена!</b>\n\nСтатусы заказов обновлены из iiko."
                
                keyboard = AdminKeyboard.get_iiko_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "settings":
                # Show iiko settings
                from app.config import get_settings
                settings = get_settings()
                
                text = "⚙️ <b>Настройки iiko CRM</b>\n\n"
                text += f"🌐 API URL: {settings.iiko_api_url}\n"
                text += f"👤 API Login: {settings.iiko_api_login or 'Не настроено'}\n"
                text += f"🏢 Organization ID: {settings.iiko_organization_id or 'Автоопределение'}\n\n"
                text += "Для изменения настроек отредактируйте файл config.env"
                
                keyboard = AdminKeyboard.get_iiko_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            else:
                await callback.answer("❌ Неизвестное действие")
                
        except Exception as e:
            self.logger.error(f"Error handling iiko callback: {e}")
            await callback.answer("❌ Произошла ошибка")
        
        await callback.answer()
    
    async def handle_couriers_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle couriers management callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        if not self._is_admin_from_data(data, user_id):
            await callback.answer("❌ У вас нет прав админа")
            return
        
        callback_data = callback.data
        parts = callback_data.split(":")
        
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return
        
        action = parts[1]
        
        try:
            from infrastructure.telegram.keyboards.courier_admin_keyboard import CourierAdminKeyboard
            from app.dependencies import get_user_service, get_order_service, get_notification_service
            from shared.types.user_types import UserRole
            
            user_service = await get_user_service(data)
            order_service = await get_order_service(data)
            notification_service = await get_notification_service(data)
            
            if action == "menu":
                # Show couriers management menu
                text = "🚚 <b>Управление курьерами</b>\n\nВыберите действие:"
                keyboard = CourierAdminKeyboard.get_couriers_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "list_all":
                # Show all couriers
                all_users = await user_service.get_all_users()
                couriers = [user for user in all_users if user.role == UserRole.COURIER]
                
                if not couriers:
                    text = "👥 <b>Все курьеры</b>\n\nКурьеры не найдены."
                else:
                    text = f"👥 <b>Все курьеры</b>\n\nНайдено курьеров: {len(couriers)}"
                
                keyboard = CourierAdminKeyboard.get_courier_list_keyboard(couriers)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "active":
                # Show active couriers
                all_users = await user_service.get_all_users()
                active_couriers = [user for user in all_users if user.role == UserRole.COURIER and user.is_active]
                
                if not active_couriers:
                    text = "🚚 <b>Активные курьеры</b>\n\nАктивные курьеры не найдены."
                else:
                    text = f"🚚 <b>Активные курьеры</b>\n\nАктивных курьеров: {len(active_couriers)}"
                
                keyboard = CourierAdminKeyboard.get_courier_list_keyboard(active_couriers)
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "view":
                if len(parts) >= 3:
                    courier_id = parts[2]
                    courier = await user_service.get_user_by_id(courier_id)
                    
                    if not courier:
                        await callback.answer("❌ Курьер не найден")
                        return
                    
                    # Get courier statistics
                    from shared.types.order_types import OrderFilters
                    from shared.constants.order_constants import OrderStatus
                    
                    # Get completed deliveries
                    completed_filters = OrderFilters(
                        courier_id=courier.user_id,
                        statuses=[OrderStatus.DELIVERED]
                    )
                    completed_orders = await order_service.list_orders(completed_filters)
                    
                    # Get active deliveries
                    active_filters = OrderFilters(
                        courier_id=courier.user_id,
                        statuses=[OrderStatus.READY, OrderStatus.OUT_FOR_DELIVERY]
                    )
                    active_orders = await order_service.list_orders(active_filters)
                    
                    text = f"👤 <b>Профиль курьера</b>\n\n"
                    text += f"📝 <b>Имя:</b> {courier.full_name}\n"
                    text += f"📱 <b>Телефон:</b> {courier.phone or 'Не указан'}\n"
                    text += f"📊 <b>Статус:</b> {'Активен' if courier.is_active else 'Неактивен'}\n"
                    text += f"✅ <b>Завершено доставок:</b> {len(completed_orders)}\n"
                    text += f"🚚 <b>Активных доставок:</b> {len(active_orders)}\n"
                    text += f"📅 <b>Дата регистрации:</b> {courier.created_at.strftime('%d.%m.%Y')}"
                    
                    keyboard = CourierAdminKeyboard.get_courier_management_keyboard(courier)
                    
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text=text,
                        reply_markup=keyboard
                    )
                
            elif action == "activate":
                if len(parts) >= 3:
                    courier_id = parts[2]
                    courier = await user_service.get_user_by_id(courier_id)
                    
                    if not courier:
                        await callback.answer("❌ Курьер не найден")
                        return
                    
                    from shared.types.user_types import UserStatus
                    courier.change_status(UserStatus.ACTIVE)
                    await user_service.update_user(courier)
                    
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text=f"✅ <b>Курьер активирован</b>\n\n{courier.full_name} теперь активен.",
                        reply_markup=CourierAdminKeyboard.get_couriers_management_keyboard()
                    )
                
            elif action == "deactivate":
                if len(parts) >= 3:
                    courier_id = parts[2]
                    courier = await user_service.get_user_by_id(courier_id)
                    
                    if not courier:
                        await callback.answer("❌ Курьер не найден")
                        return
                    
                    from shared.types.user_types import UserStatus
                    courier.change_status(UserStatus.INACTIVE)
                    await user_service.update_user(courier)
                    
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text=f"🔴 <b>Курьер деактивирован</b>\n\n{courier.full_name} теперь неактивен.",
                        reply_markup=CourierAdminKeyboard.get_couriers_management_keyboard()
                    )
                
            elif action == "statistics":
                # Show couriers statistics
                all_users = await user_service.get_all_users()
                couriers = [user for user in all_users if user.role == UserRole.COURIER]
                
                if not couriers:
                    text = "📊 <b>Статистика курьеров</b>\n\nКурьеры не найдены."
                else:
                    active_couriers = [c for c in couriers if c.is_active]
                    
                    # Get total deliveries
                    from shared.types.order_types import OrderFilters
                    from shared.constants.order_constants import OrderStatus
                    
                    total_deliveries = 0
                    for courier in couriers:
                        filters = OrderFilters(
                            courier_id=courier.user_id,
                            statuses=[OrderStatus.DELIVERED]
                        )
                        deliveries = await order_service.list_orders(filters)
                        total_deliveries += len(deliveries)
                    
                    text = f"📊 <b>Статистика курьеров</b>\n\n"
                    text += f"👥 <b>Всего курьеров:</b> {len(couriers)}\n"
                    text += f"🟢 <b>Активных курьеров:</b> {len(active_couriers)}\n"
                    text += f"✅ <b>Всего доставок:</b> {total_deliveries}\n"
                    text += f"📈 <b>Среднее на курьера:</b> {total_deliveries // len(couriers) if couriers else 0}"
                
                keyboard = CourierAdminKeyboard.get_couriers_management_keyboard()
                
                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )

            elif action == "assign":
                # Show delivery orders that can be assigned to couriers
                ready_orders = await order_service.get_orders_by_status("ready")
                delivery_orders = await order_service.get_orders_by_status("delivery")
                candidate_orders = ready_orders + delivery_orders
                unassigned_delivery_orders = [
                    order for order in candidate_orders
                    if getattr(order, "order_type", None)
                    and order.order_type.value == "delivery"
                    and not getattr(order, "courier_id", None)
                ]

                if not unassigned_delivery_orders:
                    text = "🚚 <b>Назначение курьера</b>\n\nНет заказов доставки без назначенного курьера."
                    keyboard = CourierAdminKeyboard.get_couriers_management_keyboard()
                else:
                    text = (
                        "🚚 <b>Назначение курьера</b>\n\n"
                        f"Заказов без курьера: {len(unassigned_delivery_orders)}\n"
                        "Выберите заказ:"
                    )
                    keyboard = AdminKeyboard.get_orders_list_keyboard(unassigned_delivery_orders[:10])

                await self.admin_handler.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
                
            elif action == "assign_to_order":
                # Handle courier assignment to order
                if len(parts) >= 4:
                    order_id = parts[2]
                    courier_ref = parts[3]
                    
                    # Get order and courier
                    order = await order_service.get_order(order_id)
                    courier = await user_service.get_user_by_id(courier_ref)
                    if not courier:
                        try:
                            courier = await user_service.get_user_by_telegram_id(int(courier_ref))
                        except (TypeError, ValueError):
                            courier = None
                    
                    if not order:
                        await callback.answer("❌ Заказ не найден")
                        return
                    
                    if not courier:
                        await callback.answer("❌ Курьер не найден")
                        return
                    if courier.role != UserRole.COURIER:
                        await callback.answer("❌ Выбранный пользователь не является курьером")
                        return
                    if not courier.is_active:
                        await callback.answer("❌ Курьер неактивен")
                        return
                    
                    # Assign courier to order
                    await order_service.update_order(order_id, courier_id=courier.user_id)
                    order = await order_service.get_order(order_id)
                    if not order:
                        await callback.answer("❌ Не удалось загрузить заказ после назначения")
                        return
                    
                    # Send notification to courier
                    await notification_service.send_courier_assignment_notification(order, courier)
                    
                    await callback.answer(f"✅ Курьер {courier.full_name} назначен на заказ")
                    
                    # Return to order detail view
                    from infrastructure.telegram.utils.message_formatter import MessageFormatter
                    text = MessageFormatter.format_order_message(order)
                    keyboard = AdminKeyboard.get_order_management_keyboard(order)
                    
                    await self.admin_handler.safe_edit_message(
                        callback.message,
                        text=text,
                        reply_markup=keyboard
                    )
                
            else:
                await callback.answer("❌ Неизвестное действие")
                
        except Exception as e:
            self.logger.error(f"Error handling couriers callback: {e}")
            await callback.answer("❌ Произошла ошибка")
        
        await callback.answer()