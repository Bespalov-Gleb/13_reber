"""Base domain exception."""


class DomainException(Exception):
    """Base exception for domain layer."""
    
    def __init__(self, message: str, error_code: str | None = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationException(DomainException):
    """Exception raised when domain validation fails."""
    pass


class BusinessRuleException(DomainException):
    """Exception raised when business rule is violated."""
    pass


class EntityNotFoundException(DomainException):
    """Exception raised when entity is not found."""
    pass


class DuplicateEntityException(DomainException):
    """Exception raised when trying to create duplicate entity."""
    pass


class InvalidOperationException(DomainException):
    """Exception raised when operation is invalid for current state."""
    pass