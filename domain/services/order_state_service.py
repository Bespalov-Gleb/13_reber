"""Order state service for managing order creation flow."""

from typing import Dict, Optional

from shared.types.order_states import OrderState, OrderContext


class OrderStateService:
    """Service for managing order creation states."""
    
    def __init__(self):
        self._contexts: Dict[int, OrderContext] = {}
    
    def get_context(self, user_id: int) -> OrderContext:
        """Get order context for user."""
        if user_id not in self._contexts:
            self._contexts[user_id] = OrderContext()
        return self._contexts[user_id]
    
    def set_state(self, user_id: int, state: OrderState):
        """Set order state for user."""
        context = self.get_context(user_id)
        context.set_state(state)
    
    def get_state(self, user_id: int) -> OrderState:
        """Get current order state for user."""
        context = self.get_context(user_id)
        return context.state
    
    def set_temp_data(self, user_id: int, key: str, value: str):
        """Set temporary data for user."""
        context = self.get_context(user_id)
        context.set_temp_data(key, value)
    
    def get_temp_data(self, user_id: int, key: str, default: str = None) -> str:
        """Get temporary data for user."""
        context = self.get_context(user_id)
        return context.get_temp_data(key, default)
    
    def reset_context(self, user_id: int):
        """Reset order context for user."""
        if user_id in self._contexts:
            self._contexts[user_id].reset()
    
    def get_context_data(self, user_id: int) -> OrderContext:
        """Get full context for user."""
        return self.get_context(user_id)


# Global instance
order_state_service = OrderStateService()
