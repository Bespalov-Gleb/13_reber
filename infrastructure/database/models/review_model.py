"""Review SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class ReviewModel(Base):
    """Review database model."""
    
    __tablename__ = "reviews"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    order_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("orders.id"), nullable=True)
    menu_item_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("menu_items.id"), nullable=True)
    
    # Review content
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 stars
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Review status
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_answered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    admin_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel")
    order: Mapped[Optional["OrderModel"]] = relationship("OrderModel")
    menu_item: Mapped[Optional["MenuItemModel"]] = relationship("MenuItemModel")
    
    def __repr__(self) -> str:
        return f"<ReviewModel(id={self.id}, user_id={self.user_id}, rating={self.rating})>"
