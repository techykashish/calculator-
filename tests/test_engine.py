import math
import unittest

from calculator.engine import (
    CalculationError,
    evaluate_expression,
    format_result,
)


class EvaluateExpressionTests(unittest.TestCase):
    def test_operator_precedence_and_parentheses(self) -> None:
        self.assertEqual(evaluate_expression("2 + 3 * 4"), 14)
        self.assertEqual(evaluate_expression("(2 + 3) * 4"), 20)

    def test_scientific_functions_and_angle_modes(self) -> None:
        self.assertAlmostEqual(evaluate_expression("sin(30)", "DEG"), 0.5)
        self.assertAlmostEqual(evaluate_expression("sin(pi/2)", "RAD"), 1)
        self.assertAlmostEqual(evaluate_expression("sqrt(81) + log(100)"), 11)
        self.assertEqual(evaluate_expression("fact(5)"), 120)

    def test_constants_percent_and_display_symbols(self) -> None:
        self.assertAlmostEqual(evaluate_expression("π × 2"), math.pi * 2)
        self.assertEqual(evaluate_expression("25%"), 0.25)
        self.assertEqual(evaluate_expression("5 − 2"), 3)

    def test_division_by_zero_has_clear_error(self) -> None:
        with self.assertRaisesRegex(CalculationError, "divide by zero"):
            evaluate_expression("1 / 0")

    def test_rejects_code_execution_and_unknown_functions(self) -> None:
        for expression in ("__import__('os')", "2 ** 1001", "unknown(2)"):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    evaluate_expression(expression)

    def test_rejects_non_finite_results(self) -> None:
        with self.assertRaises(CalculationError):
            evaluate_expression("1e308 * 1e308")

    def test_rejects_expressions_over_the_input_limit(self) -> None:
        with self.assertRaisesRegex(CalculationError, "too long"):
            evaluate_expression("1" * 513)

    def test_formats_numbers_for_display(self) -> None:
        self.assertEqual(format_result(5.0), "5")
        self.assertEqual(format_result(0.125), "0.125")


if __name__ == "__main__":
    unittest.main()
