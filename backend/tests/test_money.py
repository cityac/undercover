from decimal import Decimal

import pytest

from backend.money import to_cents, to_str


def test_to_cents():
    assert to_cents("1250.00") == 125000
    assert to_cents(Decimal("0.01")) == 1
    assert to_cents(420.0) == 42000
    assert to_cents("1000") == 100000


@pytest.mark.parametrize("bad", ["-1.00", "1.005", "abc", "NaN", "Infinity"])
def test_to_cents_refuses(bad):
    with pytest.raises(ValueError, match="amount|decimal"):
        to_cents(bad)


def test_to_str():
    assert to_str(125000) == "1250.00"
    assert to_str(5) == "0.05"
    assert to_str(0) == "0.00"
