"""Menu keyboard for Telegram bot."""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from infrastructure.telegram.keyboards.base_keyboard import BaseKeyboard
from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from shared.constants.bot_constants import CALLBACK_PREFIX_CATEGORY, CALLBACK_PREFIX_ITEM


class MenuKeyboard(BaseKeyboard):
    """Menu keyboard for the bot."""
    
    @staticmethod
    def get_categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
        """Get categories keyboard."""
        buttons = []
        
        # Create category buttons (2 per row)
        for i in range(0, len(categories), 2):
            row = []
            
            # First category in row
            category = categories[i]
            row.append(
                BaseKeyboard.create_callback_button(
                    text=f"📁 {category.name}",
                    prefix=CALLBACK_PREFIX_CATEGORY,
                    id=category.category_id
                )
            )
            
            # Second category in row (if exists)
            if i + 1 < len(categories):
                category = categories[i + 1]
                row.append(
                    BaseKeyboard.create_callback_button(
                        text=f"📁 {category.name}",
                        prefix=CALLBACK_PREFIX_CATEGORY,
                        id=category.category_id
                    )
                )
            
            buttons.append(row)
        
        # Add navigation buttons
        buttons.append([
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_menu_items_keyboard(menu_items: List[MenuItem], category_id: str) -> InlineKeyboardMarkup:
        """Get menu items keyboard."""
        buttons = []
        
        # Create menu item buttons (1 per row for better readability)
        for item in menu_items:
            # Create button text with price
            button_text = f"🍽️ {item.name} - {item.price // 100}₽"
            
            buttons.append([
                BaseKeyboard.create_callback_button(
                    text=button_text,
                    prefix=CALLBACK_PREFIX_ITEM,
                    id=item.item_id
                )
            ])
        
        # Add navigation buttons
        buttons.append([
            InlineKeyboardButton(text="🔙 К категориям", callback_data="menu"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_menu_item_keyboard(menu_item: MenuItem) -> InlineKeyboardMarkup:
        """Get menu item actions keyboard."""
        buttons = []
        
        # Quantity control like in cart edit: if not in cart, show only plus; else show -/+
        # We cannot know cart quantity here without service; so show generic + button
        if menu_item.is_available:
            buttons.append([
                BaseKeyboard.create_callback_button(
                    text="➕",
                    prefix="cart",
                    action="add",
                    item_id=menu_item.item_id
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    text="❌ Временно недоступно",
                    callback_data="unavailable"
                )
            ])
        
        # Navigation buttons
        buttons.append([
            InlineKeyboardButton(text="🔙 К категории", callback_data=f"category:id:{menu_item.category_id}"),
            InlineKeyboardButton(text="📖 Меню", callback_data="menu")
        ])
        
        buttons.append([
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_back_to_categories_keyboard() -> InlineKeyboardMarkup:
        """Get back to categories keyboard."""
        buttons = [
            [
                InlineKeyboardButton(text="🔙 К категориям", callback_data="menu"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_quantity_keyboard(item_id: str, current_quantity: int = 1) -> InlineKeyboardMarkup:
        """Get quantity selection keyboard."""
        buttons = []
        
        # Quantity buttons (1-5)
        quantity_row = []
        for i in range(1, 6):
            if i == current_quantity:
                quantity_row.append(
                    InlineKeyboardButton(
                        text=f"[{i}]",
                        callback_data=f"quantity:{item_id}:{i}"
                    )
                )
            else:
                quantity_row.append(
                    InlineKeyboardButton(
                        text=str(i),
                        callback_data=f"quantity:{item_id}:{i}"
                    )
                )
        buttons.append(quantity_row)
        
        # Control buttons
        control_row = []
        if current_quantity > 1:
            control_row.append(
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"quantity:{item_id}:{current_quantity - 1}"
                )
            )
        
        control_row.append(
            InlineKeyboardButton(
                text="➕",
                callback_data=f"quantity:{item_id}:{current_quantity + 1}"
            )
        )
        buttons.append(control_row)
        
        # Action buttons
        buttons.append([
            BaseKeyboard.create_callback_button(
                text="✅ Добавить в корзину",
                prefix="cart",
                action="add_confirm",
                item_id=item_id,
                quantity=current_quantity
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"item:{item_id}")
        ])
        
        return BaseKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_comment_keyboard(item_id: str, quantity: int) -> InlineKeyboardMarkup:
        """Get comment keyboard."""
        buttons = [
            [
                BaseKeyboard.create_callback_button(
                    text="✅ Без комментария",
                    prefix="cart",
                    action="add_final",
                    item_id=item_id,
                    quantity=quantity
                )
            ],
            [
                BaseKeyboard.create_callback_button(
                    text="✏️ Добавить комментарий",
                    prefix="cart",
                    action="add_comment",
                    item_id=item_id,
                    quantity=quantity
                )
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"item:{item_id}")
            ]
        ]
        
        return BaseKeyboard.create_inline_keyboard(buttons)