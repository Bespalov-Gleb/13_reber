"""Review handler for review system."""

from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram import F
from infrastructure.telegram.handlers.base_handler import BaseHandler
from infrastructure.telegram.keyboards.review_keyboard import ReviewKeyboard
from infrastructure.telegram.utils.message_formatter import MessageFormatter
from domain.services.review_service import ReviewService
from app.dependencies import get_review_service, get_user_service


class ReviewHandler(BaseHandler):
    """Handler for review operations."""

    def __init__(self):
        super().__init__()
        self._pending_comment_reviews: dict[int, str] = {}
    
    def _register_handlers(self) -> None:
        """Register review handlers."""
        # Callback handlers
        self.router.callback_query.register(
            self.handle_review_callback,
            F.data.startswith("review")
        )
        self.router.message.register(
            self.handle_review_text_message,
            F.text,
            lambda message: bool(self._pending_comment_reviews.get(message.from_user.id))
        )
    
    async def handle_review_callback(self, callback: CallbackQuery, **kwargs) -> None:
        """Handle review callback."""
        data = kwargs.get("data", {})
        user_id = data.get("user_id", callback.from_user.id)
        callback_data = callback.data
        
        # Parse callback data
        parts = callback_data.split(":")
        if len(parts) < 2:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        action = parts[1]
        
        try:
            if action == "rating":
                await self._handle_rating_selection(callback, parts, user_id, data)
            elif action == "comment":
                await self._handle_comment_selection(callback, parts, user_id, data)
            elif action == "confirm":
                await self._handle_review_confirmation(callback, parts, user_id, data)
            elif action == "edit":
                await self._handle_review_edit(callback, parts, user_id, data)
            elif action == "cancel":
                await self._handle_review_cancel(callback, parts, user_id, data)
            elif action == "view":
                await self._handle_review_view(callback, parts, user_id, data)
            elif action == "page":
                await self._handle_review_pagination(callback, parts, user_id, data)
            elif action == "back":
                await self._handle_review_back(callback, user_id, data)
            else:
                await callback.answer("❌ Неизвестное действие")
                return
                
        except Exception as e:
            self.logger.error(f"Review callback error: {e}")
            await callback.answer("❌ Произошла ошибка")
            return
        
        await callback.answer()
    
    async def handle_review_text_message(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle text messages for review comments."""
        if data is None:
            data = {}
        
        user_id = data.get("user_id", message.from_user.id)
        text = message.text
        review_id = self._pending_comment_reviews.get(user_id)
        if not review_id:
            return

        review_service = await get_review_service(data)
        review = await review_service.get_review_by_id(review_id)
        if not review:
            self._pending_comment_reviews.pop(user_id, None)
            await message.answer("❌ Отзыв не найден. Попробуйте снова.")
            return

        review.comment = text.strip() if text else None
        await review_service.update_review(review)
        self._pending_comment_reviews.pop(user_id, None)
        await message.answer(
            "💬 <b>Комментарий сохранен.</b>\nПодтвердите публикацию отзыва:",
            reply_markup=ReviewKeyboard.get_review_confirmation_keyboard(review_id)
        )
    
    async def _handle_rating_selection(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle rating selection."""
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        try:
            rating = int(parts[2])
        except ValueError:
            await callback.answer("❌ Неверный рейтинг")
            return
        
        # Extract order_id or menu_item_id from callback data
        order_id = None
        menu_item_id = None
        
        for i, part in enumerate(parts):
            if part == "order" and i + 1 < len(parts):
                order_id = parts[i + 1]
            elif part == "item" and i + 1 < len(parts):
                menu_item_id = parts[i + 1]
        
        # Create review with rating
        review_service = await get_review_service(data)
        user_service = await get_user_service(data)
        
        try:
            db_user = await user_service.get_user_by_telegram_id(user_id)
            if not db_user:
                await callback.answer("❌ Пользователь не найден")
                return

            review = await review_service.create_review(
                user_id=db_user.user_id,
                rating=rating,
                order_id=order_id,
                menu_item_id=menu_item_id
            )
            
            # Show comment selection
            text = f"✅ <b>Рейтинг {rating} звезд сохранен!</b>\n\nХотите добавить комментарий к отзыву?"
            keyboard = ReviewKeyboard.get_comment_keyboard(review.review_id)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except ValueError as e:
            await callback.answer(f"❌ {str(e)}")
        except Exception as e:
            self.logger.error(f"Error creating review: {e}")
            await callback.answer("❌ Ошибка при создании отзыва")
    
    async def _handle_comment_selection(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle comment selection."""
        if len(parts) < 4:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        action = parts[2]
        review_id = parts[3]
        
        if action == "add":
            # Set state for text input
            text = "💬 <b>Добавьте комментарий к отзыву</b>\n\nНапишите ваш отзыв:"
            self._pending_comment_reviews[user_id] = review_id
            await self.safe_edit_message(
                callback.message,
                text=text
            )
            # In a real implementation, you'd set the user's state to expect comment input
            
        elif action == "skip":
            # Skip comment and show confirmation
            await self._show_review_confirmation(callback, review_id, user_id, data)
    
    async def _handle_review_confirmation(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle review confirmation."""
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        review_id = parts[2]
        review_service = await get_review_service(data)
        
        try:
            review = await review_service.get_review_by_id(review_id)
            if not review:
                await callback.answer("❌ Отзыв не найден")
                return
            
            # Show success message
            text = f"✅ <b>Отзыв опубликован!</b>\n\n"
            text += f"{review.get_rating_stars()} {review.get_rating_text()}\n"
            if review.comment:
                text += f"💬 {review.comment}\n"
            text += f"📅 {review.created_at.strftime('%d.%m.%Y')}\n\n"
            text += "Спасибо за ваш отзыв!"
            
            await self.safe_edit_message(
                callback.message,
                text=text
            )
            
        except Exception as e:
            self.logger.error(f"Error confirming review: {e}")
            await callback.answer("❌ Ошибка при подтверждении отзыва")
    
    async def _handle_review_edit(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle review edit."""
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        review_id = parts[2]
        # Show rating selection again
        text = "⭐ <b>Выберите новый рейтинг</b>"
        keyboard = ReviewKeyboard.get_rating_keyboard()
        
        await self.safe_edit_message(
            callback.message,
            text=text,
            reply_markup=keyboard
        )
    
    async def _handle_review_cancel(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle review cancellation."""
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        review_id = parts[2]
        review_service = await get_review_service(data)
        
        try:
            await review_service.delete_review(review_id)
            
            text = "❌ <b>Отзыв отменен</b>\n\nВы можете оставить отзыв позже."
            await self.safe_edit_message(
                callback.message,
                text=text
            )
            
        except Exception as e:
            self.logger.error(f"Error canceling review: {e}")
            await callback.answer("❌ Ошибка при отмене отзыва")
    
    async def _handle_review_view(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle review view."""
        if len(parts) < 3:
            await callback.answer("❌ Ошибка: неверные данные")
            return
        
        review_id = parts[2]
        review_service = await get_review_service(data)
        
        try:
            review = await review_service.get_review_by_id(review_id)
            if not review:
                await callback.answer("❌ Отзыв не найден")
                return
            
            # Format review details
            text = f"📝 <b>Отзыв</b>\n\n"
            text += f"{review.get_rating_stars()} {review.get_rating_text()}\n"
            if review.comment:
                text += f"💬 {review.comment}\n"
            text += f"📅 {review.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            
            if review.admin_response:
                text += f"\n👨‍💼 <b>Ответ администратора:</b>\n{review.admin_response}"
            
            keyboard = ReviewKeyboard.get_review_detail_keyboard(review)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error viewing review: {e}")
            await callback.answer("❌ Ошибка при просмотре отзыва")
    
    async def _handle_review_pagination(self, callback: CallbackQuery, parts: list, user_id: int, data: Dict[str, Any]) -> None:
        """Handle review pagination."""
        # This would handle pagination for review lists
        # Implementation depends on how reviews are displayed
        await callback.answer("📄 Пагинация отзывов")
    
    async def _handle_review_back(self, callback: CallbackQuery, user_id: int, data: Dict[str, Any]) -> None:
        """Handle review back navigation."""
        # Navigate back to previous screen
        text = "⬅️ <b>Возврат в главное меню</b>"
        await self.safe_edit_message(
            callback.message,
            text=text
        )
    
    async def _show_review_confirmation(self, callback: CallbackQuery, review_id: str, user_id: int, data: Dict[str, Any]) -> None:
        """Show review confirmation."""
        review_service = await get_review_service(data)
        
        try:
            review = await review_service.get_review_by_id(review_id)
            if not review:
                await callback.answer("❌ Отзыв не найден")
                return
            
            # Format review summary
            text = f"📝 <b>Подтверждение отзыва</b>\n\n"
            text += f"{review.get_rating_stars()} {review.get_rating_text()}\n"
            if review.comment:
                text += f"💬 {review.comment}\n"
            text += f"\nПодтвердить публикацию отзыва?"
            
            keyboard = ReviewKeyboard.get_review_confirmation_keyboard(review_id)
            
            await self.safe_edit_message(
                callback.message,
                text=text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error showing review confirmation: {e}")
            await callback.answer("❌ Ошибка при подтверждении отзыва")
