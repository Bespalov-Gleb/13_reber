"""Admin state service for managing admin editing states."""

from typing import Dict, Optional
from shared.types.admin_states import AdminState, AdminContext


class AdminStateService:
    """Service for managing admin editing states."""
    
    def __init__(self):
        self._admin_contexts: Dict[int, AdminContext] = {}
    
    def get_admin_context(self, user_id: int) -> AdminContext:
        """Get admin context for user."""
        if user_id not in self._admin_contexts:
            self._admin_contexts[user_id] = AdminContext()
        return self._admin_contexts[user_id]
    
    def set_admin_state(self, user_id: int, state: AdminState):
        """Set admin state."""
        context = self.get_admin_context(user_id)
        context.set_state(state)
    
    def get_admin_state(self, user_id: int) -> AdminState:
        """Get admin state."""
        context = self.get_admin_context(user_id)
        return context.state
    
    def set_temp_data(self, user_id: int, key: str, value: str):
        """Set temporary data."""
        context = self.get_admin_context(user_id)
        context.set_temp_data(key, value)
    
    def get_temp_data(self, user_id: int, key: str, default: str = None) -> str:
        """Get temporary data."""
        context = self.get_admin_context(user_id)
        return context.get_temp_data(key, default)
    
    def set_editing_id(self, user_id: int, editing_id: str):
        """Set editing ID."""
        context = self.get_admin_context(user_id)
        context.set_editing_id(editing_id)
    
    def get_editing_id(self, user_id: int) -> Optional[str]:
        """Get editing ID."""
        context = self.get_admin_context(user_id)
        return context.editing_id
    
    def reset_admin_context(self, user_id: int):
        """Reset admin context."""
        context = self.get_admin_context(user_id)
        context.reset()
    
    def is_admin_editing(self, user_id: int) -> bool:
        """Check if admin is in editing mode."""
        state = self.get_admin_state(user_id)
        return state != AdminState.IDLE


# Global instance
admin_state_service = AdminStateService()