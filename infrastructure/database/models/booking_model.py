"""Booking SQLAlchemy model."""

from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class BookingModel(Base):
    """Booking database model."""
    
    __tablename__ = "bookings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Booking details
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    booking_time: Mapped[time] = mapped_column(Time, nullable=False)
    guests_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Contact information
    contact_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Additional information
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Booking status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, confirmed, cancelled
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel")
    
    def __repr__(self) -> str:
        return f"<BookingModel(id={self.id}, user_id={self.user_id}, date={self.booking_date}, time={self.booking_time})>"
