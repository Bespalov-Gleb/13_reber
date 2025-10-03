"""Base keyboard class for Telegram."""

from typing import List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from shared.constants.bot_constants import CALLBACK_SEPARATOR
from shared.utils.helpers import build_callback_data


class BaseKeyboard:
    """Base keyboard class."""
    
    @staticmethod
    def create_inline_keyboard(
        buttons: List[List[InlineKeyboardButton]],
        row_width: int = 2
    ) -> InlineKeyboardMarkup:
        """Create inline keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=buttons, row_width=row_width)
    
    @staticmethod
    def create_reply_keyboard(
        buttons: List[List[KeyboardButton]],
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
        selective: bool = False
    ) -> ReplyKeyboardMarkup:
        """Create reply keyboard."""
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective
        )
    
    @staticmethod
    def create_inline_button(
        text: str,
        callback_data: str,
        url: Optional[str] = None
    ) -> InlineKeyboardButton:
        """Create inline button."""
        if url:
            return InlineKeyboardButton(text=text, url=url)
        return InlineKeyboardButton(text=text, callback_data=callback_data)
    
    @staticmethod
    def create_reply_button(text: str) -> KeyboardButton:
        """Create reply button."""
        return KeyboardButton(text=text)
    
    @staticmethod
    def create_callback_button(
        text: str,
        prefix: str,
        **kwargs
    ) -> InlineKeyboardButton:
        """Create callback button with prefix."""
        callback_data = build_callback_data(prefix, **kwargs)
        return InlineKeyboardButton(text=text, callback_data=callback_data)
    
    @staticmethod
    def create_pagination_buttons(
        current_page: int,
        total_pages: int,
        prefix: str,
        **kwargs
    ) -> List[InlineKeyboardButton]:
        """Create pagination buttons."""
        buttons = []
        
        if current_page > 1:
            buttons.append(
                BaseKeyboard.create_callback_button(
                    "⬅️ Назад",
                    prefix,
                    page=current_page - 1,
                    **kwargs
                )
            )
        
        if current_page < total_pages:
            buttons.append(
                BaseKeyboard.create_callback_button(
                    "Вперед ➡️",
                    prefix,
                    page=current_page + 1,
                    **kwargs
                )
            )
        
        return buttons
    
    @staticmethod
    def create_navigation_buttons() -> List[InlineKeyboardButton]:
        """Create navigation buttons."""
        return [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    
    @staticmethod
    def create_confirm_buttons(
        confirm_text: str = "✅ Подтвердить",
        cancel_text: str = "❌ Отменить",
        confirm_callback: str = "confirm",
        cancel_callback: str = "cancel"
    ) -> List[InlineKeyboardButton]:
        """Create confirm/cancel buttons."""
        return [
            InlineKeyboardButton(text=confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(text=cancel_text, callback_data=cancel_callback),
        ]
    
    @staticmethod
    def create_quantity_buttons(
        current_quantity: int = 1,
        max_quantity: int = 10
    ) -> List[List[InlineKeyboardButton]]:
        """Create quantity selection buttons."""
        buttons = []
        
        # Quantity buttons
        quantity_row = []
        for i in range(1, min(max_quantity + 1, 6)):  # Max 5 buttons per row
            if i == current_quantity:
                quantity_row.append(
                    InlineKeyboardButton(
                        text=f"[{i}]",
                        callback_data=f"quantity:{i}"
                    )
                )
            else:
                quantity_row.append(
                    InlineKeyboardButton(
                        text=str(i),
                        callback_data=f"quantity:{i}"
                    )
                )
        buttons.append(quantity_row)
        
        # Control buttons
        control_row = []
        if current_quantity > 1:
            control_row.append(
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"quantity:{current_quantity - 1}"
                )
            )
        
        control_row.append(
            InlineKeyboardButton(
                text="➕",
                callback_data=f"quantity:{current_quantity + 1}"
            )
        )
        buttons.append(control_row)
        
        return buttons