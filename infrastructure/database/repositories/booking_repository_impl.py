"""Booking repository implementation."""

from typing import List, Optional
from datetime import date, time, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc

from domain.entities.booking import Booking
from domain.repositories.booking_repository import BookingRepository
from infrastructure.database.models.booking_model import BookingModel


class BookingRepositoryImpl(BookingRepository):
    """Booking repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_booking(self, booking: Booking) -> Booking:
        """Create booking."""
        db_booking = BookingModel(
            id=booking.booking_id,
            user_id=booking.user_id,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            guests_count=booking.guests_count,
            contact_name=booking.contact_name,
            contact_phone=booking.contact_phone,
            comment=booking.comment,
            status=booking.status,
            created_at=booking.created_at,
            updated_at=booking.updated_at
        )
        
        self.session.add(db_booking)
        await self.session.flush()
        
        return self._model_to_entity(db_booking)
    
    async def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID."""
        result = await self.session.execute(
            select(BookingModel).where(BookingModel.id == booking_id)
        )
        db_booking = result.scalar_one_or_none()
        
        if db_booking:
            return self._model_to_entity(db_booking)
        return None
    
    async def update_booking(self, booking: Booking) -> Booking:
        """Update booking."""
        result = await self.session.execute(
            select(BookingModel).where(BookingModel.id == booking.booking_id)
        )
        db_booking = result.scalar_one_or_none()
        
        if not db_booking:
            raise ValueError(f"Booking with id {booking.booking_id} not found")
        
        # Update fields
        db_booking.booking_date = booking.booking_date
        db_booking.booking_time = booking.booking_time
        db_booking.guests_count = booking.guests_count
        db_booking.contact_name = booking.contact_name
        db_booking.contact_phone = booking.contact_phone
        db_booking.comment = booking.comment
        db_booking.status = booking.status
        db_booking.updated_at = booking.updated_at
        
        await self.session.flush()
        
        return self._model_to_entity(db_booking)
    
    async def delete_booking(self, booking_id: str) -> bool:
        """Delete booking."""
        result = await self.session.execute(
            select(BookingModel).where(BookingModel.id == booking_id)
        )
        db_booking = result.scalar_one_or_none()
        
        if not db_booking:
            return False
        
        await self.session.delete(db_booking)
        await self.session.flush()
        
        return True
    
    async def get_bookings_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get bookings by user ID."""
        result = await self.session.execute(
            select(BookingModel)
            .where(BookingModel.user_id == user_id)
            .order_by(desc(BookingModel.booking_date), desc(BookingModel.booking_time))
            .limit(limit)
            .offset(offset)
        )
        db_bookings = result.scalars().all()
        
        return [self._model_to_entity(db_booking) for db_booking in db_bookings]
    
    async def get_bookings_by_date(self, booking_date: date) -> List[Booking]:
        """Get bookings by date."""
        result = await self.session.execute(
            select(BookingModel)
            .where(and_(
                BookingModel.booking_date == booking_date,
                BookingModel.status != "cancelled"
            ))
            .order_by(BookingModel.booking_time)
        )
        db_bookings = result.scalars().all()
        
        return [self._model_to_entity(db_booking) for db_booking in db_bookings]
    
    async def get_bookings_by_status(self, status: str, limit: int = 50, offset: int = 0) -> List[Booking]:
        """Get bookings by status."""
        result = await self.session.execute(
            select(BookingModel)
            .where(BookingModel.status == status)
            .order_by(desc(BookingModel.booking_date), desc(BookingModel.booking_time))
            .limit(limit)
            .offset(offset)
        )
        db_bookings = result.scalars().all()
        
        return [self._model_to_entity(db_booking) for db_booking in db_bookings]
    
    async def get_upcoming_bookings(self, limit: int = 20, offset: int = 0) -> List[Booking]:
        """Get upcoming bookings."""
        today = date.today()
        result = await self.session.execute(
            select(BookingModel)
            .where(and_(
                BookingModel.booking_date >= today,
                BookingModel.status != "cancelled"
            ))
            .order_by(BookingModel.booking_date, BookingModel.booking_time)
            .limit(limit)
            .offset(offset)
        )
        db_bookings = result.scalars().all()
        
        return [self._model_to_entity(db_booking) for db_booking in db_bookings]
    
    async def get_today_bookings(self) -> List[Booking]:
        """Get today's bookings."""
        today = date.today()
        return await self.get_bookings_by_date(today)
    
    async def check_booking_conflict(self, booking_date: date, booking_time: time, guests_count: int) -> bool:
        """Check if there's a booking conflict for the given date/time."""
        # Check for overlapping time slots (assuming 2-hour slots)
        from datetime import timedelta
        
        # Calculate time range (1 hour before and after)
        start_time = (datetime.combine(booking_date, booking_time) - timedelta(hours=1)).time()
        end_time = (datetime.combine(booking_date, booking_time) + timedelta(hours=1)).time()
        
        result = await self.session.execute(
            select(func.count(BookingModel.id))
            .where(and_(
                BookingModel.booking_date == booking_date,
                BookingModel.booking_time >= start_time,
                BookingModel.booking_time <= end_time,
                BookingModel.status != "cancelled"
            ))
        )
        
        conflict_count = result.scalar() or 0
        
        # Simple conflict check - can be made more sophisticated
        # For now, we'll allow up to 2 bookings per time slot
        return conflict_count >= 2
    
    async def get_booking_count_by_date(self, booking_date: date) -> int:
        """Get booking count for a specific date."""
        result = await self.session.execute(
            select(func.count(BookingModel.id))
            .where(and_(
                BookingModel.booking_date == booking_date,
                BookingModel.status != "cancelled"
            ))
        )
        return result.scalar() or 0
    
    def _model_to_entity(self, db_booking: BookingModel) -> Booking:
        """Convert database model to domain entity."""
        return Booking(
            booking_id=db_booking.id,
            user_id=db_booking.user_id,
            booking_date=db_booking.booking_date,
            booking_time=db_booking.booking_time,
            guests_count=db_booking.guests_count,
            contact_name=db_booking.contact_name,
            contact_phone=db_booking.contact_phone,
            comment=db_booking.comment,
            status=db_booking.status,
            created_at=db_booking.created_at,
            updated_at=db_booking.updated_at
        )
