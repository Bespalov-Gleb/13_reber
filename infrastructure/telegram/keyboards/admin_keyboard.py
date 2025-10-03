"""Admin keyboard for Telegram bot."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from shared.constants.bot_constants import CALLBACK_PREFIX_ADMIN


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