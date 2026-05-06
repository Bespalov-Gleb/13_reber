"""Notification service for business logic."""

from typing import List, Optional

from aiogram import Bot
from aiogram.types import Message

from domain.entities.order import Order
from domain.entities.payment import Payment
from domain.entities.user import User
from shared.constants.order_constants import OrderStatus, OrderType
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from app.config import get_settings
from shared.services.notification_templates import render_notification_template


class NotificationService:
    """Notification service for business logic."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.settings = get_settings()
    
    async def send_order_status_notification(self, order: Order, user: User, old_status: Optional[OrderStatus] = None) -> bool:
        """Send order status notification to user."""
        try:
            # Map status to emoji and text
            status_messages = {
                OrderStatus.PENDING: "✅ Заказ принят",
                OrderStatus.CONFIRMED: "✅ Заказ подтвержден",
                OrderStatus.PREPARING: "👨‍🍳 Заказ готовится",
                OrderStatus.READY: "🚶 Заказ готов к самовывозу" if order.order_type == OrderType.PICKUP else "🚚 Заказ готов к доставке",
                OrderStatus.OUT_FOR_DELIVERY: "🚚 Заказ передан в доставку",
                OrderStatus.DELIVERED: "🎉 Заказ доставлен",
                OrderStatus.PICKED_UP: "🎉 Заказ выполнен",
                OrderStatus.CANCELLED: "❌ Заказ отменен",
                OrderStatus.REFUNDED: "💰 Заказ возвращен"
            }
            
            status_text = status_messages.get(order.status, f"📋 Статус заказа изменен: {order.status.value}")
            
            # Format message (uses editable templates for key delivery milestones)
            if order.status == OrderStatus.READY:
                message = render_notification_template(
                    "order_ready",
                    {
                        "order_id_short": order.order_id[:8],
                        "total_rub": str(order.total // 100),
                        "order_type": "доставка" if order.order_type == OrderType.DELIVERY else "самовывоз",
                    },
                )
            elif order.status == OrderStatus.OUT_FOR_DELIVERY:
                message = render_notification_template(
                    "order_delivery",
                    {
                        "order_id_short": order.order_id[:8],
                        "address": order.delivery_info.address if order.delivery_info else "Не указан",
                    },
                )
            elif order.status in (OrderStatus.DELIVERED, OrderStatus.PICKED_UP):
                message = render_notification_template(
                    "order_delivered",
                    {
                        "order_id_short": order.order_id[:8],
                    },
                )
            else:
                message = MessageFormatter.format_order_status_notification(order, order.status)
            
            # Send to user
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=message,
                parse_mode="HTML"
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send order status notification: {e}")
            return False
    
    async def send_admin_new_order_notification(self, order: Order, user: User) -> bool:
        """Send new order notification to admin chat."""
        try:
            if not self.settings.admin_chat_id:
                print("⚠️ ADMIN_CHAT_ID not configured, skipping admin notification")
                return False
            
            # Format admin message
            message = MessageFormatter.format_admin_new_order_notification(order, user)
            
            # Create inline keyboard for order management
            from infrastructure.telegram.keyboards.admin_keyboard import AdminKeyboard
            keyboard = AdminKeyboard.get_order_management_keyboard(order)
            
            # Send to admin chat
            await self.bot.send_message(
                chat_id=self.settings.admin_chat_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send admin notification: {e}")
            return False
    
    async def send_payment_completed_notification(self, payment: Payment, user: User) -> bool:
        """Send payment completed notification."""
        try:
            # TODO: Implement actual notification sending via Telegram
            print(f"📧 Payment completed notification sent to user {user.telegram_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to send payment completed notification: {e}")
            return False
    
    async def send_payment_failed_notification(self, payment: Payment, user: User) -> bool:
        """Send payment failed notification."""
        try:
            # TODO: Implement actual notification sending via Telegram
            print(f"📧 Payment failed notification sent to user {user.telegram_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to send payment failed notification: {e}")
            return False
    
    async def send_delivery_notification(self, order: Order, user: User) -> bool:
        """Send delivery notification."""
        try:
            # TODO: Implement actual notification sending via Telegram
            print(f"📧 Delivery notification sent to user {user.telegram_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to send delivery notification: {e}")
            return False
    
    async def send_pickup_notification(self, order: Order, user: User) -> bool:
        """Send pickup notification."""
        try:
            # TODO: Implement actual notification sending via Telegram
            print(f"📧 Pickup notification sent to user {user.telegram_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to send pickup notification: {e}")
            return False
    
    async def send_admin_notification(self, message: str, order: Optional[Order] = None) -> bool:
        """Send notification to admin."""
        try:
            # TODO: Implement actual notification sending to admin chat
            print(f"📧 Admin notification: {message}")
            return True
        except Exception as e:
            print(f"❌ Failed to send admin notification: {e}")
            return False
    
    async def send_courier_notification(self, message: str, order: Order) -> bool:
        """Send notification to courier."""
        try:
            # TODO: Implement actual notification sending to courier
            print(f"📧 Courier notification: {message}")
            return True
        except Exception as e:
            print(f"❌ Failed to send courier notification: {e}")
            return False
    
    async def send_promotion_notification(self, message: str, user_ids: List[str]) -> int:
        """Send promotion notification to users."""
        try:
            # TODO: Implement actual notification sending to multiple users
            print(f"📧 Promotion notification sent to {len(user_ids)} users")
            return len(user_ids)
        except Exception as e:
            print(f"❌ Failed to send promotion notification: {e}")
            return 0
    
    async def send_review_request_notification(self, order: Order, user: User) -> bool:
        """Send review request notification to user."""
        try:
            # Format review request message
            message = f"🎉 <b>Заказ выполнен!</b>\n\n"
            message += f"📋 Заказ #{order.order_id[:8]} успешно завершен.\n\n"
            message += "⭐ <b>Поделитесь впечатлениями!</b>\n"
            message += "Ваш отзыв поможет нам стать лучше.\n\n"
            message += "Нажмите кнопку ниже, чтобы оставить отзыв:"
            
            # Create inline keyboard for review
            from infrastructure.telegram.keyboards.review_keyboard import ReviewKeyboard
            keyboard = ReviewKeyboard.get_rating_keyboard(order_id=order.order_id)
            
            # Send to user
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send review request notification: {e}")
            return False
    
    async def send_courier_on_way_notification(self, order: Order, customer: User) -> bool:
        """Send notification to customer that courier is on the way."""
        try:
            message = f"🚚 <b>Курьер в пути!</b>\n\n"
            message += f"📦 Заказ #{order.order_id[:8]}\n"
            message += f"🚚 Курьер выехал к вам\n\n"
            message += f"📍 Адрес доставки: {order.delivery_info.address if order.delivery_info else 'Не указан'}\n"
            message += f"📞 Телефон курьера будет доступен в ближайшее время\n\n"
            message += "Ожидайте доставку!"
            
            await self.bot.send_message(
                chat_id=customer.telegram_id,
                text=message,
                parse_mode="HTML"
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send courier on way notification: {e}")
            return False
    
    async def send_order_delivered_notification(self, order: Order, customer: User) -> bool:
        """Send notification to customer that order is delivered."""
        try:
            message = f"🎉 <b>Заказ доставлен!</b>\n\n"
            message += f"📦 Заказ #{order.order_id[:8]} успешно доставлен\n\n"
            message += "Спасибо за заказ! Приятного аппетита! 🍽️\n\n"
            message += "⭐ Не забудьте оставить отзыв о заказе"
            
            await self.bot.send_message(
                chat_id=customer.telegram_id,
                text=message,
                parse_mode="HTML"
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send order delivered notification: {e}")
            return False
    
    async def send_courier_assignment_notification(self, order: Order, courier: User) -> bool:
        """Send notification to courier about new assignment."""
        try:
            message = f"🚚 <b>Новый заказ для доставки!</b>\n\n"
            message += f"📦 Заказ #{order.order_id[:8]}\n"
            message += f"💰 Сумма: {order.total // 100}₽\n"
            message += f"📍 Адрес: {order.delivery_info.address if order.delivery_info else 'Не указан'}\n"
            message += f"📞 Телефон клиента: {order.delivery_info.phone if order.delivery_info else 'Не указан'}\n\n"
            message += "Используйте команду /courier для управления доставками"
            
            await self.bot.send_message(
                chat_id=courier.telegram_id,
                text=message,
                parse_mode="HTML"
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send courier assignment notification: {e}")
            return False
    
    async def send_admin_delivery_problem_notification(self, order: Order, problem_description: str) -> bool:
        """Send notification to admin about delivery problem."""
        try:
            if not self.settings.admin_chat_id:
                print("⚠️ ADMIN_CHAT_ID not configured, skipping admin notification")
                return False
            
            message = f"⚠️ <b>ПРОБЛЕМА С ДОСТАВКОЙ</b>\n\n"
            message += f"📦 Заказ #{order.order_id[:8]}\n"
            message += f"🚚 Курьер: {order.courier_id or 'Не назначен'}\n"
            message += f"❌ Проблема: {problem_description}\n"
            message += f"📍 Адрес: {order.delivery_info.address if order.delivery_info else 'Не указан'}\n"
            message += f"📞 Телефон клиента: {order.delivery_info.phone if order.delivery_info else 'Не указан'}\n\n"
            message += "Требуется вмешательство администратора"
            
            await self.bot.send_message(
                chat_id=self.settings.admin_chat_id,
                text=message,
                parse_mode="HTML"
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to send admin delivery problem notification: {e}")
            return False