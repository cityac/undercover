"""US dollar amounts as integer cents."""

from decimal import Decimal, InvalidOperation

CENT = Decimal("0.01")


def to_cents(amount: Decimal | str | float) -> int:
    """Convert a dollar amount to cents, refusing negatives and fractions of a cent."""
    try:
        value = Decimal(str(amount))
    except InvalidOperation as error:
        raise ValueError(f"{amount} is not an amount") from error
    if not value.is_finite() or value < 0:
        raise ValueError(f"{amount} is not a valid amount")
    if value != value.quantize(CENT):
        raise ValueError(f"{amount} has more than two decimal places")
    return int(value * 100)


def to_str(cents: int) -> str:
    """Format cents as a dollar string with two decimals, such as 1250.00."""
    return f"{Decimal(cents) / 100:.2f}"
