"""Admin handler extensions for menu editing."""

from typing import Any, Dict, TYPE_CHECKING
from datetime import datetime

from aiogram.types import Message

if TYPE_CHECKING:
    from infrastructure.telegram.handlers.admin_handler import AdminHandler
from infrastructure.telegram.keyboards.admin_keyboard import AdminKeyboard
from domain.services.admin_state_service import admin_state_service
from shared.types.admin_states import AdminState
from shared.utils.helpers import generate_id
from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from app.dependencies import get_menu_service, get_user_service
from shared.types.user_types import UserRole
from shared.services.notification_templates import set_notification_template


class AdminHandlerExtensions:
    """Extensions for AdminHandler to handle menu editing."""

    def __init__(self, admin_handler: "AdminHandler"):
        self.admin_handler = admin_handler
        # Logger будет инициализирован после super().__init__()
        self.logger = None

    async def handle_admin_text_message(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle admin text messages during editing."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)

        state = admin_state_service.get_admin_state(user_id)
        text = message.text

        if state == AdminState.ADDING_CATEGORY_NAME:
            await self._handle_adding_category_name(message, text)
        elif state == AdminState.ADDING_CATEGORY_DESCRIPTION:
            await self._handle_adding_category_description(message, text)
        elif state == AdminState.ADDING_CATEGORY_IMAGE and text == "-":
            # Skip photo for category
            admin_state_service.set_temp_data(user_id, "image_url", "")
            await self._create_category_from_temp_data(message)
        elif state == AdminState.EDITING_CATEGORY_NAME:
            await self._handle_editing_category_name(message, text)
        elif state == AdminState.EDITING_CATEGORY_DESCRIPTION:
            await self._handle_editing_category_description(message, text)
        elif state == AdminState.ADDING_ITEM_NAME:
            await self._handle_adding_item_name(message, text)
        elif state == AdminState.ADDING_ITEM_DESCRIPTION:
            await self._handle_adding_item_description(message, text)
        elif state == AdminState.ADDING_ITEM_PRICE:
            await self._handle_adding_item_price(message, text)
        elif state == AdminState.ADDING_ITEM_INGREDIENTS:
            await self._handle_adding_item_ingredients(message, text)
        elif state == AdminState.ADDING_ITEM_ALLERGENS:
            await self._handle_adding_item_allergens(message, text)
        elif state == AdminState.ADDING_ITEM_WEIGHT:
            await self._handle_adding_item_weight(message, text)
        elif state == AdminState.ADDING_ITEM_CALORIES:
            await self._handle_adding_item_calories(message, text)
        elif state == AdminState.ADDING_ITEM_IMAGE and text == "-":
            # Skip photo for item
            admin_state_service.set_temp_data(user_id, "image_url", "")
            await self._create_item_from_temp_data(message)
        elif state == AdminState.EDITING_ITEM_NAME:
            await self._handle_editing_item_name(message, text)
        elif state == AdminState.EDITING_ITEM_DESCRIPTION:
            await self._handle_editing_item_description(message, text)
        elif state == AdminState.EDITING_ITEM_PRICE:
            await self._handle_editing_item_price(message, text)
        elif state == AdminState.EDITING_ITEM_INGREDIENTS:
            await self._handle_editing_item_ingredients(message, text)
        elif state == AdminState.EDITING_ITEM_ALLERGENS:
            await self._handle_editing_item_allergens(message, text)
        elif state == AdminState.EDITING_ITEM_WEIGHT:
            await self._handle_editing_item_weight(message, text)
        elif state == AdminState.EDITING_ITEM_CALORIES:
            await self._handle_editing_item_calories(message, text)
        elif state == AdminState.COURIER_ROLE_BY_USERNAME:
            await self._handle_courier_role_by_username(message, text)
        elif state == AdminState.EDITING_NOTIFICATION_TEMPLATE:
            await self._handle_editing_notification_template(message, text)
        elif state == AdminState.COMPOSING_NOTIFICATION_ANNOUNCEMENT:
            await self._handle_composing_notification_announcement(message, text)
        else:
            await message.answer("❌ Неизвестное состояние")
            admin_state_service.reset_admin_context(user_id)

    async def handle_admin_photo(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle admin photo messages during editing."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)

        state = admin_state_service.get_admin_state(user_id)

        if state in [AdminState.ADDING_CATEGORY_IMAGE, AdminState.EDITING_CATEGORY_IMAGE,
                     AdminState.ADDING_ITEM_IMAGE, AdminState.EDITING_ITEM_IMAGE]:
            await self._handle_photo_upload(message)
        elif state == AdminState.ATTACHING_NOTIFICATION_MEDIA:
            await self._handle_notification_media_upload(message, media_type="photo", file_id=message.photo[-1].file_id)
        else:
            await message.answer("❌ Фото не ожидается в текущем состоянии")

    async def handle_admin_video(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle admin video messages during editing."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)
        state = admin_state_service.get_admin_state(user_id)
        if state == AdminState.ATTACHING_NOTIFICATION_MEDIA and message.video:
            await self._handle_notification_media_upload(message, media_type="video", file_id=message.video.file_id)
            return
        await message.answer("❌ Видео не ожидается в текущем состоянии")

    async def handle_admin_document(self, message: Message, data: Dict[str, Any] = None) -> None:
        """Handle admin document messages during editing."""
        if data is None:
            data = {}
        user_id = data.get("user_id", message.from_user.id)
        state = admin_state_service.get_admin_state(user_id)
        if state == AdminState.ATTACHING_NOTIFICATION_MEDIA and message.document:
            await self._handle_notification_media_upload(message, media_type="document", file_id=message.document.file_id)
            return
        await message.answer("❌ Документ не ожидается в текущем состоянии")

    # Category creation handlers
    async def _handle_adding_category_name(self, message: Message, text: str) -> None:
        """Handle adding category name."""
        admin_state_service.set_temp_data(message.from_user.id, "name", text)
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_CATEGORY_DESCRIPTION)

        await message.answer(
            "📝 <b>Добавление категории</b>\n\nВведите описание категории (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_adding_category_description(self, message: Message, text: str) -> None:
        """Handle adding category description."""
        description = text if text != "-" else None
        admin_state_service.set_temp_data(message.from_user.id, "description", description or "")
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_CATEGORY_IMAGE)

        await message.answer(
            "📷 <b>Добавление категории</b>\n\nОтправьте фото категории (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_editing_category_name(self, message: Message, text: str) -> None:
        """Handle editing category name."""
        category_id = admin_state_service.get_editing_id(message.from_user.id)
        if not category_id:
            await message.answer("❌ Ошибка: ID категории не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        # Use current session if available via admin_handler (middleware passes session in message context)
        try:
            session = None
            if hasattr(self.admin_handler, "router"):
                # no direct access to data here; fallback to plain getter
                pass
            menu_service = await get_menu_service()
        except Exception:
            menu_service = await get_menu_service()
        try:
            category = await menu_service.get_category(category_id)
            if category:
                category.name = text
                await menu_service.update_category(category)
                await message.answer(
                    "✅ <b>Название категории обновлено</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Категория не найдена</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_category_description(self, message: Message, text: str) -> None:
        """Handle editing category description."""
        category_id = admin_state_service.get_editing_id(message.from_user.id)
        if not category_id:
            await message.answer("❌ Ошибка: ID категории не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        try:
            menu_service = await get_menu_service()
        except Exception:
            menu_service = await get_menu_service()
        try:
            category = await menu_service.get_category(category_id)
            if category:
                category.description = text if text != "-" else None
                await menu_service.update_category(category)
                await message.answer(
                    "✅ <b>Описание категории обновлено</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Категория не найдена</b>",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    # Item creation handlers
    async def _handle_adding_item_name(self, message: Message, text: str) -> None:
        """Handle adding item name."""
        admin_state_service.set_temp_data(message.from_user.id, "name", text)
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_DESCRIPTION)

        await message.answer(
            "📝 <b>Добавление блюда</b>\n\nВведите описание блюда (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_adding_item_description(self, message: Message, text: str) -> None:
        """Handle adding item description."""
        description = text if text != "-" else None
        admin_state_service.set_temp_data(message.from_user.id, "description", description or "")
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_PRICE)

        await message.answer(
            "💰 <b>Добавление блюда</b>\n\nВведите цену в рублях (например: 250):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_adding_item_price(self, message: Message, text: str) -> None:
        """Handle adding item price."""
        try:
            price = int(text) * 100  # Convert to kopecks
            admin_state_service.set_temp_data(message.from_user.id, "price", str(price))
            admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_CATEGORY)

            # Show categories for selection
            menu_service = await get_menu_service()
            categories = await menu_service.get_categories(active_only=False)

            if not categories:
                await message.answer(
                    "❌ <b>Нет доступных категорий</b>\n\nСначала создайте категорию",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
                admin_state_service.reset_admin_context(message.from_user.id)
                return

            keyboard = AdminKeyboard.get_categories_selection_keyboard(categories)
            await message.answer(
                "📁 <b>Добавление блюда</b>\n\nВыберите категорию:",
                reply_markup=keyboard
            )
        except ValueError:
            await message.answer(
                "❌ <b>Неверный формат цены</b>\n\nВведите число (например: 250):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )

    async def _handle_adding_item_ingredients(self, message: Message, text: str) -> None:
        """Handle adding item ingredients."""
        ingredients = text if text != "-" else None
        admin_state_service.set_temp_data(message.from_user.id, "ingredients", ingredients or "")
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_ALLERGENS)

        await message.answer(
            "⚠️ <b>Добавление блюда</b>\n\nВведите аллергены (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_adding_item_allergens(self, message: Message, text: str) -> None:
        """Handle adding item allergens."""
        allergens = text if text != "-" else None
        admin_state_service.set_temp_data(message.from_user.id, "allergens", allergens or "")
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_WEIGHT)

        await message.answer(
            "⚖️ <b>Добавление блюда</b>\n\nВведите вес в граммах (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_adding_item_weight(self, message: Message, text: str) -> None:
        """Handle adding item weight."""
        weight = text if text != "-" else None
        admin_state_service.set_temp_data(message.from_user.id, "weight", weight or "")
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_CALORIES)

        await message.answer(
            "🔥 <b>Добавление блюда</b>\n\nВведите калории (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    async def _handle_adding_item_calories(self, message: Message, text: str) -> None:
        """Handle adding item calories."""
        calories = text if text != "-" else None
        admin_state_service.set_temp_data(message.from_user.id, "calories", calories or "")
        admin_state_service.set_admin_state(message.from_user.id, AdminState.ADDING_ITEM_IMAGE)

        await message.answer(
            "📷 <b>Добавление блюда</b>\n\nОтправьте фото блюда (или отправьте '-' для пропуска):",
            reply_markup=AdminKeyboard.get_cancel_keyboard()
        )

    # Item editing handlers
    async def _handle_editing_item_name(self, message: Message, text: str) -> None:
        """Handle editing item name."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        menu_service = await get_menu_service()
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.name = text
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Название блюда обновлено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_item_description(self, message: Message, text: str) -> None:
        """Handle editing item description."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        menu_service = await get_menu_service()
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.description = text if text != "-" else None
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Описание блюда обновлено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_item_price(self, message: Message, text: str) -> None:
        """Handle editing item price."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        try:
            price = int(text) * 100  # Convert to kopecks
            menu_service = await get_menu_service()
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.price = price
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Цена блюда обновлена</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except ValueError:
            await message.answer(
                "❌ <b>Неверный формат цены</b>\n\nВведите число (например: 250):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            return
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_item_ingredients(self, message: Message, text: str) -> None:
        """Handle editing item ingredients."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        menu_service = await get_menu_service()
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.ingredients = text if text != "-" else None
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Состав блюда обновлен</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_item_allergens(self, message: Message, text: str) -> None:
        """Handle editing item allergens."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        menu_service = await get_menu_service()
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.allergens = text if text != "-" else None
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Аллергены блюда обновлены</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_item_weight(self, message: Message, text: str) -> None:
        """Handle editing item weight."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        menu_service = await get_menu_service()
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                item.weight = text if text != "-" else None
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Вес блюда обновлен</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_editing_item_calories(self, message: Message, text: str) -> None:
        """Handle editing item calories."""
        item_id = admin_state_service.get_editing_id(message.from_user.id)
        if not item_id:
            await message.answer("❌ Ошибка: ID блюда не найден")
            admin_state_service.reset_admin_context(message.from_user.id)
            return

        menu_service = await get_menu_service()
        try:
            item = await menu_service.get_menu_item(item_id)
            if item:
                if text == "-":
                    item.calories = None
                else:
                    item.calories = int(text)
                await menu_service.update_menu_item(item)
                await message.answer(
                    "✅ <b>Калории блюда обновлены</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
            else:
                await message.answer(
                    "❌ <b>Блюдо не найдено</b>",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
        except ValueError:
            await message.answer(
                "❌ <b>Неверный формат калорий</b>\n\nВведите число (например: 289):",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            return
        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(message.from_user.id)

    async def _handle_photo_upload(self, message: Message) -> None:
        """Handle photo upload."""
        user_id = message.from_user.id
        state = admin_state_service.get_admin_state(user_id)

        # Get the largest photo
        photo = message.photo[-1]
        file_id = photo.file_id

        if state in [AdminState.ADDING_CATEGORY_IMAGE, AdminState.EDITING_CATEGORY_IMAGE]:
            await self._handle_category_photo_upload(message, file_id)
        elif state in [AdminState.ADDING_ITEM_IMAGE, AdminState.EDITING_ITEM_IMAGE]:
            await self._handle_item_photo_upload(message, file_id)

    async def _handle_courier_role_by_username(self, message: Message, text: str) -> None:
        """Toggle courier role by Telegram username."""
        user_id = message.from_user.id
        raw_value = (text or "").strip()

        if raw_value == "-":
            admin_state_service.reset_admin_context(user_id)
            await message.answer(
                "❌ Действие отменено",
                reply_markup=AdminKeyboard.get_users_management_keyboard()
            )
            return

        normalized = raw_value.lstrip("@").strip()
        if not normalized:
            await message.answer(
                "❌ Укажите username в формате @username или username",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            return

        try:
            user_service = await get_user_service()
            candidates = await user_service.search_users(normalized)
            username_lower = normalized.lower()
            matched = next(
                (candidate for candidate in candidates if (candidate.username or "").lower() == username_lower),
                None
            )

            if not matched:
                await message.answer(
                    f"❌ Пользователь с username @{normalized} не найден",
                    reply_markup=AdminKeyboard.get_cancel_keyboard()
                )
                return

            if matched.role == UserRole.ADMIN:
                await message.answer(
                    "❌ Нельзя менять роль администратора через этот сценарий",
                    reply_markup=AdminKeyboard.get_users_management_keyboard()
                )
                admin_state_service.reset_admin_context(user_id)
                return

            if matched.role == UserRole.COURIER:
                matched.role = UserRole.CUSTOMER
                result_text = "✅ Роль курьера снята"
            else:
                matched.role = UserRole.COURIER
                result_text = "✅ Пользователь назначен курьером"

            await user_service.update_user(matched)

            await message.answer(
                f"{result_text}\n\n👤 @{matched.username or 'без username'}\n🆔 TG ID: {matched.telegram_id}",
                reply_markup=AdminKeyboard.get_users_management_keyboard()
            )
            admin_state_service.reset_admin_context(user_id)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Courier role toggle by username failed: {e}")
            await message.answer(
                f"❌ Ошибка при изменении роли: {str(e)}",
                reply_markup=AdminKeyboard.get_users_management_keyboard()
            )
            admin_state_service.reset_admin_context(user_id)

    async def _handle_editing_notification_template(self, message: Message, text: str) -> None:
        """Handle notification template text editing."""
        user_id = message.from_user.id
        template_type = admin_state_service.get_temp_data(user_id, "notification_template_type")
        if not template_type:
            await message.answer("❌ Не найден шаблон для редактирования")
            admin_state_service.reset_admin_context(user_id)
            return

        new_text = (text or "").strip()
        if not new_text:
            await message.answer(
                "❌ Текст шаблона не может быть пустым. Отправьте новый текст:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            return

        try:
            set_notification_template(template_type, new_text)
            await message.answer(
                f"✅ Шаблон <b>{template_type}</b> обновлен",
                reply_markup=AdminKeyboard.get_notification_template_editor_keyboard(template_type)
            )
        except ValueError:
            await message.answer("❌ Неизвестный шаблон уведомления")
        finally:
            admin_state_service.reset_admin_context(user_id)

    async def _handle_notification_media_upload(self, message: Message, media_type: str, file_id: str) -> None:
        """Store selected media for notification sending."""
        user_id = message.from_user.id
        audience = admin_state_service.get_temp_data(user_id, "notification_send_audience")
        if not audience:
            await message.answer("❌ Сначала выберите аудиторию для рассылки")
            admin_state_service.reset_admin_context(user_id)
            return

        admin_state_service.set_temp_data(user_id, "notification_send_media_type", media_type)
        admin_state_service.set_temp_data(user_id, "notification_send_media_file_id", file_id)
        admin_state_service.set_admin_state(user_id, AdminState.IDLE)
        await message.answer(
            "✅ Медиа прикреплено к уведомлению",
            reply_markup=AdminKeyboard.get_notification_send_preview_keyboard(has_media=True)
        )

    async def _handle_composing_notification_announcement(self, message: Message, text: str) -> None:
        """Handle announcement text input for broadcast notifications."""
        user_id = message.from_user.id
        announcement_text = (text or "").strip()
        if not announcement_text:
            await message.answer(
                "❌ Текст объявления не может быть пустым. Отправьте текст:",
                reply_markup=AdminKeyboard.get_cancel_keyboard()
            )
            return

        admin_state_service.set_temp_data(user_id, "notification_send_text", announcement_text)
        admin_state_service.set_admin_state(user_id, AdminState.IDLE)
        await message.answer(
            "✅ Текст объявления сохранен. Можно прикрепить медиа или отправить.",
            reply_markup=AdminKeyboard.get_notification_send_preview_keyboard(has_media=False)
        )

    async def _handle_category_photo_upload(self, message: Message, file_id: str) -> None:
        """Handle category photo upload."""
        user_id = message.from_user.id
        state = admin_state_service.get_admin_state(user_id)

        if state == AdminState.ADDING_CATEGORY_IMAGE:
            # Save photo info and create category
            admin_state_service.set_temp_data(user_id, "image_url", file_id)
            await self._create_category_from_temp_data(message)
        elif state == AdminState.EDITING_CATEGORY_IMAGE:
            # Update category photo
            category_id = admin_state_service.get_editing_id(user_id)
            if not category_id:
                await message.answer("❌ Ошибка: ID категории не найден")
                admin_state_service.reset_admin_context(user_id)
                return

            menu_service = await get_menu_service()
            try:
                category = await menu_service.get_category(category_id)
                if category:
                    category.image_url = file_id
                    await menu_service.update_category(category)
                    await message.answer(
                        "✅ <b>Фото категории обновлено</b>",
                        reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ <b>Категория не найдена</b>",
                        reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                    )
            except Exception as e:
                await message.answer(
                    f"❌ <b>Ошибка:</b> {str(e)}",
                    reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
                )

            admin_state_service.reset_admin_context(user_id)

    async def _handle_item_photo_upload(self, message: Message, file_id: str) -> None:
        """Handle item photo upload."""
        user_id = message.from_user.id
        state = admin_state_service.get_admin_state(user_id)

        if state == AdminState.ADDING_ITEM_IMAGE:
            # Save photo info and create item
            admin_state_service.set_temp_data(user_id, "image_url", file_id)
            await self._create_item_from_temp_data(message)
        elif state == AdminState.EDITING_ITEM_IMAGE:
            # Update item photo
            item_id = admin_state_service.get_editing_id(user_id)
            if not item_id:
                await message.answer("❌ Ошибка: ID блюда не найден")
                admin_state_service.reset_admin_context(user_id)
                return

            menu_service = await get_menu_service()
            try:
                item = await menu_service.get_menu_item(item_id)
                if item:
                    item.image_url = file_id
                    await menu_service.update_menu_item(item)
                    await message.answer(
                        "✅ <b>Фото блюда обновлено</b>",
                        reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ <b>Блюдо не найдено</b>",
                        reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                    )
            except Exception as e:
                await message.answer(
                    f"❌ <b>Ошибка:</b> {str(e)}",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )

            admin_state_service.reset_admin_context(user_id)

    async def _create_category_from_temp_data(self, message: Message) -> None:
        """Create category from temporary data."""
        user_id = message.from_user.id
        # Используем сессию из middleware если есть
        try:
            from aiogram.fsm.context import FSMContext  # optional import, ignore if not present
        except Exception:
            FSMContext = None  # type: ignore
        menu_service = await get_menu_service()

        try:

            name = admin_state_service.get_temp_data(user_id, "name")
            description = admin_state_service.get_temp_data(user_id, "description") or None
            image_url = admin_state_service.get_temp_data(user_id, "image_url") or None

            category = Category(
                category_id=generate_id(),
                name=name,
                description=description,
                image_url=image_url,
                sort_order=0,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            await menu_service.create_category(category)

            await message.answer(
                "✅ <b>Категория создана успешно!</b>",
                reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
            )

        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка при создании категории:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_categories_keyboard()
            )

        admin_state_service.reset_admin_context(user_id)

    async def _create_item_from_temp_data(self, message: Message) -> None:
        """Create item from temporary data."""
        user_id = message.from_user.id
        menu_service = await get_menu_service()

        try:

            name = admin_state_service.get_temp_data(user_id, "name")
            description = admin_state_service.get_temp_data(user_id, "description") or None
            price_raw = admin_state_service.get_temp_data(user_id, "price")
            category_id = admin_state_service.get_temp_data(user_id, "category_id")
            ingredients = admin_state_service.get_temp_data(user_id, "ingredients") or None
            allergens = admin_state_service.get_temp_data(user_id, "allergens") or None
            weight = admin_state_service.get_temp_data(user_id, "weight") or None
            calories_raw = admin_state_service.get_temp_data(user_id, "calories") or None
            image_url = admin_state_service.get_temp_data(user_id, "image_url") or None

            # Validate required fields
            if not name or not price_raw or not category_id:
                await message.answer(
                    "❌ <b>Недостаточно данных</b>\n\nПожалуйста, начните добавление блюда заново.",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
                admin_state_service.reset_admin_context(user_id)
                return

            try:
                price = int(price_raw)
            except ValueError:
                await message.answer(
                    "❌ <b>Неверный формат цены</b>",
                    reply_markup=AdminKeyboard.get_cancel_keyboard()
                )
                return

            try:
                calories = int(calories_raw) if calories_raw not in (None, "") else None
            except ValueError:
                calories = None

            # Ensure category exists
            category = await menu_service.get_category(category_id)
            if not category:
                await message.answer(
                    "❌ <b>Категория не найдена</b>\n\nВыберите категорию заново.",
                    reply_markup=AdminKeyboard.get_back_to_items_keyboard()
                )
                admin_state_service.reset_admin_context(user_id)
                return

            item = MenuItem(
                item_id=generate_id(),
                category_id=category_id,
                name=name,
                description=description,
                price=price,
                image_url=image_url,
                ingredients=ingredients,
                allergens=allergens,
                weight=weight,
                calories=calories,
                is_available=True,
                is_popular=False,
                sort_order=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            await menu_service.create_menu_item(item)

            await message.answer(
                "✅ <b>Блюдо создано успешно!</b>",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        except Exception as e:
            await message.answer(
                f"❌ <b>Ошибка при создании блюда:</b> {str(e)}",
                reply_markup=AdminKeyboard.get_back_to_items_keyboard()
            )

        admin_state_service.reset_admin_context(user_id)
