"""Order handler for Telegram bot."""

from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.cart_keyboard import CartKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.order_service import OrderService
from domain.services.cart_service import CartService
from app.dependencies import get_order_service, get_cart_service


class OrderHandler(BaseHandler):
    """Handler for order operations."""
    
    def _register_handlers(self) -> None:
        """Register order handlers."""
        # Message handlers
        self.router.message.register(
            self.handle_order_command,
            F.text == "🚚 Оформить заказ"
        )
        
        # Callback handlers
        # More specific callbacks must be registered before generic ones
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
        # Generic 'order' entry point from main menu
        self.router.callback_query.register(
            self.handle_order_callback,
            F.data == "order"
        )
        # Back and cancel actions on payment selection
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
        
        # Show order type selection
        await message.answer(
            text="🚚 <b>Оформление заказа</b>\n\nВыберите способ получения:",
            reply_markup=CartKeyboard.get_order_type_keyboard()
        )
        
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
                await self.safe_edit_message(
                    callback.message,
                    text="🚚 <b>Оформление заказа</b>\n\nВыберите способ получения:",
                    reply_markup=CartKeyboard.get_order_type_keyboard()
                )
            await callback.answer()
            return
        
        # Fallback actions (e.g., order:back)
        action = CallbackParser.get_action(callback_data)
        if action == "back":
            # Go back to cart
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            from infrastructure.telegram.utils.message_formatter import MessageFormatter
            cart_text = MessageFormatter.format_cart_message(cart)
            await self.safe_edit_message(
                callback.message,
                text=cart_text,
                reply_markup=CartKeyboard.get_cart_keyboard(cart)
            )
        
        await callback.answer()
    
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
        
        # Store order type in user data (in real app, use Redis or database)
        # For now, we'll pass it through the callback data
        
        # Show payment method selection
        await self.safe_edit_message(
            callback.message,
            text="💳 <b>Способ оплаты</b>\n\nВыберите способ оплаты:",
            reply_markup=CartKeyboard.get_payment_method_keyboard()
        )
        
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
            await callback.answer("❌ Корзина пуста")
            return
        
        # Format order confirmation
        order_text = f"📋 <b>Подтверждение заказа</b>\n\n"
        order_text += f"🛒 <b>Товары:</b>\n"
        
        from infrastructure.telegram.utils.message_formatter import MessageFormatter
        from shared.utils.formatters import format_price
        for item in cart.get_items_list():
            order_text += f"• {item.name} x{item.quantity} - {format_price(item.price * item.quantity)}\n"
        
        order_text += f"\n💰 <b>Итого:</b> {cart.total_price // 100}₽\n"
        order_text += f"💳 <b>Оплата:</b> {payment_method}\n"
        
        if payment_method == "online":
            order_text += "\n⚠️ После подтверждения заказа вы будете перенаправлены на страницу оплаты."
        elif payment_method == "cash":
            order_text += "\n💵 Оплата наличными при получении."
        elif payment_method == "card":
            order_text += "\n💳 Оплата картой при получении."
        
        # Show order confirmation
        await self.safe_edit_message(
            callback.message,
            text=order_text,
            reply_markup=CartKeyboard.get_order_confirmation_keyboard()
        )
        
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
        else:
            from app.dependencies import container
            order_service = container.get_order_service(session)
            cart_service = container.get_cart_service(session)
        
        try:
            # Get user's cart
            cart = await cart_service.get_or_create_cart(user_id)
            
            if cart.is_empty():
                await callback.answer("❌ Корзина пуста")
                return
            
            # Create order
            order = await order_service.create_order(
                user_id=user_id,
                cart=cart,
                order_type="delivery",  # TODO: Get from user data
                payment_method="online",  # TODO: Get from user data
                comment=None  # TODO: Get from user input
            )
            
            # Clear cart
            await cart_service.clear_cart(user_id)
            
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