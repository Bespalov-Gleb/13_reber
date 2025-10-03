"""Order repository implementation."""

from datetime import datetime
from typing import List, Optional

from domain.entities.order import Order, OrderItem
from domain.entities.menu_item import MenuItem
from domain.repositories.order_repository import OrderRepository
from infrastructure.database.models.order_model import OrderModel
from infrastructure.database.models.menu_item_model import MenuItemModel
from shared.constants.order_constants import OrderStatus, OrderType, PaymentStatus, PaymentMethod
from shared.types.order_types import OrderFilters
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload


class OrderRepositoryImpl(OrderRepository):
    """Order repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, order: Order) -> Order:
        """Create new order."""
        # Prepare JSON items snapshot
        items_json = []
        for it in order.items:
            items_json.append({
                "item_id": it.item_id or getattr(it.menu_item, "item_id", None),
                "name": it.name or getattr(it.menu_item, "name", None),
                "price": it.price,
                "quantity": it.quantity,
                "comment": it.comment,
            })

        db_order = OrderModel(
            id=order.order_id,
            user_id=order.user_id,
            total=order.total,
            status=order.status.value,
            order_type=order.order_type.value,
            payment_method=order.payment_method.value,
            payment_status=order.payment_status.value if order.payment_status else None,
            delivery_address=order.delivery_info.address if order.delivery_info else None,
            delivery_phone=order.delivery_info.phone if order.delivery_info else None,
            items=items_json,
            comment=order.comment,
            created_at=order.created_at or datetime.now(),
            updated_at=order.updated_at or datetime.now()
        )
        
        self.session.add(db_order)
        await self.session.flush()  # Get the ID
        
        # Items are already stored as JSON in OrderModel
        
        await self.session.flush()
        await self.session.refresh(db_order)
        
        return await self.get_by_id(db_order.id)
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id)
        )
        db_order = result.scalar_one_or_none()
        
        if db_order:
            return self._model_to_entity(db_order)
        return None
    
    async def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Order]:
        """Get orders by user ID."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def update(self, order: Order) -> Order:
        """Update order."""
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order.order_id)
        )
        db_order = result.scalar_one_or_none()
        
        if not db_order:
            raise ValueError(f"Order with id {order.order_id} not found")
        
        db_order.total = order.total
        db_order.status = order.status.value
        db_order.payment_status = order.payment_status.value if order.payment_status else None
        db_order.delivery_address = order.delivery_info.address if order.delivery_info else None
        db_order.delivery_phone = order.delivery_info.phone if order.delivery_info else None
        db_order.pickup_phone = order.pickup_info.phone if order.pickup_info else None
        db_order.comment = order.comment
        db_order.updated_at = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(db_order)
        
        return await self.get_by_id(db_order.id)
    
    async def delete(self, order_id: str) -> bool:
        """Delete order."""
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        db_order = result.scalar_one_or_none()
        
        if not db_order:
            return False
        
        await self.session.delete(db_order)
        await self.session.flush()
        return True
    
    async def list_orders(self, filters: OrderFilters) -> List[Order]:
        """List orders with filters."""
        query = select(OrderModel).options(
        )
        
        conditions = []
        
        if filters.status:
            conditions.append(OrderModel.status == filters.status.value)
        
        if filters.order_type:
            conditions.append(OrderModel.order_type == filters.order_type.value)
        
        if filters.payment_status:
            conditions.append(OrderModel.payment_status == filters.payment_status.value)
        
        if filters.user_id:
            conditions.append(OrderModel.user_id == filters.user_id)
        
        if filters.date_from:
            conditions.append(OrderModel.created_at >= filters.date_from)
        
        if filters.date_to:
            conditions.append(OrderModel.created_at <= filters.date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(OrderModel.created_at.desc())
        
        if filters.limit:
            query = query.limit(filters.limit)
        
        if filters.offset:
            query = query.offset(filters.offset)
        
        result = await self.session.execute(query)
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def get_orders_by_status(self, status: OrderStatus, limit: int = 100, offset: int = 0) -> List[Order]:
        """Get orders by status."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.status == status.value)
            .order_by(OrderModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def get_orders_by_type(self, order_type: OrderType, limit: int = 100, offset: int = 0) -> List[Order]:
        """Get orders by type."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.order_type == order_type.value)
            .order_by(OrderModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def get_orders_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Get orders by date range."""
        result = await self.session.execute(
            select(OrderModel)
            .where(
                and_(
                    OrderModel.created_at >= start_date,
                    OrderModel.created_at <= end_date
                )
            )
            .order_by(OrderModel.created_at.desc())
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def get_orders_by_payment_status(self, payment_status: PaymentStatus) -> List[Order]:
        """Get orders by payment status."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.payment_status == payment_status.value)
            .order_by(OrderModel.created_at.desc())
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def count_orders(self, filters: Optional[OrderFilters] = None) -> int:
        """Count orders with optional filters."""
        query = select(func.count(OrderModel.id))
        
        if filters:
            conditions = []
            
            if filters.status:
                conditions.append(OrderModel.status == filters.status.value)
            
            if filters.order_type:
                conditions.append(OrderModel.order_type == filters.order_type.value)
            
            if filters.payment_status:
                conditions.append(OrderModel.payment_status == filters.payment_status.value)
            
            if filters.user_id:
                conditions.append(OrderModel.user_id == filters.user_id)
            
            if filters.date_from:
                conditions.append(OrderModel.created_at >= filters.date_from)
            
            if filters.date_to:
                conditions.append(OrderModel.created_at <= filters.date_to)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def get_user_order_count(self, user_id: str) -> int:
        """Get user's order count."""
        result = await self.session.execute(
            select(func.count(OrderModel.id)).where(OrderModel.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def get_user_total_spent(self, user_id: str) -> int:
        """Get user's total spent amount."""
        result = await self.session.execute(
            select(func.sum(OrderModel.total)).where(OrderModel.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def get_orders_requiring_attention(self) -> List[Order]:
        """Get orders that require attention (pending, preparing, etc.)."""
        result = await self.session.execute(
            select(OrderModel)
            .where(
                OrderModel.status.in_([
                    OrderStatus.PENDING.value,
                    OrderStatus.CONFIRMED.value,
                    OrderStatus.PREPARING.value,
                    OrderStatus.READY.value
                ])
            )
            .order_by(OrderModel.created_at.asc())
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def get_delivery_orders(self) -> List[Order]:
        """Get orders for delivery."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.order_type == OrderType.DELIVERY.value)
            .order_by(OrderModel.created_at.desc())
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    async def get_pickup_orders(self) -> List[Order]:
        """Get orders for pickup."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.order_type == OrderType.PICKUP.value)
            .order_by(OrderModel.created_at.desc())
        )
        db_orders = result.scalars().all()
        
        return [self._model_to_entity(order) for order in db_orders]
    
    def _model_to_entity(self, db_order: OrderModel) -> Order:
        """Convert OrderModel to Order entity."""
        order_items = []
        for obj in (db_order.items or []):
            # obj is dict serialized above
            from domain.entities.order_item import OrderItem
            order_item = OrderItem(
                order_item_id="",  # not persisted separately in JSON
                order_id=db_order.id,
                menu_item=None,
                item_id=obj.get("item_id"),
                name=obj.get("name"),
                quantity=int(obj.get("quantity", 0)),
                price=int(obj.get("price", 0)),
                comment=obj.get("comment")
            )
            order_items.append(order_item)
        
        # Create delivery/pickup info
        delivery_info = None
        pickup_info = None
        
        if db_order.order_type == OrderType.DELIVERY.value and db_order.delivery_address:
            from shared.types.order_types import DeliveryInfo
            delivery_info = DeliveryInfo(
                address=db_order.delivery_address,
                phone=db_order.delivery_phone or ""
            )
        elif db_order.order_type == OrderType.PICKUP.value and db_order.pickup_phone:
            from shared.types.order_types import PickupInfo
            pickup_info = PickupInfo(
                phone=db_order.pickup_phone
            )
        
        return Order(
            order_id=db_order.id,
            user_id=db_order.user_id,
            items=order_items,
            total=db_order.total,
            status=OrderStatus(db_order.status),
            order_type=OrderType(db_order.order_type),
            payment_method=PaymentMethod(db_order.payment_method),
            payment_status=PaymentStatus(db_order.payment_status) if db_order.payment_status else None,
            delivery_info=delivery_info,
            pickup_info=pickup_info,
            comment=db_order.comment,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at
        )
    
    def _menu_item_model_to_entity(self, db_item: MenuItemModel) -> MenuItem:
        """Convert MenuItemModel to MenuItem entity."""
        from domain.entities.menu_item import MenuItem
        return MenuItem(
            item_id=db_item.id,
            category_id=db_item.category_id,
            name=db_item.name,
            description=db_item.description,
            price=db_item.price,
            image_url=db_item.image_url,
            ingredients=db_item.ingredients,
            allergens=db_item.allergens,
            weight=db_item.weight,
            calories=db_item.calories,
            is_available=db_item.is_available,
            is_popular=db_item.is_popular,
            sort_order=db_item.sort_order,
            created_at=db_item.created_at,
            updated_at=db_item.updated_at
        )