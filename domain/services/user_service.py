"""User service for user-related business logic."""

from datetime import datetime, date
from typing import List, Optional
from uuid import uuid4

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> User:
        """Create a new user."""
        user = User(
            id=str(uuid4()),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_active=True,
            is_blocked=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return await self.user_repository.create(user)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        return await self.user_repository.get_by_telegram_id(telegram_id)

    async def update_user(self, user: User) -> User:
        """Update user."""
        user.updated_at = datetime.now()
        return await self.user_repository.update(user)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        return await self.user_repository.delete(user_id)

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        return await self.user_repository.list_all()

    async def get_users_by_date(self, target_date: date) -> List[User]:
        """Get users created on a specific date."""
        all_users = await self.user_repository.list_all()
        return [user for user in all_users if user.created_at.date() == target_date]

    async def get_active_users(self) -> List[User]:
        """Get active users."""
        all_users = await self.user_repository.list_all()
        return [user for user in all_users if user.is_active and not user.is_blocked]

    async def get_admin_users(self) -> List[User]:
        """Get admin users."""
        all_users = await self.user_repository.list_all()
        return [user for user in all_users if user.is_admin]

    async def block_user(self, user_id: str) -> bool:
        """Block a user."""
        user = await self.user_repository.get_by_id(user_id)
        if user:
            user.is_blocked = True
            user.updated_at = datetime.now()
            await self.user_repository.update(user)
            return True
        return False

    async def unblock_user(self, user_id: str) -> bool:
        """Unblock a user."""
        user = await self.user_repository.get_by_id(user_id)
        if user:
            user.is_blocked = False
            user.updated_at = datetime.now()
            await self.user_repository.update(user)
            return True
        return False

    async def get_user_count(self) -> int:
        """Get total user count."""
        users = await self.user_repository.list_all()
        return len(users)

    async def search_users(self, query: str) -> List[User]:
        """Search users by username, first name, or last name."""
        all_users = await self.user_repository.list_all()
        query_lower = query.lower()
        
        return [
            user for user in all_users
            if (user.username and query_lower in user.username.lower()) or
               (user.first_name and query_lower in user.first_name.lower()) or
               (user.last_name and query_lower in user.last_name.lower())
        ]
