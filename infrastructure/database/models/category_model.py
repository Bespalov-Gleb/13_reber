"""Category SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class CategoryModel(Base):
    """Category database model."""
    
    __tablename__ = "categories"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu_items: Mapped[list["MenuItemModel"]] = relationship("MenuItemModel", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<CategoryModel(id={self.id}, name={self.name}, active={self.is_active})>"