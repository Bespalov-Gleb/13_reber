"""Payment-related exceptions."""

from domain.exceptions.domain_exception import DomainException


class PaymentException(DomainException):
    """Base exception for payment operations."""
    pass


class PaymentNotFoundException(PaymentException):
    """Exception raised when payment is not found."""
    pass


class PaymentAlreadyExistsException(PaymentException):
    """Exception raised when trying to create duplicate payment."""
    pass


class PaymentProcessingException(PaymentException):
    """Exception raised when payment processing fails."""
    pass


class PaymentValidationException(PaymentException):
    """Exception raised when payment validation fails."""
    pass


class PaymentProviderException(PaymentException):
    """Exception raised when payment provider returns error."""
    pass


class PaymentTimeoutException(PaymentException):
    """Exception raised when payment times out."""
    pass


class PaymentRefundException(PaymentException):
    """Exception raised when payment refund fails."""
    pass


class InsufficientFundsException(PaymentException):
    """Exception raised when insufficient funds for payment."""
    pass


class InvalidPaymentMethodException(PaymentException):
    """Exception raised when payment method is invalid."""
    pass


class PaymentSecurityException(PaymentException):
    """Exception raised when payment security check fails."""
    pass