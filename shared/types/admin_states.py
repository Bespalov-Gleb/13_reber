"""Admin states for menu editing."""

from enum import Enum


class AdminState(str, Enum):
    """Admin states for menu editing."""
    
    # Category states
    ADDING_CATEGORY_NAME = "adding_category_name"
    ADDING_CATEGORY_DESCRIPTION = "adding_category_description"
    ADDING_CATEGORY_IMAGE = "adding_category_image"
    EDITING_CATEGORY_NAME = "editing_category_name"
    EDITING_CATEGORY_DESCRIPTION = "editing_category_description"
    EDITING_CATEGORY_IMAGE = "editing_category_image"
    
    # Item states
    ADDING_ITEM_NAME = "adding_item_name"
    ADDING_ITEM_DESCRIPTION = "adding_item_description"
    ADDING_ITEM_PRICE = "adding_item_price"
    ADDING_ITEM_INGREDIENTS = "adding_item_ingredients"
    ADDING_ITEM_ALLERGENS = "adding_item_allergens"
    ADDING_ITEM_WEIGHT = "adding_item_weight"
    ADDING_ITEM_CALORIES = "adding_item_calories"
    ADDING_ITEM_IMAGE = "adding_item_image"
    ADDING_ITEM_CATEGORY = "adding_item_category"
    
    EDITING_ITEM_NAME = "editing_item_name"
    EDITING_ITEM_DESCRIPTION = "editing_item_description"
    EDITING_ITEM_PRICE = "editing_item_price"
    EDITING_ITEM_INGREDIENTS = "editing_item_ingredients"
    EDITING_ITEM_ALLERGENS = "editing_item_allergens"
    EDITING_ITEM_WEIGHT = "editing_item_weight"
    EDITING_ITEM_CALORIES = "editing_item_calories"
    EDITING_ITEM_IMAGE = "editing_item_image"
    EDITING_ITEM_CATEGORY = "editing_item_category"
    
    # Default state
    IDLE = "idle"


class AdminContext:
    """Admin context for storing temporary data."""
    
    def __init__(self):
        self.state = AdminState.IDLE
        self.temp_data = {}
        self.editing_id = None  # ID of item/category being edited
    
    def reset(self):
        """Reset context."""
        self.state = AdminState.IDLE
        self.temp_data = {}
        self.editing_id = None
    
    def set_state(self, state: AdminState):
        """Set current state."""
        self.state = state
    
    def set_temp_data(self, key: str, value: str):
        """Set temporary data."""
        self.temp_data[key] = value
    
    def get_temp_data(self, key: str, default: str = None) -> str:
        """Get temporary data."""
        return self.temp_data.get(key, default)
    
    def set_editing_id(self, editing_id: str):
        """Set editing ID."""
        self.editing_id = editing_id