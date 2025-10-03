"""Base handler class for Telegram."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from infrastructure.logging.logger import get_logger


class BaseHandler(ABC):
    """Base handler class for Telegram handlers."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.router = Router()
        self._register_handlers()
    
    @abstractmethod
    def _register_handlers(self) -> None:
        """Register handlers for this router."""
        pass
    
    async def handle_message(self, message: Message, data: Dict[str, Any]) -> None:
        """Handle incoming message."""
        self.logger.info(
            "Handling message",
            user_id=data.get("user_id"),
            message_text=message.text,
            handler=self.__class__.__name__
        )
    
    async def handle_callback(self, callback: CallbackQuery, data: Dict[str, Any]) -> None:
        """Handle incoming callback query."""
        self.logger.info(
            "Handling callback",
            user_id=data.get("user_id"),
            callback_data=callback.data,
            handler=self.__class__.__name__
        )
    
    def get_router(self) -> Router:
        """Get router for this handler."""
        return self.router

    async def safe_edit_message(self, message: Message, text: str, reply_markup=None) -> None:
        """Safely edit a message text or caption; fallback to delete+send if needed."""
        try:
            await message.edit_text(text=text, reply_markup=reply_markup)
            return
        except TelegramBadRequest as e:
            # When original message has no text (e.g., photo with caption), try editing caption
            try:
                await message.edit_caption(caption=text, reply_markup=reply_markup)
                return
            except Exception:
                pass
            # Fallback: delete and send a new text message
            try:
                await message.delete()
            except Exception:
                pass
            await message.answer(text=text, reply_markup=reply_markup)

    async def replace_with_text_message(self, message: Message, text: str, reply_markup=None) -> None:
        """Always replace current message with a fresh text message (no media kept)."""
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text=text, reply_markup=reply_markup)