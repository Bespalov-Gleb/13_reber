"""Callback data parser for Telegram."""

from typing import Dict, Optional

from shared.constants.bot_constants import CALLBACK_PREFIX_CART, CALLBACK_PREFIX_CATEGORY, CALLBACK_PREFIX_ITEM, CALLBACK_PREFIX_MENU, CALLBACK_PREFIX_ORDER, CALLBACK_PREFIX_PAYMENT, CALLBACK_SEPARATOR
from shared.utils.helpers import extract_callback_data


class CallbackParser:
    """Callback data parser for Telegram."""
    
    @staticmethod
    def parse_menu_callback(callback_data: str) -> Dict[str, str]:
        """Parse menu callback data."""
        return extract_callback_data(callback_data, CALLBACK_PREFIX_MENU)
    
    @staticmethod
    def parse_category_callback(callback_data: str) -> Dict[str, str]:
        """Parse category callback data."""
        return extract_callback_data(callback_data, CALLBACK_PREFIX_CATEGORY)
    
    @staticmethod
    def parse_item_callback(callback_data: str) -> Dict[str, str]:
        """Parse item callback data."""
        return extract_callback_data(callback_data, CALLBACK_PREFIX_ITEM)
    
    @staticmethod
    def parse_cart_callback(callback_data: str) -> Dict[str, str]:
        """Parse cart callback data."""
        return extract_callback_data(callback_data, CALLBACK_PREFIX_CART)
    
    @staticmethod
    def parse_order_callback(callback_data: str) -> Dict[str, str]:
        """Parse order callback data."""
        return extract_callback_data(callback_data, CALLBACK_PREFIX_ORDER)
    
    @staticmethod
    def parse_payment_callback(callback_data: str) -> Dict[str, str]:
        """Parse payment callback data."""
        return extract_callback_data(callback_data, CALLBACK_PREFIX_PAYMENT)
    
    @staticmethod
    def get_category_id(callback_data: str) -> Optional[str]:
        """Get category ID from callback data."""
        data = CallbackParser.parse_category_callback(callback_data)
        return data.get("id")
    
    @staticmethod
    def get_item_id(callback_data: str) -> Optional[str]:
        """Get item ID from callback data."""
        data = CallbackParser.parse_item_callback(callback_data)
        return data.get("id")
    
    @staticmethod
    def get_cart_action(callback_data: str) -> Optional[str]:
        """Get cart action from callback data."""
        data = CallbackParser.parse_cart_callback(callback_data)
        return data.get("action")
    
    @staticmethod
    def get_order_id(callback_data: str) -> Optional[str]:
        """Get order ID from callback data."""
        data = CallbackParser.parse_order_callback(callback_data)
        return data.get("id")
    
    @staticmethod
    def get_payment_id(callback_data: str) -> Optional[str]:
        """Get payment ID from callback data."""
        data = CallbackParser.parse_payment_callback(callback_data)
        return data.get("id")
    
    @staticmethod
    def get_page_number(callback_data: str) -> Optional[int]:
        """Get page number from callback data."""
        data = extract_callback_data(callback_data, "")
        page_str = data.get("page")
        if page_str:
            try:
                return int(page_str)
            except ValueError:
                pass
        return None
    
    @staticmethod
    def get_quantity(callback_data: str) -> Optional[int]:
        """Get quantity from callback data."""
        data = extract_callback_data(callback_data, "")
        quantity_str = data.get("quantity")
        if quantity_str:
            try:
                return int(quantity_str)
            except ValueError:
                pass
        return None
    
    @staticmethod
    def get_action(callback_data: str) -> Optional[str]:
        """Get action from callback data."""
        data = extract_callback_data(callback_data, "")
        return data.get("action")
    
    @staticmethod
    def get_value(callback_data: str, key: str) -> Optional[str]:
        """Get value by key from callback data."""
        data = extract_callback_data(callback_data, "")
        return data.get(key)
    
    @staticmethod
    def is_menu_callback(callback_data: str) -> bool:
        """Check if callback is menu related."""
        return callback_data.startswith(CALLBACK_PREFIX_MENU)
    
    @staticmethod
    def is_category_callback(callback_data: str) -> bool:
        """Check if callback is category related."""
        return callback_data.startswith(CALLBACK_PREFIX_CATEGORY)
    
    @staticmethod
    def is_item_callback(callback_data: str) -> bool:
        """Check if callback is item related."""
        return callback_data.startswith(CALLBACK_PREFIX_ITEM)
    
    @staticmethod
    def is_cart_callback(callback_data: str) -> bool:
        """Check if callback is cart related."""
        return callback_data.startswith(CALLBACK_PREFIX_CART)
    
    @staticmethod
    def is_order_callback(callback_data: str) -> bool:
        """Check if callback is order related."""
        return callback_data.startswith(CALLBACK_PREFIX_ORDER)
    
    @staticmethod
    def is_payment_callback(callback_data: str) -> bool:
        """Check if callback is payment related."""
        return callback_data.startswith(CALLBACK_PREFIX_PAYMENT)