"""Telegram bot creation and configuration."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import get_settings
from infrastructure.telegram.middlewares.auth_middleware import AuthMiddleware
from infrastructure.telegram.middlewares.error_middleware import ErrorMiddleware
from infrastructure.telegram.middlewares.logging_middleware import LoggingMiddleware


def create_bot(token: str) -> Bot:
    """Create and configure bot instance."""
    return Bot(
        token=token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
        )
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher."""
    dp = Dispatcher()
    
    # Register middlewares (order matters: logging -> db -> auth -> error)
    from infrastructure.telegram.middlewares.db_session_middleware import DbSessionMiddleware

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    dp.message.middleware(ErrorMiddleware())
    dp.callback_query.middleware(ErrorMiddleware())
    
    # Register handlers
    from infrastructure.telegram.handlers.start_handler import StartHandler
    from infrastructure.telegram.handlers.menu_handler import MenuHandler
    from infrastructure.telegram.handlers.cart_handler import CartHandler
    from infrastructure.telegram.handlers.order_handler import OrderHandler
    from infrastructure.telegram.handlers.payment_handler import PaymentHandler
    from infrastructure.telegram.handlers.admin_handler import AdminHandler
    from infrastructure.telegram.handlers.help_handler import HelpHandler
    
    # Create handler instances
    start_handler = StartHandler()
    menu_handler = MenuHandler()
    cart_handler = CartHandler()
    order_handler = OrderHandler()
    payment_handler = PaymentHandler()
    admin_handler = AdminHandler()
    help_handler = HelpHandler()
    
    # Include routers
    dp.include_router(start_handler.get_router())
    dp.include_router(menu_handler.get_router())
    dp.include_router(cart_handler.get_router())
    dp.include_router(order_handler.get_router())
    dp.include_router(payment_handler.get_router())
    dp.include_router(admin_handler.get_router())
    dp.include_router(help_handler.get_router())
    
    return dp