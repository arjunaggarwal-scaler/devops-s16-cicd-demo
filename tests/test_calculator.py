import pytest

from app.calculator import add, calculate, divide, multiply, power, subtract


def test_add():
    assert add(10, 5) == 15


def test_subtract():
    assert subtract(10, 5) == 5


def test_multiply():
    assert multiply(10, 5) == 50


def test_divide():
    assert divide(10, 5) == 2


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)


def test_power():
    assert power(2, 10) == 1024


@pytest.mark.parametrize(
    "operation, a, b, expected",
    [("add", 1, 2, 3), ("subtract", 1, 2, -1), ("multiply", 3, 4, 12),
     ("divide", 9, 3, 3), ("power", 3, 2, 9)],
)
def test_calculate_dispatch(operation, a, b, expected):
    assert calculate(operation, a, b) == expected


def test_calculate_unknown_operation():
    with pytest.raises(KeyError):
        calculate("modulo", 1, 2)
