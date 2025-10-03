"""Database connection and session management."""

from typing import AsyncGenerator, Optional
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Global engine and session maker
_engine = None
_session_maker = None
_session_ctx: ContextVar[Optional[AsyncSession]] = ContextVar("db_async_session", default=None)


async def init_database(database_url: str) -> None:
    """Initialize database connection."""
    global _engine, _session_maker
    
    _engine = create_async_engine(
        database_url,
        echo=get_settings().database_echo,
        future=True,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    _session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with _session_maker() as session:
        try:
            token: Token[Optional[AsyncSession]] = _session_ctx.set(session)
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            # reset contextvar and close
            _session_ctx.reset(token)
            await session.close()


async def close_database() -> None:
    """Close database connection."""
    global _engine
    if _engine:
        await _engine.dispose()


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Expose configured sessionmaker.
    Raises if database wasn't initialized yet.
    """
    if _session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _session_maker


def set_current_session(session: AsyncSession) -> Token[Optional[AsyncSession]]:
    """Put session into context and return reset token."""
    return _session_ctx.set(session)


def get_current_session() -> Optional[AsyncSession]:
    """Get session from context set by middleware."""
    return _session_ctx.get()