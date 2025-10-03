"""Order-related exceptions."""

from domain.exceptions.domain_exception import DomainException


class OrderException(DomainException):
    """Base exception for order operations."""
    pass


class OrderNotFoundException(OrderException):
    """Exception raised when order is not found."""
    pass


class InvalidOrderStatusException(OrderException):
    """Exception raised when order status transition is invalid."""
    pass


class OrderAlreadyExistsException(OrderException):
    """Exception raised when trying to create duplicate order."""
    pass


class OrderCancellationException(OrderException):
    """Exception raised when order cannot be cancelled."""
    pass


class OrderModificationException(OrderException):
    """Exception raised when order cannot be modified."""
    pass


class InsufficientOrderAmountException(OrderException):
    """Exception raised when order amount is below minimum."""
    pass


class OrderItemNotFoundException(OrderException):
    """Exception raised when order item is not found."""
    pass


class OrderDeliveryException(OrderException):
    """Exception raised when delivery is not available."""
    pass


class OrderTimeException(OrderException):
    """Exception raised when order time is invalid."""
    pass