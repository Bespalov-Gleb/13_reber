"""Order service for business logic."""

from typing import List, Optional
from datetime import datetime

from domain.entities.order import Order
from domain.entities.cart import Cart
from domain.repositories.cart_repository import CartRepository
from domain.repositories.order_repository import OrderRepository
from domain.repositories.user_repository import UserRepository
from shared.constants.order_constants import OrderStatus, OrderType, PaymentMethod
from shared.types.order_types import DeliveryInfo, OrderFilters, PickupInfo
from shared.utils.helpers import generate_id


class OrderService:
    """Order service for business logic."""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        cart_repository: CartRepository,
        user_repository: UserRepository,
    ):
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.user_repository = user_repository
    
    async def _ensure_user(self, user_id_or_telegram: str | int) -> str:
        """Return internal user_id (UUID string) for given telegram id or internal id.
        Creates minimal user if not exists.
        """
        # If looks like UUID string, presume internal id
        try:
            # int conversion will fail for UUID; succeed for telegram ids
            telegram_id = int(user_id_or_telegram)
        except (TypeError, ValueError):
            return str(user_id_or_telegram)

        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if user:
            return user.user_id

        # Create minimal user
        from domain.entities.user import User
        from shared.types.user_types import UserRole, UserStatus
        from shared.utils.helpers import generate_id
        new_user = User(
            user_id=generate_id(),
            telegram_id=telegram_id,
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        created = await self.user_repository.create(new_user)
        return created.user_id

    async def create_order_from_cart(
        self,
        user_id: str,
        order_type: OrderType,
        payment_method: PaymentMethod,
        delivery_info: Optional[DeliveryInfo] = None,
        pickup_info: Optional[PickupInfo] = None,
        comment: Optional[str] = None,
    ) -> Order:
        """Create order from user's cart."""
        # Resolve to internal user id and get user's cart
        internal_user_id = await self._ensure_user(user_id)
        cart = await self.cart_repository.get_by_user_id(internal_user_id)
        if not cart or cart.is_empty():
            raise ValueError("Cart is empty")
        
        # Create order
        
        order = Order(
            order_id=generate_id(),
            user_id=internal_user_id,
            items=[],  # Will be populated from cart
            total=cart.total_price,
            status=OrderStatus.PENDING,
            order_type=order_type,
            payment_method=payment_method,
            delivery_info=delivery_info,
            pickup_info=pickup_info,
            comment=comment,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Convert cart items to order items (lookup menu_item by id)
        for cart_item in cart.get_items_list():
            from domain.entities.order_item import OrderItem
            # Lookup MenuItem via repository by id
            from domain.repositories.menu_repository import MenuRepository  # type: ignore
            # We don't have menu_repository on service; use repository from cart_repository if available
            # Simpler: use cart_item fields (name/price) directly
            order_item = OrderItem(
                order_item_id=generate_id(),
                order_id=order.order_id,
                menu_item=None,
                item_id=cart_item.item_id,
                name=cart_item.name,
                quantity=cart_item.quantity,
                price=cart_item.price,
                comment=cart_item.comment,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            order.items.append(order_item)
        
        # Save order
        return await self.order_repository.create(order)
    
    async def create_order(
        self,
        user_id: str | int,
        cart: Cart,
        order_type: str,
        payment_method: str,
        comment: Optional[str] = None,
    ) -> Order:
        """Create order from cart (simplified version)."""
        internal_user_id = await self._ensure_user(user_id)

        order = Order(
            order_id=generate_id(),
            user_id=internal_user_id,
            items=[],
            total=cart.total_price,
            status=OrderStatus.PENDING,
            order_type=OrderType(order_type),
            payment_method=PaymentMethod(payment_method),
            comment=comment,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Convert cart items to order items (no direct menu_item in CartItem)
        for cart_item in cart.get_items_list():
            from domain.entities.order_item import OrderItem
            order_item = OrderItem(
                order_item_id=generate_id(),
                order_id=order.order_id,
                menu_item=None,
                item_id=cart_item.item_id,
                name=cart_item.name,
                quantity=cart_item.quantity,
                price=cart_item.price,
                comment=cart_item.comment,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            order.items.append(order_item)
        
        # Save order
        return await self.order_repository.create(order)
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return await self.order_repository.get_by_id(order_id)
    
    async def get_user_orders(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """Get user's orders."""
        return await self.order_repository.get_by_user_id(user_id, limit, offset)
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """Update order status."""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order with id {order_id} not found")
        
        order.status = status
        order.updated_at = datetime.now()
        
        return await self.order_repository.update(order)
    
    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> Order:
        """Cancel order."""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order with id {order_id} not found")
        
        order.status = OrderStatus.CANCELLED
        order.comment = reason if reason else order.comment
        order.updated_at = datetime.now()
        
        return await self.order_repository.update(order)
    
    async def list_orders(self, filters: OrderFilters) -> List[Order]:
        """List orders with filters."""
        return await self.order_repository.list_orders(filters)
    
    async def get_orders_requiring_attention(self) -> List[Order]:
        """Get orders that require attention."""
        return await self.order_repository.get_orders_requiring_attention()
    
    async def validate_order(self, order: Order) -> bool:
        """Validate order data."""
        if not order.items:
            return False
        if order.total <= 0:
            return False
        # Add more validation rules as needed
        return True
    
    async def calculate_order_total(self, order: Order) -> int:
        """Calculate order total amount."""
        total = 0
        for item in order.items:
            total += item.price * item.quantity
        return total