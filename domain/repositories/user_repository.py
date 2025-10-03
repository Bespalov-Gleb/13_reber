"""User repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.user import User


class UserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users."""
        pass
    
    @abstractmethod
    async def get_admins(self) -> List[User]:
        """Get all admin users."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total user count."""
        pass