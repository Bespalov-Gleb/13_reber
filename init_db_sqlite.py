"""Database initialization script with SQLite for testing."""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from infrastructure.database.connection import Base
from infrastructure.database.models import *  # Import all models


async def init_database():
    """Initialize database tables with SQLite."""
    # Use SQLite for testing
    database_url = "sqlite+aiosqlite:///./cafe_bot_test.db"
    
    engine = create_async_engine(database_url, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("SQLite database initialized successfully!")
    print("Database file: cafe_bot_test.db")


if __name__ == "__main__":
    asyncio.run(init_database())