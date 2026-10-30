"""Safe expression parsing and evaluation for the calculator."""

from __future__ import annotations

import ast
import math
import operator
import re
from collections.abc import Callable


class CalculationError(ValueError):
    """Raised when an expression is invalid or cannot be calculated."""


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MAX_EXPRESSION_LENGTH = 512


def _functions(angle_mode: str) -> dict[str, Callable[[float], float]]:
    to_radians = math.radians if angle_mode == "DEG" else float
    from_radians = math.degrees if angle_mode == "DEG" else float
    return {
        "sin": lambda value: math.sin(to_radians(value)),
        "cos": lambda value: math.cos(to_radians(value)),
        "tan": lambda value: math.tan(to_radians(value)),
        "asin": lambda value: from_radians(math.asin(value)),
        "acos": lambda value: from_radians(math.acos(value)),
        "atan": lambda value: from_radians(math.atan(value)),
        "sqrt": math.sqrt,
        "ln": math.log,
        "log": math.log10,
        "abs": abs,
        "fact": _factorial,
    }


def _factorial(value: float) -> int:
    if value < 0 or not value.is_integer() or value > 170:
        raise CalculationError("Factorial requires a whole number from 0 to 170.")
    return math.factorial(int(value))


def _prepare_expression(expression: str) -> str:
    prepared = (
        expression.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("π", "pi")
        .replace("√", "sqrt")
    )
    return re.sub(r"(?<=[\d.)])\s*%", "/100", prepared)


def evaluate_expression(expression: str, angle_mode: str = "DEG") -> float:
    """Evaluate an arithmetic expression without executing arbitrary Python."""
    if angle_mode not in {"DEG", "RAD"}:
        raise CalculationError("Angle mode must be DEG or RAD.")
    if not expression.strip():
        raise CalculationError("Enter an expression first.")
    if len(expression) > _MAX_EXPRESSION_LENGTH:
        raise CalculationError("Expression is too long.")

    try:
        tree = ast.parse(_prepare_expression(expression), mode="eval")
        result = float(_evaluate_node(tree.body, _functions(angle_mode)))
    except CalculationError:
        raise
    except (
        SyntaxError,
        TypeError,
        ValueError,
        ZeroDivisionError,
        OverflowError,
        RecursionError,
    ) as error:
        raise CalculationError(_error_message(error)) from error

    if not math.isfinite(result):
        raise CalculationError("The result is outside the supported number range.")
    return result


def _evaluate_node(
    node: ast.expr, functions: dict[str, Callable[[float], float]]
) -> float:
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        return float(node.value)

    if isinstance(node, ast.Name):
        constants = {"pi": math.pi, "e": math.e}
        if node.id in constants:
            return constants[node.id]
        raise CalculationError(f"Unknown value: {node.id}")

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_node(node.left, functions)
        right = _evaluate_node(node.right, functions)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise CalculationError("Exponent is too large.")
        return _BINARY_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand, functions))

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function = functions.get(node.func.id)
        if function is None:
            raise CalculationError(f"Unknown function: {node.func.id}")
        if len(node.args) != 1 or node.keywords:
            raise CalculationError(f"{node.func.id} expects one argument.")
        return function(_evaluate_node(node.args[0], functions))

    raise CalculationError("That expression is not supported.")


def _error_message(error: Exception) -> str:
    if isinstance(error, ZeroDivisionError):
        return "Cannot divide by zero."
    if isinstance(error, OverflowError):
        return "The result is outside the supported number range."
    if isinstance(error, ValueError):
        return "Check the expression and function inputs."
    return "Check the expression and try again."


def format_result(value: float) -> str:
    """Format a result without unnecessary trailing zeroes."""
    if value == 0:
        return "0"
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.12g}"
