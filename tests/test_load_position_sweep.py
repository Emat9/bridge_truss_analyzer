"""Checks for the point-load position sweep."""

import unittest

from bridge_truss.load_position_sweep import run_load_position_sweep


class LoadPositionSweepTests(unittest.TestCase):
    def test_default_sweep_covers_three_interior_deck_joints(self) -> None:
        results = run_load_position_sweep()

        self.assertEqual([result.load_node for result in results], ["B1", "B2", "B3"])

    def test_symmetric_load_positions_have_equal_failure_loads(self) -> None:
        left, _, right = run_load_position_sweep()

        self.assertAlmostEqual(
            left.predicted_failure_load_n,
            right.predicted_failure_load_n,
            places=6,
        )

    def test_each_load_position_has_a_positive_failure_load(self) -> None:
        results = run_load_position_sweep()

        for result in results:
            self.assertGreater(result.predicted_failure_load_n, 0.0)


if __name__ == "__main__":
    unittest.main()
