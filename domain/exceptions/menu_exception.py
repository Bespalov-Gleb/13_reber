"""Menu-related exceptions."""

from domain.exceptions.domain_exception import DomainException


class MenuException(DomainException):
    """Base exception for menu operations."""
    pass


class MenuItemNotFoundException(MenuException):
    """Exception raised when menu item is not found."""
    pass


class MenuCategoryNotFoundException(MenuException):
    """Exception raised when menu category is not found."""
    pass


class MenuItemAlreadyExistsException(MenuException):
    """Exception raised when trying to create duplicate menu item."""
    pass


class MenuCategoryAlreadyExistsException(MenuException):
    """Exception raised when trying to create duplicate menu category."""
    pass


class MenuItemUnavailableException(MenuException):
    """Exception raised when menu item is unavailable."""
    pass


class InvalidMenuItemException(MenuException):
    """Exception raised when menu item data is invalid."""
    pass


class InvalidMenuCategoryException(MenuException):
    """Exception raised when menu category data is invalid."""
    pass


class MenuItemModificationException(MenuException):
    """Exception raised when menu item cannot be modified."""
    pass


class MenuCategoryModificationException(MenuException):
    """Exception raised when menu category cannot be modified."""
    pass