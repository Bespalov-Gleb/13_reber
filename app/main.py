"""Main application entry point."""

import asyncio
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from app.config import get_settings
from infrastructure.database.connection import init_database
from infrastructure.logging.logger import setup_logging
from infrastructure.telegram.bot import create_bot, create_dispatcher
# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: web.Application):
    """Application lifespan manager."""
    settings = get_settings()

    # Setup logging
    setup_logging(settings.log_level, settings.log_format)
    logger = logging.getLogger(__name__)

    # Initialize database
    await init_database(settings.database_url)
    logger.info("Database initialized")

    # Initialize bot
    bot = create_bot(settings.bot_token)
    dp = create_dispatcher()

    # Setup webhook if in production
    if settings.is_production and settings.bot_webhook_url:
        webhook_url = f"{settings.bot_webhook_url}{settings.bot_webhook_path}"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret
        )
        logger.info(f"Webhook set to {webhook_url}")

    # Store bot and dispatcher in app context
    app["bot"] = bot
    app["dispatcher"] = dp

    logger.info("Application started")

    yield

    # Cleanup
    if settings.is_production and settings.bot_webhook_url:
        await bot.delete_webhook()
        logger.info("Webhook deleted")

    await bot.session.close()
    logger.info("Application stopped")


async def health_check(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({"status": "ok", "service": "cafe-bot"})


def create_app() -> web.Application:
    """Create and configure web application."""
    settings = get_settings()

    app = web.Application()
    app.router.add_get("/health", health_check)

    # Setup webhook handler if in production
    if settings.is_production and settings.bot_webhook_url:
        bot = app["bot"]
        dp = app["dispatcher"]

        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.webhook_secret
        )
        webhook_handler.register(app, path=settings.bot_webhook_path)

    return app


async def main():
    """Main function."""
    settings = get_settings()

    if settings.is_production:
        # Production mode with webhook
        app = create_app()
        setup_application(app, app["dispatcher"], bot=app["bot"])

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", 8000)
        await site.start()

        print("Bot started in production mode with webhook")
        print(f"Webhook URL: {settings.bot_webhook_url}{settings.bot_webhook_path}")

        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            pass
        finally:
            await runner.cleanup()
    else:
        # Development mode with polling
        bot = create_bot(settings.bot_token)
        dp = create_dispatcher()

        # Initialize database
        await init_database(settings.database_url)

        print("Bot started in development mode with polling")

        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            pass
        finally:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
