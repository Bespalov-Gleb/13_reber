"""Courier handler for Telegram bot."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.courier_keyboard import CourierKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from domain.services.order_service import OrderService
from domain.services.user_service import UserService
from domain.services.notification_service import NotificationService
from app.dependencies import get_order_service, get_user_service, get_notification_service
from shared.constants.order_constants import OrderStatus
from shared.types.user_types import UserRole


class CourierHandler(BaseHandler):
    """Handler for courier operations."""
    
    def __init__(self):
        super().__init__()
        self.router = Router()
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register courier handlers."""
        # Courier command
        self.router.message.register(
            self.handle_courier_command,
            F.text == "/courier"
        )
        
        # Courier callbacks
        self.router.callback_query.register(
            self.handle_courier_callback,
            F.data.startswith("courier:")
        )
    
    async def handle_courier_command(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle courier command."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", message.from_user.id)
        
        # Check if user is courier
        is_courier = await self._check_courier_role(user_id, data)
        
        if not is_courier:
            await message.answer("❌ У вас нет прав курьера. Обратитесь к администратору.")
            return
        
        # Get courier main menu
        keyboard = CourierKeyboard.get_courier_main_menu()
        
        await message.answer(
            text="🚚 <b>Панель курьера</b>\n\nВыберите действие:",
            reply_markup=keyboard
        )
        
        self.logger.info(f"Courier command handled for user {user_id}")
    
    async def handle_courier_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle courier callbacks."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        # Check if user is courier
        is_courier = await self._check_courier_role(user_id, data)
        
        if not is_courier:
            await callback.answer("❌ У вас нет прав курьера")
            return
        
        callback_data = callback.data
        parts = callback_data.split(":")
        
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return
        
        action = parts[1]
        
        try:
            if action == "main_menu":
                await self._show_courier_main_menu(callback)
            elif action == "active_deliveries":
                await self._show_active_deliveries(callback, data)
            elif action == "delivery_history":
                await self._show_delivery_history(callback, data)
            elif action == "profile":
                await self._show_courier_profile(callback, data)
            elif action == "statistics":
                await self._show_courier_statistics(callback, data)
            elif action == "order":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._show_order_details(callback, order_id, data)
            elif action == "start_delivery":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._start_delivery(callback, order_id, data)
            elif action == "delivered":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._mark_delivered(callback, order_id, data)
            elif action == "delivery_problem":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._show_delivery_problem_menu(callback, order_id)
            elif action == "call":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._call_customer(callback, order_id, data)
            elif action == "maps":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._open_maps(callback, order_id, data)
            elif action == "problem":
                if len(parts) >= 4:
                    problem_type = parts[2]
                    order_id = parts[3]
                    await self._report_delivery_problem(callback, order_id, problem_type, data)
            elif action == "confirm_start_delivery":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._confirm_start_delivery(callback, order_id, data)
            elif action == "confirm_delivered":
                if len(parts) >= 3:
                    order_id = parts[2]
                    await self._confirm_delivered(callback, order_id, data)
            else:
                await callback.answer("❌ Неизвестное действие")
                
        except Exception as e:
            self.logger.error(f"Error handling courier callback: {e}")
            await callback.answer("❌ Произошла ошибка")
        
        await callback.answer()
    
    async def _check_courier_role(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Check if user has courier role."""
        try:
            user_service = await get_user_service(data)
            user = await user_service.get_user_by_telegram_id(user_id)
            
            if user and user.is_courier:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking courier role: {e}")
            return False
    
    async def _show_courier_main_menu(self, callback: CallbackQuery) -> None:
        """Show courier main menu."""
        keyboard = CourierKeyboard.get_courier_main_menu()
        
        await self.safe_edit_message(
            callback.message,
            text="🚚 <b>Панель курьера</b>\n\nВыберите действие:",
            reply_markup=keyboard
        )
    
    async def _show_active_deliveries(self, callback: CallbackQuery, data: Dict[str, Any]) -> None:
        """Show active deliveries for courier."""
        try:
            user_id = data.get("user_id", callback.from_user.id)
            order_service = await get_order_service(data)
            user_service = await get_user_service(data)
            
            # Get courier user
            courier = await user_service.get_user_by_telegram_id(user_id)
            if not courier:
                await callback.answer("❌ Курьер не найден")
                return
            
            # Get orders assigned to this courier
            from shared.types.order_types import OrderFilters
            filters = OrderFilters(
                courier_id=courier.user_id,
                statuses=[OrderStatus.READY, OrderStatus.OUT_FOR_DELIVERY]
            )
            
            orders = await order_service.list_orders(filters)
            
            if not orders:
                text = "📭 <b>Активные доставки</b>\n\nУ вас нет активных доставок."
            else:
                text = f"🚚 <b>Активные доставки</b>\n\nНайдено доставок: {len(orders)}"
            
            keyboard = CourierKeyboard.get_active_deliveries_keyboard(orders)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error showing active deliveries: {e}")
            await callback.answer("❌ Ошибка загрузки доставок")
    
    async def _show_delivery_history(self, callback: CallbackQuery, data: Dict[str, Any]) -> None:
        """Show delivery history for courier."""
        try:
            user_id = data.get("user_id", callback.from_user.id)
            order_service = await get_order_service(data)
            user_service = await get_user_service(data)
            
            # Get courier user
            courier = await user_service.get_user_by_telegram_id(user_id)
            if not courier:
                await callback.answer("❌ Курьер не найден")
                return
            
            # Get completed orders for this courier
            from shared.types.order_types import OrderFilters
            filters = OrderFilters(
                courier_id=courier.user_id,
                statuses=[OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REFUNDED]
            )
            
            orders = await order_service.list_orders(filters)
            
            if not orders:
                text = "📭 <b>История доставок</b>\n\nУ вас пока нет завершенных доставок."
            else:
                text = f"📋 <b>История доставок</b>\n\nВсего доставок: {len(orders)}"
            
            keyboard = CourierKeyboard.get_delivery_history_keyboard(orders)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error showing delivery history: {e}")
            await callback.answer("❌ Ошибка загрузки истории")
    
    async def _show_courier_profile(self, callback: CallbackQuery, data: Dict[str, Any]) -> None:
        """Show courier profile."""
        try:
            user_id = data.get("user_id", callback.from_user.id)
            user_service = await get_user_service(data)
            
            user = await user_service.get_user_by_telegram_id(user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден")
                return
            
            # Get courier statistics
            order_service = await get_order_service(data)
            from shared.types.order_types import OrderFilters
            
            # Get completed deliveries count
            completed_filters = OrderFilters(
                courier_id=user.user_id,
                statuses=[OrderStatus.DELIVERED]
            )
            completed_orders = await order_service.list_orders(completed_filters)
            
            # Get total earnings (simplified - just count orders)
            total_earnings = len(completed_orders) * 100  # 100 rubles per delivery (example)
            
            text = f"👤 <b>Профиль курьера</b>\n\n"
            text += f"📝 <b>Имя:</b> {user.full_name}\n"
            text += f"📱 <b>Телефон:</b> {user.phone or 'Не указан'}\n"
            text += f"📊 <b>Завершенных доставок:</b> {len(completed_orders)}\n"
            text += f"💰 <b>Заработано:</b> {total_earnings}₽\n"
            text += f"📅 <b>Дата регистрации:</b> {user.created_at.strftime('%d.%m.%Y')}"
            
            keyboard = CourierKeyboard.get_courier_profile_keyboard()
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error showing courier profile: {e}")
            await callback.answer("❌ Ошибка загрузки профиля")
    
    async def _show_courier_statistics(self, callback: CallbackQuery, data: Dict[str, Any]) -> None:
        """Show courier statistics."""
        try:
            user_id = data.get("user_id", callback.from_user.id)
            order_service = await get_order_service(data)
            user_service = await get_user_service(data)
            
            # Get courier user
            courier = await user_service.get_user_by_telegram_id(user_id)
            if not courier:
                await callback.answer("❌ Курьер не найден")
                return
            
            # Get statistics for last 30 days
            from shared.types.order_types import OrderFilters
            from datetime import datetime, timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Get all orders for this courier in last 30 days
            filters = OrderFilters(
                courier_id=courier.user_id,
                date_from=start_date,
                date_to=end_date
            )
            
            all_orders = await order_service.list_orders(filters)
            
            # Calculate statistics
            completed = len([o for o in all_orders if o.status == OrderStatus.DELIVERED])
            cancelled = len([o for o in all_orders if o.status == OrderStatus.CANCELLED])
            total_earnings = completed * 100  # 100 rubles per delivery (example)
            
            text = f"📊 <b>Статистика курьера</b>\n\n"
            text += f"📅 <b>Период:</b> Последние 30 дней\n\n"
            text += f"✅ <b>Завершено доставок:</b> {completed}\n"
            text += f"❌ <b>Отменено доставок:</b> {cancelled}\n"
            text += f"💰 <b>Заработано:</b> {total_earnings}₽\n"
            text += f"📈 <b>Среднее в день:</b> {completed // 30 if completed > 0 else 0} доставок"
            
            keyboard = CourierKeyboard.get_courier_main_menu()
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error showing courier statistics: {e}")
            await callback.answer("❌ Ошибка загрузки статистики")
    
    async def _show_order_details(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Show order details for courier."""
        try:
            order_service = await get_order_service(data)
            user_service = await get_user_service(data)
            
            order = await order_service.get_order(order_id)
            if not order:
                await callback.answer("❌ Заказ не найден")
                return
            
            # Get customer info
            customer = await user_service.get_user_by_id(order.user_id)
            
            # Format order details
            text = f"📦 <b>Детали заказа</b>\n\n"
            text += f"🆔 <b>Номер заказа:</b> #{order.order_id[:8]}\n"
            text += f"👤 <b>Клиент:</b> {customer.full_name if customer else 'Неизвестно'}\n"
            text += f"📞 <b>Телефон:</b> {order.delivery_info.phone if order.delivery_info else 'Не указан'}\n"
            text += f"📍 <b>Адрес:</b> {order.delivery_info.address if order.delivery_info else 'Не указан'}\n"
            text += f"💰 <b>Сумма:</b> {order.total // 100}₽\n"
            text += f"💳 <b>Оплата:</b> {'Наличные' if order.payment_method.value == 'cash' else 'Карта'}\n"
            text += f"📊 <b>Статус:</b> {order.status.display_name}\n\n"
            
            if order.comment:
                text += f"💬 <b>Комментарий:</b> {order.comment}\n\n"
            
            text += f"📦 <b>Состав заказа:</b>\n"
            for item in order.items:
                text += f"• {item.name} x{item.quantity} - {item.price * item.quantity // 100}₽\n"
            
            keyboard = CourierKeyboard.get_order_management_keyboard(order)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error showing order details: {e}")
            await callback.answer("❌ Ошибка загрузки заказа")
    
    async def _start_delivery(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Start delivery process."""
        try:
            order_service = await get_order_service(data)
            
            order = await order_service.get_order(order_id)
            if not order:
                await callback.answer("❌ Заказ не найден")
                return
            
            if order.status != OrderStatus.READY:
                await callback.answer("❌ Заказ не готов к доставке")
                return
            
            # Show confirmation
            text = f"🚚 <b>Начать доставку</b>\n\n"
            text += f"Заказ #{order.order_id[:8]} готов к доставке.\n"
            text += f"Адрес: {order.delivery_info.address if order.delivery_info else 'Не указан'}\n\n"
            text += "Подтвердите начало доставки:"
            
            keyboard = CourierKeyboard.get_confirmation_keyboard("start_delivery", order_id)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error starting delivery: {e}")
            await callback.answer("❌ Ошибка начала доставки")
    
    async def _confirm_start_delivery(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Confirm start delivery."""
        try:
            order_service = await get_order_service(data)
            notification_service = await get_notification_service(data)
            
            # Update order status
            await order_service.update_order_status(order_id, OrderStatus.OUT_FOR_DELIVERY)
            
            # Get order and customer for notification
            order = await order_service.get_order(order_id)
            if order:
                from app.dependencies import get_user_service
                user_service = await get_user_service(data)
                customer = await user_service.get_user_by_id(order.user_id)
                
                if customer:
                    # Notify customer that courier is on the way
                    await notification_service.send_courier_on_way_notification(order, customer)
            
            await self.safe_edit_message(
                callback.message,
                text="✅ <b>Доставка начата!</b>\n\nКлиент уведомлен о том, что курьер в пути.",
                reply_markup=CourierKeyboard.get_courier_main_menu()
            )
            
        except Exception as e:
            self.logger.error(f"Error confirming start delivery: {e}")
            await callback.answer("❌ Ошибка подтверждения доставки")
    
    async def _mark_delivered(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Mark order as delivered."""
        try:
            order_service = await get_order_service(data)
            
            order = await order_service.get_order(order_id)
            if not order:
                await callback.answer("❌ Заказ не найден")
                return
            
            if order.status != OrderStatus.OUT_FOR_DELIVERY:
                await callback.answer("❌ Заказ не в доставке")
                return
            
            # Show confirmation
            text = f"✅ <b>Подтвердить доставку</b>\n\n"
            text += f"Заказ #{order.order_id[:8]} доставлен клиенту?\n\n"
            text += "Подтвердите завершение доставки:"
            
            keyboard = CourierKeyboard.get_confirmation_keyboard("delivered", order_id)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error marking delivered: {e}")
            await callback.answer("❌ Ошибка подтверждения доставки")
    
    async def _confirm_delivered(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Confirm order delivered."""
        try:
            order_service = await get_order_service(data)
            notification_service = await get_notification_service(data)
            
            # Update order status
            await order_service.update_order_status(order_id, OrderStatus.DELIVERED)
            
            # Get order and customer for notification
            order = await order_service.get_order(order_id)
            if order:
                from app.dependencies import get_user_service
                user_service = await get_user_service(data)
                customer = await user_service.get_user_by_id(order.user_id)
                
                if customer:
                    # Notify customer that order is delivered
                    await notification_service.send_order_delivered_notification(order, customer)
            
            await self.safe_edit_message(
                callback.message,
                text="🎉 <b>Доставка завершена!</b>\n\nКлиент уведомлен о доставке заказа.",
                reply_markup=CourierKeyboard.get_courier_main_menu()
            )
            
        except Exception as e:
            self.logger.error(f"Error confirming delivered: {e}")
            await callback.answer("❌ Ошибка подтверждения доставки")
    
    async def _show_delivery_problem_menu(self, callback: CallbackQuery, order_id: str) -> None:
        """Show delivery problem menu."""
        text = f"❌ <b>Проблема с доставкой</b>\n\n"
        text += f"Заказ #{order_id[:8]}\n\n"
        text += "Выберите тип проблемы:"
        
        keyboard = CourierKeyboard.get_delivery_problem_keyboard(order_id)
        
        await self.safe_edit_message(
            callback.message,
            text=text,
            reply_markup=keyboard
        )
    
    async def _report_delivery_problem(self, callback: CallbackQuery, order_id: str, problem_type: str, data: Dict[str, Any]) -> None:
        """Report delivery problem."""
        try:
            order_service = await get_order_service(data)
            notification_service = await get_notification_service(data)
            
            problem_messages = {
                "no_answer": "Клиент не отвечает на звонки",
                "wrong_address": "Неверный адрес доставки",
                "refused": "Клиент отказался от заказа",
                "other": "Другая проблема"
            }
            
            problem_message = problem_messages.get(problem_type, "Неизвестная проблема")
            
            # Update order status to cancelled with reason
            await order_service.cancel_order(order_id, f"Проблема с доставкой: {problem_message}")
            
            # Notify admin about the problem
            order = await order_service.get_order(order_id)
            if order:
                await notification_service.send_admin_delivery_problem_notification(order, problem_message)
            
            await self.safe_edit_message(
                callback.message,
                text=f"📢 <b>Проблема зафиксирована</b>\n\n"
                     f"Заказ #{order_id[:8]} отменен.\n"
                     f"Причина: {problem_message}\n\n"
                     f"Администратор уведомлен о проблеме.",
                reply_markup=CourierKeyboard.get_courier_main_menu()
            )
            
        except Exception as e:
            self.logger.error(f"Error reporting delivery problem: {e}")
            await callback.answer("❌ Ошибка сообщения о проблеме")
    
    async def _call_customer(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Call customer."""
        try:
            order_service = await get_order_service(data)
            
            order = await order_service.get_order(order_id)
            if not order or not order.delivery_info or not order.delivery_info.phone:
                await callback.answer("❌ Телефон клиента не указан")
                return
            
            phone = order.delivery_info.phone
            # Create phone link
            phone_link = f"tel:{phone}"
            
            text = f"📞 <b>Звонок клиенту</b>\n\n"
            text += f"Заказ: #{order_id[:8]}\n"
            text += f"Телефон: {phone}\n\n"
            text += f"Нажмите на ссылку для звонка:\n{phone_link}"
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=CourierKeyboard.get_courier_main_menu()
            )
            
        except Exception as e:
            self.logger.error(f"Error calling customer: {e}")
            await callback.answer("❌ Ошибка звонка клиенту")
    
    async def _open_maps(self, callback: CallbackQuery, order_id: str, data: Dict[str, Any]) -> None:
        """Open maps with delivery address."""
        try:
            order_service = await get_order_service(data)
            
            order = await order_service.get_order(order_id)
            if not order or not order.delivery_info or not order.delivery_info.address:
                await callback.answer("❌ Адрес доставки не указан")
                return
            
            address = order.delivery_info.address
            
            # Create maps links
            yandex_maps_link = f"https://yandex.ru/maps/?text={address}"
            google_maps_link = f"https://www.google.com/maps/search/?api=1&query={address}"
            
            text = f"🗺️ <b>Маршрут доставки</b>\n\n"
            text += f"Заказ: #{order_id[:8]}\n"
            text += f"Адрес: {address}\n\n"
            text += f"<b>Яндекс.Карты:</b>\n{yandex_maps_link}\n\n"
            text += f"<b>Google Maps:</b>\n{google_maps_link}"
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=CourierKeyboard.get_courier_main_menu()
            )
            
        except Exception as e:
            self.logger.error(f"Error opening maps: {e}")
            await callback.answer("❌ Ошибка открытия карт")
