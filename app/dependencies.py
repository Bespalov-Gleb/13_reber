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
from domain.services.notification_service import NotificationService
from domain.services.order_service import OrderService
from domain.services.payment_service import PaymentService
from domain.services.statistics_service import StatisticsService
from domain.services.user_service import UserService
from domain.services.order_state_service import OrderStateService
from domain.services.promotion_service import PromotionService
from domain.services.review_service import ReviewService
from domain.services.booking_service import BookingService
from domain.services.iiko_sync_service import IikoSyncService
from infrastructure.external.maps.yandex_maps import YandexMapsProvider
from infrastructure.database.connection import get_session, get_current_session
from infrastructure.database.repositories.cart_repository_impl import CartRepositoryImpl
from infrastructure.database.repositories.menu_repository_impl import MenuRepositoryImpl
from infrastructure.database.repositories.order_repository_impl import OrderRepositoryImpl
from infrastructure.database.repositories.payment_repository_impl import PaymentRepositoryImpl
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.database.repositories.promotion_repository_impl import PromotionRepositoryImpl
from infrastructure.database.repositories.review_repository_impl import ReviewRepositoryImpl
from infrastructure.database.repositories.booking_repository_impl import BookingRepositoryImpl
from infrastructure.external.crm.iiko_integration import IikoCRMProvider


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
    
    def get_promotion_repository(self, session: AsyncSession) -> "PromotionRepository":
        """Get promotion repository."""
        from domain.repositories.promotion_repository import PromotionRepository
        return PromotionRepositoryImpl(session)
    
    def get_review_repository(self, session: AsyncSession) -> "ReviewRepository":
        """Get review repository."""
        from domain.repositories.review_repository import ReviewRepository
        return ReviewRepositoryImpl(session)
    
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
        
        # Initialize payment integration based on settings
        settings = self.settings
        if settings.yookassa_shop_id and settings.yookassa_secret_key:
            from infrastructure.external.payment.yookassa_payment import YooKassaPaymentIntegration
            payment_integration = YooKassaPaymentIntegration(
                shop_id=settings.yookassa_shop_id,
                secret_key=settings.yookassa_secret_key,
                test_mode=not settings.is_production
            )
        elif settings.cloudpayments_public_id and settings.cloudpayments_api_secret:
            from infrastructure.external.payment.cloudpayments_payment import CloudPaymentsPaymentIntegration
            payment_integration = CloudPaymentsPaymentIntegration(
                public_id=settings.cloudpayments_public_id,
                api_secret=settings.cloudpayments_api_secret,
                test_mode=not settings.is_production
            )
        else:
            # Fallback to test YooKassa if no payment system configured
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
    
    def get_promotion_service(self, session: AsyncSession) -> PromotionService:
        """Get promotion service."""
        promotion_repo = self.get_promotion_repository(session)
        return PromotionService(promotion_repo)
    
    def get_review_service(self, session: AsyncSession) -> ReviewService:
        """Get review service."""
        review_repo = self.get_review_repository(session)
        return ReviewService(review_repo)
    
    def get_booking_repository(self, session: AsyncSession) -> "BookingRepository":
        """Get booking repository."""
        from domain.repositories.booking_repository import BookingRepository
        return BookingRepositoryImpl(session)
    
    def get_booking_service(self, session: AsyncSession) -> BookingService:
        """Get booking service."""
        booking_repo = self.get_booking_repository(session)
        return BookingService(booking_repo)
    
    def get_iiko_provider(self) -> IikoCRMProvider:
        """Get iiko CRM provider."""
        return IikoCRMProvider(
            api_url=self.settings.iiko_api_url,
            api_login=self.settings.iiko_api_login,
            organization_id=self.settings.iiko_organization_id
        )
    
    def get_iiko_sync_service(self, session: AsyncSession) -> IikoSyncService:
        """Get iiko sync service."""
        menu_repo = self.get_menu_repository(session)
        menu_service = self.get_menu_service(session)
        iiko_provider = self.get_iiko_provider()
        return IikoSyncService(menu_repo, menu_service, iiko_provider)
    
    def get_notification_service(self, session: AsyncSession) -> NotificationService:
        """Get notification service."""
        return NotificationService(self.bot)
    
    def get_order_state_service(self) -> OrderStateService:
        """Get order state service."""
        from domain.services.order_state_service import order_state_service
        return order_state_service
    
    def get_maps_service(self) -> YandexMapsProvider:
        """Get maps service."""
        settings = get_settings()
        geocoder_key = settings.yandex_geocoder_api_key or settings.yandex_maps_api_key
        suggest_key = settings.yandex_suggest_api_key or settings.yandex_maps_api_key
        if not geocoder_key:
            raise ValueError("Yandex Geocoder API key not configured")
        # Suggest can use dedicated key, with fallback to geocoder/general key.
        return YandexMapsProvider(geocoder_api_key=geocoder_key, suggest_api_key=suggest_key)


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


async def get_promotion_service(data: dict | None = None) -> PromotionService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_promotion_service(session)  # type: ignore[arg-type]


async def get_review_service(data: dict | None = None) -> ReviewService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_review_service(session)  # type: ignore[arg-type]


async def get_notification_service(data: dict | None = None) -> NotificationService:
    """Get notification service bound to current request session."""
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_notification_service(session)  # type: ignore[arg-type]


async def get_booking_service(data: dict | None = None) -> BookingService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_booking_service(session)  # type: ignore[arg-type]


async def get_iiko_sync_service(data: dict | None = None) -> IikoSyncService:
    session = None
    if data and isinstance(data, dict):
        session = data.get("session")
    if session is None:
        session = get_current_session()
    if session is None:
        from infrastructure.database.connection import get_sessionmaker
        session = get_sessionmaker()()
    return container.get_iiko_sync_service(session)  # type: ignore[arg-type]


async def get_order_state_service() -> OrderStateService:
    """Get order state service."""
    return container.get_order_state_service()


async def get_maps_service() -> YandexMapsProvider:
    """Get maps service."""
    return container.get_maps_service()


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

