"""Booking repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, time

from domain.entities.booking import Booking


class BookingRepository(ABC):
    """Booking repository interface."""
    
    @abstractmethod
    async def create_booking(self, booking: Booking) -> Booking:
        """Create booking."""
        pass
    
    @abstractmethod
    async def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID."""
        pass
    
    @abstractmethod
    async def update_booking(self, booking: Booking) -> Booking:
        """Update booking."""
        pass
    
    @abstractmethod
    async def delete_booking(self, booking_id: str) -> bool:
        """Delete booking."""
        pass
    
    @abstractmethod
    async def get_bookings_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get bookings by user ID."""
        pass
    
    @abstractmethod
    async def get_bookings_by_date(self, booking_date: date) -> List[Booking]:
        """Get bookings by date."""
        pass
    
    @abstractmethod
    async def get_bookings_by_status(self, status: str, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get bookings by status."""
        pass
    
    @abstractmethod
    async def get_upcoming_bookings(self, limit: int = 20, offset: int = 0) -> List[Booking]:
        """Get upcoming bookings."""
        pass
    
    @abstractmethod
    async def get_today_bookings(self) -> List[Booking]:
        """Get today's bookings."""
        pass
    
    @abstractmethod
    async def check_booking_conflict(self, booking_date: date, booking_time: time, guests_count: int) -> bool:
        """Check if there's a booking conflict for the given date/time."""
        pass
    
    @abstractmethod
    async def get_booking_count_by_date(self, booking_date: date) -> int:
        """Get booking count for a specific date."""
        pass
