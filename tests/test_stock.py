import pytest

from med_tracker.core.stock import (
    calculate_days_left,
    find_low_stock,
    is_low_stock,
    verify_enough_stock,
)
from med_tracker.database import Medication
from med_tracker.exceptions import InsufficientStockError


def make(name: str = "Med", total: int = 30, dose: int = 2) -> Medication:
    """Small factory so each test reads clearly."""
    return Medication(name=name, total_pills=total, daily_dosage=dose)


def test_calculate_days_left() -> None:
    assert calculate_days_left(20, 3) == 6  # 20 // 3 = 6, not 6.6


def test_is_low_stock_above() -> None:
    assert is_low_stock(16, 14) is False


def test_is_low_stock_boundary_equal() -> None:
    assert is_low_stock(14, 14) is True


def test_is_low_stock_below() -> None:
    assert is_low_stock(12, 14) is True


def test_find_low_stock_low() -> None:
    assert find_low_stock([make("A", 10, 1)]) == {"A": 10}


def test_find_low_stock_enough() -> None:
    assert find_low_stock([make("A", 100, 1)]) == {}


def test_find_low_stock_empty() -> None:
    assert find_low_stock([]) == {}


def test_find_low_stock_zero_dosage() -> None:
    # Verifies the zero-division error.
    assert find_low_stock([make("A", 100, 0)]) == {}


def test_find_low_stock_custom_threshold() -> None:
    assert find_low_stock([make("A", 30, 2)], 30) == {"A": 15}


def test_verify_enough_stock_ok() -> None:
    verify_enough_stock(make("A", 10, 2))  # Enough means no raise


def test_verify_enough_stock_raises() -> None:
    with pytest.raises(InsufficientStockError):
        verify_enough_stock(make("A", 1, 3))
