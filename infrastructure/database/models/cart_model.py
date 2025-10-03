"""Cart SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class CartModel(Base):
    """Cart database model."""
    
    __tablename__ = "carts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="carts")
    items: Mapped[list["CartItemModel"]] = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<CartModel(id={self.id}, user_id={self.user_id})>"


class CartItemModel(Base):
    """Cart item database model."""
    
    __tablename__ = "cart_items"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id: Mapped[str] = mapped_column(String(36), ForeignKey("carts.id"), nullable=False)
    menu_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("menu_items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart: Mapped["CartModel"] = relationship("CartModel", back_populates="items")
    menu_item: Mapped["MenuItemModel"] = relationship("MenuItemModel")
    
    def __repr__(self) -> str:
        return f"<CartItemModel(id={self.id}, cart_id={self.cart_id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})>"