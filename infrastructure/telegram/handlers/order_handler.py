"""Order handler for Telegram bot."""

from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.cart_keyboard import CartKeyboard
from infrastructure.telegram.keyboards.order_keyboard import OrderKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.order_service import OrderService
from domain.services.cart_service import CartService
from domain.services.user_service import UserService
from domain.services.notification_service import NotificationService
from domain.services.order_state_service import OrderStateService
from infrastructure.external.maps.yandex_maps import YandexMapsProvider
from shared.types.order_states import OrderState
from app.dependencies import (
    get_order_service, get_cart_service, get_user_service, 
    get_notification_service, get_order_state_service, get_maps_service
)
from infrastructure.telegram.handlers.order_handler_helpers import OrderHandlerHelpers


class OrderHandler(BaseHandler):
    """Handler for order operations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helpers = OrderHandlerHelpers(self.logger)
    
    def _register_handlers(self) -> None:
        """Register order handlers."""
        # Message handlers
        self.router.message.register(
            self.handle_order_command,
            F.text == "🚚 Оформить заказ"
        )
        
        # Text message handler for order flow
        self.router.message.register(
            self.handle_order_text_message,
            F.text
        )
        
        # Callback handlers - order by specificity
        self.router.callback_query.register(
            self.handle_order_address_callback,
            F.data.startswith("order:address")
        )
        self.router.callback_query.register(
            self.handle_order_phone_callback,
            F.data.startswith("order:phone")
        )
        self.router.callback_query.register(
            self.handle_order_time_callback,
            F.data.startswith("order:time")
        )
        self.router.callback_query.register(
            self.handle_order_comment_callback,
            F.data.startswith("order:comment")
        )
        self.router.callback_query.register(
            self.handle_order_promo_callback,
            F.data.startswith("order:promo")
        )
        self.router.callback_query.register(
            self.handle_order_type_callback,
            F.data.startswith("order:type")
        )
        self.router.callback_query.register(
            self.handle_payment_method_callback,
            F.data.startswith("order:payment")
        )
        self.router.callback_query.register(
            self.handle_order_confirm_callback,
            F.data.startswith("order:confirm")
        )
        self.router.callback_query.register(
            self.handle_order_edit_callback,
            F.data.startswith("order:edit")
        )
        # Generic 'order' entry point from main menu
        self.router.callback_query.register(
            self.handle_order_callback,
            F.data == "order"
        )
        # Back and cancel actions
        self.router.callback_query.register(
            self.handle_order_back_callback,
            F.data == "order:back"
        )
        self.router.callback_query.register(
            self.handle_order_cancel_callback,
            F.data == "order:cancel"
        )
    
    async def handle_order_command(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle order command."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)
        
        # Check if cafe is open
        from app.config import get_settings
        from shared.utils.helpers import is_working_hours
        from infrastructure.telegram.keyboards.main_keyboard import MainKeyboard
        
        settings = get_settings()
        if not is_working_hours(settings.cafe_working_hours):
            closed_message = MessageFormatter.format_closed_message(
                cafe_name=settings.cafe_name,
                working_hours=settings.cafe_working_hours,
                cafe_address=settings.cafe_address,
                cafe_phone=settings.cafe_phone
            )
            await message.answer(
                text=closed_message,
                reply_markup=MainKeyboard.get_back_to_main()
            )
            return
        
        # Get cart service
        session = data.get("session")
        if session is None:
            cart_service = await get_cart_service(data)
        else:
            from app.dependencies import container
            cart_service = container.get_cart_service(session)
        
        # Get user's cart
        cart = await cart_service.get_or_create_cart(user_id)
        
        if cart.is_empty():
            await message.answer(
                text="🛒 <b>Корзина пуста</b>\n\nДобавьте товары из меню!",
                reply_markup=CartKeyboard.get_empty_cart_keyboard()
            )
            return
        
        # Start order flow
        await self.helpers._show_order_type_selection(message, user_id, data)
        
        self.logger.info(
            "Order command handled",
            user_id=user_id,
            items_count=cart.item_count,
            total=cart.total_price
        )
    
    async def handle_order_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle order callback."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Entry point from main menu ("order")
        if callback_data == "order":
            # Check if cafe is open
            from app.config import get_settings
            from shared.utils.helpers import is_working_hours
            from infrastructure.telegram.keyboards.main_keyboard import MainKeyboard
            
            settings = get_settings()
            if not is_working_hours(settings.cafe_working_hours):
                closed_message = MessageFormatter.format_closed_message(
                    cafe_name=settings.cafe_name,
                    working_hours=settings.cafe_working_hours,
                    cafe_address=settings.cafe_address,
                    cafe_phone=settings.cafe_phone
                )
                await self.safe_edit_message(
                    callback.message,
                    text=closed_message,
                    reply_markup=MainKeyboard.get_back_to_main()
                )
                await callback.answer()
                return
            
            # Ensure cart exists
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            if cart.is_empty():
                await self.safe_edit_message(
                    callback.message,
                    text="🛒 <b>Корзина пуста</b>\n\nДобавьте товары из меню!",
                    reply_markup=CartKeyboard.get_empty_cart_keyboard()
                )
            else:
                # Start order flow
                await self.helpers._show_order_type_selection(callback, user_id, data)
            await callback.answer()
            return
        
        # Fallback actions (e.g., order:back)
        action = CallbackParser.get_action(callback_data)
        if action == "back":
            # Handle back navigation based on current state
            await self._handle_back_navigation(callback, user_id, data)
        
        await callback.answer()
    
    async def _handle_back_navigation(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle back navigation based on current state."""
        order_state_service = await get_order_state_service()
        current_state = order_state_service.get_state(user_id)
        
        if current_state == OrderState.SELECTING_ORDER_TYPE:
            # Go back to cart
            session = data.get("session")
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            cart_text = MessageFormatter.format_cart_message(cart)
            await self.safe_edit_message(
                callback.message,
                text=cart_text,
                reply_markup=CartKeyboard.get_cart_keyboard(cart)
            )
        elif current_state == OrderState.SELECTING_ADDRESS_SUGGESTION:
            # Go back to address input
            await self.helpers._show_address_input(callback, user_id, data)
        elif current_state == OrderState.ENTERING_DELIVERY_ADDRESS:
            # Go back to payment method selection
            await self.helpers._show_payment_method_selection(callback, user_id, data)
        elif current_state == OrderState.ENTERING_DELIVERY_PHONE:
            # Go back to address input
            await self.helpers._show_address_input(callback, user_id, data)
        elif current_state == OrderState.SELECTING_ORDER_TIME:
            # Go back to phone input (if delivery) or payment method (if pickup)
            context = order_state_service.get_context_data(user_id)
            if context.order_type == "delivery":
                await self.helpers._show_delivery_phone_input(callback, user_id, data)
            else:
                await self.helpers._show_payment_method_selection(callback, user_id, data)
        elif current_state == OrderState.ENTERING_SCHEDULED_TIME:
            # Go back to time selection
            await self.helpers._show_order_time_selection(callback, user_id, data)
        elif current_state == OrderState.ENTERING_ORDER_COMMENT:
            # Go back to time selection
            await self.helpers._show_order_time_selection(callback, user_id, data)
        elif current_state == OrderState.CONFIRMING_ORDER:
            # Go back to comment selection
            await self.helpers._show_comment_selection(callback, user_id, data)
        else:
            # Default: go back to cart
            session = data.get("session")
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            cart_text = MessageFormatter.format_cart_message(cart)
            await self.safe_edit_message(
                callback.message,
                text=cart_text,
                reply_markup=CartKeyboard.get_cart_keyboard(cart)
            )
    
    async def handle_order_type_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle order type selection."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse order type
        order_type = callback_data.split(":")[-1]  # delivery or pickup
        
        if order_type not in ["delivery", "pickup"]:
            await callback.answer("❌ Ошибка: неверный тип заказа")
            return
        
        # Store order type in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_order_type(order_type)
        
        # Show payment method selection
        await self.helpers._show_payment_method_selection(callback, user_id, data)
        
        await callback.answer()
        
        self.logger.info(
            "Order type selected",
            user_id=user_id,
            order_type=order_type
        )
    
    async def handle_payment_method_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payment method selection."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse payment method
        payment_method = callback_data.split(":")[-1]  # online, cash, card
        
        if payment_method not in ["online", "cash", "card"]:
            await callback.answer("❌ Ошибка: неверный способ оплаты")
            return
        
        # Store payment method in context
        order_state_service = await get_order_state_service()
        context = order_state_service.get_context_data(user_id)
        context.set_payment_method(payment_method)
        
        # Check if delivery is selected
        if context.order_type == "delivery":
            # Show address input
            await self.helpers._show_address_input(callback, user_id, data)
        else:
            # Pickup - go directly to time selection
            await self.helpers._show_order_time_selection(callback, user_id, data)
        
        await callback.answer()
        
        self.logger.info(
            "Payment method selected",
            user_id=user_id,
            payment_method=payment_method
        )

    async def handle_order_back_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Back to order type selection."""
        await self.safe_edit_message(
            callback.message,
            text="🚚 <b>Оформление заказа</b>\n\nВыберите способ получения:",
            reply_markup=CartKeyboard.get_order_type_keyboard()
        )
        await callback.answer()

    async def handle_order_cancel_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Cancel ordering and return to cart."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        
        # Reset order context
        order_state_service = await get_order_state_service()
        order_state_service.reset_context(user_id)
        
        if session is None:
            cart_service = await get_cart_service(data)
        else:
            from app.dependencies import container
            cart_service = container.get_cart_service(session)
        cart = await cart_service.get_or_create_cart(user_id)
        cart_text = MessageFormatter.format_cart_message(cart)
        await self.safe_edit_message(
            callback.message,
            text=cart_text,
            reply_markup=CartKeyboard.get_cart_keyboard(cart)
        )
        await callback.answer()
    
    async def handle_order_confirm_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle order confirmation."""
        data = kwargs.get("data", {})
        session = data.get("session")
        user_id = data.get("user_id", callback.from_user.id)
        
        # Get services
        if session is None:
            order_service = await get_order_service(data)
            cart_service = await get_cart_service(data)
            user_service = await get_user_service(data)
            notification_service = await get_notification_service(data)
        else:
            from app.dependencies import container
            order_service = container.get_order_service(session)
            cart_service = container.get_cart_service(session)
            user_service = container.get_user_service(session)
            notification_service = container.get_notification_service(session)
        
        try:
            # Get user's cart
            cart = await cart_service.get_or_create_cart(user_id)
            
            if cart.is_empty():
                await callback.answer("❌ Корзина пуста")
                return
            
            # Get order context
            order_state_service = await get_order_state_service()
            context = order_state_service.get_context_data(user_id)
            
            # Create order with context data
            order = await order_service.create_order(
                user_id=user_id,
                cart=cart,
                order_type=context.order_type or "pickup",
                payment_method=context.payment_method or "cash",
                comment=context.comment
            )
            
            # Clear cart and reset order context
            await cart_service.clear_cart(user_id)
            order_state_service.reset_context(user_id)
            
            # Send notifications
            try:
                user = await user_service.get_user_by_id(order.user_id)
                if user:
                    # Notify user about order creation
                    await notification_service.send_order_status_notification(order, user, None)
                    # Notify admin about new order
                    await notification_service.send_admin_new_order_notification(order, user)
            except Exception as e:
                self.logger.error(f"Failed to send notifications: {e}")
            
            # Send order confirmation
            order_text = MessageFormatter.format_order_confirmation(order)
            
            from infrastructure.telegram.keyboards.main_keyboard import MainKeyboard
            await self.safe_edit_message(
                callback.message,
                text=order_text,
                reply_markup=MainKeyboard.get_back_to_main()
            )
            
            self.logger.info(
                "Order confirmed",
                user_id=user_id,
                order_id=order.order_id,
                total=order.total
            )
            
        except Exception as e:
            self.logger.error(f"Order creation error: {e}")
            from infrastructure.telegram.keyboards.main_keyboard import MainKeyboard
            await self.safe_edit_message(
                callback.message,
                text="❌ <b>Ошибка при создании заказа</b>\n\nПопробуйте еще раз.",
                reply_markup=MainKeyboard.get_back_to_main()
            )
        
        await callback.answer()
    
    async def handle_order_text_message(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle text messages during order flow."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", message.from_user.id)
        text = message.text
        
        # Get order state service
        order_state_service = await get_order_state_service()
        current_state = order_state_service.get_state(user_id)
        
        # Only process if user is in order flow
        if current_state == OrderState.IDLE:
            return
        
        try:
            if current_state == OrderState.ENTERING_DELIVERY_ADDRESS:
                await self.helpers._handle_address_input(message, text, user_id, data)
            elif current_state == OrderState.ENTERING_DELIVERY_PHONE:
                await self.helpers._handle_phone_input(message, text, user_id, data)
            elif current_state == OrderState.ENTERING_SCHEDULED_TIME:
                await self.helpers._handle_time_input(message, text, user_id, data)
            elif current_state == OrderState.ENTERING_ORDER_COMMENT:
                await self.helpers._handle_comment_input(message, text, user_id, data)
            elif current_state == OrderState.ENTERING_PROMO_CODE:
                await self.helpers._handle_promo_code_input(message, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling order text message: {e}")
            await message.answer("❌ Произошла ошибка. Попробуйте еще раз.")
    
    async def handle_order_address_callback(self, callback: CallbackQuery, data: Dict[str, Any] = None) -> None:
        """Handle address selection callbacks."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        parts = callback_data.split(":")
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        action = parts[2]
        
        try:
            if action == "select":
                # User selected an address suggestion
                suggestion_index = int(parts[3])
                await self.helpers._handle_address_selection(callback, suggestion_index, user_id, data)
            elif action == "manual":
                # User wants to enter address manually
                await self.helpers._handle_manual_address_input(callback, user_id, data)
            elif action == "retry":
                # User wants to try another address
                await self.helpers._handle_address_retry(callback, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling address callback: {e}")
            await callback.answer("❌ Произошла ошибка")
    
    async def handle_order_phone_callback(self, callback: CallbackQuery, data: Dict[str, Any] = None) -> None:
        """Handle phone selection callbacks."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        parts = callback_data.split(":")
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        action = parts[2]
        
        try:
            if action == "use_my":
                # Use user's phone number
                phone = callback.from_user.phone_number or "Не указан"
                await self.helpers._handle_phone_selection(callback, phone, user_id, data)
            elif action == "manual":
                # User wants to enter phone manually
                await self.helpers._handle_manual_phone_input(callback, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling phone callback: {e}")
            await callback.answer("❌ Произошла ошибка")
    
    async def handle_order_time_callback(self, callback: CallbackQuery, data: Dict[str, Any] = None) -> None:
        """Handle time selection callbacks."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        parts = callback_data.split(":")
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        action = parts[2]
        
        try:
            if action == "asap":
                # As soon as possible
                await self.helpers._handle_time_selection(callback, "asap", None, user_id, data)
            elif action == "scheduled":
                # Scheduled time
                await self.helpers._handle_scheduled_time_input(callback, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling time callback: {e}")
            await callback.answer("❌ Произошла ошибка")
    
    async def handle_order_comment_callback(self, callback: CallbackQuery, data: Dict[str, Any] = None) -> None:
        """Handle comment selection callbacks."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        parts = callback_data.split(":")
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        action = parts[2]
        
        try:
            if action == "add":
                # User wants to add comment
                await self.helpers._handle_comment_input_request(callback, user_id, data)
            elif action == "skip":
                # User wants to skip comment
                await self.helpers._handle_comment_selection(callback, None, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling comment callback: {e}")
            await callback.answer("❌ Произошла ошибка")
    
    async def handle_order_promo_callback(self, callback: CallbackQuery, data: Dict[str, Any] = None) -> None:
        """Handle promo code selection callbacks."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", callback.from_user.id)
        
        try:
            await self.helpers._handle_promo_code_callback(callback, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling promo callback: {e}")
            await callback.answer("❌ Произошла ошибка")
    
    async def handle_order_edit_callback(self, callback: CallbackQuery, data: Dict[str, Any] = None) -> None:
        """Handle order edit callback."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", callback.from_user.id)
        
        try:
            # Reset to order type selection
            order_state_service = await get_order_state_service()
            order_state_service.set_state(user_id, OrderState.SELECTING_ORDER_TYPE)
            
            await self.helpers._show_order_type_selection(callback, user_id, data)
        except Exception as e:
            self.logger.error(f"Error handling edit callback: {e}")
            await callback.answer("❌ Произошла ошибка")