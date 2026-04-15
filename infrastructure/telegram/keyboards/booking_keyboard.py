"""Booking keyboard for booking flow."""

from typing import List, Dict, Any
from datetime import date, time

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shared.utils.helpers import build_callback_data


class BookingKeyboard:
    """Keyboard for booking flow."""
    
    @staticmethod
    def create_inline_keyboard(buttons: List[List[Dict[str, Any]]]) -> InlineKeyboardMarkup:
        """Create inline keyboard from button configuration."""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button["text"],
                        callback_data=button["callback_data"]
                    )
                )
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_inline_button(text: str, callback_data: str) -> Dict[str, Any]:
        """Create inline button configuration."""
        return {"text": text, "callback_data": callback_data}
    
    @staticmethod
    def get_guests_count_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for guests count selection."""
        buttons = []
        for i in range(1, 9):  # 1-8 guests
            buttons.append(
                BookingKeyboard.create_inline_button(
                    text=f"{i} чел.",
                    callback_data=build_callback_data("booking:guests", count=i)
                )
            )
        
        # Split into rows of 4
        rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
        
        return BookingKeyboard.create_inline_keyboard(rows)
    
    @staticmethod
    def get_date_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for date selection (next 7 days)."""
        from datetime import date, timedelta
        
        buttons = []
        today = date.today()
        
        for i in range(7):  # Next 7 days
            booking_date = today + timedelta(days=i)
            day_name = booking_date.strftime("%a")
            day_number = booking_date.strftime("%d.%m")
            
            buttons.append(
                BookingKeyboard.create_inline_button(
                    text=f"{day_name} {day_number}",
                    callback_data=build_callback_data("booking:date", date=booking_date.isoformat())
                )
            )
        
        # Split into rows of 2
        rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        
        return BookingKeyboard.create_inline_keyboard(rows)
    
    @staticmethod
    def get_time_keyboard(available_times: List[time]) -> InlineKeyboardMarkup:
        """Get keyboard for time selection."""
        buttons = []
        
        for time_slot in available_times:
            time_str = time_slot.strftime("%H:%M")
            buttons.append(
                BookingKeyboard.create_inline_button(
                    text=time_str,
                    callback_data=build_callback_data("booking:time", time=time_str)
                )
            )
        
        # Split into rows of 3
        rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
        
        return BookingKeyboard.create_inline_keyboard(rows)
    
    @staticmethod
    def get_contact_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for contact information input."""
        return BookingKeyboard.create_inline_keyboard([
            [
                BookingKeyboard.create_inline_button(
                    "📝 Ввести имя",
                    "booking:contact:name"
                )
            ],
            [
                BookingKeyboard.create_inline_button(
                    "📞 Ввести телефон",
                    "booking:contact:phone"
                )
            ],
            [
                BookingKeyboard.create_inline_button(
                    "💬 Добавить комментарий",
                    "booking:contact:comment"
                )
            ],
            [
                BookingKeyboard.create_inline_button(
                    "✅ Подтвердить бронирование",
                    "booking:confirm"
                )
            ],
            [
                BookingKeyboard.create_inline_button(
                    "❌ Отменить",
                    "booking:cancel"
                )
            ]
        ])
    
    @staticmethod
    def get_confirmation_keyboard(booking_id: str) -> InlineKeyboardMarkup:
        """Get keyboard for booking confirmation."""
        return BookingKeyboard.create_inline_keyboard([
            [
                BookingKeyboard.create_inline_button(
                    "✅ Подтвердить",
                    build_callback_data("booking:confirm:yes", booking_id=booking_id)
                ),
                BookingKeyboard.create_inline_button(
                    "❌ Отменить",
                    build_callback_data("booking:confirm:no", booking_id=booking_id)
                )
            ]
        ])
    
    @staticmethod
    def get_booking_management_keyboard(booking: 'Booking') -> InlineKeyboardMarkup:
        """Get keyboard for booking management (admin)."""
        buttons = []
        
        if booking.status == "pending":
            buttons.append([
                BookingKeyboard.create_inline_button(
                    "✅ Подтвердить",
                    build_callback_data("admin_bookings:confirm", booking_id=booking.booking_id)
                ),
                BookingKeyboard.create_inline_button(
                    "❌ Отменить",
                    build_callback_data("admin_bookings:cancel", booking_id=booking.booking_id)
                )
            ])
        
        buttons.append([
            BookingKeyboard.create_inline_button(
                "📞 Позвонить",
                f"tel:{booking.contact_phone}"
            )
        ])
        
        buttons.append([
            BookingKeyboard.create_inline_button(
                "⬅️ Назад",
                "admin_bookings:menu"
            )
        ])
        
        return BookingKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_booking_list_keyboard(bookings: List['Booking'], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
        """Get keyboard for booking list."""
        buttons = []
        
        # Add booking buttons
        start_idx = page * per_page
        end_idx = start_idx + per_page
        
        for booking in bookings[start_idx:end_idx]:
            date_str = booking.booking_date.strftime("%d.%m")
            time_str = booking.booking_time.strftime("%H:%M")
            status_emoji = {
                "pending": "⏳",
                "confirmed": "✅",
                "cancelled": "❌"
            }.get(booking.status, "❓")
            
            buttons.append([
                BookingKeyboard.create_inline_button(
                    f"{status_emoji} {date_str} {time_str} ({booking.guests_count} чел.)",
                    build_callback_data("admin_bookings:view", booking_id=booking.booking_id)
                )
            ])
        
        # Add pagination
        if len(bookings) > per_page:
            pagination_buttons = []
            
            if page > 0:
                pagination_buttons.append(
                    BookingKeyboard.create_inline_button(
                        "⬅️",
                        build_callback_data("admin_bookings:page", page=page-1)
                    )
                )
            
            if end_idx < len(bookings):
                pagination_buttons.append(
                    BookingKeyboard.create_inline_button(
                        "➡️",
                        build_callback_data("admin_bookings:page", page=page+1)
                    )
                )
            
            if pagination_buttons:
                buttons.append(pagination_buttons)
        
        # Add back button
        buttons.append([
            BookingKeyboard.create_inline_button(
                "⬅️ Назад",
                "admin_bookings:menu"
            )
        ])
        
        return BookingKeyboard.create_inline_keyboard(buttons)
