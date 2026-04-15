"""Helper methods for order handler."""

from typing import Any, Dict, List
from aiogram.types import CallbackQuery, Message
from infrastructure.telegram.keyboards.order_keyboard import OrderKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from domain.services.order_state_service import OrderStateService
from domain.services.cart_service import CartService
from domain.services.user_service import UserService
from domain.services.notification_service import NotificationService
from infrastructure.external.maps.yandex_maps import YandexMapsProvider
from shared.types.order_states import OrderState
from app.dependencies import (
    get_order_state_service, get_cart_service, get_user_service,
    get_notification_service, get_maps_service
)


class OrderHandlerHelpers:
    """Helper methods for order handler."""
    
    def __init__(self, logger):
        self.logger = logger
    
    async def _show_order_type_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show order type selection."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.SELECTING_ORDER_TYPE)
        
        text = "🚚 <b>Оформление заказа</b>\n\nВыберите способ получения:"
        keyboard = OrderKeyboard.get_order_type_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_payment_method_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show payment method selection."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.SELECTING_ORDER_TYPE)  # Will be updated after payment selection
        
        text = "💳 <b>Способ оплаты</b>\n\nВыберите способ оплаты:"
        keyboard = OrderKeyboard.get_payment_method_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_address_input(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show address input."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_DELIVERY_ADDRESS)
        
        text = "📍 <b>Адрес доставки</b>\n\nВведите адрес доставки:"
        keyboard = OrderKeyboard.get_back_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_address_suggestions(self, callback: CallbackQuery, suggestions: List[Dict[str, str]], user_id: int, data: Dict[str, Any]) -> None:
        """Show address suggestions."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.SELECTING_ADDRESS_SUGGESTION)
        
        # Store suggestions in temp data
        for i, suggestion in enumerate(suggestions):
            order_state_service.set_temp_data(user_id, f"suggestion_{i}", suggestion["full_address"])
        
        text = "📍 <b>Выберите адрес</b>\n\nНайдены следующие варианты:"
        keyboard = OrderKeyboard.get_address_suggestions_keyboard(suggestions)
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_delivery_phone_input(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show delivery phone input."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_DELIVERY_PHONE)
        
        text = "📱 <b>Телефон для доставки</b>\n\nУкажите номер телефона для связи с курьером:"
        keyboard = OrderKeyboard.get_delivery_phone_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_order_time_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show order time selection."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.SELECTING_ORDER_TIME)
        
        text = "🕐 <b>Время заказа</b>\n\nКогда вы хотите получить заказ?"
        keyboard = OrderKeyboard.get_order_time_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_scheduled_time_input(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show scheduled time input."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_SCHEDULED_TIME)
        
        text = "🕐 <b>Время получения</b>\n\nВведите желаемое время в формате ЧЧ:ММ (например, 14:30):"
        keyboard = OrderKeyboard.get_back_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_comment_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show comment selection."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_ORDER_COMMENT)
        
        text = "💬 <b>Комментарий к заказу</b>\n\nХотите добавить комментарий к заказу?"
        keyboard = OrderKeyboard.get_comment_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_promo_code_selection(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show promo code selection."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_PROMO_CODE)
        
        text = "🎁 <b>Промокод</b>\n\nУ вас есть промокод на скидку?"
        keyboard = OrderKeyboard.get_promo_code_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_promo_code_input(self, message: Message, user_id: int, data: Dict[str, Any]) -> None:
        """Handle promo code input."""
        promo_code = message.text.strip().upper()
        
        # Get cart service to calculate order amount
        cart_service = await get_cart_service(data)
        cart = await cart_service.get_cart(str(user_id))
        
        if not cart or not cart.items:
            await message.answer("❌ Корзина пуста")
            return
        
        # Get promotion service
        from app.dependencies import get_promotion_service
        promotion_service = await get_promotion_service(data)
        
        # Validate promo code
        is_valid, promotion, message_text = await promotion_service.validate_promotion_code(
            promo_code, cart.total_price, str(user_id)
        )
        
        if not is_valid:
            await message.answer(f"❌ {message_text}")
            return
        
        # Apply promotion
        try:
            discount_amount, usage = await promotion_service.apply_promotion_to_order(
                promotion, "temp_order_id", str(user_id), cart.total_price
            )
            
            # Update order context
            order_state_service = await get_order_state_service()
            context = order_state_service.get_context_data(user_id)
            context.promo_code = promo_code
            context.promo_discount = discount_amount
            
            # Show success message
            discount_rub = discount_amount // 100
            success_text = f"✅ <b>Промокод применен!</b>\n\n"
            success_text += f"🎁 <b>Промокод:</b> {promo_code}\n"
            success_text += f"💰 <b>Скидка:</b> {discount_rub}₽\n"
            success_text += f"📝 <b>Описание:</b> {promotion.description or 'Скидка по промокоду'}\n\n"
            success_text += "Переходим к подтверждению заказа..."
            
            await message.answer(success_text)
            
            # Go to confirmation
            await self._show_order_confirmation(message, user_id, data)
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при применении промокода: {str(e)}")
    
    async def _handle_promo_code_callback(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle promo code callback."""
        action = callback.data.split(":")[-1]
        
        if action == "add":
            # Set state for text input
            order_state_service = await get_order_state_service()
            order_state_service.set_state(user_id, OrderState.ENTERING_PROMO_CODE)
            
            text = "🎁 <b>Введите промокод</b>\n\nНапишите код промокода:"
            await callback.message.edit_text(text=text)
            
        elif action == "skip":
            # Skip promo code and go to confirmation
            await self._show_order_confirmation(callback, user_id, data)
        
        await callback.answer()
    
    async def _show_order_confirmation(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show order confirmation."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.CONFIRMING_ORDER)
        
        # Get order context
        context = order_state_service.get_context_data(user_id)
        
        # Get cart service to show order summary
        cart_service = await get_cart_service(data)
        cart = await cart_service.get_cart(str(user_id))
        
        if not cart or not cart.items:
            await callback.answer("❌ Корзина пуста")
            return
        
        # Format order summary
        text = self._format_order_summary(context, cart)
        keyboard = OrderKeyboard.get_confirmation_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _show_delivery_zone_error(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Show delivery zone error."""
        text = "❌ <b>Адрес вне зоны доставки</b>\n\nК сожалению, доставка по указанному адресу недоступна. Выберите один из вариантов:"
        keyboard = OrderKeyboard.get_delivery_zone_error_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_address_input(self, message: Message, text: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle address input."""
        try:
            # Get maps service
            maps_service = await get_maps_service()
            
            # Get address suggestions
            suggestions = await maps_service.suggest_addresses(text, limit=5)
            
            if suggestions:
                # Show suggestions
                await self._show_address_suggestions(message, suggestions, user_id, data)
            else:
                # No suggestions found, ask to try again
                await message.answer(
                    "❌ Адрес не найден. Попробуйте ввести более точный адрес или выберите 'Ввести вручную'.",
                    reply_markup=OrderKeyboard.get_back_keyboard()
                )
        except Exception as e:
            self.logger.error(f"Error handling address input: {e}")
            await message.answer("❌ Произошла ошибка при поиске адреса. Попробуйте еще раз.")
    
    async def _handle_address_selection(self, callback: CallbackQuery, suggestion_index: int, user_id: int, data: Dict[str, Any]) -> None:
        """Handle address selection."""
        order_state_service = await get_order_state_service()
        
        # Get selected address
        selected_address = order_state_service.get_temp_data(user_id, f"suggestion_{suggestion_index}")
        if not selected_address:
            await callback.answer("❌ Адрес не найден")
            return
        
        # Store address in context
        context = order_state_service.get_context_data(user_id)
        context.set_delivery_address(selected_address)
        
        # Validate delivery zone
        try:
            maps_service = await get_maps_service()
            # TODO: Get cafe coordinates from settings
            cafe_coordinates = (55.7558, 37.6176)  # Moscow coordinates as example
            
            is_in_zone = await maps_service.validate_delivery_zone(selected_address, cafe_coordinates)
            
            if is_in_zone:
                # Address is in delivery zone, proceed to phone input
                await self._show_delivery_phone_input(callback, user_id, data)
            else:
                # Address is outside delivery zone
                await self._show_delivery_zone_error(callback, user_id, data)
        except Exception as e:
            self.logger.error(f"Error validating delivery zone: {e}")
            # Proceed anyway if validation fails
            await self._show_delivery_phone_input(callback, user_id, data)
    
    async def _handle_manual_address_input(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle manual address input."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_DELIVERY_ADDRESS)
        
        text = "📍 <b>Введите адрес вручную</b>\n\nВведите полный адрес доставки:"
        keyboard = OrderKeyboard.get_back_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_address_retry(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle address retry."""
        await self._show_address_input(callback, user_id, data)
    
    async def _handle_phone_input(self, message: Message, text: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle phone input."""
        # Basic phone validation
        if len(text) < 10:
            await message.answer("❌ Номер телефона слишком короткий. Попробуйте еще раз.")
            return
        
        # Store phone in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_delivery_phone(text)
        
        # Proceed to time selection
        await self._show_order_time_selection(message, user_id, data)
    
    async def _handle_phone_selection(self, callback: CallbackQuery, phone: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle phone selection."""
        # Store phone in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_delivery_phone(phone)
        
        # Proceed to time selection
        await self._show_order_time_selection(callback, user_id, data)
    
    async def _handle_manual_phone_input(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle manual phone input."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_DELIVERY_PHONE)
        
        text = "📱 <b>Введите номер телефона</b>\n\nВведите номер телефона для связи с курьером:"
        keyboard = OrderKeyboard.get_back_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_time_input(self, message: Message, text: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle time input."""
        # Basic time validation (HH:MM format)
        try:
            time_parts = text.split(":")
            if len(time_parts) != 2:
                raise ValueError("Invalid format")
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Invalid time")
            
            # Store time in context
            order_state_service = await get_order_state_service()
            context = order_state_service.get_context_data(user_id)
            context.set_order_time_type("scheduled")
            context.set_scheduled_time(text)
            
            # Proceed to comment selection
            await self._show_comment_selection(message, user_id, data)
            
        except ValueError:
            await message.answer("❌ Неверный формат времени. Введите время в формате ЧЧ:ММ (например, 14:30)")
    
    async def _handle_time_selection(self, callback: CallbackQuery, time_type: str, scheduled_time: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle time selection."""
        # Store time in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_order_time_type(time_type)
        if scheduled_time:
            context.set_scheduled_time(scheduled_time)
        
        # Proceed to comment selection
        await self._show_comment_selection(callback, user_id, data)
    
    async def _handle_scheduled_time_input(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle scheduled time input."""
        await self._show_scheduled_time_input(callback, user_id, data)
    
    async def _handle_comment_input(self, message: Message, text: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle comment input."""
        # Store comment in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_comment(text)
        
        # Proceed to confirmation
        await self._show_order_confirmation(message, user_id, data)
    
    async def _handle_comment_input_request(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle comment input request."""
        order_state_service = await get_order_state_service()
        order_state_service.set_state(user_id, OrderState.ENTERING_ORDER_COMMENT)
        
        text = "💬 <b>Комментарий к заказу</b>\n\nВведите комментарий к заказу:"
        keyboard = OrderKeyboard.get_back_keyboard()
        
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_comment_selection(self, callback: CallbackQuery, comment: str, user_id: int, data: Dict[str, Any]) -> None:
        """Handle comment selection."""
        # Store comment in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_comment(comment)
        
        # Proceed to promo code selection
        await self._show_promo_code_selection(callback, user_id, data)
    
    def _format_order_summary(self, context, cart) -> str:
        """Format order summary."""
        text = "📋 <b>Подтверждение заказа</b>\n\n"
        
        # Order type
        if context.order_type == "delivery":
            text += "🚚 <b>Доставка</b>\n"
            text += f"📍 Адрес: {context.delivery_address}\n"
            text += f"📱 Телефон: {context.delivery_phone}\n"
        else:
            text += "🏪 <b>Самовывоз</b>\n"
        
        # Time
        if context.order_time_type == "asap":
            text += "⚡ Время: Как можно скорее\n"
        else:
            text += f"🕐 Время: {context.scheduled_time}\n"
        
        # Payment method
        if context.payment_method == "online":
            text += "💳 Оплата: Онлайн\n"
        else:
            text += "💵 Оплата: Наличными\n"
        
        # Comment
        if context.comment:
            text += f"💬 Комментарий: {context.comment}\n"
        
        text += "\n📦 <b>Заказ:</b>\n"
        
        # Cart items
        total = 0
        for item in cart.items:
            item_total = item.price * item.quantity
            total += item_total
            text += f"• {item.name} x{item.quantity} - {item_total // 100}₽\n"
        
        text += f"\n💰 <b>Итого: {total // 100}₽</b>"
        
        return text
