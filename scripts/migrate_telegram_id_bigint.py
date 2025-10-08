"""One-off migration: convert users.telegram_id to BIGINT.

Usage (from repo root):
  python cafe_bot/scripts/migrate_telegram_id_bigint.py

Reads DB URL from app settings (cafe_bot/config.env).
Idempotent: skips if the column is already BIGINT.
"""

import asyncio
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.config import get_settings
from pydantic import ValidationError
import os
from pathlib import Path


def _load_db_url_fallback() -> str | None:
    # 1) ENV var
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    # 2) Parse cafe_bot/config.env manually
    env_path = Path(__file__).resolve().parents[1] / "config.env"
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    if key.strip().lower() == "database_url":
                        return val.strip().strip('"').strip("'")
    return None


async def migrate() -> None:
    try:
        settings = get_settings()
        db_url = settings.database_url
    except ValidationError:
        db_url = _load_db_url_fallback()
        if not db_url:
            raise RuntimeError(
                "DATABASE_URL not found. Set env var DATABASE_URL or fill cafe_bot/config.env with database_url=..."
            )

    engine = create_async_engine(db_url, future=True)
    async with engine.begin() as conn:
        # Detect current data type
        check_sql = text(
            """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'telegram_id'
            """
        )
        result = await conn.execute(check_sql)
        row = result.first()
        current_type: Optional[str] = row[0] if row else None

        if current_type and current_type.lower() in ("bigint", "int8"):
            print("users.telegram_id is already BIGINT — nothing to do")
            return

        # Perform migration
        print("Altering users.telegram_id to BIGINT ...")
        alter_sql = text(
            "ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT USING telegram_id::bigint;"
        )
        await conn.execute(alter_sql)
        print("Done")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate())


