"""iiko CRM integration implementation."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import aiohttp
from domain.entities.category import Category
from domain.entities.menu_item import MenuItem
from domain.entities.order import Order, OrderStatus, OrderType
from infrastructure.external.crm.base_crm import BaseCRMProvider


class IikoCRMProvider(BaseCRMProvider):
    """iiko CRM provider implementation using iiko API."""
    
    def __init__(self, api_url: str, api_login: str, organization_id: str = None):
        """
        Initialize iiko CRM provider.
        
        Args:
            api_url: iiko API base URL (e.g., https://api-ru.iiko.services)
            api_login: iiko API login (created in iikoWeb)
            organization_id: Organization ID in iiko (optional, will be fetched if not provided)
        """
        self.api_url = api_url.rstrip('/')
        self.api_login = api_login
        self.organization_id = organization_id
        self.token = None
        self.token_expires_at = None
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # API endpoints
        self.auth_url = f"{self.api_url}/api/1/access_token"
        self.organizations_url = f"{self.api_url}/api/1/organizations"
        self.terminal_groups_url = f"{self.api_url}/api/1/terminal_groups"
        self.order_types_url = f"{self.api_url}/api/1/deliveries/order_types"
        self.payment_types_url = f"{self.api_url}/api/1/payment_types"
        self.command_status_url = f"{self.api_url}/api/1/commands/status"
        self.menu_url = f"{self.api_url}/api/1/nomenclature"
        self.deliveries_url = f"{self.api_url}/api/1/deliveries/create"
        self.delivery_status_url = f"{self.api_url}/api/1/deliveries/by_id"
        self._terminal_group_id: Optional[str] = None
        self._order_type_ids: Dict[str, str] = {}
        self._payment_type_ids: Dict[str, str] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self) -> None:
        """Close underlying HTTP session safely."""
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None
    
    async def _authenticate(self) -> bool:
        """Authenticate with iiko API and get access token."""
        try:
            session = await self._get_session()
            
            auth_data = {
                "apiLogin": self.api_login
            }
            
            async with session.post(
                self.auth_url,
                json=auth_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.token = result.get("token")
                    if self.token:
                        # iiko tokens typically expire in 1 hour
                        self.token_expires_at = datetime.now() + timedelta(hours=1)
                        self.logger.info("Successfully authenticated with iiko API")
                        return True
                    else:
                        self.logger.error("No token received from iiko API")
                        return False
                else:
                    error_text = await response.text()
                    self.logger.error(f"Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid token."""
        if not self.token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return await self._authenticate()
        return True
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to iiko API."""
        if not await self._ensure_authenticated():
            return None
        
        session = await self._get_session()
        headers = kwargs.get('headers', {})
        headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        kwargs['headers'] = headers
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # Token expired, try to re-authenticate
                    self.token = None
                    if await self._authenticate():
                        headers["Authorization"] = f"Bearer {self.token}"
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                else:
                    error_text = await response.text()
                    self.logger.error(f"API request failed: {response.status} - {error_text}")
                    return None
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            return None
    
    async def _get_organization_id(self) -> Optional[str]:
        """Get organization ID if not provided."""
        if self.organization_id:
            return self.organization_id
        
        data = await self._make_request("POST", self.organizations_url, json={})
        if data and "organizations" in data:
            organizations = data["organizations"]
            if organizations:
                # Use the first organization or find by name
                org = organizations[0]
                self.organization_id = org["id"]
                self.logger.info(f"Using organization: {org.get('name', 'Unknown')} (ID: {self.organization_id})")
                return self.organization_id
        
        self.logger.error("No organizations found")
        return None

    async def _get_terminal_group_id(self, organization_id: str) -> Optional[str]:
        """Get terminal group ID for organization."""
        if self._terminal_group_id:
            return self._terminal_group_id

        data = await self._make_request(
            "POST",
            self.terminal_groups_url,
            json={"organizationIds": [organization_id], "includeDisabled": False},
        )
        if not data:
            return None

        groups = data.get("terminalGroups") or []
        if not groups:
            self.logger.error("No terminal groups found for organization")
            return None

        items = groups[0].get("items") or []
        if not items:
            self.logger.error("No terminal group items found")
            return None

        terminal_id = items[0].get("id")
        if terminal_id:
            self._terminal_group_id = terminal_id
        return terminal_id

    async def _load_order_types(self, organization_id: str) -> None:
        """Load and cache delivery order types."""
        if self._order_type_ids:
            return

        data = await self._make_request(
            "POST",
            self.order_types_url,
            json={"organizationIds": [organization_id]},
        )
        order_types = data.get("orderTypes") if data else None
        if not order_types:
            self.logger.error("No order types received from iiko")
            return

        for order_type in order_types:
            name = (order_type.get("name") or "").lower()
            service_type = (order_type.get("orderServiceType") or "").lower()
            order_type_id = order_type.get("id")
            if not order_type_id:
                continue
            # Match by service type first.
            if "delivery" in service_type:
                self._order_type_ids["delivery"] = order_type_id
            elif "selfservice" in service_type or "pickup" in service_type:
                self._order_type_ids["pickup"] = order_type_id
            # Fallback by localized name.
            if "достав" in name:
                self._order_type_ids["delivery"] = order_type_id
            elif "самовывоз" in name:
                self._order_type_ids["pickup"] = order_type_id

        # Last resort: first order type
        if not self._order_type_ids and order_types:
            fallback_id = order_types[0].get("id")
            if fallback_id:
                self._order_type_ids["delivery"] = fallback_id

    async def _load_payment_types(self, organization_id: str) -> None:
        """Load and cache payment types."""
        if self._payment_type_ids:
            return

        data = await self._make_request(
            "POST",
            self.payment_types_url,
            json={"organizationIds": [organization_id]},
        )
        payment_types = data.get("paymentTypes") if data else None
        if not payment_types:
            self.logger.error("No payment types received from iiko")
            return

        # Prefer explicit kind mapping.
        for payment in payment_types:
            payment_id = payment.get("id")
            if not payment_id:
                continue
            kind = (payment.get("paymentTypeKind") or "").lower()
            name = (payment.get("name") or "").lower()

            if "cash" in kind or "нал" in name:
                self._payment_type_ids.setdefault("cash", payment_id)
            if "card" in kind or "карт" in name:
                self._payment_type_ids.setdefault("card", payment_id)

        # online payments are usually card/acquiring in iiko mappings
        if "online" not in self._payment_type_ids:
            if "card" in self._payment_type_ids:
                self._payment_type_ids["online"] = self._payment_type_ids["card"]

        # Fallback for any missing values
        fallback_id = next((p.get("id") for p in payment_types if p.get("id")), None)
        if fallback_id:
            self._payment_type_ids.setdefault("cash", fallback_id)
            self._payment_type_ids.setdefault("card", fallback_id)
            self._payment_type_ids.setdefault("online", fallback_id)
    
    async def test_connection(self) -> bool:
        """Test connection to iiko system."""
        try:
            if not await self._authenticate():
                return False
            
            org_id = await self._get_organization_id()
            return org_id is not None
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_categories(self) -> List[Category]:
        """Get categories from iiko system."""
        try:
            org_id = await self._get_organization_id()
            if not org_id:
                return []
            
            data = await self._make_request("POST", self.menu_url, json={
                "organizationId": org_id
            })
            
            if not data or "groups" not in data:
                return []
            
            categories = []
            for group in data["groups"]:
                category = Category(
                    id=group["id"],
                    name=group["name"],
                    description=group.get("description", ""),
                    is_active=group.get("isDeleted", False) == False,
                    sort_order=group.get("sortOrder", 0),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                categories.append(category)
            
            self.logger.info(f"Retrieved {len(categories)} categories from iiko")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return []
    
    async def get_menu_items(self) -> List[MenuItem]:
        """Get menu items from iiko system."""
        try:
            org_id = await self._get_organization_id()
            if not org_id:
                return []
            
            data = await self._make_request("POST", self.menu_url, json={
                "organizationId": org_id
            })
            
            if not data or "products" not in data:
                return []
            
            menu_items = []
            for product in data["products"]:
                # Skip deleted or inactive items
                if product.get("isDeleted", False):
                    continue
                
                # Get price from size prices
                price = 0
                if "sizePrices" in product and product["sizePrices"]:
                    price = product["sizePrices"][0].get("price", {}).get("currentPrice", 0)
                
                menu_item = MenuItem(
                    id=product["id"],
                    name=product["name"],
                    description=product.get("description", ""),
                    price=price,  # Price in kopecks
                    category_id=product.get("groupId", ""),
                    is_available=not product.get("isDeleted", False),
                    image_url=product.get("imageLinks", [{}])[0].get("url", "") if product.get("imageLinks") else "",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                menu_items.append(menu_item)
            
            self.logger.info(f"Retrieved {len(menu_items)} menu items from iiko")
            return menu_items
            
        except Exception as e:
            self.logger.error(f"Error getting menu items: {e}")
            return []
    
    async def create_order(self, order: Order) -> bool:
        """Create order in iiko system."""
        try:
            org_id = await self._get_organization_id()
            if not org_id:
                return False

            terminal_group_id = await self._get_terminal_group_id(org_id)
            if not terminal_group_id:
                self.logger.error("Failed to resolve terminalGroupId")
                return False

            await self._load_order_types(org_id)
            await self._load_payment_types(org_id)
            
            # Convert order to iiko delivery format
            delivery_data = self._convert_order_to_delivery(order, org_id, terminal_group_id)
            if not delivery_data:
                self.logger.error("Failed to build delivery payload")
                return False
            
            data = await self._make_request("POST", self.deliveries_url, json=delivery_data)
            
            if not data:
                self.logger.error(f"Failed to create order {order.order_id} in iiko")
                return False

            correlation_id = data.get("correlationId")
            if not correlation_id:
                # Some configurations may return order info directly.
                if data.get("orderInfo") and data["orderInfo"].get("id"):
                    self.logger.info(f"Order {order.order_id} created in iiko")
                    return True
                self.logger.error("iiko create order: correlationId is missing")
                return False

            success = await self._wait_command_success(org_id, correlation_id)
            if success:
                self.logger.info(f"Order {order.order_id} created in iiko (correlationId: {correlation_id})")
            else:
                self.logger.error(f"iiko command failed for order {order.order_id} (correlationId: {correlation_id})")
            return success
                
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            return False
    
    async def _wait_command_success(self, organization_id: str, correlation_id: str) -> bool:
        """Poll iiko command status for async create operations."""
        for _ in range(20):
            status = await self._make_request(
                "POST",
                self.command_status_url,
                json={"organizationId": organization_id, "correlationId": correlation_id},
            )
            if status:
                state = (status.get("state") or "").lower()
                if state == "success":
                    return True
                if state == "error":
                    self.logger.error(f"iiko command error: {status.get('exception')}")
                    return False
            await asyncio.sleep(1)
        self.logger.error("iiko command status timeout")
        return False

    def _convert_order_to_delivery(self, order: Order, org_id: str, terminal_group_id: str) -> Optional[Dict[str, Any]]:
        """Convert internal order to iiko delivery format."""
        order_type_key = "delivery" if order.order_type.value == "delivery" else "pickup"
        order_type_id = self._order_type_ids.get(order_type_key)
        if not order_type_id:
            fallback_order_type_id = self._order_type_ids.get("delivery")
            if not fallback_order_type_id:
                self.logger.error(f"Order type id not found for '{order_type_key}'")
                return None
            self.logger.warning(
                f"Order type id not found for '{order_type_key}', fallback to delivery order type"
            )
            order_type_id = fallback_order_type_id

        payment_method_key = order.payment_method.value
        payment_type_id = self._payment_type_ids.get(payment_method_key)
        if not payment_type_id:
            self.logger.error(f"Payment type id not found for '{payment_method_key}'")
            return None

        # We don't have expanded user entity at this layer.
        customer_name = "Клиент"
        phone = ""
        if order.delivery_info and order.delivery_info.phone:
            phone = order.delivery_info.phone
        elif order.pickup_info and order.pickup_info.phone:
            phone = order.pickup_info.phone
        
        # Prepare order items
        order_items = []
        for item in order.items:
            order_items.append({
                "productId": item.item_id,
                "type": "Product",
                "amount": item.quantity,
                "productSizeId": None,  # Use default size
                "modifiers": [],  # No modifiers for now
                "positionId": None
            })
        
        # Prepare delivery data
        delivery_data = {
            "organizationId": org_id,
            "terminalGroupId": terminal_group_id,
            "order": {
                "id": order.order_id,
                "externalNumber": order.order_id,
                "orderTypeId": order_type_id,
                "orderServiceType": "DeliveryByCourier" if order.order_type == OrderType.DELIVERY else "Pickup",
                "deliveryPoint": {
                    "address": {
                        "street": {
                            "name": order.delivery_info.address if order.delivery_info else "Самовывоз"
                        },
                        "house": "",
                        "flat": "",
                        "entrance": "",
                        "floor": "",
                        "doorphone": "",
                        "comment": order.delivery_info.comment if order.delivery_info else ""
                    },
                    "coordinates": {
                        "latitude": 0.0,
                        "longitude": 0.0
                    }
                },
                "phone": phone,
                "customer": {
                    "name": customer_name,
                    "phone": phone
                },
                "comment": order.comment or "",
                "items": order_items,
                "payments": [
                    {
                        "paymentTypeKind": "Cash" if order.payment_method.value == "cash" else "Card",
                        "paymentTypeId": payment_type_id,
                        "sum": order.total
                    }
                ],
                "tips": [],
                "discounts": [],
                "sourceKey": "telegram_bot"
            }
        }
        
        return delivery_data
    
    async def get_order_status(self, order_id: str) -> Optional[str]:
        """Get order status from iiko system."""
        try:
            org_id = await self._get_organization_id()
            if not org_id:
                return None
            
            data = await self._make_request("POST", self.delivery_status_url, json={
                "organizationId": org_id,
                "orderIds": [order_id]
            })
            
            if data and "orders" in data and data["orders"]:
                order_data = data["orders"][0]
                status = order_data.get("status", "")
                
                # Map iiko status to our status
                status_mapping = {
                    "New": "pending",
                    "WaitCooking": "confirmed",
                    "ReadyForCooking": "confirmed",
                    "StartedCooking": "confirmed",
                    "CookingCompleted": "ready",
                    "Waiting": "ready",
                    "OnWay": "out_for_delivery",
                    "Delivered": "delivered",
                    "Closed": "delivered",
                    "Cancelled": "cancelled"
                }
                
                return status_mapping.get(status, "pending")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return None
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in iiko system."""
        # iiko typically manages order status internally
        # This method can be used for manual status updates if needed
        self.logger.info(f"Order status update requested for {order_id}: {status}")
        return True
    
    async def sync_categories(self, categories: List[Category]) -> bool:
        """Sync categories with iiko system."""
        # iiko typically manages categories internally
        # This method can be used for manual sync if needed
        self.logger.info(f"Categories sync requested: {len(categories)} categories")
        return True
    
    async def sync_menu_items(self, items: List[MenuItem]) -> bool:
        """Sync menu items with iiko system."""
        # iiko typically manages menu items internally
        # This method can be used for manual sync if needed
        self.logger.info(f"Menu items sync requested: {len(items)} items")
        return True
    
    async def update_category(self, category: Category) -> bool:
        """Update category in iiko system."""
        # iiko typically manages categories internally
        self.logger.info(f"Category update requested: {category.name}")
        return True
    
    async def update_menu_item(self, item: MenuItem) -> bool:
        """Update menu item in iiko system."""
        # iiko typically manages menu items internally
        self.logger.info(f"Menu item update requested: {item.name}")
        return True
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete category from iiko system."""
        # iiko typically manages categories internally
        self.logger.info(f"Category deletion requested: {category_id}")
        return True
    
    async def delete_menu_item(self, item_id: str) -> bool:
        """Delete menu item from iiko system."""
        # iiko typically manages menu items internally
        self.logger.info(f"Menu item deletion requested: {item_id}")
        return True
    
    async def _refresh_token(self) -> bool:
        """Refresh iiko API token."""
        return await self._authenticate()