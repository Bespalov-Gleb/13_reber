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
from domain.services.admin_state_service import admin_state_service
from shared.types.admin_states import AdminState
from shared.services.notification_templates import (
    get_notification_template,
    set_notification_template,
    reset_notification_template,
)
from shared.types.user_types import UserRole


class AdminManagementHandlers(BaseHandler):
    """Handlers for admin management operations."""

    _template_variables = {
        "welcome": "{first_name}, {cafe_name}, {working_hours}",
        "order_ready": "{order_id_short}, {total_rub}, {order_type}",
        "order_delivery": "{order_id_short}, {address}",
        "order_delivered": "{order_id_short}",
    }

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
            elif action == "courier_toggle_username":
                admin_state_service.set_admin_state(callback.from_user.id, AdminState.COURIER_ROLE_BY_USERNAME)
                text = (
                    "🚚 <b>Управление ролью курьера</b>\n\n"
                    "Отправьте username пользователя (например: <code>@ivan</code> или <code>ivan</code>).\n"
                    "Роль будет переключена:\n"
                    "• CUSTOMER → COURIER\n"
                    "• COURIER → CUSTOMER\n\n"
                    "Для отмены отправьте <code>-</code>."
                )
                keyboard = AdminKeyboard.get_cancel_keyboard()
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
                keyboard = AdminKeyboard.get_notification_send_keyboard()
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

    async def handle_notification_send_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle notification send callbacks."""
        callback_data = callback.data or ""
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return

        action = parts[1]
        if action not in {"audience", "attach_media", "remove_media", "send"}:
            await callback.answer("❌ Неизвестное действие")
            return

        user_id = callback.from_user.id
        if action == "audience":
            audience = parts[2] if len(parts) > 2 else None
            if audience not in {"users", "admins", "couriers", "all"}:
                await callback.answer("❌ Неизвестная аудитория")
                return
            admin_state_service.set_temp_data(user_id, "notification_send_audience", audience)
            admin_state_service.set_temp_data(user_id, "notification_send_text", "")
            admin_state_service.set_temp_data(user_id, "notification_send_media_type", "")
            admin_state_service.set_temp_data(user_id, "notification_send_media_file_id", "")
            admin_state_service.set_admin_state(user_id, AdminState.COMPOSING_NOTIFICATION_ANNOUNCEMENT)
            audience_title = {
                "users": "пользователям",
                "admins": "админам",
                "couriers": "курьерам",
                "all": "всем",
            }[audience]
            await self.safe_edit_message(
                callback.message,
                text=(
                    f"📣 <b>Рассылка: {audience_title}</b>\n\n"
                    "Отправьте текст объявления одним сообщением."
                ),
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            await callback.answer()
            return

        if action == "attach_media":
            if not admin_state_service.get_temp_data(user_id, "notification_send_text"):
                await callback.answer("❌ Сначала введите текст объявления")
                return
            admin_state_service.set_admin_state(user_id, AdminState.ATTACHING_NOTIFICATION_MEDIA)
            await self.safe_edit_message(
                callback.message,
                text=(
                    "📎 <b>Прикрепление медиа</b>\n\n"
                    "Отправьте одним сообщением фото, видео или документ."
                ),
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            await callback.answer()
            return

        if action == "remove_media":
            admin_state_service.set_temp_data(user_id, "notification_send_media_type", "")
            admin_state_service.set_temp_data(user_id, "notification_send_media_file_id", "")
            audience = admin_state_service.get_temp_data(user_id, "notification_send_audience", "users")
            await self.safe_edit_message(
                callback.message,
                text=(
                    f"📣 <b>Рассылка ({audience})</b>\n\n"
                    "Медиа удалено. Можно отправить текст или прикрепить новое."
                ),
                reply_markup=AdminKeyboard.get_notification_send_preview_keyboard(has_media=False)
            )
            await callback.answer("✅ Медиа удалено")
            return

        announcement_text = admin_state_service.get_temp_data(user_id, "notification_send_text")
        audience = admin_state_service.get_temp_data(user_id, "notification_send_audience")
        if not announcement_text or audience not in {"users", "admins", "couriers", "all"}:
            await callback.answer("❌ Не заполнены данные рассылки")
            return
        media_type = admin_state_service.get_temp_data(user_id, "notification_send_media_type")
        media_file_id = admin_state_service.get_temp_data(user_id, "notification_send_media_file_id")

        try:
            user_service = await get_user_service(kwargs.get("data", {}))
            all_users = await user_service.get_all_users()
            recipients = []
            for user in all_users:
                if not user.is_active or not user.telegram_id:
                    continue
                if audience == "all":
                    recipients.append(user)
                elif audience == "users" and user.role == UserRole.CUSTOMER:
                    recipients.append(user)
                elif audience == "admins" and user.role == UserRole.ADMIN:
                    recipients.append(user)
                elif audience == "couriers" and user.role == UserRole.COURIER:
                    recipients.append(user)

            sent_count = 0
            for recipient in recipients:
                try:
                    if media_type and media_file_id:
                        if media_type == "photo":
                            await callback.bot.send_photo(
                                chat_id=recipient.telegram_id,
                                photo=media_file_id,
                                caption=announcement_text,
                                parse_mode="HTML",
                            )
                        elif media_type == "video":
                            await callback.bot.send_video(
                                chat_id=recipient.telegram_id,
                                video=media_file_id,
                                caption=announcement_text,
                                parse_mode="HTML",
                            )
                        elif media_type == "document":
                            await callback.bot.send_document(
                                chat_id=recipient.telegram_id,
                                document=media_file_id,
                                caption=announcement_text,
                                parse_mode="HTML",
                            )
                    else:
                        await callback.bot.send_message(
                            chat_id=recipient.telegram_id,
                            text=announcement_text,
                            parse_mode="HTML",
                        )
                    sent_count += 1
                except Exception:
                    continue

            await callback.answer(f"✅ Отправлено: {sent_count}")
        except Exception as e:
            self.logger.error(f"Notification send error: {e}")
            await callback.answer("❌ Не удалось отправить уведомление")
            return

    async def handle_notification_template_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle notification template callback."""
        data = kwargs.get("data", {})

        callback_data = callback.data
        parts = callback_data.split(":")
        template_type = parts[1]

        try:
            current_template = get_notification_template(template_type)
            available_vars = self._template_variables.get(template_type, "нет")
            text = f"📝 <b>Шаблон: {template_type}</b>\n\n"
            text += "Текущий текст:\n"
            text += f"<blockquote>{current_template}</blockquote>\n\n"
            text += f"Доступные переменные: <code>{available_vars}</code>"
            
            keyboard = AdminKeyboard.get_notification_template_editor_keyboard(template_type)
            
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

    async def handle_notification_template_edit_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Enter text editing mode for notification template."""
        callback_data = callback.data or ""
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return

        template_type = parts[1]
        if template_type not in self._template_variables:
            await callback.answer("❌ Неизвестный шаблон")
            return

        user_id = callback.from_user.id
        admin_state_service.set_admin_state(user_id, AdminState.EDITING_NOTIFICATION_TEMPLATE)
        admin_state_service.set_temp_data(user_id, "notification_template_type", template_type)
        await self.safe_edit_message(
            callback.message,
            text=(
                f"✏️ <b>Редактирование шаблона: {template_type}</b>\n\n"
                "Отправьте новый текст шаблона одним сообщением.\n"
                "Чтобы отменить, нажмите кнопку ниже.\n\n"
                f"Доступные переменные: <code>{self._template_variables.get(template_type, 'нет')}</code>"
            ),
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )
        await callback.answer()

    async def handle_notification_template_reset_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Reset notification template to default text."""
        callback_data = callback.data or ""
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Неверные данные")
            return
        template_type = parts[1]
        try:
            reset_notification_template(template_type)
        except ValueError:
            await callback.answer("❌ Неизвестный шаблон")
            return

        current_template = get_notification_template(template_type)
        await self.safe_edit_message(
            callback.message,
            text=(
                f"📝 <b>Шаблон: {template_type}</b>\n\n"
                "Шаблон сброшен к значению по умолчанию.\n\n"
                f"<blockquote>{current_template}</blockquote>"
            ),
            reply_markup=AdminKeyboard.get_notification_template_editor_keyboard(template_type)
        )
        await callback.answer("✅ Шаблон сброшен")
