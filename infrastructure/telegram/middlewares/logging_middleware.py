"""Logging middleware for Telegram handlers."""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging incoming events."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Log incoming events."""
        
        start_time = time.time()
        
        # Extract event information
        if isinstance(event, Message):
            event_type = "message"
            event_data = {
                "text": event.text,
                "chat_id": event.chat.id,
                "message_id": event.message_id,
            }
        elif isinstance(event, CallbackQuery):
            event_type = "callback_query"
            event_data = {
                "data": event.data,
                "chat_id": event.message.chat.id if event.message else None,
                "message_id": event.message.message_id if event.message else None,
            }
        else:
            event_type = "unknown"
            event_data = {}
        
        # Log incoming event
        logger.info(
            "Incoming event",
            event_type=event_type,
            user_id=getattr(event.from_user, "id", None),
            username=getattr(event.from_user, "username", None),
            **event_data
        )
        
        try:
            # Process event
            result = await handler(event, data)
            
            # Log successful processing
            processing_time = time.time() - start_time
            logger.info(
                "Event processed successfully",
                event_type=event_type,
                processing_time=processing_time,
                user_id=getattr(event.from_user, "id", None)
            )
            
            return result
            
        except Exception as e:
            # Log error
            processing_time = time.time() - start_time
            logger.error(
                "Event processing failed",
                event_type=event_type,
                error=str(e),
                error_type=type(e).__name__,
                processing_time=processing_time,
                user_id=getattr(event.from_user, "id", None),
                exc_info=True
            )
            raise