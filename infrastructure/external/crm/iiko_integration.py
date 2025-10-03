"""iiko CRM integration implementation."""

from typing import List, Optional

from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from domain.entities.order import Order
from infrastructure.external.crm.base_crm import BaseCRMProvider


class IikoCRMProvider(BaseCRMProvider):
    """iiko CRM provider implementation."""
    
    def __init__(self, api_url: str, login: str, password: str):
        self.api_url = api_url
        self.login = login
        self.password = password
        self.token = None
    
    async def create_order(self, order: Order) -> bool:
        """Create order in iiko system."""
        # TODO: Implement iiko order creation
        raise NotImplementedError
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in iiko system."""
        # TODO: Implement iiko order status update
        raise NotImplementedError
    
    async def get_order_status(self, order_id: str) -> Optional[str]:
        """Get order status from iiko system."""
        # TODO: Implement iiko order status retrieval
        raise NotImplementedError
    
    async def sync_menu_items(self, items: List[MenuItem]) -> bool:
        """Sync menu items with iiko system."""
        # TODO: Implement iiko menu items sync
        raise NotImplementedError
    
    async def sync_categories(self, categories: List[Category]) -> bool:
        """Sync categories with iiko system."""
        # TODO: Implement iiko categories sync
        raise NotImplementedError
    
    async def get_menu_items(self) -> List[MenuItem]:
        """Get menu items from iiko system."""
        # TODO: Implement iiko menu items retrieval
        raise NotImplementedError
    
    async def get_categories(self) -> List[Category]:
        """Get categories from iiko system."""
        # TODO: Implement iiko categories retrieval
        raise NotImplementedError
    
    async def update_menu_item(self, item: MenuItem) -> bool:
        """Update menu item in iiko system."""
        # TODO: Implement iiko menu item update
        raise NotImplementedError
    
    async def update_category(self, category: Category) -> bool:
        """Update category in iiko system."""
        # TODO: Implement iiko category update
        raise NotImplementedError
    
    async def delete_menu_item(self, item_id: str) -> bool:
        """Delete menu item from iiko system."""
        # TODO: Implement iiko menu item deletion
        raise NotImplementedError
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete category from iiko system."""
        # TODO: Implement iiko category deletion
        raise NotImplementedError
    
    async def test_connection(self) -> bool:
        """Test connection to iiko system."""
        # TODO: Implement iiko connection test
        raise NotImplementedError
    
    async def _authenticate(self) -> bool:
        """Authenticate with iiko API."""
        # TODO: Implement iiko authentication
        raise NotImplementedError
    
    async def _refresh_token(self) -> bool:
        """Refresh iiko API token."""
        # TODO: Implement iiko token refresh
        raise NotImplementedError