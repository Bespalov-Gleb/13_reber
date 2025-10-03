"""Authentication middleware for Telegram handlers."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication and authorization."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Process authentication for incoming events."""
        
        settings = get_settings()
        
        # Extract user information
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)
        
        if not user:
            logger.warning("Event without user information", event_type=type(event).__name__)
            return await handler(event, data)
        
        # Check if user is admin
        is_admin = user.id in settings.admin_user_ids
        
        # Add user context to data
        data["user"] = user
        data["is_admin"] = is_admin
        data["user_id"] = user.id
        
        logger.debug(
            "User authenticated",
            user_id=user.id,
            username=user.username,
            is_admin=is_admin
        )
        
        return await handler(event, data=data)