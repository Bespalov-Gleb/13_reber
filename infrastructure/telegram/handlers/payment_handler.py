"""Payment handler for Telegram bot."""

from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.cart_keyboard import CartKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from infrastructure.telegram.utils.callback_parser import CallbackParser
from domain.services.payment_service import PaymentService
from domain.services.order_service import OrderService
from app.dependencies import get_payment_service, get_order_service


class PaymentHandler(BaseHandler):
    """Handler for payment operations."""
    
    def _register_handlers(self) -> None:
        """Register payment handlers."""
        # Callback handlers
        self.router.callback_query.register(
            self.handle_payment_callback,
            F.data.startswith("payment")
        )
        
        self.router.callback_query.register(
            self.handle_payment_success_callback,
            F.data.startswith("payment_success")
        )
        
        self.router.callback_query.register(
            self.handle_payment_failed_callback,
            F.data.startswith("payment_failed")
        )
    
    async def handle_payment_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payment callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        action = CallbackParser.get_action(callback_data)
        order_id = CallbackParser.get_order_id(callback_data)
        
        if not action or not order_id:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        # Get services
        session = data.get("session")
        if session is None:
            payment_service = await get_payment_service(data)
            order_service = await get_order_service(data)
        else:
            from app.dependencies import container
            payment_service = container.get_payment_service(session)
            order_service = container.get_order_service(session)
        
        try:
            if action == "create":
                # Create payment
                order = await order_service.get_order(order_id)
                if not order:
                    await callback.answer("❌ Заказ не найден")
                    return
                
                # Create payment
                payment = await payment_service.create_payment(order)
                
                # Send payment message
                payment_text = MessageFormatter.format_payment_message(
                    payment.payment_url, 
                    payment.amount
                )
                
                keyboard = CartKeyboard.create_inline_keyboard([
                    [
                        CartKeyboard.create_inline_button(
                            "💳 Оплатить",
                            payment.payment_url
                        )
                    ],
                    [
                        CartKeyboard.create_inline_button(
                            "❌ Отменить",
                            f"payment:cancel:{payment.payment_id}"
                        )
                    ]
                ])
                
                await self.safe_edit_message(
                    callback.message,
                    text=payment_text,
                    reply_markup=keyboard
                )
                
            elif action == "cancel":
                # Cancel payment
                payment_id = CallbackParser.get_payment_id(callback_data)
                if not payment_id:
                    await callback.answer("❌ Ошибка: неверные данные")
                    return
                
                success = await payment_service.cancel_payment(payment_id)
                
                if success:
                    await self.safe_edit_message(
                        callback.message,
                        text="❌ <b>Платеж отменен</b>",
                        reply_markup=CartKeyboard.get_back_to_main()
                    )
                else:
                    await callback.answer("❌ Не удалось отменить платеж")
                    return
                
            elif action == "check":
                # Check payment status
                payment_id = CallbackParser.get_payment_id(callback_data)
                if not payment_id:
                    await callback.answer("❌ Ошибка: неверные данные")
                    return
                
                payment = await payment_service.get_payment_status(payment_id)
                
                if payment.status == "succeeded":
                    await self.safe_edit_message(
                        callback.message,
                        text=MessageFormatter.format_payment_success(payment.amount),
                        reply_markup=CartKeyboard.get_back_to_main()
                    )
                elif payment.status == "cancelled":
                    await self.safe_edit_message(
                        callback.message,
                        text="❌ <b>Платеж отменен</b>",
                        reply_markup=CartKeyboard.get_back_to_main()
                    )
                else:
                    await callback.answer("⏳ Платеж еще обрабатывается")
                    return
                
        except Exception as e:
            self.logger.error(f"Payment error: {e}")
            await callback.answer("❌ Произошла ошибка при обработке платежа")
            return
        
        await callback.answer()
        
        self.logger.info(
            "Payment callback handled",
            user_id=user_id,
            action=action,
            order_id=order_id
        )
    
    async def handle_payment_success_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payment success callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse payment ID
        payment_id = CallbackParser.get_payment_id(callback_data)
        
        if not payment_id:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        # Get payment service
        session = data.get("session")
        if session is None:
            payment_service = await get_payment_service(data)
        else:
            from app.dependencies import container
            payment_service = container.get_payment_service(session)
        
        try:
            # Get payment status
            payment = await payment_service.get_payment_status(payment_id)
            
            if payment.status == "succeeded":
                await self.safe_edit_message(
                    callback.message,
                    text=MessageFormatter.format_payment_success(payment.amount),
                    reply_markup=CartKeyboard.get_back_to_main()
                )
            else:
                await self.safe_edit_message(
                    callback.message,
                    text="⏳ <b>Платеж обрабатывается</b>\n\nПопробуйте проверить статус позже.",
                    reply_markup=CartKeyboard.get_back_to_main()
                )
                
        except Exception as e:
            self.logger.error(f"Payment success error: {e}")
            await self.safe_edit_message(
                callback.message,
                text="❌ <b>Ошибка при проверке платежа</b>",
                reply_markup=CartKeyboard.get_back_to_main()
            )
        
        await callback.answer()
        
        self.logger.info(
            "Payment success callback handled",
            user_id=user_id,
            payment_id=payment_id
        )
    
    async def handle_payment_failed_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle payment failed callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        
        await self.safe_edit_message(
            callback.message,
            text=MessageFormatter.format_payment_failed(),
            reply_markup=CartKeyboard.get_back_to_main()
        )
        
        await callback.answer()
        
        self.logger.info(
            "Payment failed callback handled",
            user_id=user_id
        )