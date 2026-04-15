"""Admin keyboard for Telegram bot."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from shared.constants.bot_constants import CALLBACK_PREFIX_ADMIN
from shared.types.user_types import UserStatus


class AdminKeyboard(BaseKeyboard):
    """Admin keyboard for the bot."""
    
    @staticmethod
    def get_admin_menu() -> InlineKeyboardMarkup:
        """Get admin menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🍽️ Управление меню", callback_data="admin:menu"),
                InlineKeyboardButton(text="📋 Заказы", callback_data="admin:orders"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users"),
            ],
            [
                InlineKeyboardButton(text="💰 Платежи", callback_data="admin:payments"),
                InlineKeyboardButton(text="📢 Уведомления", callback_data="admin:notifications"),
            ],
            [
                InlineKeyboardButton(text="🪑 Бронирования", callback_data="admin_bookings:menu"),
            ],
            [
                InlineKeyboardButton(text="🍽️ iiko CRM", callback_data="admin_iiko:menu"),
            ],
            [
                InlineKeyboardButton(text="🚚 Курьеры", callback_data="admin_couriers:menu"),
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_menu_management_keyboard() -> InlineKeyboardMarkup:
        """Get menu management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📁 Категории", callback_data="menu_edit:categories"),
                InlineKeyboardButton(text="🍽️ Блюда", callback_data="menu_edit:items"),
            ],
            [
                InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category"),
                InlineKeyboardButton(text="➕ Добавить блюдо", callback_data="add_item"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_orders_management_keyboard() -> InlineKeyboardMarkup:
        """Get orders management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="⏳ Ожидающие", callback_data="orders:pending"),
                InlineKeyboardButton(text="👨‍🍳 Готовятся", callback_data="orders:preparing"),
            ],
            [
                InlineKeyboardButton(text="✅ Готовые", callback_data="orders:ready"),
                InlineKeyboardButton(text="🚚 В доставке", callback_data="orders:delivery"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_categories_management_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
        """Get categories management keyboard."""
        buttons = []
        
        # Create category buttons (1 per row for better readability)
        for category in categories:
            status_icon = "✅" if category.is_active else "❌"
            button_text = f"{status_icon} {category.name}"
            
            buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"edit_category:edit:id:{category.category_id}"
                )
            ])
        
        # Add action buttons
        buttons.append([
            InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category"),
        ])
        
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="menu_edit:back"),
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_items_management_keyboard(items: List[MenuItem]) -> InlineKeyboardMarkup:
        """Get items management keyboard."""
        buttons = []
        
        # Create item buttons (1 per row for better readability)
        for item in items:
            status_icon = "✅" if item.is_available else "❌"
            button_text = f"{status_icon} {item.name} - {item.price // 100}₽"
            
            buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"edit_item:edit:id:{item.item_id}"
                )
            ])
        
        # Add action buttons
        buttons.append([
            InlineKeyboardButton(text="➕ Добавить блюдо", callback_data="add_item"),
        ])
        
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="menu_edit:back"),
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_empty_categories_keyboard() -> InlineKeyboardMarkup:
        """Get empty categories keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="➕ Добавить категорию", callback_data="add_category"),
            ],
            [
            InlineKeyboardButton(text="🔙 Назад", callback_data="menu_edit:back"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_empty_items_keyboard() -> InlineKeyboardMarkup:
        """Get empty items keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="➕ Добавить блюдо", callback_data="add_item"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu_edit:back"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_category_actions_keyboard(category_id: str) -> InlineKeyboardMarkup:
        """Get category actions keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_category:edit:id:{category_id}"),
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"edit_category:delete:id:{category_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙 К категориям", callback_data="menu_edit:categories"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_item_actions_keyboard(item_id: str) -> InlineKeyboardMarkup:
        """Get item actions keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_item:edit:id:{item_id}"),
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"edit_item:delete:id:{item_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙 К блюдам", callback_data="menu_edit:items"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)

    @staticmethod
    def get_confirm_delete_category_keyboard(category_id: str, items_count: int) -> InlineKeyboardMarkup:
        """Confirm deletion of category (with possible cascade)."""
        buttons = [
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"edit_category:delete_confirm:id:{category_id}"
                ),
                InlineKeyboardButton(
                    text="🔙 Отмена",
                    callback_data="menu_edit:categories"
                )
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)

    @staticmethod
    def get_confirm_delete_item_keyboard(item_id: str) -> InlineKeyboardMarkup:
        """Confirm deletion of a single item."""
        buttons = [
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"edit_item:delete_confirm:id:{item_id}"
                ),
                InlineKeyboardButton(
                    text="🔙 Отмена",
                    callback_data="menu_edit:items"
                )
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
        """Get back to admin keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К админ-панели", callback_data="admin:back"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_menu_management_keyboard() -> InlineKeyboardMarkup:
        """Get back to menu management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К управлению меню", callback_data="admin:menu"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_categories_keyboard() -> InlineKeyboardMarkup:
        """Get back to categories keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К категориям", callback_data="menu_edit:categories"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_items_keyboard() -> InlineKeyboardMarkup:
        """Get back to items keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К блюдам", callback_data="menu_edit:items"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_cancel_keyboard() -> InlineKeyboardMarkup:
        """Get cancel keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_editing"),
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_admin_menu() -> InlineKeyboardMarkup:
        """Get back to admin menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 Админ-панель", callback_data="admin:back"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_categories_keyboard() -> InlineKeyboardMarkup:
        """Get back to categories keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К категориям", callback_data="menu_edit:categories"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_items_keyboard() -> InlineKeyboardMarkup:
        """Get back to items keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К блюдам", callback_data="menu_edit:items"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_admin_menu_management() -> InlineKeyboardMarkup:
        """Get back to admin menu management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 Управление меню", callback_data="admin:menu"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_categories_selection_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
        """Get categories selection keyboard."""
        buttons = []
        
        # Create category buttons (2 per row)
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    category = categories[i + j]
                    row.append(
                        InlineKeyboardButton(
                            text=category.name,
                            callback_data=f"select_category:id:{category.category_id}"
                        )
                    )
            buttons.append(row)
        
        # Add cancel button
        buttons.append([
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_editing"),
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_item_edit_keyboard(item_id: str) -> InlineKeyboardMarkup:
        """Get item edit keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📝 Название", callback_data=f"edit_item:name:id:{item_id}"),
                InlineKeyboardButton(text="📄 Описание", callback_data=f"edit_item:description:id:{item_id}"),
            ],
            [
                InlineKeyboardButton(text="💰 Цена", callback_data=f"edit_item:price:id:{item_id}"),
                InlineKeyboardButton(text="🥘 Состав", callback_data=f"edit_item:ingredients:id:{item_id}"),
            ],
            [
                InlineKeyboardButton(text="⚠️ Аллергены", callback_data=f"edit_item:allergens:id:{item_id}"),
                InlineKeyboardButton(text="⚖️ Вес", callback_data=f"edit_item:weight:id:{item_id}"),
            ],
            [
                InlineKeyboardButton(text="🔥 Калории", callback_data=f"edit_item:calories:id:{item_id}"),
                InlineKeyboardButton(text="📷 Фото", callback_data=f"edit_item:image:id:{item_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu_edit:items"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_category_edit_keyboard(category_id: str) -> InlineKeyboardMarkup:
        """Get category edit keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📝 Название", callback_data=f"edit_category:name:id:{category_id}"),
                InlineKeyboardButton(text="📄 Описание", callback_data=f"edit_category:description:id:{category_id}"),
            ],
            [
                InlineKeyboardButton(text="📷 Фото", callback_data=f"edit_category:image:id:{category_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu_edit:categories"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_orders_management_keyboard() -> InlineKeyboardMarkup:
        """Get orders management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="⏳ Ожидающие", callback_data="orders:pending"),
                InlineKeyboardButton(text="👨‍🍳 В приготовлении", callback_data="orders:preparing"),
            ],
            [
                InlineKeyboardButton(text="✅ Готовые", callback_data="orders:ready"),
                InlineKeyboardButton(text="🚚 В доставке", callback_data="orders:delivery"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_orders_list_keyboard(orders: List['Order'], page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
        """Get orders list keyboard with pagination."""
        buttons = []
        
        # Show orders for current page
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_orders = orders[start_idx:end_idx]
        
        for order in page_orders:
            # Format order info: ID, status, total
            order_info = f"#{order.order_id[:8]} - {order.status.value} - {order.total // 100}₽"
            buttons.append([
                InlineKeyboardButton(
                    text=order_info,
                    callback_data=f"order_detail:{order.order_id}"
                )
            ])
        
        # Pagination buttons
        if len(orders) > per_page:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(
                    InlineKeyboardButton(text="⬅️", callback_data=f"orders:page:{page-1}")
                )
            if end_idx < len(orders):
                nav_buttons.append(
                    InlineKeyboardButton(text="➡️", callback_data=f"orders:page:{page+1}")
                )
            if nav_buttons:
                buttons.append(nav_buttons)
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin:orders")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_order_management_keyboard(order: 'Order') -> InlineKeyboardMarkup:
        """Get order management keyboard based on order status."""
        buttons = []
        
        # Status-specific buttons
        if order.status.value == "pending":
            buttons.append([
                InlineKeyboardButton(text="✅ Принять", callback_data=f"order_accept:{order.order_id}"),
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"order_cancel:{order.order_id}"),
            ])
        elif order.status.value == "preparing":
            buttons.append([
                InlineKeyboardButton(text="✅ Готов", callback_data=f"order_ready:{order.order_id}"),
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"order_cancel:{order.order_id}"),
            ])
        elif order.status.value == "ready":
            if order.order_type.value == "delivery":
                buttons.append([
                    InlineKeyboardButton(text="🚚 В доставку", callback_data=f"order_delivery:{order.order_id}"),
                ])
            else:  # pickup
                buttons.append([
                    InlineKeyboardButton(text="✅ Выдан", callback_data=f"order_picked_up:{order.order_id}"),
                ])
        elif order.status.value == "delivery":
            buttons.append([
                InlineKeyboardButton(text="✅ Доставлен", callback_data=f"order_delivered:{order.order_id}"),
            ])
        
        # Courier assignment button (if order is ready for delivery and no courier assigned)
        if order.order_type.value == "delivery" and order.status.value in ["ready", "delivery"] and not order.courier_id:
            buttons.append([
                InlineKeyboardButton(text="🚚 Назначить курьера", callback_data=f"order_assign_courier:{order.order_id}"),
            ])
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 К списку заказов", callback_data="admin:orders")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_statistics_keyboard() -> InlineKeyboardMarkup:
        """Get statistics keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📊 Обзор", callback_data="stats:overview"),
                InlineKeyboardButton(text="📈 Продажи", callback_data="stats:sales"),
            ],
            [
                InlineKeyboardButton(text="👥 Пользователи", callback_data="stats:users"),
                InlineKeyboardButton(text="🍽️ Меню", callback_data="stats:menu"),
            ],
            [
                InlineKeyboardButton(text="📅 Сегодня", callback_data="stats:today"),
                InlineKeyboardButton(text="📅 Неделя", callback_data="stats:week"),
            ],
            [
                InlineKeyboardButton(text="📅 Месяц", callback_data="stats:month"),
                InlineKeyboardButton(text="📅 Год", callback_data="stats:year"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_users_management_keyboard() -> InlineKeyboardMarkup:
        """Get users management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="👥 Все пользователи", callback_data="users:all"),
                InlineKeyboardButton(text="🆕 Новые сегодня", callback_data="users:new_today"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="users:stats"),
                InlineKeyboardButton(text="🔍 Поиск", callback_data="users:search"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_users_list_keyboard(users: List['User'], page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
        """Get users list keyboard with pagination."""
        buttons = []
        
        # Show users for current page
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_users = users[start_idx:end_idx]
        
        for user in page_users:
            # Format user info: name, username, status
            user_info = f"{user.first_name or 'Без имени'}"
            if user.username:
                user_info += f" (@{user.username})"
            if getattr(user, 'status', None) == UserStatus.BLOCKED:
                user_info += " 🚫"
            
            buttons.append([
                InlineKeyboardButton(
                    text=user_info,
                    callback_data=f"user_detail:{user.user_id}"
                )
            ])
        
        # Pagination buttons
        if len(users) > per_page:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(
                    InlineKeyboardButton(text="⬅️", callback_data=f"users:page:{page-1}")
                )
            if end_idx < len(users):
                nav_buttons.append(
                    InlineKeyboardButton(text="➡️", callback_data=f"users:page:{page+1}")
                )
            if nav_buttons:
                buttons.append(nav_buttons)
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin:users")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_user_detail_keyboard(user: 'User') -> InlineKeyboardMarkup:
        """Get user detail keyboard."""
        buttons = []
        
        # Management buttons based on user status
        if getattr(user, 'status', None) == UserStatus.BLOCKED:
            buttons.append([
                InlineKeyboardButton(text="✅ Разблокировать", callback_data=f"user_unblock:{user.user_id}"),
            ])
        else:
            buttons.append([
                InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"user_block:{user.user_id}"),
            ])
        
        # Admin role toggle
        if getattr(user, 'is_admin', False):
            buttons.append([
                InlineKeyboardButton(text="👤 Снять админа", callback_data=f"user_remove_admin:{user.user_id}"),
            ])
        else:
            buttons.append([
                InlineKeyboardButton(text="👤 Сделать админом", callback_data=f"user_make_admin:{user.user_id}"),
            ])

        buttons.append([
            InlineKeyboardButton(text="📋 Заказы", callback_data=f"user_orders:{user.user_id}"),
        ])
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 К списку пользователей", callback_data="admin:users")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_payments_management_keyboard() -> InlineKeyboardMarkup:
        """Get payments management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="💰 Все платежи", callback_data="payments:all"),
                InlineKeyboardButton(text="⏳ Ожидающие", callback_data="payments:pending"),
            ],
            [
                InlineKeyboardButton(text="✅ Завершенные", callback_data="payments:completed"),
                InlineKeyboardButton(text="❌ Неудачные", callback_data="payments:failed"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_payments_list_keyboard(payments: List['Payment'], page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
        """Get payments list keyboard with pagination."""
        buttons = []
        
        # Show payments for current page
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_payments = payments[start_idx:end_idx]
        
        for payment in page_payments:
            # Format payment info: amount, status, date
            payment_info = f"{payment.amount // 100}₽ - {payment.status.value} - {payment.created_at.strftime('%d.%m')}"
            buttons.append([
                InlineKeyboardButton(
                    text=payment_info,
                    callback_data=f"payment_detail:{payment.id}"
                )
            ])
        
        # Pagination buttons
        if len(payments) > per_page:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(
                    InlineKeyboardButton(text="⬅️", callback_data=f"payments:page:{page-1}")
                )
            if end_idx < len(payments):
                nav_buttons.append(
                    InlineKeyboardButton(text="➡️", callback_data=f"payments:page:{page+1}")
                )
            if nav_buttons:
                buttons.append(nav_buttons)
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin:payments")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_payment_detail_keyboard(payment: 'Payment') -> InlineKeyboardMarkup:
        """Get payment detail keyboard."""
        buttons = []
        
        # Management buttons based on payment status
        if payment.status.value == "succeeded":
            buttons.append([
                InlineKeyboardButton(text="💸 Возврат", callback_data=f"payment_refund:{payment.id}"),
            ])
        elif payment.status.value == "pending":
            buttons.append([
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"payment_cancel:{payment.id}"),
            ])
        
        # Back button
        buttons.append([
            InlineKeyboardButton(text="🔙 К списку платежей", callback_data="admin:payments")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_notifications_management_keyboard() -> InlineKeyboardMarkup:
        """Get notifications management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📢 Отправить", callback_data="notify:send"),
                InlineKeyboardButton(text="📝 Шаблоны", callback_data="notify:templates"),
            ],
            [
                InlineKeyboardButton(text="📋 История", callback_data="notify:history"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_notification_templates_keyboard() -> InlineKeyboardMarkup:
        """Get notification templates keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📢 Приветствие", callback_data="notify_template:welcome"),
                InlineKeyboardButton(text="📋 Заказ готов", callback_data="notify_template:order_ready"),
            ],
            [
                InlineKeyboardButton(text="🚚 Заказ в доставке", callback_data="notify_template:order_delivery"),
                InlineKeyboardButton(text="✅ Заказ доставлен", callback_data="notify_template:order_delivered"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin:notifications")
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_bookings_management_keyboard() -> InlineKeyboardMarkup:
        """Get bookings management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="📅 Все бронирования", callback_data="admin_bookings:list_all"),
                InlineKeyboardButton(text="📅 На сегодня", callback_data="admin_bookings:today"),
            ],
            [
                InlineKeyboardButton(text="⏳ Ожидающие", callback_data="admin_bookings:pending"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_iiko_management_keyboard() -> InlineKeyboardMarkup:
        """Get iiko management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔄 Синхронизировать меню", callback_data="admin_iiko:sync_menu"),
                InlineKeyboardButton(text="📊 Статус подключения", callback_data="admin_iiko:test_connection"),
            ],
            [
                InlineKeyboardButton(text="📋 Синхронизировать заказы", callback_data="admin_iiko:sync_orders"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_iiko:settings"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="admin"),
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)