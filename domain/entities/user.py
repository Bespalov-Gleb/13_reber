"""User entity."""

from datetime import datetime
from typing import Optional

from shared.types.user_types import UserRole, UserStatus


class User:
    """User domain entity."""
    
    def __init__(
        self,
        user_id: str,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        role: UserRole = UserRole.CUSTOMER,
        status: UserStatus = UserStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.username or f"User {self.telegram_id}"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_courier(self) -> bool:
        """Check if user is courier."""
        return self.role == UserRole.COURIER
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    def update_phone(self, phone: str) -> None:
        """Update user's phone number."""
        self.phone = phone
        self.updated_at = datetime.now()
    
    def update_name(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> None:
        """Update user's name."""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        self.updated_at = datetime.now()
    
    def change_role(self, role: UserRole) -> None:
        """Change user's role."""
        self.role = role
        self.updated_at = datetime.now()
    
    def change_status(self, status: UserStatus) -> None:
        """Change user's status."""
        self.status = status
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"User(id={self.user_id}, telegram_id={self.telegram_id}, name={self.full_name})"
    
    def __repr__(self) -> str:
        return self.__str__()