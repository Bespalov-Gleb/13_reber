"""Booking handler for Telegram bot."""

from typing import Any, Dict
from datetime import date, time, datetime

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F

from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.booking_keyboard import BookingKeyboard
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.booking_service import BookingService
from app.dependencies import get_booking_service, get_user_service


class BookingHandler(BaseHandler):
    """Handler for booking operations."""

    def __init__(self):
        super().__init__()
        self._booking_contexts: dict[int, dict[str, Any]] = {}
        self._booking_input_states: dict[int, str] = {}

    def _get_booking_context(self, user_id: int) -> dict[str, Any]:
        """Get in-memory booking context for user."""
        if user_id not in self._booking_contexts:
            self._booking_contexts[user_id] = {}
        return self._booking_contexts[user_id]
    
    def _register_handlers(self) -> None:
        """Register booking handlers."""
        self.router.callback_query.register(
            self.handle_booking_callback,
            F.data.startswith("booking:")
        )
        self.router.message.register(
            self.handle_booking_text_message,
            F.text,
            lambda message: bool(self._booking_input_states.get(message.from_user.id))
        )
    
    async def handle_booking_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle booking callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        action = CallbackParser.get_action(callback_data)
        
        try:
            if action == "guests":
                await self._handle_guests_selection(callback, user_id, data)
            elif action == "date":
                await self._handle_date_selection(callback, user_id, data)
            elif action == "time":
                await self._handle_time_selection(callback, user_id, data)
            elif action == "contact":
                await self._handle_contact_selection(callback, user_id, data)
            elif action == "confirm":
                await self._handle_confirmation(callback, user_id, data)
            elif action == "cancel":
                await self._handle_cancellation(callback, user_id, data)
            else:
                await callback.answer("❌ Неизвестное действие")
                
        except Exception as e:
            self.logger.error(f"Error handling booking callback: {e}")
            await callback.answer("❌ Произошла ошибка")
        
        await callback.answer()
    
    async def handle_booking_text_message(self, message: Message, **kwargs) -> None:
        """Handle text messages during booking flow."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", message.from_user.id)
        text = (message.text or "").strip()
        input_state = self._booking_input_states.get(user_id)
        if not input_state:
            return

        booking_data = self._get_booking_context(user_id)
        if input_state == "contact_name":
            if not text:
                await message.answer("❌ Имя не может быть пустым. Введите имя:")
                return
            booking_data["contact_name"] = text
        elif input_state == "contact_phone":
            from shared.utils.helpers import parse_phone_number
            normalized_phone = parse_phone_number(text)
            if not normalized_phone:
                await message.answer("❌ Неверный формат телефона. Пример: +79991234567")
                return
            booking_data["contact_phone"] = normalized_phone
        elif input_state == "comment":
            booking_data["comment"] = None if text == "-" else text

        self._booking_input_states.pop(user_id, None)

        date_str = booking_data["booking_date"].strftime("%d.%m.%Y") if booking_data.get("booking_date") else "—"
        time_str = booking_data["booking_time"].strftime("%H:%M") if booking_data.get("booking_time") else "—"
        guests_count = booking_data.get("guests_count", "—")
        contact_name = booking_data.get("contact_name", "Не указано")
        contact_phone = booking_data.get("contact_phone", "Не указан")
        comment = booking_data.get("comment", "—") or "—"

        summary_text = "📋 <b>Подтверждение бронирования</b>\n\n"
        summary_text += f"👥 Гостей: {guests_count}\n"
        summary_text += f"📅 Дата: {date_str}\n"
        summary_text += f"🕐 Время: {time_str}\n"
        summary_text += f"📝 Имя: {contact_name}\n"
        summary_text += f"📞 Телефон: {contact_phone}\n"
        summary_text += f"💬 Комментарий: {comment}\n\n"
        summary_text += "Вы можете изменить данные кнопками ниже или подтвердить бронирование."
        await message.answer(summary_text, reply_markup=BookingKeyboard.get_contact_keyboard())
    
    async def _handle_guests_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle guests count selection."""
        count = CallbackParser.get_guests_count(callback.data)
        if count is None:
            await callback.answer("❌ Не удалось определить количество гостей")
            return
        
        booking_data = self._get_booking_context(user_id)
        booking_data["guests_count"] = count
        
        # Show date selection
        text = f"👥 Выбрано гостей: {count}\n\n📅 Выберите дату бронирования:"
        keyboard = BookingKeyboard.get_date_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_date_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle date selection."""
        booking_date_str = CallbackParser.get_booking_date(callback.data)
        if not booking_date_str:
            await callback.answer("❌ Неверная дата")
            return
        booking_date = date.fromisoformat(booking_date_str)
        
        booking_data = self._get_booking_context(user_id)
        booking_data["booking_date"] = booking_date
        
        # Get available time slots
        booking_service = await get_booking_service(data)
        available_times = await booking_service.get_available_time_slots(booking_date)
        
        if not available_times:
            await callback.message.edit_text(
                text="❌ На выбранную дату нет свободных столиков.\n\nПожалуйста, выберите другую дату.",
                reply_markup=BookingKeyboard.get_date_keyboard()
            )
            return
        
        # Show time selection
        date_str = booking_date.strftime("%d.%m.%Y")
        text = f"📅 Выбрана дата: {date_str}\n\n🕐 Выберите время:"
        keyboard = BookingKeyboard.get_time_keyboard(available_times)
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_time_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle time selection."""
        time_str = CallbackParser.get_booking_time(callback.data)
        if not time_str:
            await callback.answer("❌ Неверное время")
            return
        booking_time = time.fromisoformat(time_str)
        
        booking_data = self._get_booking_context(user_id)
        booking_data["booking_time"] = booking_time
        
        # Show contact information input
        if "booking_date" not in booking_data or "guests_count" not in booking_data:
            await callback.answer("❌ Данные бронирования потеряны. Начните заново.")
            return
        date_str = booking_data["booking_date"].strftime("%d.%m.%Y")
        time_str = booking_time.strftime("%H:%M")
        guests_count = booking_data["guests_count"]
        
        text = f"📋 <b>Подтверждение бронирования</b>\n\n"
        text += f"👥 Гостей: {guests_count}\n"
        text += f"📅 Дата: {date_str}\n"
        text += f"🕐 Время: {time_str}\n\n"
        text += f"Для завершения бронирования введите контактную информацию:"
        
        keyboard = BookingKeyboard.get_contact_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_contact_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle contact information selection."""
        sub_action = CallbackParser.get_sub_action(callback.data)
        
        if sub_action == "name":
            self._booking_input_states[user_id] = "contact_name"
            await callback.message.edit_text(
                text="📝 Введите ваше имя:",
                reply_markup=None
            )
        elif sub_action == "phone":
            self._booking_input_states[user_id] = "contact_phone"
            await callback.message.edit_text(
                text="📞 Введите ваш телефон:",
                reply_markup=None
            )
        elif sub_action == "comment":
            self._booking_input_states[user_id] = "comment"
            await callback.message.edit_text(
                text="💬 Введите комментарий к бронированию (необязательно, '-' чтобы пропустить):",
                reply_markup=None
            )
        elif sub_action == "confirm":
            await self._create_booking(callback, user_id, data)
    
    async def _create_booking(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Create booking."""
        booking_data = self._get_booking_context(user_id)
        if booking_data.get("_creating"):
            await callback.answer("⏳ Бронирование уже создается, подождите")
            return
        
        # Check if all required data is present
        required_fields = ["guests_count", "booking_date", "booking_time"]
        for field in required_fields:
            if field not in booking_data:
                await callback.answer("❌ Не все данные заполнены")
                return
        
        contact_name = booking_data.get("contact_name")
        contact_phone = booking_data.get("contact_phone")
        comment = booking_data.get("comment")
        if not contact_name or not contact_phone:
            await callback.answer("❌ Заполните имя и телефон перед подтверждением")
            return
        
        booking_data["_creating"] = True
        try:
            booking_service = await get_booking_service(data)
            user_service = await get_user_service(data)
            db_user = await user_service.get_user_by_telegram_id(user_id)
            if not db_user:
                await callback.message.edit_text(
                    text="❌ Пользователь не найден в базе. Нажмите /start и попробуйте снова.",
                    reply_markup=None
                )
                return

            booking = await booking_service.create_booking(
                user_id=db_user.user_id,
                booking_date=booking_data["booking_date"],
                booking_time=booking_data["booking_time"],
                guests_count=booking_data["guests_count"],
                contact_name=contact_name,
                contact_phone=contact_phone,
                comment=comment
            )
            
            # Show success message
            date_str = booking.booking_date.strftime("%d.%m.%Y")
            time_str = booking.booking_time.strftime("%H:%M")
            
            text = f"✅ <b>Бронирование создано!</b>\n\n"
            text += f"🆔 ID: {booking.booking_id[:8]}\n"
            text += f"👥 Гостей: {booking.guests_count}\n"
            text += f"📅 Дата: {date_str}\n"
            text += f"🕐 Время: {time_str}\n"
            text += f"📊 Статус: Ожидает подтверждения\n\n"
            text += f"Мы свяжемся с вами для подтверждения бронирования."
            
            await callback.message.edit_text(
                text=text,
                reply_markup=None
            )
            self._booking_contexts.pop(user_id, None)
            self._booking_input_states.pop(user_id, None)
            
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ Ошибка при создании бронирования: {str(e)}",
                reply_markup=None
            )
        finally:
            booking_data.pop("_creating", None)
    
    async def _handle_confirmation(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle booking confirmation."""
        await self._create_booking(callback, user_id, data)
    
    async def _handle_cancellation(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle booking cancellation."""
        self._booking_contexts.pop(user_id, None)
        self._booking_input_states.pop(user_id, None)
        await callback.message.edit_text(
            text="❌ Бронирование отменено.",
            reply_markup=None
        )
