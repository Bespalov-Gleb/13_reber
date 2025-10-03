"""Cafe settings SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class CafeSettingsModel(Base):
    """Cafe settings database model for content management."""
    
    __tablename__ = "cafe_settings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    cafe_name: Mapped[str] = mapped_column(String(200), nullable=False, default="Кафе")
    cafe_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cafe_address: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    cafe_phone: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    cafe_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Working hours
    working_hours: Mapped[str] = mapped_column(String(100), nullable=False, default="09:00-22:00")
    working_days: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # ["monday", "tuesday", ...]
    
    # Delivery settings
    delivery_zone_radius: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)  # в метрах
    delivery_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=200)  # в копейках
    free_delivery_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)  # в копейках
    min_order_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=500)  # в копейках
    
    # Cafe coordinates
    latitude: Mapped[Optional[float]] = mapped_column(String(20), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(String(20), nullable=True)
    
    # Social media
    instagram_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    vk_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    telegram_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Bot settings
    welcome_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_info_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pickup_info_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Images
    cafe_logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cafe_photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<CafeSettingsModel(id={self.id}, cafe_name={self.cafe_name})>"