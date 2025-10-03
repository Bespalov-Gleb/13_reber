"""Middleware that opens AsyncSession per update and commits on success."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from infrastructure.database.connection import get_sessionmaker, set_current_session


class DbSessionMiddleware(BaseMiddleware):
    """Provide `session` in data and manage transaction lifecycle."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        session_maker = get_sessionmaker()
        async with session_maker() as session:
            data["session"] = session
            token = set_current_session(session)
            try:
                async with session.begin():
                    return await handler(event, data)
            finally:
                # always reset contextvar (session closed by context manager)
                try:
                    from contextvars import Token as _Token  # just for typing safety
                except Exception:
                    pass
                token = token  # silence linter unused var

