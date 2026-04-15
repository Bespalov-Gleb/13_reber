"""Booking domain entity."""

from datetime import datetime, date, time
from typing import Optional
from dataclasses import dataclass


@dataclass
class Booking:
    """Booking domain entity."""
    
    booking_id: str
    user_id: str
    
    # Booking details
    booking_date: date
    booking_time: time
    guests_count: int
    
    # Contact information
    contact_name: str
    contact_phone: str
    
    # Additional information
    comment: Optional[str] = None
    
    # Booking status
    status: str = "pending"  # pending, confirmed, cancelled
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def is_valid_guests_count(self) -> bool:
        """Check if guests count is valid (1-20)."""
        return 1 <= self.guests_count <= 20
    
    def is_future_booking(self) -> bool:
        """Check if booking is in the future."""
        booking_datetime = datetime.combine(self.booking_date, self.booking_time)
        return booking_datetime > datetime.now()
    
    def is_today(self) -> bool:
        """Check if booking is for today."""
        return self.booking_date == date.today()
    
    def is_tomorrow(self) -> bool:
        """Check if booking is for tomorrow."""
        from datetime import timedelta
        tomorrow = date.today() + timedelta(days=1)
        return self.booking_date == tomorrow
    
    def get_booking_datetime(self) -> datetime:
        """Get booking as datetime object."""
        return datetime.combine(self.booking_date, self.booking_time)
    
    def get_status_display(self) -> str:
        """Get status display text."""
        status_display = {
            "pending": "⏳ Ожидает подтверждения",
            "confirmed": "✅ Подтверждено",
            "cancelled": "❌ Отменено"
        }
        return status_display.get(self.status, "❓ Неизвестно")
    
    def get_guests_display(self) -> str:
        """Get guests count display text."""
        if self.guests_count == 1:
            return "1 гость"
        elif 2 <= self.guests_count <= 4:
            return f"{self.guests_count} гостя"
        else:
            return f"{self.guests_count} гостей"
