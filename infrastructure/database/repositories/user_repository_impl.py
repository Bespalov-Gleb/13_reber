"""User repository implementation."""

from typing import List, Optional
from datetime import datetime

from domain.entities.user import User
from shared.types.user_types import UserRole, UserStatus
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models.user_model import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


class UserRepositoryImpl(UserRepository):
    """User repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create new user."""
        db_user = UserModel(
            id=user.user_id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
            status=user.status.value if isinstance(user.status, UserStatus) else str(user.status),
            created_at=user.created_at or datetime.now(),
            updated_at=user.updated_at or datetime.now()
        )
        
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        
        return self._model_to_entity(db_user)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return self._model_to_entity(db_user)
        return None
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return self._model_to_entity(db_user)
        return None
    
    async def update(self, user: User) -> User:
        """Update user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.user_id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise ValueError(f"User with id {user.user_id} not found")
        
        db_user.username = user.username
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.phone = user.phone
        db_user.role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        db_user.status = user.status.value if isinstance(user.status, UserStatus) else str(user.status)
        db_user.updated_at = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(db_user)
        
        return self._model_to_entity(db_user)
    
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return False
        
        await self.session.delete(db_user)
        await self.session.flush()
        return True
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users."""
        result = await self.session.execute(
            select(UserModel)
            .offset(offset)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        db_users = result.scalars().all()
        
        return [self._model_to_entity(user) for user in db_users]
    
    async def get_admins(self) -> List[User]:
        """Get all admin users."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.is_admin == True)
        )
        db_users = result.scalars().all()
        
        return [self._model_to_entity(user) for user in db_users]
    
    async def count(self) -> int:
        """Get total user count."""
        result = await self.session.execute(
            select(func.count(UserModel.id))
        )
        return result.scalar() or 0
    
    def _model_to_entity(self, db_user: UserModel) -> User:
        """Convert UserModel to User entity."""
        role = UserRole(db_user.role) if isinstance(db_user.role, str) else db_user.role
        status = UserStatus(db_user.status) if isinstance(db_user.status, str) else db_user.status
        return User(
            user_id=db_user.id,
            telegram_id=db_user.telegram_id,
            username=db_user.username,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            phone=db_user.phone,
            role=role,
            status=status,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def list_all(self) -> List[User]:
        """List all users without pagination."""
        result = await self.session.execute(select(UserModel))
        db_users = result.scalars().all()
        return [self._model_to_entity(db_user) for db_user in db_users]
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return self._model_to_entity(db_user)
        return None