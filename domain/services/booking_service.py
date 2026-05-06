"""Booking service for business logic."""

from typing import List, Optional
from datetime import date, time, datetime, timedelta

from domain.entities.booking import Booking
from domain.repositories.booking_repository import BookingRepository
from shared.utils.helpers import generate_id


class BookingService:
    """Booking service for business logic."""
    
    def __init__(self, booking_repository: BookingRepository):
        self.booking_repository = booking_repository
    
    async def create_booking(
        self,
        user_id: str,
        booking_date: date,
        booking_time: time,
        guests_count: int,
        contact_name: str,
        contact_phone: str,
        comment: Optional[str] = None
    ) -> Booking:
        """Create a new booking."""
        # Validate booking date (not in the past)
        if booking_date < date.today():
            raise ValueError("Нельзя забронировать столик на прошедшую дату")
        
        # Validate booking time (not in the past for today)
        if booking_date == date.today():
            current_time = datetime.now().time()
            if booking_time <= current_time:
                raise ValueError("Нельзя забронировать столик на прошедшее время")
        
        # Validate guests count
        if guests_count < 1 or guests_count > 20:
            raise ValueError("Количество гостей должно быть от 1 до 20")
        
        # Check for conflicts
        has_conflict = await self.booking_repository.check_booking_conflict(
            booking_date, booking_time, guests_count
        )
        if has_conflict:
            raise ValueError("На это время уже есть бронирование. Выберите другое время.")
        
        # Create booking
        booking = Booking(
            booking_id=generate_id(),
            user_id=user_id,
            booking_date=booking_date,
            booking_time=booking_time,
            guests_count=guests_count,
            contact_name=contact_name,
            contact_phone=contact_phone,
            comment=comment,
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return await self.booking_repository.create_booking(booking)
    
    async def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID."""
        return await self.booking_repository.get_booking_by_id(booking_id)
    
    async def update_booking_status(self, booking_id: str, status: str) -> Booking:
        """Update booking status."""
        booking = await self.booking_repository.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")
        
        if status not in ["pending", "confirmed", "cancelled"]:
            raise ValueError("Invalid booking status")
        
        booking.status = status
        booking.updated_at = datetime.now()
        
        return await self.booking_repository.update_booking(booking)
    
    async def cancel_booking(self, booking_id: str) -> Booking:
        """Cancel a booking."""
        return await self.update_booking_status(booking_id, "cancelled")
    
    async def confirm_booking(self, booking_id: str) -> Booking:
        """Confirm a booking."""
        return await self.update_booking_status(booking_id, "confirmed")
    
    async def get_user_bookings(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get user's bookings."""
        return await self.booking_repository.get_bookings_by_user(user_id, limit, offset)
    
    async def get_today_bookings(self) -> List[Booking]:
        """Get today's bookings."""
        return await self.booking_repository.get_today_bookings()
    
    async def get_upcoming_bookings(self, limit: int = 20, offset: int = 0) -> List[Booking]:
        """Get upcoming bookings."""
        return await self.booking_repository.get_upcoming_bookings(limit, offset)
    
    async def get_bookings_by_status(self, status: str, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get bookings by status."""
        return await self.booking_repository.get_bookings_by_status(status, limit, offset)
    
    async def get_available_time_slots(self, booking_date: date) -> List[time]:
        """Get available time slots for a specific date."""
        # Define available time slots (every 2 hours from 10:00 to 22:00)
        available_slots = []
        start_time = time(10, 0)
        end_time = time(22, 0)
        current_dt = datetime.combine(booking_date, start_time)
        end_dt = datetime.combine(booking_date, end_time)

        while current_dt <= end_dt:
            current_time = current_dt.time()
            # Check if this time slot is available
            has_conflict = await self.booking_repository.check_booking_conflict(
                booking_date, current_time, 1
            )
            if not has_conflict:
                available_slots.append(current_time)
            
            # Add 2 hours
            current_dt += timedelta(hours=2)
        
        return available_slots
    
    async def get_booking_statistics(self) -> dict:
        """Get booking statistics."""
        today = date.today()
        
        # Get today's bookings
        today_bookings = await self.booking_repository.get_today_bookings()
        
        # Get pending bookings
        pending_bookings = await self.booking_repository.get_bookings_by_status("pending")
        
        # Get confirmed bookings
        confirmed_bookings = await self.booking_repository.get_bookings_by_status("confirmed")
        
        # Get upcoming bookings
        upcoming_bookings = await self.booking_repository.get_upcoming_bookings()
        
        return {
            "today_bookings": len(today_bookings),
            "pending_bookings": len(pending_bookings),
            "confirmed_bookings": len(confirmed_bookings),
            "upcoming_bookings": len(upcoming_bookings),
            "total_guests_today": sum(booking.guests_count for booking in today_bookings)
        }
