"""Menu item SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class MenuItemModel(Base):
    """Menu item database model."""
    
    __tablename__ = "menu_items"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # в копейках
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ingredients: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    allergens: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="menu_items")
    
    def __repr__(self) -> str:
        return f"<MenuItemModel(id={self.id}, name={self.name}, price={self.price}, available={self.is_available})>"