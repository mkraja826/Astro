"""Boundary tests for independent feasibility-only Jyotisha classifications."""

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classifications import (  # noqa: E402
    d1_sign_index,
    d9_sign_index,
    nakshatra_index,
    pada,
)

EPSILON = Decimal("0.000000001")
NAVAMSA = Decimal(10) / Decimal(3)
NAKSHATRA = Decimal(40) / Decimal(3)


class ClassificationBoundaryTests(unittest.TestCase):
    """Verify half-open intervals and 360-degree wrapping."""

    def test_zero_and_360_wrap(self) -> None:
        self.assertEqual(d1_sign_index(0), 0)
        self.assertEqual(d1_sign_index(360), 0)
        self.assertEqual(d9_sign_index(360), 0)
        self.assertEqual(nakshatra_index(360), 0)
        self.assertEqual(pada(360), 1)
        self.assertEqual(d1_sign_index(-EPSILON), 11)

    def test_thirty_degree_sign_boundary(self) -> None:
        self.assertEqual(d1_sign_index(Decimal(30) - EPSILON), 0)
        self.assertEqual(d1_sign_index(Decimal(30)), 1)
        self.assertEqual(d1_sign_index(Decimal(30) + EPSILON), 1)

    def test_navamsa_boundary(self) -> None:
        self.assertEqual(d9_sign_index(NAVAMSA - EPSILON), 0)
        self.assertEqual(d9_sign_index(NAVAMSA), 1)
        self.assertEqual(d9_sign_index(NAVAMSA + EPSILON), 1)

    def test_nakshatra_boundary(self) -> None:
        self.assertEqual(nakshatra_index(NAKSHATRA - EPSILON), 0)
        self.assertEqual(nakshatra_index(NAKSHATRA), 1)
        self.assertEqual(nakshatra_index(NAKSHATRA + EPSILON), 1)

    def test_pada_boundary(self) -> None:
        self.assertEqual(pada(NAVAMSA - EPSILON), 1)
        self.assertEqual(pada(NAVAMSA), 2)
        self.assertEqual(pada(NAVAMSA + EPSILON), 2)
        self.assertEqual(pada(NAKSHATRA - EPSILON), 4)
        self.assertEqual(pada(NAKSHATRA), 1)


if __name__ == "__main__":
    unittest.main()
