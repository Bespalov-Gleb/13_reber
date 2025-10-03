"""Error handling middleware for Telegram handlers."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import CallbackQuery, Message

from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """Middleware for handling errors in Telegram handlers."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Handle errors in event processing."""
        
        try:
            return await handler(event, data)
            
        except TelegramBadRequest as e:
            logger.error(
                "Telegram bad request error",
                error=str(e),
                user_id=getattr(event.from_user, "id", None),
                chat_id=getattr(event.chat, "id", None) if hasattr(event, "chat") else None
            )
            
            # Try to send error message to user
            try:
                if isinstance(event, Message):
                    await event.answer("❌ Произошла ошибка при обработке запроса. Попробуйте еще раз.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Произошла ошибка. Попробуйте еще раз.", show_alert=True)
            except Exception:
                pass  # Ignore errors when sending error messages
                
        except TelegramForbiddenError as e:
            logger.error(
                "Telegram forbidden error - bot blocked by user",
                error=str(e),
                user_id=getattr(event.from_user, "id", None)
            )
            # Don't try to send message to blocked user
            
        except Exception as e:
            logger.error(
                "Unexpected error in handler",
                error=str(e),
                error_type=type(e).__name__,
                user_id=getattr(event.from_user, "id", None),
                exc_info=True
            )
            
            # Try to send generic error message to user
            try:
                if isinstance(event, Message):
                    await event.answer("❌ Произошла внутренняя ошибка. Обратитесь к администратору.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("❌ Произошла ошибка. Обратитесь к администратору.", show_alert=True)
            except Exception:
                pass  # Ignore errors when sending error messages