"""Fast source-level contract checks; run with python3 -m unittest -v."""

import unittest

from app import classify


class ClassifyTests(unittest.TestCase):
    def test_below_boundary(self):
        self.assertEqual(classify(0.2), "negative")

    def test_exact_boundary(self):
        self.assertEqual(classify(0.5), "positive")

    def test_above_boundary(self):
        self.assertEqual(classify(0.9), "positive")

    def test_endpoints(self):
        self.assertEqual(classify(0), "negative")
        self.assertEqual(classify(1), "positive")

    def test_invalid_values(self):
        for value in (-0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                classify(value)


if __name__ == "__main__":
    unittest.main()
