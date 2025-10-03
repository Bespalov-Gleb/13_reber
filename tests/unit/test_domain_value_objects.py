"""Unit tests for domain value objects."""

import pytest

from domain.value_objects.money import Money
from domain.value_objects.address import Address
from domain.value_objects.phone import Phone
from domain.value_objects.order_status import OrderStatus
from shared.constants.payment_constants import PaymentCurrency


class TestMoney:
    """Test Money value object."""
    
    def test_create_money(self):
        """Test money creation."""
        money = Money(10000, PaymentCurrency.RUB)
        
        assert money.amount == 10000
        assert money.currency == PaymentCurrency.RUB
        assert money.rubles == 100
        assert money.kopecks == 0
    
    def test_create_money_with_kopecks(self):
        """Test money creation with kopecks."""
        money = Money(10050, PaymentCurrency.RUB)
        
        assert money.amount == 10050
        assert money.rubles == 100
        assert money.kopecks == 50
    
    def test_create_money_from_rubles(self):
        """Test money creation from rubles and kopecks."""
        money = Money.from_rubles(100, 50, PaymentCurrency.RUB)
        
        assert money.amount == 10050
        assert money.rubles == 100
        assert money.kopecks == 50
    
    def test_create_zero_money(self):
        """Test zero money creation."""
        money = Money.zero(PaymentCurrency.RUB)
        
        assert money.amount == 0
        assert money.rubles == 0
        assert money.kopecks == 0
        assert money.is_zero() is True
    
    def test_money_negative_amount_raises_error(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(-100, PaymentCurrency.RUB)
    
    def test_money_add(self):
        """Test money addition."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(5000, PaymentCurrency.RUB)
        
        result = money1.add(money2)
        
        assert result.amount == 15000
        assert result.currency == PaymentCurrency.RUB
    
    def test_money_add_different_currencies_raises_error(self):
        """Test that adding different currencies raises error."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(10000, PaymentCurrency.USD)
        
        with pytest.raises(ValueError, match="Cannot add money with different currencies"):
            money1.add(money2)
    
    def test_money_subtract(self):
        """Test money subtraction."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(3000, PaymentCurrency.RUB)
        
        result = money1.subtract(money2)
        
        assert result.amount == 7000
        assert result.currency == PaymentCurrency.RUB
    
    def test_money_subtract_greater_amount_raises_error(self):
        """Test that subtracting greater amount raises error."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(15000, PaymentCurrency.RUB)
        
        with pytest.raises(ValueError, match="Cannot subtract amount greater than current amount"):
            money1.subtract(money2)
    
    def test_money_multiply(self):
        """Test money multiplication."""
        money = Money(10000, PaymentCurrency.RUB)
        
        result = money.multiply(1.5)
        
        assert result.amount == 15000
        assert result.currency == PaymentCurrency.RUB
    
    def test_money_multiply_negative_factor_raises_error(self):
        """Test that multiplying by negative factor raises error."""
        money = Money(10000, PaymentCurrency.RUB)
        
        with pytest.raises(ValueError, match="Factor cannot be negative"):
            money.multiply(-1.5)
    
    def test_money_divide(self):
        """Test money division."""
        money = Money(10000, PaymentCurrency.RUB)
        
        result = money.divide(2)
        
        assert result.amount == 5000
        assert result.currency == PaymentCurrency.RUB
    
    def test_money_divide_zero_raises_error(self):
        """Test that dividing by zero raises error."""
        money = Money(10000, PaymentCurrency.RUB)
        
        with pytest.raises(ValueError, match="Divisor must be positive"):
            money.divide(0)
    
    def test_money_is_positive(self):
        """Test money is positive check."""
        money = Money(10000, PaymentCurrency.RUB)
        
        assert money.is_positive() is True
        assert money.is_negative() is False
        assert money.is_zero() is False
    
    def test_money_is_negative(self):
        """Test money is negative check."""
        money = Money(-10000, PaymentCurrency.RUB)
        
        assert money.is_negative() is True
        assert money.is_positive() is False
        assert money.is_zero() is False
    
    def test_money_equality(self):
        """Test money equality."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(10000, PaymentCurrency.RUB)
        money3 = Money(10000, PaymentCurrency.USD)
        
        assert money1 == money2
        assert money1 != money3
    
    def test_money_comparison(self):
        """Test money comparison."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(15000, PaymentCurrency.RUB)
        money3 = Money(5000, PaymentCurrency.RUB)
        
        assert money1 < money2
        assert money1 > money3
        assert money1 <= money2
        assert money1 >= money3
    
    def test_money_string_representation(self):
        """Test money string representation."""
        money1 = Money(10000, PaymentCurrency.RUB)
        money2 = Money(10050, PaymentCurrency.RUB)
        
        assert str(money1) == "100 ₽"
        assert str(money2) == "100.50 ₽"


class TestAddress:
    """Test Address value object."""
    
    def test_create_address(self):
        """Test address creation."""
        address = Address(
            street="Тверская улица",
            house="1",
            apartment="10"
        )
        
        assert address.street == "Тверская улица"
        assert address.house == "1"
        assert address.apartment == "10"
        assert address.city == "Москва"
    
    def test_create_address_without_apartment(self):
        """Test address creation without apartment."""
        address = Address(
            street="Тверская улица",
            house="1"
        )
        
        assert address.street == "Тверская улица"
        assert address.house == "1"
        assert address.apartment is None
    
    def test_address_full_address(self):
        """Test address full address property."""
        address = Address(
            street="Тверская улица",
            house="1",
            apartment="10",
            entrance="2",
            floor="3"
        )
        
        expected = "Тверская улица, 1, кв. 10, подъезд 2, этаж 3"
        assert address.full_address == expected
    
    def test_address_short_address(self):
        """Test address short address property."""
        address = Address(
            street="Тверская улица",
            house="1",
            apartment="10"
        )
        
        expected = "Тверская улица, 1, кв. 10"
        assert address.short_address == expected
    
    def test_address_set_coordinates(self):
        """Test address coordinates setting."""
        address = Address(
            street="Тверская улица",
            house="1"
        )
        
        address.set_coordinates(55.7558, 37.6176)
        
        assert address.has_coordinates is True
        assert address.latitude == 55.7558
        assert address.longitude == 37.6176
    
    def test_address_set_invalid_coordinates_raises_error(self):
        """Test that setting invalid coordinates raises error."""
        address = Address(
            street="Тверская улица",
            house="1"
        )
        
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            address.set_coordinates(95.0, 37.6176)
        
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            address.set_coordinates(55.7558, 185.0)
    
    def test_address_clear_coordinates(self):
        """Test address coordinates clearing."""
        address = Address(
            street="Тверская улица",
            house="1"
        )
        
        address.set_coordinates(55.7558, 37.6176)
        assert address.has_coordinates is True
        
        address.clear_coordinates()
        assert address.has_coordinates is False
        assert address.latitude is None
        assert address.longitude is None
    
    def test_address_equality(self):
        """Test address equality."""
        address1 = Address(
            street="Тверская улица",
            house="1",
            apartment="10"
        )
        
        address2 = Address(
            street="Тверская улица",
            house="1",
            apartment="10"
        )
        
        address3 = Address(
            street="Тверская улица",
            house="2",
            apartment="10"
        )
        
        assert address1 == address2
        assert address1 != address3
    
    def test_address_string_representation(self):
        """Test address string representation."""
        address = Address(
            street="Тверская улица",
            house="1",
            apartment="10"
        )
        
        expected = "Тверская улица, 1, кв. 10, подъезд 2, этаж 3"
        assert str(address) == address.full_address


class TestPhone:
    """Test Phone value object."""
    
    def test_create_phone_russian_format(self):
        """Test phone creation with Russian format."""
        phone = Phone("8 (999) 123-45-67")
        
        assert phone.phone == "79991234567"
        assert phone.formatted == "+7 (999) 123-45-67"
        assert phone.international == "+79991234567"
        assert phone.national == "8 (999) 123-45-67"
    
    def test_create_phone_international_format(self):
        """Test phone creation with international format."""
        phone = Phone("+7 (999) 123-45-67")
        
        assert phone.phone == "79991234567"
        assert phone.formatted == "+7 (999) 123-45-67"
    
    def test_create_phone_without_country_code(self):
        """Test phone creation without country code."""
        phone = Phone("(999) 123-45-67")
        
        assert phone.phone == "79991234567"
        assert phone.formatted == "+7 (999) 123-45-67"
    
    def test_create_phone_digits_only(self):
        """Test phone creation with digits only."""
        phone = Phone("79991234567")
        
        assert phone.phone == "79991234567"
        assert phone.formatted == "+7 (999) 123-45-67"
    
    def test_create_phone_invalid_format_raises_error(self):
        """Test that invalid phone format raises error."""
        with pytest.raises(ValueError, match="Invalid phone number format"):
            Phone("123")
        
        with pytest.raises(ValueError, match="Invalid phone number format"):
            Phone("abc")
    
    def test_phone_country_code(self):
        """Test phone country code property."""
        phone = Phone("+7 (999) 123-45-67")
        
        assert phone.country_code == "7"
    
    def test_phone_area_code(self):
        """Test phone area code property."""
        phone = Phone("+7 (999) 123-45-67")
        
        assert phone.area_code == "999"
    
    def test_phone_number(self):
        """Test phone number property."""
        phone = Phone("+7 (999) 123-45-67")
        
        assert phone.number == "1234567"
    
    def test_phone_is_mobile(self):
        """Test phone is mobile check."""
        mobile_phone = Phone("+7 (999) 123-45-67")
        landline_phone = Phone("+7 (495) 123-45-67")
        
        assert mobile_phone.is_mobile() is True
        assert landline_phone.is_mobile() is False
    
    def test_phone_equality(self):
        """Test phone equality."""
        phone1 = Phone("+7 (999) 123-45-67")
        phone2 = Phone("8 (999) 123-45-67")
        phone3 = Phone("+7 (999) 123-45-68")
        
        assert phone1 == phone2
        assert phone1 != phone3
    
    def test_phone_string_representation(self):
        """Test phone string representation."""
        phone = Phone("+7 (999) 123-45-67")
        
        assert str(phone) == "+7 (999) 123-45-67"


class TestOrderStatus:
    """Test OrderStatus value object."""
    
    def test_order_status_enum_values(self):
        """Test order status enum values."""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PREPARING.value == "preparing"
        assert OrderStatus.READY.value == "ready"
        assert OrderStatus.OUT_FOR_DELIVERY.value == "delivery"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.PICKED_UP.value == "picked_up"
        assert OrderStatus.CANCELLED.value == "cancelled"
        assert OrderStatus.REFUNDED.value == "refunded"
    
    def test_order_status_display_names(self):
        """Test order status display names."""
        assert OrderStatus.PENDING.display_name == "⏳ Ожидает подтверждения"
        assert OrderStatus.CONFIRMED.display_name == "✅ Подтвержден"
        assert OrderStatus.PREPARING.display_name == "👨‍🍳 Готовится"
        assert OrderStatus.READY.display_name == "🍽️ Готов"
        assert OrderStatus.OUT_FOR_DELIVERY.display_name == "🚚 В доставке"
        assert OrderStatus.DELIVERED.display_name == "🎉 Доставлен"
        assert OrderStatus.PICKED_UP.display_name == "🎉 Получен"
        assert OrderStatus.CANCELLED.display_name == "❌ Отменен"
        assert OrderStatus.REFUNDED.display_name == "💰 Возвращен"
    
    def test_order_status_is_active(self):
        """Test order status is active check."""
        assert OrderStatus.PENDING.is_active is True
        assert OrderStatus.CONFIRMED.is_active is True
        assert OrderStatus.PREPARING.is_active is True
        assert OrderStatus.READY.is_active is True
        assert OrderStatus.OUT_FOR_DELIVERY.is_active is True
        assert OrderStatus.DELIVERED.is_active is False
        assert OrderStatus.PICKED_UP.is_active is False
        assert OrderStatus.CANCELLED.is_active is False
        assert OrderStatus.REFUNDED.is_active is False
    
    def test_order_status_is_final(self):
        """Test order status is final check."""
        assert OrderStatus.PENDING.is_final is False
        assert OrderStatus.CONFIRMED.is_final is False
        assert OrderStatus.PREPARING.is_final is False
        assert OrderStatus.READY.is_final is False
        assert OrderStatus.OUT_FOR_DELIVERY.is_final is False
        assert OrderStatus.DELIVERED.is_final is True
        assert OrderStatus.PICKED_UP.is_final is True
        assert OrderStatus.CANCELLED.is_final is True
        assert OrderStatus.REFUNDED.is_final is True
    
    def test_order_status_is_successful(self):
        """Test order status is successful check."""
        assert OrderStatus.PENDING.is_successful is False
        assert OrderStatus.CONFIRMED.is_successful is False
        assert OrderStatus.PREPARING.is_successful is False
        assert OrderStatus.READY.is_successful is False
        assert OrderStatus.OUT_FOR_DELIVERY.is_successful is False
        assert OrderStatus.DELIVERED.is_successful is True
        assert OrderStatus.PICKED_UP.is_successful is True
        assert OrderStatus.CANCELLED.is_successful is False
        assert OrderStatus.REFUNDED.is_successful is False
    
    def test_order_status_is_failed(self):
        """Test order status is failed check."""
        assert OrderStatus.PENDING.is_failed is False
        assert OrderStatus.CONFIRMED.is_failed is False
        assert OrderStatus.PREPARING.is_failed is False
        assert OrderStatus.READY.is_failed is False
        assert OrderStatus.OUT_FOR_DELIVERY.is_failed is False
        assert OrderStatus.DELIVERED.is_failed is False
        assert OrderStatus.PICKED_UP.is_failed is False
        assert OrderStatus.CANCELLED.is_failed is True
        assert OrderStatus.REFUNDED.is_failed is True
    
    def test_order_status_can_be_cancelled(self):
        """Test order status can be cancelled check."""
        assert OrderStatus.PENDING.can_be_cancelled is True
        assert OrderStatus.CONFIRMED.can_be_cancelled is True
        assert OrderStatus.PREPARING.can_be_cancelled is False
        assert OrderStatus.READY.can_be_cancelled is False
        assert OrderStatus.OUT_FOR_DELIVERY.can_be_cancelled is False
        assert OrderStatus.DELIVERED.can_be_cancelled is False
        assert OrderStatus.PICKED_UP.can_be_cancelled is False
        assert OrderStatus.CANCELLED.can_be_cancelled is False
        assert OrderStatus.REFUNDED.can_be_cancelled is False
    
    def test_order_status_can_be_modified(self):
        """Test order status can be modified check."""
        assert OrderStatus.PENDING.can_be_modified is True
        assert OrderStatus.CONFIRMED.can_be_modified is False
        assert OrderStatus.PREPARING.can_be_modified is False
        assert OrderStatus.READY.can_be_modified is False
        assert OrderStatus.OUT_FOR_DELIVERY.can_be_modified is False
        assert OrderStatus.DELIVERED.can_be_modified is False
        assert OrderStatus.PICKED_UP.can_be_modified is False
        assert OrderStatus.CANCELLED.can_be_modified is False
        assert OrderStatus.REFUNDED.can_be_modified is False
    
    def test_order_status_requires_payment(self):
        """Test order status requires payment check."""
        assert OrderStatus.PENDING.requires_payment is True
        assert OrderStatus.CONFIRMED.requires_payment is True
        assert OrderStatus.PREPARING.requires_payment is False
        assert OrderStatus.READY.requires_payment is False
        assert OrderStatus.OUT_FOR_DELIVERY.requires_payment is False
        assert OrderStatus.DELIVERED.requires_payment is False
        assert OrderStatus.PICKED_UP.requires_payment is False
        assert OrderStatus.CANCELLED.requires_payment is False
        assert OrderStatus.REFUNDED.requires_payment is False
    
    def test_order_status_is_ready_for_pickup(self):
        """Test order status is ready for pickup check."""
        assert OrderStatus.PENDING.is_ready_for_pickup is False
        assert OrderStatus.CONFIRMED.is_ready_for_pickup is False
        assert OrderStatus.PREPARING.is_ready_for_pickup is False
        assert OrderStatus.READY.is_ready_for_pickup is True
        assert OrderStatus.OUT_FOR_DELIVERY.is_ready_for_pickup is False
        assert OrderStatus.DELIVERED.is_ready_for_pickup is False
        assert OrderStatus.PICKED_UP.is_ready_for_pickup is False
        assert OrderStatus.CANCELLED.is_ready_for_pickup is False
        assert OrderStatus.REFUNDED.is_ready_for_pickup is False
    
    def test_order_status_is_ready_for_delivery(self):
        """Test order status is ready for delivery check."""
        assert OrderStatus.PENDING.is_ready_for_delivery is False
        assert OrderStatus.CONFIRMED.is_ready_for_delivery is False
        assert OrderStatus.PREPARING.is_ready_for_delivery is False
        assert OrderStatus.READY.is_ready_for_delivery is True
        assert OrderStatus.OUT_FOR_DELIVERY.is_ready_for_delivery is False
        assert OrderStatus.DELIVERED.is_ready_for_delivery is False
        assert OrderStatus.PICKED_UP.is_ready_for_delivery is False
        assert OrderStatus.CANCELLED.is_ready_for_delivery is False
        assert OrderStatus.REFUNDED.is_ready_for_delivery is False
    
    def test_order_status_get_active_statuses(self):
        """Test get active statuses."""
        active_statuses = OrderStatus.get_active_statuses()
        
        assert OrderStatus.PENDING in active_statuses
        assert OrderStatus.CONFIRMED in active_statuses
        assert OrderStatus.PREPARING in active_statuses
        assert OrderStatus.READY in active_statuses
        assert OrderStatus.OUT_FOR_DELIVERY in active_statuses
        assert OrderStatus.DELIVERED not in active_statuses
        assert OrderStatus.PICKED_UP not in active_statuses
        assert OrderStatus.CANCELLED not in active_statuses
        assert OrderStatus.REFUNDED not in active_statuses
    
    def test_order_status_get_final_statuses(self):
        """Test get final statuses."""
        final_statuses = OrderStatus.get_final_statuses()
        
        assert OrderStatus.PENDING not in final_statuses
        assert OrderStatus.CONFIRMED not in final_statuses
        assert OrderStatus.PREPARING not in final_statuses
        assert OrderStatus.READY not in final_statuses
        assert OrderStatus.OUT_FOR_DELIVERY not in final_statuses
        assert OrderStatus.DELIVERED in final_statuses
        assert OrderStatus.PICKED_UP in final_statuses
        assert OrderStatus.CANCELLED in final_statuses
        assert OrderStatus.REFUNDED in final_statuses
    
    def test_order_status_get_successful_statuses(self):
        """Test get successful statuses."""
        successful_statuses = OrderStatus.get_successful_statuses()
        
        assert OrderStatus.PENDING not in successful_statuses
        assert OrderStatus.CONFIRMED not in successful_statuses
        assert OrderStatus.PREPARING not in successful_statuses
        assert OrderStatus.READY not in successful_statuses
        assert OrderStatus.OUT_FOR_DELIVERY not in successful_statuses
        assert OrderStatus.DELIVERED in successful_statuses
        assert OrderStatus.PICKED_UP in successful_statuses
        assert OrderStatus.CANCELLED not in successful_statuses
        assert OrderStatus.REFUNDED not in successful_statuses
    
    def test_order_status_get_failed_statuses(self):
        """Test get failed statuses."""
        failed_statuses = OrderStatus.get_failed_statuses()
        
        assert OrderStatus.PENDING not in failed_statuses
        assert OrderStatus.CONFIRMED not in failed_statuses
        assert OrderStatus.PREPARING not in failed_statuses
        assert OrderStatus.READY not in failed_statuses
        assert OrderStatus.OUT_FOR_DELIVERY not in failed_statuses
        assert OrderStatus.DELIVERED not in failed_statuses
        assert OrderStatus.PICKED_UP not in failed_statuses
        assert OrderStatus.CANCELLED in failed_statuses
        assert OrderStatus.REFUNDED in failed_statuses
    
    def test_order_status_string_representation(self):
        """Test order status string representation."""
        assert str(OrderStatus.PENDING) == "⏳ Ожидает подтверждения"
        assert str(OrderStatus.CONFIRMED) == "✅ Подтвержден"
        assert str(OrderStatus.PREPARING) == "👨‍🍳 Готовится"
        assert str(OrderStatus.READY) == "🍽️ Готов"
        assert str(OrderStatus.OUT_FOR_DELIVERY) == "🚚 В доставке"
        assert str(OrderStatus.DELIVERED) == "🎉 Доставлен"
        assert str(OrderStatus.PICKED_UP) == "🎉 Получен"
        assert str(OrderStatus.CANCELLED) == "❌ Отменен"
        assert str(OrderStatus.REFUNDED) == "💰 Возвращен"