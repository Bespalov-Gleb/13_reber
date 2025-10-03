"""User registered domain event."""

from datetime import datetime
from typing import Any, Dict

from domain.entities.user import User


class UserRegistered:
    """Domain event for user registration."""
    
    def __init__(self, user: User, occurred_at: datetime | None = None):
        self.user = user
        self.occurred_at = occurred_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": "user_registered",
            "user_id": self.user.user_id,
            "telegram_id": self.user.telegram_id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "role": self.user.role.value,
            "occurred_at": self.occurred_at.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"UserRegistered(user_id={self.user.user_id}, telegram_id={self.user.telegram_id}, name={self.user.full_name})"
    
    def __repr__(self) -> str:
        return self.__str__()