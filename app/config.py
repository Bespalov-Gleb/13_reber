"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file="cafe_bot/config.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Bot Configuration
    bot_token: str = Field(..., description="Telegram bot token")
    bot_webhook_url: str | None = Field(None, description="Webhook URL for production")
    bot_webhook_path: str = Field("/webhook", description="Webhook path")
    
    # Database Configuration
    database_url: str = Field(..., description="Database connection URL")
    database_echo: bool = Field(False, description="Enable SQLAlchemy echo")
    
    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379/0", description="Redis connection URL")
    
    # Payment Systems
    yookassa_shop_id: str | None = Field(None, description="YooKassa shop ID")
    yookassa_secret_key: str | None = Field(None, description="YooKassa secret key")
    cloudpayments_public_id: str | None = Field(None, description="CloudPayments public ID")
    cloudpayments_api_secret: str | None = Field(None, description="CloudPayments API secret")
    stripe_publishable_key: str | None = Field(None, description="Stripe publishable key")
    stripe_secret_key: str | None = Field(None, description="Stripe secret key")
    
    # Maps Services
    yandex_maps_api_key: str | None = Field(None, description="Yandex Maps API key")
    google_maps_api_key: str | None = Field(None, description="Google Maps API key")
    
    # CRM Integration
    iiko_api_url: str = Field("https://api-ru.iiko.services", description="iiko API URL")
    iiko_api_login: str | None = Field(None, description="iiko API login")
    iiko_api_password: str | None = Field(None, description="iiko API password")
    google_sheets_credentials_file: str | None = Field(None, description="Google Sheets credentials file")
    google_sheets_spreadsheet_id: str | None = Field(None, description="Google Sheets spreadsheet ID")
    
    # Admin Configuration
    admin_user_ids: List[int] = Field(default_factory=list, description="Admin user IDs")
    admin_chat_id: int | None = Field(None, description="Admin chat ID")
    
    # Cafe Configuration
    cafe_name: str = Field("Кафе", description="Cafe name")
    cafe_address: str = Field("", description="Cafe address")
    cafe_phone: str = Field("", description="Cafe phone")
    cafe_working_hours: str = Field("09:00-22:00", description="Cafe working hours")
    cafe_delivery_zone_radius: int = Field(5000, description="Delivery zone radius in meters")
    cafe_min_order_amount: int = Field(500, description="Minimum order amount in kopecks")
    
    # Logging
    log_level: str = Field("INFO", description="Log level")
    log_format: str = Field("json", description="Log format")
    
    # Security
    secret_key: str = Field(..., description="Secret key for encryption")
    webhook_secret: str | None = Field(None, description="Webhook secret for validation")
    
    # Development
    debug: bool = Field(False, description="Debug mode")
    environment: str = Field("development", description="Environment")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    # Normalize ADMIN_USER_IDS from env: supports "1,2", "[1,2]", 1
    @field_validator("admin_user_ids", mode="before")
    @classmethod
    def _normalize_admin_user_ids(cls, value):
        if value is None:
            return []
        # If already list -> return as is
        if isinstance(value, list):
            return [int(v) for v in value]
        # If single int -> wrap
        if isinstance(value, int):
            return [value]
        # If bytes -> decode
        if isinstance(value, (bytes, bytearray)):
            value = value.decode()
        if isinstance(value, str):
            s = value.strip()
            # JSON list
            if s.startswith("[") and s.endswith("]"):
                try:
                    import json
                    parsed = json.loads(s)
                    return [int(v) for v in parsed]
                except Exception:
                    pass
            # Comma-separated
            parts = [p for p in (x.strip() for x in s.split(",")) if p]
            if parts:
                return [int(p) for p in parts]
            # Fallback: single numeric string
            try:
                return [int(s)]
            except Exception:
                return []
        # Fallback
        return []


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()