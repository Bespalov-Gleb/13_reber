"""Dependency injection container."""

from typing import Annotated

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from domain.repositories.cart_repository import CartRepository
from domain.repositories.menu_repository import MenuRepository
from domain.repositories.order_repository import OrderRepository
from domain.repositories.payment_repository import PaymentRepository
from domain.repositories.user_repository import UserRepository
from domain.services.cart_service import CartService
from domain.services.menu_service import MenuService
from domain.services.order_service import OrderService
from domain.services.payment_service import PaymentService
from domain.services.statistics_service import StatisticsService
from domain.services.user_service import UserService
from infrastructure.database.connection import get_session, get_current_session
from infrastructure.database.repositories.cart_repository_impl import CartRepositoryImpl
from infrastructure.database.repositories.menu_repository_impl import MenuRepositoryImpl
from infrastructure.database.repositories.order_repository_impl import OrderRepositoryImpl
from infrastructure.database.repositories.payment_repository_impl import PaymentRepositoryImpl
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl


class DIContainer:
    """Dependency injection container."""
    
    def __init__(self):
        self._settings = get_settings()
        self._bot: Bot | None = None
        self._dispatcher: Dispatcher | None = None
    
    @property
    def settings(self):
        """Get settings."""
        return self._settings
    
    @property
    def bot(self) -> Bot:
        """Get bot instance."""
        if self._bot is None:
            from infrastructure.telegram.bot import create_bot
            self._bot = create_bot(self._settings.bot_token)
        return self._bot
    
    @property
    def dispatcher(self) -> Dispatcher:
        """Get dispatcher instance."""
        if self._dispatcher is None:
            from infrastructure.telegram.bot import create_dispatcher
            self._dispatcher = create_dispatcher()
        return self._dispatcher
    
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Get user repository."""
        return UserRepositoryImpl(session)
    
    def get_menu_repository(self, session: AsyncSession) -> MenuRepository:
        """Get menu repository."""
        return MenuRepositoryImpl(session)
    
    def get_cart_repository(self, session: AsyncSession) -> CartRepository:
        """Get cart repository."""
        return CartRepositoryImpl(session)
    
    def get_order_repository(self, session: AsyncSession) -> OrderRepository:
        """Get order repository."""
        return OrderRepositoryImpl(session)
    
    def get_payment_repository(self, session: AsyncSession) -> PaymentRepository:
        """Get payment repository."""
        return PaymentRepositoryImpl(session)
    
    def get_menu_service(self, session: AsyncSession) -> MenuService:
        """Get menu service."""
        menu_repo = self.get_menu_repository(session)
        return MenuService(menu_repo)
    
    def get_cart_service(self, session: AsyncSession) -> CartService:
        """Get cart service."""
        cart_repo = self.get_cart_repository(session)
        menu_repo = self.get_menu_repository(session)
        user_repo = self.get_user_repository(session)
        return CartService(cart_repo, menu_repo, user_repo)

    def get_order_service(self, session: AsyncSession) -> OrderService:
        """Get order service."""
        order_repo = self.get_order_repository(session)
        cart_repo = self.get_cart_repository(session)
        user_repo = self.get_user_repository(session)
        return OrderService(order_repo, cart_repo, user_repo)

    def get_payment_service(self, session: AsyncSession) -> PaymentService:
        """Get payment service."""
        payment_repo = self.get_payment_repository(session)
        order_repo = self.get_order_repository(session)
        # TODO: Initialize payment integration
        from infrastructure.external.payment.yookassa_payment import YooKassaPaymentIntegration
        payment_integration = YooKassaPaymentIntegration(
            shop_id="test_shop_id",
            secret_key="test_secret_key",
            test_mode=True
        )
        return PaymentService(payment_repo, order_repo, payment_integration)
    
    def get_statistics_service(self, session: AsyncSession) -> StatisticsService:
        """Get statistics service."""
        order_repo = self.get_order_repository(session)
        user_repo = self.get_user_repository(session)
        menu_repo = self.get_menu_repository(session)
        return StatisticsService(order_repo, user_repo, menu_repo)
    
    def get_user_service(self, session: AsyncSession) -> UserService:
        """Get user service."""
        user_repo = self.get_user_repository(session)
        return UserService(user_repo)


# Global container instance
container = DIContainer()


# Service getters
async def get_menu_service(data: dict | None = None) -> MenuService:
    """Get menu service bound to current request session.
    Prefer session from middleware; as fallback use one provided in `data`.
    """
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        # Last resort: open maker directly (kept for backward compatibility)
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_menu_service(session)  # type: ignore[arg-type]


async def get_cart_service(data: dict | None = None) -> CartService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_cart_service(session)  # type: ignore[arg-type]


async def get_order_service(data: dict | None = None) -> OrderService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_order_service(session)  # type: ignore[arg-type]


async def get_payment_service(data: dict | None = None) -> PaymentService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_payment_service(session)  # type: ignore[arg-type]


async def get_statistics_service(data: dict | None = None) -> StatisticsService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_statistics_service(session)  # type: ignore[arg-type]


async def get_user_service(data: dict | None = None) -> UserService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_user_service(session)  # type: ignore[arg-type]


# Dependency annotations for FastAPI-style dependency injection
def get_container() -> DIContainer:
    """Get DI container."""
    return container


def get_db_session() -> AsyncSession:
    """Get database session."""
    return get_session()


def get_user_repo(session: Annotated[AsyncSession, get_db_session]) -> UserRepository:
    """Get user repository."""
    return container.get_user_repository(session)


def get_menu_repo(session: Annotated[AsyncSession, get_db_session]) -> MenuRepository:
    """Get menu repository."""
    return container.get_menu_repository(session)


def get_cart_repo(session: Annotated[AsyncSession, get_db_session]) -> CartRepository:
    """Get cart repository."""
    return container.get_cart_repository(session)


def get_order_repo(session: Annotated[AsyncSession, get_db_session]) -> OrderRepository:
    """Get order repository."""
    return container.get_order_repository(session)


def get_payment_repo(session: Annotated[AsyncSession, get_db_session]) -> PaymentRepository:
    """Get payment repository."""
    return container.get_payment_repository(session)

