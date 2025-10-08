"""Admin management handlers for users, payments, and notifications."""

from typing import Any, Dict
from datetime import datetime

from aiogram.types import CallbackQuery
from aiogram import F

from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.admin_keyboard import AdminKeyboard
from app.dependencies import container
from app.dependencies import (
    get_user_service,
    get_statistics_service,
    get_order_service,
    get_payment_service,
)


class AdminManagementHandlers(BaseHandler):
    """Handlers for admin management operations."""

    def _register_handlers(self) -> None:
        """Register handlers - not needed as handlers are registered in AdminHandler."""
        pass

    # Users management handlers
    async def handle_users_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle users management callbacks."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        action = parts[1]

        session = data.get("session")
        if session is None:
            user_service = await get_user_service(data)
            statistics_service = await get_statistics_service(data)
        else:
            user_service = container.get_user_service(session)
            statistics_service = container.get_statistics_service(session)

        try:
            if action == "all":
                users = await user_service.get_all_users()
                text = f"👥 <b>Все пользователи</b>\n\nНайдено: {len(users)}"
                keyboard = AdminKeyboard.get_users_list_keyboard(users)
            elif action == "new_today":
                today = datetime.now().date()
                users = await user_service.get_users_by_date(today)
                text = f"🆕 <b>Новые пользователи сегодня</b>\n\nНайдено: {len(users)}"
                keyboard = AdminKeyboard.get_users_list_keyboard(users)
            elif action == "stats":
                user_stats = await statistics_service.get_user_statistics()
                text = f"👥 <b>Статистика пользователей</b>\n\n"
                text += f"👤 Всего: {user_stats['total_users']}\n"
                text += f"🆕 Новых сегодня: {user_stats['new_users_today']}\n"
                text += f"🔥 Активных сегодня: {user_stats['active_users_today']}"
                keyboard = AdminKeyboard.get_back_to_admin_keyboard()
            else:
                await callback.answer("❌ Неизвестное действие")
                return

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Users callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке пользователей")
            return

        await callback.answer()

    async def handle_user_detail_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle user detail callback."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        target_user_id = parts[1]

        session = data.get("session")
        if session is None:
            user_service = await get_user_service(data)
        else:
            user_service = container.get_user_service(session)

        try:
            user = await user_service.get_user_by_id(target_user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден")
                return

            text = f"👤 <b>Информация о пользователе</b>\n\n"
            text += f"🆔 ID: {user.user_id}\n"
            text += f"📱 Telegram ID: {user.telegram_id}\n"
            text += f"👤 Имя: {user.first_name or 'Не указано'}\n"
            text += f"👤 Фамилия: {user.last_name or 'Не указано'}\n"
            text += f"📝 Username: @{user.username or 'Не указано'}\n"
            text += f"📞 Телефон: {user.phone or 'Не указано'}\n"
            text += f"✅ Активен: {'Да' if user.is_active else 'Нет'}\n"
            from shared.types.user_types import UserStatus
            text += f"🚫 Заблокирован: {'Да' if getattr(user, 'status', None) == UserStatus.BLOCKED else 'Нет'}\n"
            text += f"👨‍💼 Админ: {'Да' if user.is_admin else 'Нет'}\n"
            text += f"📅 Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}"

            keyboard = AdminKeyboard.get_user_detail_keyboard(user)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"User detail callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке пользователя")
            return

        await callback.answer()

    async def handle_user_management_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle user management callbacks (block/unblock)."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        # Support formats:
        #  - "user_block:{user_id}"
        #  - "user_unblock:{user_id}"
        #  - "user_orders:{user_id}"
        #  - legacy: "user:{action}:{user_id}"
        action: str | None = None
        target_user_id: str | None = None
        if callback_data.startswith("user_"):
            token = parts[0]
            action = token.split("_", 1)[1] if "_" in token else None
            target_user_id = parts[1] if len(parts) > 1 else None
        elif parts and parts[0] == "user" and len(parts) >= 3:
            action = parts[1]
            target_user_id = parts[2]
        else:
            await callback.answer("❌ Ошибка: неверные данные")
            return

        if not target_user_id:
            await callback.answer("❌ Ошибка: отсутствует идентификатор пользователя")
            return

        session = data.get("session")
        if session is None:
            user_service = await get_user_service(data)
        else:
            user_service = container.get_user_service(session)

        try:
            if action == "block":
                success = await user_service.block_user(target_user_id)
                if success:
                    await callback.answer("✅ Пользователь заблокирован")
                else:
                    await callback.answer("❌ Не удалось заблокировать пользователя")
                return
            elif action == "unblock":
                success = await user_service.unblock_user(target_user_id)
                if success:
                    await callback.answer("✅ Пользователь разблокирован")
                else:
                    await callback.answer("❌ Не удалось разблокировать пользователя")
                return
            elif action == "orders":
                # Show user orders
                if session is None:
                    order_service = await get_order_service(data)
                else:
                    order_service = container.get_order_service(session)
                orders = await order_service.get_orders_by_user_id(target_user_id)
                
                text = f"📋 <b>Заказы пользователя</b>\n\n"
                if orders:
                    text += f"Найдено заказов: {len(orders)}\n\n"
                    for order in orders[:5]:  # Show first 5 orders
                        text += f"• #{order.order_id[:8]} - {order.status.value} - {order.total // 100}₽\n"
                    if len(orders) > 5:
                        text += f"\n... и еще {len(orders) - 5} заказов"
                else:
                    text += "Заказы не найдены"
                
                keyboard = AdminKeyboard.get_back_to_admin_keyboard()
                
                await self.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=keyboard
                )
            elif action in ("make_admin", "remove_admin"):
                # Toggle admin role
                user = await user_service.get_user_by_id(target_user_id)
                if not user:
                    await callback.answer("❌ Пользователь не найден")
                    return
                from shared.types.user_types import UserRole
                if action == "make_admin":
                    user.role = UserRole.ADMIN
                    await user_service.update_user(user)
                    await callback.answer("✅ Пользователь назначен администратором")
                else:
                    user.role = UserRole.CUSTOMER
                    await user_service.update_user(user)
                    await callback.answer("✅ Роль администратора снята")

                # Refresh detail view with updated keyboard
                text = f"👤 <b>Информация о пользователе</b>\n\n"
                text += f"🆔 ID: {user.user_id}\n"
                text += f"📱 Telegram ID: {user.telegram_id}\n"
                text += f"👤 Имя: {user.first_name or 'Не указано'}\n"
                text += f"👤 Фамилия: {user.last_name or 'Не указано'}\n"
                text += f"📝 Username: @{user.username or 'Не указано'}\n"
                text += f"📞 Телефон: {user.phone or 'Не указано'}\n"
                text += f"✅ Активен: {'Да' if user.is_active else 'Нет'}\n"
                from shared.types.user_types import UserStatus
                text += f"🚫 Заблокирован: {'Да' if getattr(user, 'status', None) == UserStatus.BLOCKED else 'Нет'}\n"
                text += f"👨‍💼 Админ: {'Да' if user.is_admin else 'Нет'}\n"
                text += f"📅 Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}"

                kb = AdminKeyboard.get_user_detail_keyboard(user)
                await self.safe_edit_message(
                    callback.message,
                    text=text,
                    reply_markup=kb
                )
            else:
                await callback.answer("❌ Неизвестное действие")
                return

        except Exception as e:
            self.logger.error(f"User management callback error: {e}")
            await callback.answer("❌ Произошла ошибка при управлении пользователем")
            return

        await callback.answer()

    # Payments management handlers
    async def handle_payments_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payments management callbacks."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        action = parts[1]

        session = data.get("session")
        payment_service = container.get_payment_service(session)

        try:
            if action == "all":
                payments = await payment_service.get_all_payments()
                text = f"💰 <b>Все платежи</b>\n\nНайдено: {len(payments)}"
                keyboard = AdminKeyboard.get_payments_list_keyboard(payments)
            elif action == "pending":
                payments = await payment_service.get_payments_by_status("pending")
                text = f"⏳ <b>Ожидающие платежи</b>\n\nНайдено: {len(payments)}"
                keyboard = AdminKeyboard.get_payments_list_keyboard(payments)
            elif action == "completed":
                payments = await payment_service.get_payments_by_status("succeeded")
                text = f"✅ <b>Завершенные платежи</b>\n\nНайдено: {len(payments)}"
                keyboard = AdminKeyboard.get_payments_list_keyboard(payments)
            elif action == "failed":
                payments = await payment_service.get_payments_by_status("failed")
                text = f"❌ <b>Неудачные платежи</b>\n\nНайдено: {len(payments)}"
                keyboard = AdminKeyboard.get_payments_list_keyboard(payments)
            else:
                await callback.answer("❌ Неизвестное действие")
                return

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Payments callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке платежей")
            return

        await callback.answer()

    async def handle_payment_detail_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payment detail callback."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        payment_id = parts[1]

        session = data.get("session")
        payment_service = container.get_payment_service(session)

        try:
            payment = await payment_service.get_payment_by_id(payment_id)
            if not payment:
                await callback.answer("❌ Платеж не найден")
                return

            text = f"💰 <b>Информация о платеже</b>\n\n"
            text += f"🆔 ID: {payment.id}\n"
            text += f"💳 Сумма: {payment.amount // 100}₽\n"
            text += f"📊 Статус: {payment.status.value}\n"
            text += f"💳 Метод: {payment.payment_method.value}\n"
            text += f"📅 Дата: {payment.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            if payment.payment_url:
                text += f"🔗 Ссылка: {payment.payment_url}"

            keyboard = AdminKeyboard.get_payment_detail_keyboard(payment)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Payment detail callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке платежа")
            return

        await callback.answer()

    async def handle_payment_management_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payment management callbacks (refund/cancel)."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        action = parts[1]  # refund, cancel
        payment_id = parts[2]

        session = data.get("session")
        payment_service = container.get_payment_service(session)

        try:
            if action == "refund":
                success = await payment_service.refund_payment(payment_id)
                if success:
                    await callback.answer("✅ Платеж возвращен")
                else:
                    await callback.answer("❌ Не удалось вернуть платеж")
            elif action == "cancel":
                success = await payment_service.cancel_payment(payment_id)
                if success:
                    await callback.answer("✅ Платеж отменен")
                else:
                    await callback.answer("❌ Не удалось отменить платеж")
            else:
                await callback.answer("❌ Неизвестное действие")
                return

        except Exception as e:
            self.logger.error(f"Payment management callback error: {e}")
            await callback.answer("❌ Произошла ошибка при управлении платежом")
            return

        await callback.answer()

    # Notifications management handlers
    async def handle_notifications_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle notifications management callbacks."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        action = parts[1]

        try:
            if action == "send":
                text = "📢 <b>Отправка уведомлений</b>\n\nВыберите тип уведомления:"
                keyboard = AdminKeyboard.get_notification_templates_keyboard()
            elif action == "templates":
                text = "📝 <b>Шаблоны уведомлений</b>\n\nВыберите шаблон для редактирования:"
                keyboard = AdminKeyboard.get_notification_templates_keyboard()
            elif action == "history":
                text = "📋 <b>История уведомлений</b>\n\nИстория отправленных уведомлений будет здесь"
                keyboard = AdminKeyboard.get_back_to_admin_keyboard()
            else:
                await callback.answer("❌ Неизвестное действие")
                return

            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Notifications callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке уведомлений")
            return

        await callback.answer()

    async def handle_notification_template_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle notification template callback."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        template_type = parts[1]

        try:
            # Placeholder for template management
            text = f"📝 <b>Шаблон: {template_type}</b>\n\n"
            text += "Здесь будет редактирование шаблона уведомления"
            
            keyboard = AdminKeyboard.get_back_to_admin_keyboard()
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )

        except Exception as e:
            self.logger.error(f"Notification template callback error: {e}")
            await callback.answer("❌ Произошла ошибка при загрузке шаблона")
            return

        await callback.answer()
