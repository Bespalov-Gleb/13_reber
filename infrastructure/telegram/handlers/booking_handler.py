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
from app.dependencies import get_booking_service


class BookingHandler(BaseHandler):
    """Handler for booking operations."""
    
    def _register_handlers(self) -> None:
        """Register booking handlers."""
        self.router.callback_query.register(
            self.handle_booking_callback,
            F.data.startswith("booking:")
        )
        
        self.router.message.register(
            self.handle_booking_text_message,
            F.text
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
        text = message.text
        
        # This would need state management to know what field the user is entering
        # For now, we'll handle it in the callback flow
        await message.answer("Пожалуйста, используйте кнопки для бронирования столика.")
    
    async def _handle_guests_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle guests count selection."""
        count = CallbackParser.get_guests_count(callback.data)
        
        # Store guests count in user data
        if "booking_data" not in data:
            data["booking_data"] = {}
        data["booking_data"]["guests_count"] = count
        
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
        booking_date = date.fromisoformat(booking_date_str)
        
        # Store date in user data
        if "booking_data" not in data:
            data["booking_data"] = {}
        data["booking_data"]["booking_date"] = booking_date
        
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
        booking_time = time.fromisoformat(time_str)
        
        # Store time in user data
        if "booking_data" not in data:
            data["booking_data"] = {}
        data["booking_data"]["booking_time"] = booking_time
        
        # Show contact information input
        booking_data = data["booking_data"]
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
            await callback.message.edit_text(
                text="📝 Введите ваше имя:",
                reply_markup=None
            )
        elif sub_action == "phone":
            await callback.message.edit_text(
                text="📞 Введите ваш телефон:",
                reply_markup=None
            )
        elif sub_action == "comment":
            await callback.message.edit_text(
                text="💬 Введите комментарий к бронированию (необязательно):",
                reply_markup=None
            )
        elif sub_action == "confirm":
            await self._create_booking(callback, user_id, data)
    
    async def _create_booking(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Create booking."""
        booking_data = data.get("booking_data", {})
        
        # Check if all required data is present
        required_fields = ["guests_count", "booking_date", "booking_time"]
        for field in required_fields:
            if field not in booking_data:
                await callback.answer("❌ Не все данные заполнены")
                return
        
        # For now, we'll use default contact info
        # In a real implementation, this would come from user input
        contact_name = "Имя не указано"
        contact_phone = "Телефон не указан"
        comment = booking_data.get("comment", "")
        
        try:
            booking_service = await get_booking_service(data)
            booking = await booking_service.create_booking(
                user_id=str(user_id),
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
            
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ Ошибка при создании бронирования: {str(e)}",
                reply_markup=None
            )
    
    async def _handle_confirmation(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle booking confirmation."""
        # This would be used for admin confirmation
        pass
    
    async def _handle_cancellation(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle booking cancellation."""
        await callback.message.edit_text(
            text="❌ Бронирование отменено.",
            reply_markup=None
        )
