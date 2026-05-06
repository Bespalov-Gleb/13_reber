"""Order states for order creation flow."""

from enum import Enum


class OrderState(str, Enum):
    """Order states for order creation flow."""
    
    # Initial state
    IDLE = "idle"
    
    # Order type selection
    SELECTING_ORDER_TYPE = "selecting_order_type"
    
    # Delivery flow
    ENTERING_DELIVERY_ADDRESS = "entering_delivery_address"
    SELECTING_ADDRESS_SUGGESTION = "selecting_address_suggestion"
    ENTERING_DELIVERY_PHONE = "entering_delivery_phone"
    
    # Time selection
    SELECTING_ORDER_TIME = "selecting_order_time"
    ENTERING_SCHEDULED_TIME = "entering_scheduled_time"
    
    # Comment
    ENTERING_ORDER_COMMENT = "entering_order_comment"
    
    # Promo code
    ENTERING_PROMO_CODE = "entering_promo_code"
    
    # Final confirmation
    CONFIRMING_ORDER = "confirming_order"


class OrderContext:
    """Order context for storing temporary data during order creation."""
    
    def __init__(self):
        self.state = OrderState.IDLE
        self.temp_data = {}
        self.order_type = None  # "delivery" or "pickup"
        self.payment_method = None  # "cash" or "card"
        self.delivery_address = None
        self.delivery_phone = None
        self.order_time_type = None  # "asap" or "scheduled"
        self.scheduled_time = None
        self.comment = None
        self.promo_code = None
        self.promo_discount = 0  # in kopecks
    
    def reset(self):
        """Reset context."""
        self.state = OrderState.IDLE
        self.temp_data = {}
        self.order_type = None
        self.payment_method = None
        self.delivery_address = None
        self.delivery_phone = None
        self.order_time_type = None
        self.scheduled_time = None
        self.comment = None
        self.promo_code = None
        self.promo_discount = 0
    
    def set_state(self, state: OrderState):
        """Set current state."""
        self.state = state
    
    def set_temp_data(self, key: str, value: str):
        """Set temporary data."""
        self.temp_data[key] = value
    
    def get_temp_data(self, key: str, default: str = None) -> str:
        """Get temporary data."""
        return self.temp_data.get(key, default)
    
    def set_order_type(self, order_type: str):
        """Set order type."""
        self.order_type = order_type
    
    def set_payment_method(self, payment_method: str):
        """Set payment method."""
        self.payment_method = payment_method
    
    def set_delivery_address(self, address: str):
        """Set delivery address."""
        self.delivery_address = address
    
    def set_delivery_phone(self, phone: str):
        """Set delivery phone."""
        self.delivery_phone = phone
    
    def set_order_time_type(self, time_type: str):
        """Set order time type."""
        self.order_time_type = time_type
    
    def set_scheduled_time(self, time: str):
        """Set scheduled time."""
        self.scheduled_time = time
    
    def set_comment(self, comment: str):
        """Set order comment."""
        self.comment = comment
