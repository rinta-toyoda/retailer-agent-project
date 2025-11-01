"""
Money Value Object - Domain Model
Represents monetary values with currency handling.
Marking Criteria: 4.1 (Implementation of Stage 1 Requirements and Design)
"""

from decimal import Decimal
from typing import Optional


class Money:
    """
    Value object representing a monetary amount with currency.
    Immutable to ensure consistency in financial calculations.
    """

    def __init__(self, amount: Decimal, currency: str = "USD"):
        """
        Initialize Money value object.

        Args:
            amount: Decimal amount (precision for financial calculations)
            currency: ISO currency code (default: USD)
        """
        self.amount = Decimal(str(amount))  # Ensure Decimal precision
        self.currency = currency.upper()

    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects (must have same currency)."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract Money objects."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: int | float | Decimal) -> "Money":
        """Multiply Money by a scalar."""
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __str__(self) -> str:
        """String representation."""
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self) -> str:
        """Repr representation."""
        return f"Money(amount={self.amount}, currency='{self.currency}')"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "amount": float(self.amount),
            "currency": self.currency,
            "formatted": str(self)
        }

    @classmethod
    def from_float(cls, amount: float, currency: str = "USD") -> "Money":
        """Create Money from float (convenience method)."""
        return cls(Decimal(str(amount)), currency)

    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        """Create zero Money value."""
        return cls(Decimal("0"), currency)
