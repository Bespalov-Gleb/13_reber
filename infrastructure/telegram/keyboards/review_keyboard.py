"""Review keyboard for review system."""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from domain.entities.review import Review


class ReviewKeyboard:
    """Keyboard for review system."""
    
    @staticmethod
    def create_inline_keyboard(buttons: List[List[Dict[str, Any]]]) -> InlineKeyboardMarkup:
        """Create inline keyboard from button configuration."""
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button["text"],
                        callback_data=button["callback_data"]
                    )
                )
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_inline_button(text: str, callback_data: str) -> Dict[str, Any]:
        """Create inline button configuration."""
        return {"text": text, "callback_data": callback_data}
    
    @staticmethod
    def get_rating_keyboard(order_id: Optional[str] = None, menu_item_id: Optional[str] = None) -> InlineKeyboardMarkup:
        """Get keyboard for rating selection."""
        buttons = []
        
        # Rating buttons (1-5 stars)
        for rating in range(1, 6):
            stars = "⭐" * rating
            callback_data = f"review:rating:{rating}"
            if order_id:
                callback_data += f":order:{order_id}"
            if menu_item_id:
                callback_data += f":item:{menu_item_id}"
            
            buttons.append([
                ReviewKeyboard.create_inline_button(
                    f"{stars} ({rating})",
                    callback_data
                )
            ])
        
        # Skip button
        buttons.append([
            ReviewKeyboard.create_inline_button(
                "⏭️ Пропустить",
                "review:skip"
            )
        ])
        
        return ReviewKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_comment_keyboard(review_id: str) -> InlineKeyboardMarkup:
        """Get keyboard for comment input."""
        return ReviewKeyboard.create_inline_keyboard([
            [
                ReviewKeyboard.create_inline_button(
                    "✏️ Добавить комментарий",
                    f"review:comment:add:{review_id}"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "⏭️ Пропустить",
                    f"review:comment:skip:{review_id}"
                )
            ]
        ])
    
    @staticmethod
    def get_review_confirmation_keyboard(review_id: str) -> InlineKeyboardMarkup:
        """Get keyboard for review confirmation."""
        return ReviewKeyboard.create_inline_keyboard([
            [
                ReviewKeyboard.create_inline_button(
                    "✅ Подтвердить",
                    f"review:confirm:{review_id}"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "✏️ Изменить",
                    f"review:edit:{review_id}"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "❌ Отменить",
                    f"review:cancel:{review_id}"
                )
            ]
        ])
    
    @staticmethod
    def get_review_list_keyboard(reviews: List[Review], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
        """Get keyboard for review list with pagination."""
        buttons = []
        
        # Review buttons
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_reviews = reviews[start_idx:end_idx]
        
        for review in page_reviews:
            # Truncate comment for button text
            comment_preview = ""
            if review.comment:
                comment_preview = review.comment[:30] + "..." if len(review.comment) > 30 else review.comment
            
            button_text = f"{review.get_rating_stars()}"
            if comment_preview:
                button_text += f" - {comment_preview}"
            
            buttons.append([
                ReviewKeyboard.create_inline_button(
                    button_text,
                    f"review:view:{review.review_id}"
                )
            ])
        
        # Pagination buttons
        total_pages = (len(reviews) + per_page - 1) // per_page
        if total_pages > 1:
            pagination_buttons = []
            
            if page > 0:
                pagination_buttons.append(
                    ReviewKeyboard.create_inline_button(
                        "⬅️",
                        f"review:page:{page-1}"
                    )
                )
            
            pagination_buttons.append(
                ReviewKeyboard.create_inline_button(
                    f"{page + 1}/{total_pages}",
                    "review:page:current"
                )
            )
            
            if page < total_pages - 1:
                pagination_buttons.append(
                    ReviewKeyboard.create_inline_button(
                        "➡️",
                        f"review:page:{page+1}"
                    )
                )
            
            buttons.append(pagination_buttons)
        
        # Back button
        buttons.append([
            ReviewKeyboard.create_inline_button(
                "⬅️ Назад",
                "review:back"
            )
        ])
        
        return ReviewKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_review_detail_keyboard(review: Review) -> InlineKeyboardMarkup:
        """Get keyboard for review detail view."""
        buttons = []
        
        # Admin actions (if needed)
        if not review.is_visible:
            buttons.append([
                ReviewKeyboard.create_inline_button(
                    "👁️ Показать",
                    f"review:show:{review.review_id}"
                )
            ])
        else:
            buttons.append([
                ReviewKeyboard.create_inline_button(
                    "🙈 Скрыть",
                    f"review:hide:{review.review_id}"
                )
            ])
        
        if not review.is_answered:
            buttons.append([
                ReviewKeyboard.create_inline_button(
                    "💬 Ответить",
                    f"review:respond:{review.review_id}"
                )
            ])
        
        buttons.append([
            ReviewKeyboard.create_inline_button(
                "❌ Удалить",
                f"review:delete:{review.review_id}"
            )
        ])
        
        buttons.append([
            ReviewKeyboard.create_inline_button(
                "⬅️ Назад",
                "review:back"
            )
        ])
        
        return ReviewKeyboard.create_inline_keyboard(buttons)
    
    @staticmethod
    def get_admin_review_management_keyboard() -> InlineKeyboardMarkup:
        """Get keyboard for admin review management."""
        return ReviewKeyboard.create_inline_keyboard([
            [
                ReviewKeyboard.create_inline_button(
                    "📋 Все отзывы",
                    "admin:reviews:all"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "⭐ По рейтингу",
                    "admin:reviews:by_rating"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "📅 Недавние",
                    "admin:reviews:recent"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "❓ Без ответа",
                    "admin:reviews:unanswered"
                )
            ],
            [
                ReviewKeyboard.create_inline_button(
                    "⬅️ Назад",
                    "admin:back"
                )
            ]
        ])
