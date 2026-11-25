"""Numerical sanity checks for the truss force solver."""

import unittest

from bridge_truss.truss_analysis import analyze_default_central_load


class TrussAnalysisTests(unittest.TestCase):
    def test_symmetric_central_load_has_equal_vertical_reactions(self) -> None:
        result = analyze_default_central_load(load_n=100_000.0)

        self.assertAlmostEqual(result.reactions_n["B0"][1], 50_000.0, places=6)
        self.assertAlmostEqual(result.reactions_n["B4"][1], 50_000.0, places=6)
        self.assertAlmostEqual(result.reactions_n["B0"][0], 0.0, places=6)

    def test_reactions_balance_the_applied_load(self) -> None:
        result = analyze_default_central_load(load_n=100_000.0)

        total_vertical_force = -100_000.0 + sum(reaction[1] for reaction in result.reactions_n.values())
        self.assertAlmostEqual(total_vertical_force, 0.0, places=6)

    def test_center_joint_moves_downward_under_downward_load(self) -> None:
        result = analyze_default_central_load(load_n=100_000.0)

        self.assertLess(result.displacements_m["B2"][1], 0.0)


if __name__ == "__main__":
    unittest.main()
