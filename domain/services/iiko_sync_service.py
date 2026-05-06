"""iiko synchronization service."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from domain.entities.order import Order
from domain.repositories.menu_repository import MenuRepository
from domain.services.menu_service import MenuService
from infrastructure.external.crm.iiko_integration import IikoCRMProvider


class IikoSyncService:
    """Service for synchronizing data with iiko CRM."""
    
    def __init__(
        self,
        menu_repository: MenuRepository,
        menu_service: MenuService,
        iiko_provider: IikoCRMProvider
    ):
        self.menu_repository = menu_repository
        self.menu_service = menu_service
        self.iiko_provider = iiko_provider
        self.logger = logging.getLogger(__name__)
        self._sync_in_progress = False
        self._last_sync_time = None
        self._last_error: Optional[str] = None
    
    async def sync_menu_from_iiko(self, force: bool = False) -> bool:
        """
        Synchronize menu from iiko to local database.
        
        Args:
            force: Force sync even if recently synced
            
        Returns:
            True if sync was successful
        """
        if self._sync_in_progress:
            self.logger.warning("Menu sync already in progress")
            self._last_error = "Синхронизация уже выполняется"
            return False
        
        # Check if sync is needed
        if not force and self._last_sync_time:
            time_since_sync = datetime.now() - self._last_sync_time
            if time_since_sync < timedelta(minutes=30):  # Sync max once per 30 minutes
                self.logger.info("Menu sync skipped - recently synced")
                self._last_error = None
                return True
        
        self._sync_in_progress = True
        self._last_error = None
        
        try:
            self.logger.info("Starting menu sync from iiko")
            
            # Test connection first
            if not await self.iiko_provider.test_connection():
                self.logger.error("Failed to connect to iiko")
                self._last_error = "Не удалось подключиться к iiko (проверь IIKO_API_URL / IIKO_API_LOGIN)"
                return False
            
            # Get categories from iiko
            iiko_categories = await self.iiko_provider.get_categories()
            if not iiko_categories:
                self.logger.warning("No categories received from iiko")
                self._last_error = "iiko вернул 0 категорий (проверь публикацию меню/групп в iiko)"
                return False
            
            # Get menu items from iiko
            iiko_items = await self.iiko_provider.get_menu_items()
            if not iiko_items:
                self.logger.warning("No menu items received from iiko")
                self._last_error = "iiko вернул 0 блюд (проверь номенклатуру и принадлежность к группам)"
                return False
            
            # Sync categories
            await self._sync_categories(iiko_categories)
            
            # Sync menu items
            await self._sync_menu_items(iiko_items)
            
            self._last_sync_time = datetime.now()
            self._last_error = None
            self.logger.info(f"Menu sync completed successfully: {len(iiko_categories)} categories, {len(iiko_items)} items")
            return True
            
        except Exception as e:
            self.logger.error(f"Menu sync failed: {e}")
            self._last_error = str(e)
            return False
        finally:
            self._sync_in_progress = False
            # Prevent aiohttp session leaks on repeated sync/test calls.
            close = getattr(self.iiko_provider, "close", None)
            if callable(close):
                try:
                    await close()
                except Exception as close_error:
                    self.logger.warning(f"Failed to close iiko provider session: {close_error}")
    
    async def _sync_categories(self, iiko_categories: List[Category]) -> None:
        """Sync categories from iiko."""
        try:
            # Get existing categories
            existing_categories = await self.menu_repository.get_categories()
            existing_by_id = {cat.id: cat for cat in existing_categories}
            
            for iiko_category in iiko_categories:
                if iiko_category.id in existing_by_id:
                    # Update existing category
                    existing = existing_by_id[iiko_category.id]
                    existing.name = iiko_category.name
                    existing.description = iiko_category.description
                    existing.is_active = iiko_category.is_active
                    existing.sort_order = iiko_category.sort_order
                    existing.updated_at = datetime.now()
                    
                    await self.menu_repository.update_category(existing)
                    self.logger.debug(f"Updated category: {existing.name}")
                else:
                    # Create new category
                    await self.menu_repository.create_category(iiko_category)
                    self.logger.debug(f"Created category: {iiko_category.name}")
            
            # Deactivate categories that no longer exist in iiko
            iiko_category_ids = {cat.id for cat in iiko_categories}
            for existing in existing_categories:
                if existing.id not in iiko_category_ids and existing.is_active:
                    existing.is_active = False
                    existing.updated_at = datetime.now()
                    await self.menu_repository.update_category(existing)
                    self.logger.debug(f"Deactivated category: {existing.name}")
                    
        except Exception as e:
            self.logger.error(f"Error syncing categories: {e}")
            raise
    
    async def _sync_menu_items(self, iiko_items: List[MenuItem]) -> None:
        """Sync menu items from iiko."""
        try:
            # Get existing menu items
            existing_items = await self.menu_repository.get_menu_items()
            existing_by_id = {item.id: item for item in existing_items}
            
            for iiko_item in iiko_items:
                if iiko_item.id in existing_by_id:
                    # Update existing item
                    existing = existing_by_id[iiko_item.id]
                    existing.name = iiko_item.name
                    existing.description = iiko_item.description
                    existing.price = iiko_item.price
                    existing.category_id = iiko_item.category_id
                    existing.is_available = iiko_item.is_available
                    existing.image_url = iiko_item.image_url
                    existing.updated_at = datetime.now()
                    
                    await self.menu_repository.update_menu_item(existing)
                    self.logger.debug(f"Updated menu item: {existing.name}")
                else:
                    # Create new item
                    await self.menu_repository.create_menu_item(iiko_item)
                    self.logger.debug(f"Created menu item: {iiko_item.name}")
            
            # Deactivate items that no longer exist in iiko
            iiko_item_ids = {item.id for item in iiko_items}
            for existing in existing_items:
                if existing.id not in iiko_item_ids and existing.is_available:
                    existing.is_available = False
                    existing.updated_at = datetime.now()
                    await self.menu_repository.update_menu_item(existing)
                    self.logger.debug(f"Deactivated menu item: {existing.name}")
                    
        except Exception as e:
            self.logger.error(f"Error syncing menu items: {e}")
            raise
    
    async def send_order_to_iiko(self, order: Order) -> bool:
        """
        Send order to iiko system.
        
        Args:
            order: Order to send
            
        Returns:
            True if order was sent successfully
        """
        try:
            self.logger.info(f"Sending order {order.order_id} to iiko")
            
            # Test connection first
            if not await self.iiko_provider.test_connection():
                self.logger.error("Failed to connect to iiko")
                return False
            
            # Send order to iiko
            success = await self.iiko_provider.create_order(order)
            
            if success:
                self.logger.info(f"Order {order.order_id} sent to iiko successfully")
            else:
                self.logger.error(f"Failed to send order {order.order_id} to iiko")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending order to iiko: {e}")
            return False
        finally:
            close = getattr(self.iiko_provider, "close", None)
            if callable(close):
                try:
                    await close()
                except Exception as close_error:
                    self.logger.warning(f"Failed to close iiko provider session: {close_error}")
    
    async def get_order_status_from_iiko(self, order_id: str) -> Optional[str]:
        """
        Get order status from iiko system.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order status or None if not found
        """
        try:
            if not await self.iiko_provider.test_connection():
                self.logger.error("Failed to connect to iiko")
                return None
            
            status = await self.iiko_provider.get_order_status(order_id)
            
            if status:
                self.logger.info(f"Order {order_id} status from iiko: {status}")
            else:
                self.logger.warning(f"Order {order_id} not found in iiko")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting order status from iiko: {e}")
            return None
    
    async def sync_order_statuses(self, order_ids: List[str]) -> Dict[str, str]:
        """
        Sync order statuses from iiko for multiple orders.
        
        Args:
            order_ids: List of order IDs to check
            
        Returns:
            Dictionary mapping order_id to status
        """
        try:
            if not await self.iiko_provider.test_connection():
                self.logger.error("Failed to connect to iiko")
                return {}
            
            statuses = {}
            for order_id in order_ids:
                status = await self.iiko_provider.get_order_status(order_id)
                if status:
                    statuses[order_id] = status
            
            self.logger.info(f"Synced statuses for {len(statuses)} orders")
            return statuses
            
        except Exception as e:
            self.logger.error(f"Error syncing order statuses: {e}")
            return {}
    
    async def test_iiko_connection(self) -> bool:
        """Test connection to iiko system."""
        try:
            return await self.iiko_provider.test_connection()
        except Exception as e:
            self.logger.error(f"Error testing iiko connection: {e}")
            return False
        finally:
            close = getattr(self.iiko_provider, "close", None)
            if callable(close):
                try:
                    await close()
                except Exception as close_error:
                    self.logger.warning(f"Failed to close iiko provider session: {close_error}")
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Get last sync time."""
        return self._last_sync_time
    
    def is_sync_in_progress(self) -> bool:
        """Check if sync is currently in progress."""
        return self._sync_in_progress

    def get_last_error(self) -> Optional[str]:
        """Get last synchronization error."""
        return self._last_error
