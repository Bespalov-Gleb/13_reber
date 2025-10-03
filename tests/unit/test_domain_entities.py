"""Unit tests for domain entities."""

import pytest
from datetime import datetime

from domain.entities.user import User
from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from shared.types.user_types import UserRole, UserStatus


class TestUser:
    """Test User entity."""
    
    def test_create_user(self):
        """Test user creation."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        assert user.user_id == "test_user_1"
        assert user.telegram_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == UserRole.CUSTOMER
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True
        assert user.is_admin is False
    
    def test_user_full_name(self):
        """Test user full name property."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            first_name="Test",
            last_name="User"
        )
        
        assert user.full_name == "Test User"
    
    def test_user_full_name_without_last_name(self):
        """Test user full name without last name."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            first_name="Test"
        )
        
        assert user.full_name == "Test"
    
    def test_user_full_name_with_username_only(self):
        """Test user full name with username only."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            username="test_user"
        )
        
        assert user.full_name == "test_user"
    
    def test_user_is_admin(self):
        """Test user admin role."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            role=UserRole.ADMIN
        )
        
        assert user.is_admin is True
        assert user.is_courier is False
    
    def test_user_is_courier(self):
        """Test user courier role."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            role=UserRole.COURIER
        )
        
        assert user.is_courier is True
        assert user.is_admin is False
    
    def test_user_update_phone(self):
        """Test user phone update."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789
        )
        
        original_updated_at = user.updated_at
        user.update_phone("+7 (999) 123-45-67")
        
        assert user.phone == "+7 (999) 123-45-67"
        assert user.updated_at > original_updated_at
    
    def test_user_change_role(self):
        """Test user role change."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            role=UserRole.CUSTOMER
        )
        
        original_updated_at = user.updated_at
        user.change_role(UserRole.ADMIN)
        
        assert user.role == UserRole.ADMIN
        assert user.updated_at > original_updated_at
    
    def test_user_change_status(self):
        """Test user status change."""
        user = User(
            user_id="test_user_1",
            telegram_id=123456789,
            status=UserStatus.ACTIVE
        )
        
        original_updated_at = user.updated_at
        user.change_status(UserStatus.BLOCKED)
        
        assert user.status == UserStatus.BLOCKED
        assert user.updated_at > original_updated_at


class TestCategory:
    """Test Category entity."""
    
    def test_create_category(self):
        """Test category creation."""
        category = Category(
            category_id="test_category_1",
            name="Бургеры",
            description="Вкусные бургеры"
        )
        
        assert category.category_id == "test_category_1"
        assert category.name == "Бургеры"
        assert category.description == "Вкусные бургеры"
        assert category.is_active is True
        assert category.sort_order == 0
    
    def test_category_update_name(self):
        """Test category name update."""
        category = Category(
            category_id="test_category_1",
            name="Бургеры"
        )
        
        original_updated_at = category.updated_at
        category.update_name("Гамбургеры")
        
        assert category.name == "Гамбургеры"
        assert category.updated_at > original_updated_at
    
    def test_category_activate_deactivate(self):
        """Test category activation/deactivation."""
        category = Category(
            category_id="test_category_1",
            name="Бургеры"
        )
        
        # Test deactivation
        original_updated_at = category.updated_at
        category.deactivate()
        
        assert category.is_active is False
        assert category.updated_at > original_updated_at
        
        # Test activation
        original_updated_at = category.updated_at
        category.activate()
        
        assert category.is_active is True
        assert category.updated_at > original_updated_at


class TestMenuItem:
    """Test MenuItem entity."""
    
    def test_create_menu_item(self):
        """Test menu item creation."""
        item = MenuItem(
            item_id="test_item_1",
            category_id="test_category_1",
            name="Чизбургер",
            description="Вкусный чизбургер",
            price=35000  # 350 rubles in kopecks
        )
        
        assert item.item_id == "test_item_1"
        assert item.category_id == "test_category_1"
        assert item.name == "Чизбургер"
        assert item.description == "Вкусный чизбургер"
        assert item.price == 35000
        assert item.is_available is True
        assert item.is_popular is False
    
    def test_menu_item_update_price(self):
        """Test menu item price update."""
        item = MenuItem(
            item_id="test_item_1",
            category_id="test_category_1",
            name="Чизбургер",
            price=35000
        )
        
        original_updated_at = item.updated_at
        item.update_price(40000)
        
        assert item.price == 40000
        assert item.updated_at > original_updated_at
    
    def test_menu_item_change_availability(self):
        """Test menu item availability change."""
        item = MenuItem(
            item_id="test_item_1",
            category_id="test_category_1",
            name="Чизбургер",
            price=35000
        )
        
        # Test making unavailable
        original_updated_at = item.updated_at
        item.change_availability(False)
        
        assert item.is_available is False
        assert item.updated_at > original_updated_at
        
        # Test making available
        original_updated_at = item.updated_at
        item.change_availability(True)
        
        assert item.is_available is True
        assert item.updated_at > original_updated_at
    
    def test_menu_item_mark_popular(self):
        """Test menu item popularity marking."""
        item = MenuItem(
            item_id="test_item_1",
            category_id="test_category_1",
            name="Чизбургер",
            price=35000
        )
        
        original_updated_at = item.updated_at
        item.mark_popular(True)
        
        assert item.is_popular is True
        assert item.updated_at > original_updated_at