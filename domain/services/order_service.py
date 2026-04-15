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
        send_to_iiko: bool = True,
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
        saved_order = await self.order_repository.create(order)
        
        # Log to Google Sheets
        await self._log_order_to_sheets(saved_order)
        
        # Send to iiko if enabled
        if send_to_iiko:
            await self._send_order_to_iiko(saved_order)
        
        return saved_order
    
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
        
        old_status = order.status.value
        order.status = status
        order.updated_at = datetime.now()
        
        updated_order = await self.order_repository.update(order)
        
        # Log status change to Google Sheets
        await self._log_status_change_to_sheets(order_id, old_status, status.value)
        
        # Send review request for completed orders
        if status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP]:
            await self._send_review_request(updated_order)
        
        return updated_order
    
    async def update_order(self, order_id: str, **kwargs) -> Order:
        """Update order fields."""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order with id {order_id} not found")
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        
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
    
    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Get orders by status."""
        from shared.constants.order_constants import OrderStatus
        try:
            order_status = OrderStatus(status)
        except ValueError:
            return []
        return await self.order_repository.get_orders_by_status(order_status)
    
    async def get_orders_by_user_id(self, user_id: str) -> List[Order]:
        """Get orders by user ID."""
        return await self.order_repository.get_orders_by_user_id(user_id)
    
    async def _log_order_to_sheets(self, order: Order) -> None:
        """Log order to Google Sheets."""
        try:
            from app.config import get_settings
            settings = get_settings()
            
            if not settings.google_sheets_credentials_file or not settings.google_sheets_spreadsheet_id:
                return
            
            from infrastructure.external.crm.google_sheets import GoogleSheetsIntegration
            
            sheets = GoogleSheetsIntegration(
                credentials_file=settings.google_sheets_credentials_file,
                spreadsheet_id=settings.google_sheets_spreadsheet_id
            )
            
            # Get user info
            user = await self.user_repository.get_by_id(order.user_id)
            
            # Prepare order data
            order_data = {
                "order_id": order.order_id,
                "user_id": order.user_id,
                "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() if user else "",
                "user_phone": user.phone if user else "",
                "user_telegram_id": user.telegram_id if user else "",
                "order_type": order.order_type.value,
                "payment_method": order.payment_method.value,
                "status": order.status.value,
                "total_amount": order.total,
                "items_count": len(order.items),
                "delivery_address": order.delivery_info.address if order.delivery_info else "",
                "delivery_phone": order.delivery_info.phone if order.delivery_info else "",
                "comment": order.comment or "",
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat()
            }
            
            await sheets.log_order(order_data)
            
        except Exception as e:
            print(f"❌ Failed to log order to Google Sheets: {e}")
    
    async def _log_status_change_to_sheets(self, order_id: str, old_status: str, new_status: str) -> None:
        """Log order status change to Google Sheets."""
        try:
            from app.config import get_settings
            settings = get_settings()
            
            if not settings.google_sheets_credentials_file or not settings.google_sheets_spreadsheet_id:
                return
            
            from infrastructure.external.crm.google_sheets import GoogleSheetsIntegration
            
            sheets = GoogleSheetsIntegration(
                credentials_file=settings.google_sheets_credentials_file,
                spreadsheet_id=settings.google_sheets_spreadsheet_id
            )
            
            await sheets.log_order_status_change(
                order_id=order_id,
                old_status=old_status,
                new_status=new_status,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"❌ Failed to log status change to Google Sheets: {e}")
    
    async def _send_review_request(self, order: Order) -> None:
        """Send review request notification."""
        try:
            # Get user info
            user = await self.user_repository.get_by_id(order.user_id)
            if not user:
                return
            
            # Get notification service
            from app.dependencies import get_notification_service
            notification_service = await get_notification_service()
            
            # Send review request
            await notification_service.send_review_request_notification(order, user)
            
        except Exception as e:
            print(f"❌ Failed to send review request: {e}")
    
    async def _send_order_to_iiko(self, order: Order) -> None:
        """Send order to iiko system."""
        try:
            from app.dependencies import get_iiko_sync_service
            
            sync_service = await get_iiko_sync_service()
            if sync_service:
                success = await sync_service.send_order_to_iiko(order)
                if success:
                    print(f"✅ Order {order.order_id} sent to iiko successfully")
                else:
                    print(f"❌ Failed to send order {order.order_id} to iiko")
            else:
                print("⚠️ iiko sync service not available")
                
        except Exception as e:
            print(f"❌ Failed to send order to iiko: {e}")