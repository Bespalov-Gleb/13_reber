"""Cart handler for Telegram bot."""

from typing import Any, Dict

from aiogram.types import CallbackQuery, Message
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.cart_keyboard import CartKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from infrastructure.telegram.utils.callback_parser import CallbackParser
from app.dependencies import get_cart_service


class CartHandler(BaseHandler):
    """Handler for cart operations."""
    
    def _register_handlers(self) -> None:
        """Register cart handlers."""
        # Message handlers
        self.router.message.register(
            self.handle_cart_command,
            F.text == "🛒 Корзина"
        )
        
        # Callback handlers
        self.router.callback_query.register(
            self.handle_cart_callback,
            F.data.startswith("cart")
        )
        
        self.router.callback_query.register(
            self.handle_quantity_callback,
            F.data.startswith("quantity")
        )
    
    async def handle_cart_command(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle cart command."""
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
        
        # Format cart message
        cart_text = MessageFormatter.format_cart_message(cart)
        
        # Create cart keyboard
        keyboard = CartKeyboard.get_cart_keyboard(cart)
        
        await message.answer(
            text=cart_text,
            reply_markup=keyboard
        )
        
        self.logger.info(
            "Cart command handled",
            user_id=user_id,
            items_count=cart.item_count,
            total=cart.total_price
        )
    
    async def handle_cart_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle cart callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        action = CallbackParser.get_cart_action(callback_data)
        
        if not action:
            # Treat bare "cart" as open cart
            if callback_data == "cart":
                session = data.get("session")
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
                    cart_text = MessageFormatter.format_cart_message(cart)
                    keyboard = CartKeyboard.get_cart_keyboard(cart)
                    await self.safe_edit_message(
                        callback.message,
                        text=cart_text,
                        reply_markup=keyboard
                    )

                await callback.answer()
                self.logger.info(
                    "Cart view opened",
                    user_id=user_id
                )
                return
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        # Get cart service
        session = data.get("session")
        if session is None:
            cart_service = await get_cart_service(data)
        else:
            from app.dependencies import container
            cart_service = container.get_cart_service(session)
        
        if action == "add":
            # Add item to cart
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            if not item_id:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            
            # Show quantity selection (default 1)
            keyboard = CartKeyboard.get_quantity_keyboard(item_id)
            
            await self.safe_edit_message(
                callback.message,
                text="🛒 <b>Добавить в корзину</b>\n\nКоличество: <b>1</b>",
                reply_markup=keyboard
            )
            
        elif action == "add_confirm":
            # Confirm adding to cart
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            quantity_str = parsed.get("quantity")
            quantity = int(quantity_str) if quantity_str and quantity_str.isdigit() else None
            
            if not item_id or not quantity:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            
            # Directly add to cart (MVP: skip comment step)
            cart = await cart_service.add_item_to_cart(user_id, item_id, quantity)
            await self.safe_edit_message(
                callback.message,
                text="✅ <b>Товар добавлен в корзину!</b>",
                reply_markup=CartKeyboard.get_back_to_item_keyboard(item_id)
            )
            
        elif action == "add_final":
            # Add to cart without comment
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            quantity_str = parsed.get("quantity")
            quantity = int(quantity_str) if quantity_str and quantity_str.isdigit() else None
            
            if not item_id or not quantity:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            
            # Add to cart
            cart = await cart_service.add_item_to_cart(user_id, item_id, quantity)
            
            await self.safe_edit_message(
                callback.message,
                text="✅ <b>Товар добавлен в корзину!</b>",
                reply_markup=CartKeyboard.get_back_to_item_keyboard(item_id)
            )
            
        elif action == "add_comment":
            # Request comment (temporarily disabled in MVP, keep for future)
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            quantity_str = parsed.get("quantity")
            quantity = int(quantity_str) if quantity_str and quantity_str.isdigit() else None
            if not item_id or not quantity:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            await self.safe_edit_message(
                callback.message,
                text="✏️ <b>Добавить комментарий</b>\n\nВведите комментарий к заказу:",
                reply_markup=CartKeyboard.get_cancel_keyboard()
            )

        elif action == "edit":
            # Enter item-by-item edit mode: show first item details
            session = data.get("session")
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            items = cart.get_items_list()
            if not items:
                await callback.answer("❌ Корзина пуста")
                return
            current = items[0]
            # Load menu item for photo/details
            from app.dependencies import get_menu_service
            menu_service = await get_menu_service(data) if session is None else container.get_menu_service(session)
            menu_item = await menu_service.get_menu_item(current.item_id)
            if not menu_item:
                await callback.answer("❌ Блюдо не найдено")
                return
            # Show item edit screen
            text = MessageFormatter.format_menu_item(menu_item) + f"\n\nТекущее количество: <b>{current.quantity}</b>"
            prev_id = items[-1].item_id if len(items) > 1 else None
            next_id = items[1].item_id if len(items) > 1 else None
            keyboard = CartKeyboard.get_item_edit_keyboard(current.item_id, prev_id, next_id)
            if menu_item.image_url:
                try:
                    await callback.message.delete()
                    await callback.message.answer_photo(photo=menu_item.image_url, caption=text, reply_markup=keyboard)
                except Exception:
                    await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
            else:
                await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
            await callback.answer()
            return
        elif action == "update":
            # Increment/decrement item quantity
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            op = parsed.get("op")
            if not item_id or op not in {"inc", "dec"}:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            session = data.get("session")
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            # Find current quantity
            current_item = next((i for i in cart.get_items_list() if i.item_id == item_id), None)
            if not current_item:
                await callback.answer("❌ Позиция не найдена")
                return
            new_qty = current_item.quantity + (1 if op == "inc" else -1)
            new_qty = max(0, min(99, new_qty))
            if new_qty == 0:
                await cart_service.remove_item_from_cart(user_id, item_id)
            else:
                await cart_service.update_item_quantity(user_id, item_id, new_qty)
            # Reload for display
            from app.dependencies import get_menu_service
            menu_service = await get_menu_service(data) if session is None else container.get_menu_service(session)
            menu_item = await menu_service.get_menu_item(item_id)
            cart = await cart_service.get_or_create_cart(user_id)
            updated_item = next((i for i in cart.get_items_list() if i.item_id == item_id), None)
            # If removed, go back to cart
            if updated_item is None:
                cart_text = MessageFormatter.format_cart_message(cart)
                await self.safe_edit_message(callback.message, text=cart_text, reply_markup=CartKeyboard.get_cart_keyboard(cart))
                await callback.answer()
                return
            # Otherwise update item edit screen
            text = MessageFormatter.format_menu_item(menu_item) + f"\n\nТекущее количество: <b>{updated_item.quantity}</b>"
            # Determine neighbors for navigation
            items = cart.get_items_list()
            idx = next((i for i, it in enumerate(items) if it.item_id == item_id), 0)
            prev_id = items[idx - 1].item_id if len(items) > 1 else None
            next_id = items[(idx + 1) % len(items)].item_id if len(items) > 1 else None
            if len(items) == 1:
                prev_id = None
                next_id = None
            keyboard = CartKeyboard.get_item_edit_keyboard(item_id, prev_id, next_id)
            # Always refresh media as a new message when item has photo
            if menu_item.image_url:
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await callback.message.answer_photo(photo=menu_item.image_url, caption=text, reply_markup=keyboard)
            else:
                await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
            await callback.answer()
            return
        elif action == "navigate":
            # Navigate to previous/next item edit screen
            parsed = CallbackParser.parse_cart_callback(callback_data)
            target_item_id = parsed.get("item_id")
            if not target_item_id:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            session = data.get("session")
            if session is None:
                cart_service = await get_cart_service(data)
            else:
                from app.dependencies import container
                cart_service = container.get_cart_service(session)
            cart = await cart_service.get_or_create_cart(user_id)
            items = cart.get_items_list()
            from app.dependencies import get_menu_service
            menu_service = await get_menu_service(data) if session is None else container.get_menu_service(session)
            menu_item = await menu_service.get_menu_item(target_item_id)
            if not menu_item:
                await callback.answer("❌ Блюдо не найдено")
                return
            current = next((i for i in items if i.item_id == target_item_id), None)
            qty = current.quantity if current else 1
            text = MessageFormatter.format_menu_item(menu_item) + f"\n\nТекущее количество: <b>{qty}</b>"
            if current:
                idx = items.index(current)
                prev_id = items[idx - 1].item_id if len(items) > 1 else None
                next_id = items[(idx + 1) % len(items)].item_id if len(items) > 1 else None
                if len(items) == 1:
                    prev_id = None
                    next_id = None
            else:
                prev_id = None
                next_id = None
            keyboard = CartKeyboard.get_item_edit_keyboard(target_item_id, prev_id, next_id)
            if menu_item.image_url:
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await callback.message.answer_photo(photo=menu_item.image_url, caption=text, reply_markup=keyboard)
            else:
                await self.safe_edit_message(callback.message, text=text, reply_markup=keyboard)
            await callback.answer()
            return
            # Request comment
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            quantity_str = parsed.get("quantity")
            quantity = int(quantity_str) if quantity_str and quantity_str.isdigit() else None
            
            if not item_id or not quantity:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            
            # Store item data for comment
            # TODO: Implement comment handling
            
            await self.safe_edit_message(
                callback.message,
                text="✏️ <b>Добавить комментарий</b>\n\nВведите комментарий к заказу:",
                reply_markup=CartKeyboard.get_cancel_keyboard()
            )
            
        elif action == "remove":
            # Remove item from cart
            parsed = CallbackParser.parse_cart_callback(callback_data)
            item_id = parsed.get("item_id")
            if not item_id:
                await callback.answer("❌ Ошибка: неверные данные")
                return
            
            cart = await cart_service.remove_item_from_cart(user_id, item_id)
            
            if cart.is_empty():
                await self.safe_edit_message(
                    callback.message,
                    text="🛒 <b>Корзина пуста</b>\n\nДобавьте товары из меню!",
                    reply_markup=CartKeyboard.get_empty_cart_keyboard()
                )
            else:
                cart_text = MessageFormatter.format_cart_message(cart)
                keyboard = CartKeyboard.get_cart_keyboard(cart)
                
                await self.safe_edit_message(
                    callback.message,
                    text=cart_text,
                    reply_markup=keyboard
                )
            
        elif action == "clear":
            # Clear cart
            await cart_service.clear_cart(user_id)
            
            await self.safe_edit_message(
                callback.message,
                text="🗑️ <b>Корзина очищена</b>",
                reply_markup=CartKeyboard.get_empty_cart_keyboard()
            )
            
        elif action == "order":
            # Proceed to order
            cart = await cart_service.get_or_create_cart(user_id)
            
            if cart.is_empty():
                await callback.answer("❌ Корзина пуста")
                return
            
            # TODO: Implement order flow
            await self.safe_edit_message(
                callback.message,
                text="🚚 <b>Оформление заказа</b>\n\nВыберите способ получения:",
                reply_markup=CartKeyboard.get_order_type_keyboard()
            )
        
        await callback.answer()
        
        self.logger.info(
            "Cart callback handled",
            user_id=user_id,
            action=action
        )
    
    async def handle_quantity_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle quantity selection callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse quantity data
        parts = callback_data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        item_id = parts[1]
        try:
            quantity = int(parts[2])
        except ValueError:
            await callback.answer("❌ Неверное количество")
            return
        
        if quantity < 1 or quantity > 99:
            await callback.answer("❌ Неверное количество")
            return
        
        # Update quantity keyboard
        keyboard = CartKeyboard.get_quantity_keyboard(item_id, quantity)
        
        await self.safe_edit_message(
            callback.message,
            text=f"🛒 <b>Добавить в корзину</b>\n\nКоличество: <b>{quantity}</b>",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
        self.logger.info(
            "Quantity callback handled",
            user_id=user_id,
            item_id=item_id,
            quantity=quantity
        )