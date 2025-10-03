"""Database initialization script."""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from infrastructure.database.connection import Base
from infrastructure.database.models import *  # Import all models

# Load environment variables from .env file
load_dotenv()


async def init_database():
    """Initialize database tables."""
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/cafe_bot")
    
    engine = create_async_engine(database_url, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())