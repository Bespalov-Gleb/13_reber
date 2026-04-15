"""Message formatting utilities for Telegram."""

from typing import List, Optional

from domain.entities.cart import Cart
from domain.entities.menu_item import MenuItem
from domain.entities.order import Order
from domain.entities.user import User
from shared.utils.formatters import format_price, format_datetime, format_order_status, format_payment_method, format_order_type


class MessageFormatter:
    """Message formatter for Telegram messages."""
    
    @staticmethod
    def format_welcome_message(cafe_name: str, working_hours: str) -> str:
        """Format welcome message."""
        return f"""
🍽️ <b>Добро пожаловать в {cafe_name}!</b>

🕐 <b>Режим работы:</b> {working_hours}

Выберите действие из меню ниже:
        """.strip()
    
    @staticmethod
    def format_closed_message(cafe_name: str, working_hours: str, cafe_address: str, cafe_phone: str) -> str:
        """Format message when cafe is closed."""
        message = f"""
🚫 <b>{cafe_name} сейчас закрыто</b>

🕐 <b>Режим работы:</b> {working_hours}

📍 <b>Адрес:</b> {cafe_address}
☎️ <b>Телефон:</b> {cafe_phone}

Заказы принимаются только в рабочее время.
        """.strip()
        
        return message
    
    @staticmethod
    def format_menu_item(item: MenuItem) -> str:
        """Format menu item message."""
        message = f"<b>{item.name}</b>\n"
        
        if item.description:
            message += f"{item.description}\n"
        
        message += f"\n💰 <b>Цена:</b> {format_price(item.price)}"
        
        if item.weight:
            message += f"\n⚖️ <b>Вес:</b> {item.weight}"
        
        if item.calories:
            message += f"\n🔥 <b>Калории:</b> {item.calories} ккал"
        
        if item.ingredients:
            message += f"\n🥘 <b>Состав:</b> {item.ingredients}"
        
        if item.allergens:
            message += f"\n⚠️ <b>Аллергены:</b> {item.allergens}"
        
        if not item.is_available:
            message += "\n\n❌ <b>Временно недоступно</b>"
        
        return message
    
    @staticmethod
    def format_cart_message(cart: Cart) -> str:
        """Format cart message."""
        if cart.is_empty():
            return "🛒 <b>Корзина пуста</b>\n\nДобавьте товары из меню!"
        
        message = "🛒 <b>Ваша корзина:</b>\n\n"
        
        for item in cart.get_items_list():
            message += f"• <b>{item.name}</b>\n"
            message += f"  Количество: {item.quantity}\n"
            message += f"  Цена: {format_price(item.total_price)}\n"
            
            if item.comment:
                message += f"  Комментарий: {item.comment}\n"
            
            message += "\n"
        
        message += f"💰 <b>Итого:</b> {format_price(cart.total_price)}"
        
        return message
    
    @staticmethod
    def format_order_message(order: Order) -> str:
        """Format order message."""
        message = f"📋 <b>Заказ #{order.order_id}</b>\n\n"
        
        message += f"📅 <b>Дата:</b> {format_datetime(order.created_at)}\n"
        message += f"📦 <b>Тип:</b> {format_order_type(order.order_type)}\n"
        message += f"📊 <b>Статус:</b> {format_order_status(order.status)}\n"
        message += f"💳 <b>Оплата:</b> {format_payment_method(order.payment_method)}\n\n"
        
        message += "<b>Товары:</b>\n"
        for item in order.items:
            message += f"• {item.name} x{item.quantity} - {format_price(item.price * item.quantity)}\n"
        
        message += f"\n💰 <b>Итого:</b> {format_price(order.total)}"
        
        if order.comment:
            message += f"\n\n💬 <b>Комментарий:</b> {order.comment}"
        
        return message
    
    @staticmethod
    def format_order_confirmation(order: Order) -> str:
        """Format order confirmation message."""
        message = f"✅ <b>Заказ подтвержден!</b>\n\n"
        message += f"📋 <b>Номер заказа:</b> #{order.order_id}\n"
        message += f"📅 <b>Дата:</b> {format_datetime(order.created_at)}\n"
        message += f"📦 <b>Тип:</b> {format_order_type(order.order_type)}\n"
        message += f"💳 <b>Оплата:</b> {format_payment_method(order.payment_method)}\n\n"
        
        message += "<b>Товары:</b>\n"
        for item in order.items:
            message += f"• {item.name} x{item.quantity} - {format_price(item.price * item.quantity)}\n"
        
        message += f"\n💰 <b>Итого:</b> {format_price(order.total)}"
        
        if order.comment:
            message += f"\n\n💬 <b>Комментарий:</b> {order.comment}"
        
        message += "\n\n⏰ <b>Время приготовления:</b> 30-60 минут"
        
        return message
    
    @staticmethod
    def format_order_status_update(order: Order) -> str:
        """Format order status update message."""
        message = f"📋 <b>Заказ #{order.order_id}</b>\n\n"
        message += f"📊 <b>Статус:</b> {format_order_status(order.status)}\n"
        
        if order.status.value == "preparing":
            message += "\n👨‍🍳 Заказ начали готовить!"
        elif order.status.value == "ready":
            message += "\n🍽️ Заказ готов!"
            if order.is_pickup():
                message += "\n🚶 Можете забирать заказ!"
            else:
                message += "\n🚚 Заказ передали в доставку!"
        elif order.status.value == "delivered":
            message += "\n🎉 Заказ доставлен!"
        elif order.status.value == "picked_up":
            message += "\n🎉 Заказ получен!"
        elif order.status.value == "cancelled":
            message += "\n❌ Заказ отменен"
        
        return message
    
    @staticmethod
    def format_payment_message(payment_url: str, amount: int) -> str:
        """Format payment message."""
        return f"""
💳 <b>Оплата заказа</b>

💰 <b>Сумма:</b> {format_price(amount)}

Нажмите на кнопку ниже для оплаты:
        """.strip()
    
    @staticmethod
    def format_payment_success(amount: int) -> str:
        """Format payment success message."""
        return f"""
✅ <b>Оплата успешна!</b>

💰 <b>Сумма:</b> {format_price(amount)}

Заказ будет обработан в ближайшее время.
        """.strip()
    
    @staticmethod
    def format_payment_failed() -> str:
        """Format payment failed message."""
        return """
❌ <b>Оплата не прошла</b>

Попробуйте еще раз или выберите другой способ оплаты.
        """.strip()
    
    @staticmethod
    def format_delivery_info(address: str, phone: str, comment: Optional[str] = None) -> str:
        """Format delivery information."""
        message = f"""
🚚 <b>Информация о доставке</b>

📍 <b>Адрес:</b> {address}
📞 <b>Телефон:</b> {phone}
        """.strip()
        
        if comment:
            message += f"\n💬 <b>Комментарий:</b> {comment}"
        
        return message
    
    @staticmethod
    def format_pickup_info(phone: str, comment: Optional[str] = None) -> str:
        """Format pickup information."""
        message = f"""
🚶 <b>Информация о самовывозе</b>

📞 <b>Телефон:</b> {phone}
        """.strip()
        
        if comment:
            message += f"\n💬 <b>Комментарий:</b> {comment}"
        
        return message
    
    @staticmethod
    def format_error_message(error: str) -> str:
        """Format error message."""
        return f"❌ <b>Ошибка:</b> {error}"
    
    @staticmethod
    def format_success_message(message: str) -> str:
        """Format success message."""
        return f"✅ {message}"
    
    @staticmethod
    def format_info_message(message: str) -> str:
        """Format info message."""
        return f"ℹ️ {message}"
    
    @staticmethod
    def format_order_status_notification(order: Order, status) -> str:
        """Format order status notification message."""
        # Map status to emoji and text
        status_messages = {
            "pending": "✅ Заказ принят",
            "confirmed": "✅ Заказ подтвержден", 
            "preparing": "👨‍🍳 Заказ готовится",
            "ready": "🚶 Заказ готов к самовывозу" if order.order_type.value == "pickup" else "🚚 Заказ готов к доставке",
            "delivery": "🚚 Заказ передан в доставку",
            "delivered": "🎉 Заказ доставлен",
            "picked_up": "🎉 Заказ выполнен",
            "cancelled": "❌ Заказ отменен",
            "refunded": "💰 Заказ возвращен"
        }
        
        status_text = status_messages.get(status.value, f"📋 Статус заказа изменен: {status.value}")
        
        message = f"{status_text}\n\n"
        message += f"📋 <b>Заказ #{order.order_id[:8]}</b>\n"
        message += f"💰 <b>Сумма:</b> {format_price(order.total)}\n"
        
        if order.order_type.value == "delivery" and order.delivery_info:
            message += f"📍 <b>Адрес:</b> {order.delivery_info.address}\n"
            if order.delivery_info.phone:
                message += f"📞 <b>Телефон:</b> {order.delivery_info.phone}\n"
        elif order.order_type.value == "pickup":
            message += f"📍 <b>Самовывоз</b>\n"
        
        if order.comment:
            message += f"💬 <b>Комментарий:</b> {order.comment}\n"
        
        # Add estimated time based on status
        if status.value == "preparing":
            message += f"\n⏱️ <b>Примерное время готовности:</b> 20-30 минут"
        elif status.value == "delivery":
            message += f"\n⏱️ <b>Примерное время доставки:</b> 30-45 минут"
        
        return message
    
    @staticmethod
    def format_admin_new_order_notification(order: Order, user: User) -> str:
        """Format admin new order notification message."""
        message = f"🆕 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        message += f"📋 <b>Заказ #{order.order_id[:8]}</b>\n"
        message += f"👤 <b>Клиент:</b> {user.first_name or 'Не указано'}"
        if user.last_name:
            message += f" {user.last_name}"
        message += f"\n📱 <b>Telegram:</b> @{user.username or 'Не указан'} (ID: {user.telegram_id})\n"
        
        if user.phone:
            message += f"📞 <b>Телефон:</b> {user.phone}\n"
        
        message += f"\n💰 <b>Сумма:</b> {format_price(order.total)}\n"
        message += f"📦 <b>Тип:</b> {'Доставка' if order.order_type.value == 'delivery' else 'Самовывоз'}\n"
        message += f"💳 <b>Оплата:</b> {format_payment_method(order.payment_method)}\n"
        
        if order.order_type.value == "delivery" and order.delivery_info:
            message += f"\n📍 <b>Адрес доставки:</b>\n{order.delivery_info.address}\n"
            if order.delivery_info.phone:
                message += f"📞 <b>Телефон для доставки:</b> {order.delivery_info.phone}\n"
            if order.delivery_info.comment:
                message += f"💬 <b>Комментарий к доставке:</b> {order.delivery_info.comment}\n"
        elif order.order_type.value == "pickup":
            message += f"\n📍 <b>Самовывоз</b>\n"
        
        if order.comment:
            message += f"\n💬 <b>Комментарий к заказу:</b> {order.comment}\n"
        
        # Add order items
        message += f"\n📦 <b>Состав заказа:</b>\n"
        for item in order.items:
            message += f"• {item.name} x{item.quantity} - {format_price(item.price * item.quantity)}\n"
            if item.comment:
                message += f"  💬 {item.comment}\n"
        
        message += f"\n🕐 <b>Время заказа:</b> {format_datetime(order.created_at)}"
        
        return message
    
    @staticmethod
    def format_admin_order_management_message(order: Order, user: User) -> str:
        """Format admin order management message with action buttons."""
        message = f"📋 <b>УПРАВЛЕНИЕ ЗАКАЗОМ</b>\n\n"
        message += f"🆔 <b>Заказ #{order.order_id[:8]}</b>\n"
        message += f"👤 <b>Клиент:</b> {user.first_name or 'Не указано'}"
        if user.last_name:
            message += f" {user.last_name}"
        message += f"\n📱 <b>Telegram:</b> @{user.username or 'Не указан'} (ID: {user.telegram_id})\n"
        
        if user.phone:
            message += f"📞 <b>Телефон:</b> {user.phone}\n"
        
        message += f"\n💰 <b>Сумма:</b> {format_price(order.total)}\n"
        message += f"📦 <b>Тип:</b> {'Доставка' if order.order_type.value == 'delivery' else 'Самовывоз'}\n"
        message += f"💳 <b>Оплата:</b> {format_payment_method(order.payment_method)}\n"
        message += f"📊 <b>Статус:</b> {format_order_status(order.status)}\n"
        
        if order.order_type.value == "delivery" and order.delivery_info:
            message += f"\n📍 <b>Адрес доставки:</b>\n{order.delivery_info.address}\n"
            if order.delivery_info.phone:
                message += f"📞 <b>Телефон для доставки:</b> {order.delivery_info.phone}\n"
            if order.delivery_info.comment:
                message += f"💬 <b>Комментарий к доставке:</b> {order.delivery_info.comment}\n"
        elif order.order_type.value == "pickup":
            message += f"\n📍 <b>Самовывоз</b>\n"
        
        if order.comment:
            message += f"\n💬 <b>Комментарий к заказу:</b> {order.comment}\n"
        
        # Add order items
        message += f"\n📦 <b>Состав заказа:</b>\n"
        for item in order.items:
            message += f"• {item.name} x{item.quantity} - {format_price(item.price * item.quantity)}\n"
            if item.comment:
                message += f"  💬 {item.comment}\n"
        
        message += f"\n🕐 <b>Время заказа:</b> {format_datetime(order.created_at)}"
        
        return message