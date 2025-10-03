"""Test data fixtures."""

from datetime import datetime
from typing import List

from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from domain.entities.user import User
from shared.types.user_types import UserRole, UserStatus


def create_test_user(
    user_id: str = "test_user_1",
    telegram_id: int = 123456789,
    username: str = "test_user",
    first_name: str = "Test",
    last_name: str = "User",
    role: UserRole = UserRole.CUSTOMER,
    status: UserStatus = UserStatus.ACTIVE
) -> User:
    """Create test user."""
    return User(
        user_id=user_id,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
        status=status,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_admin_user(
    user_id: str = "test_admin_1",
    telegram_id: int = 987654321,
    username: str = "test_admin",
    first_name: str = "Test",
    last_name: str = "Admin"
) -> User:
    """Create test admin user."""
    return create_test_user(
        user_id=user_id,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.ADMIN
    )


def create_test_category(
    category_id: str = "test_category_1",
    name: str = "Бургеры",
    description: str = "Вкусные бургеры",
    sort_order: int = 1
) -> Category:
    """Create test category."""
    return Category(
        category_id=category_id,
        name=name,
        description=description,
        sort_order=sort_order,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_menu_item(
    item_id: str = "test_item_1",
    category_id: str = "test_category_1",
    name: str = "Чизбургер",
    description: str = "Вкусный чизбургер с говядиной",
    price: int = 35000,  # 350 rubles in kopecks
    weight: str = "200г",
    calories: int = 450
) -> MenuItem:
    """Create test menu item."""
    return MenuItem(
        item_id=item_id,
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        weight=weight,
        calories=calories,
        is_available=True,
        is_popular=False,
        sort_order=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def create_test_categories() -> List[Category]:
    """Create test categories."""
    return [
        create_test_category("cat_1", "Бургеры", "Вкусные бургеры", 1),
        create_test_category("cat_2", "Салаты", "Свежие салаты", 2),
        create_test_category("cat_3", "Напитки", "Прохладительные напитки", 3),
        create_test_category("cat_4", "Десерты", "Сладкие десерты", 4),
    ]


def create_test_menu_items() -> List[MenuItem]:
    """Create test menu items."""
    return [
        create_test_menu_item("item_1", "cat_1", "Чизбургер", "Вкусный чизбургер", 35000),
        create_test_menu_item("item_2", "cat_1", "Гамбургер", "Классический гамбургер", 30000),
        create_test_menu_item("item_3", "cat_2", "Цезарь", "Салат Цезарь с курицей", 25000),
        create_test_menu_item("item_4", "cat_3", "Кола", "Кока-кола 0.5л", 8000),
        create_test_menu_item("item_5", "cat_4", "Тирамису", "Классический тирамису", 20000),
    ]


def create_test_users() -> List[User]:
    """Create test users."""
    return [
        create_test_user("user_1", 111111111, "user1", "Иван", "Иванов"),
        create_test_user("user_2", 222222222, "user2", "Петр", "Петров"),
        create_test_admin_user("admin_1", 999999999, "admin", "Админ", "Админов"),
    ]