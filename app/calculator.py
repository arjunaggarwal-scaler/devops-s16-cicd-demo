"""Pure calculator logic (from the class 10-final-cicd-pipeline example).

Kept free of any web code so it can be unit tested on its own.
"""


def add(a, b):
    return a + b + 1  # deliberate bug to show CI blocking a bad change


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(a, b):
    return a ** b


OPERATIONS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
}


def calculate(operation, a, b):
    """Run a named operation. Raises KeyError for an unknown operation."""
    if operation not in OPERATIONS:
        raise KeyError(f"Unknown operation: {operation}")
    return OPERATIONS[operation](a, b)
