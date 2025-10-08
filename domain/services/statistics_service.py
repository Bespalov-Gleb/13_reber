"""Statistics service for calculating various statistics."""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from domain.repositories.order_repository import OrderRepository
from domain.repositories.user_repository import UserRepository
from domain.repositories.menu_repository import MenuRepository
from shared.types.order_types import OrderFilters
from shared.constants.order_constants import OrderStatus


class StatisticsService:
    """Service for calculating various statistics."""

    def __init__(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        menu_repository: MenuRepository
    ):
        self.order_repository = order_repository
        self.user_repository = user_repository
        self.menu_repository = menu_repository

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary statistics."""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Today's statistics
        today_orders = await self.order_repository.get_orders_by_filters(
            OrderFilters(date_from=datetime.combine(today, datetime.min.time()), 
                        date_to=datetime.combine(today, datetime.max.time()))
        )
        
        # Yesterday's statistics
        yesterday_orders = await self.order_repository.get_orders_by_filters(
            OrderFilters(date_from=datetime.combine(yesterday, datetime.min.time()), 
                        date_to=datetime.combine(yesterday, datetime.max.time()))
        )
        
        # Calculate today's metrics
        today_revenue = sum(order.total for order in today_orders 
                          if order.status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP])
        today_avg_order = today_revenue // len(today_orders) if today_orders else 0
        
        # Calculate yesterday's metrics
        yesterday_revenue = sum(order.total for order in yesterday_orders 
                              if order.status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP])
        yesterday_avg_order = yesterday_revenue // len(yesterday_orders) if yesterday_orders else 0
        
        # User statistics
        all_users = await self.user_repository.list_all()
        new_users_today = len([u for u in all_users if u.created_at.date() == today])
        active_users_today = len(set(order.user_id for order in today_orders))
        
        # Menu statistics
        categories = await self.menu_repository.list_categories()
        menu_items = await self.menu_repository.list_menu_items()
        
        return {
            'today': {
                'orders': len(today_orders),
                'revenue': today_revenue,
                'avg_order': today_avg_order
            },
            'yesterday': {
                'orders': len(yesterday_orders),
                'revenue': yesterday_revenue,
                'avg_order': yesterday_avg_order
            },
            'users': {
                'total_users': len(all_users),
                'new_users_today': new_users_today,
                'active_users_today': active_users_today
            },
            'menu': {
                'total_categories': len(categories),
                'total_items': len(menu_items)
            }
        }

    async def get_sales_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get sales statistics for a period."""
        orders = await self.order_repository.get_orders_by_filters(
            OrderFilters(date_from=start_date, date_to=end_date)
        )
        
        # Filter completed orders for revenue calculation
        completed_orders = [order for order in orders 
                          if order.status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP]]
        
        total_sales = sum(order.total for order in completed_orders)
        
        # Sales by day
        sales_by_day = {}
        for order in completed_orders:
            day = order.created_at.date().strftime('%Y-%m-%d')
            sales_by_day[day] = sales_by_day.get(day, 0) + order.total
        
        # Sales by hour
        sales_by_hour = {}
        for order in completed_orders:
            hour = order.created_at.hour
            sales_by_hour[hour] = sales_by_hour.get(hour, 0) + order.total
        
        return {
            'total_sales': total_sales,
            'sales_by_day': sorted(sales_by_day.items(), key=lambda x: x[1], reverse=True),
            'sales_by_hour': sorted(sales_by_hour.items(), key=lambda x: x[1], reverse=True)
        }

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        all_users = await self.user_repository.list_all()
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Count new users
        new_users_today = len([u for u in all_users if u.created_at.date() == today])
        new_users_this_week = len([u for u in all_users if u.created_at.date() >= week_ago])
        new_users_this_month = len([u for u in all_users if u.created_at.date() >= month_ago])
        
        # Active users (users who made orders)
        today_orders = await self.order_repository.get_orders_by_filters(
            OrderFilters(date_from=datetime.combine(today, datetime.min.time()), 
                        date_to=datetime.combine(today, datetime.max.time()))
        )
        week_orders = await self.order_repository.get_orders_by_filters(
            OrderFilters(date_from=datetime.combine(week_ago, datetime.min.time()), 
                        date_to=datetime.now())
        )
        
        active_users_today = len(set(order.user_id for order in today_orders))
        active_users_this_week = len(set(order.user_id for order in week_orders))
        
        return {
            'total_users': len(all_users),
            'new_users_today': new_users_today,
            'new_users_this_week': new_users_this_week,
            'new_users_this_month': new_users_this_month,
            'active_users_today': active_users_today,
            'active_users_this_week': active_users_this_week
        }

    async def get_menu_statistics(self) -> Dict[str, Any]:
        """Get menu statistics."""
        categories = await self.menu_repository.list_categories()
        menu_items = await self.menu_repository.list_menu_items()
        
        # Count active items
        active_categories = len([c for c in categories if c.is_active])
        active_items = len([item for item in menu_items if item.is_available])
        
        # Top categories by item count
        category_counts = {}
        for item in menu_items:
            category_counts[item.category_id] = category_counts.get(item.category_id, 0) + 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Top items (placeholder - would need order item data)
        top_items = []  # This would require order item statistics
        
        return {
            'total_categories': len(categories),
            'active_categories': active_categories,
            'total_items': len(menu_items),
            'active_items': active_items,
            'top_categories': top_categories,
            'top_items': top_items
        }

    async def get_order_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get order statistics for a period."""
        orders = await self.order_repository.get_orders_by_filters(
            OrderFilters(date_from=start_date, date_to=end_date)
        )
        
        # Revenue only from completed orders (delivered/picked up)
        completed_orders = [order for order in orders 
                          if order.status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP]]
        total_revenue = sum(order.total for order in completed_orders)
        average_order_value = total_revenue // len(completed_orders) if completed_orders else 0
        
        # Orders by status
        orders_by_status = {}
        for order in orders:
            status = order.status.value
            orders_by_status[status] = orders_by_status.get(status, 0) + 1
        
        # Orders by type
        orders_by_type = {}
        for order in orders:
            order_type = order.order_type.value
            orders_by_type[order_type] = orders_by_type.get(order_type, 0) + 1
        
        return {
            'total_orders': len(orders),
            'total_revenue': total_revenue,
            'average_order_value': average_order_value,
            'orders_by_status': orders_by_status,
            'orders_by_type': orders_by_type
        }
