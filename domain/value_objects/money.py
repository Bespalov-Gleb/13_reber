"""Money value object."""

from typing import Optional

from shared.constants.payment_constants import PaymentCurrency


class Money:
    """Money value object."""
    
    def __init__(self, amount: int, currency: PaymentCurrency = PaymentCurrency.RUB):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        
        self.amount = amount  # Amount in kopecks
        self.currency = currency
    
    @property
    def rubles(self) -> int:
        """Get amount in rubles."""
        return self.amount // 100
    
    @property
    def kopecks(self) -> int:
        """Get kopecks part."""
        return self.amount % 100
    
    @classmethod
    def from_rubles(cls, rubles: int, kopecks: int = 0, currency: PaymentCurrency = PaymentCurrency.RUB) -> "Money":
        """Create Money from rubles and kopecks."""
        amount = rubles * 100 + kopecks
        return cls(amount, currency)
    
    @classmethod
    def zero(cls, currency: PaymentCurrency = PaymentCurrency.RUB) -> "Money":
        """Create zero amount Money."""
        return cls(0, currency)
    
    def add(self, other: "Money") -> "Money":
        """Add another Money amount."""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: "Money") -> "Money":
        """Subtract another Money amount."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        
        if self.amount < other.amount:
            raise ValueError("Cannot subtract amount greater than current amount")
        
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: float) -> "Money":
        """Multiply amount by factor."""
        if factor < 0:
            raise ValueError("Factor cannot be negative")
        
        new_amount = int(self.amount * factor)
        return Money(new_amount, self.currency)
    
    def divide(self, divisor: float) -> "Money":
        """Divide amount by divisor."""
        if divisor <= 0:
            raise ValueError("Divisor must be positive")
        
        new_amount = int(self.amount / divisor)
        return Money(new_amount, self.currency)
    
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == 0
    
    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > 0
    
    def is_negative(self) -> bool:
        """Check if amount is negative."""
        return self.amount < 0
    
    def __str__(self) -> str:
        if self.currency == PaymentCurrency.RUB:
            if self.kopecks == 0:
                return f"{self.rubles:,} ₽".replace(",", " ")
            else:
                return f"{self.rubles:,}.{self.kopecks:02d} ₽".replace(",", " ")
        else:
            return f"{self.amount / 100:.2f} {self.currency.value}"
    
    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency.value})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currencies")
        return self.amount < other.amount
    
    def __le__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currencies")
        return self.amount <= other.amount
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currencies")
        return self.amount > other.amount
    
    def __ge__(self, other) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currencies")
        return self.amount >= other.amount
    
    def __add__(self, other) -> "Money":
        return self.add(other)
    
    def __sub__(self, other) -> "Money":
        return self.subtract(other)
    
    def __mul__(self, factor) -> "Money":
        return self.multiply(factor)
    
    def __truediv__(self, divisor) -> "Money":
        return self.divide(divisor)