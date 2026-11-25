"""Checks for force-diagram display values."""

import unittest

from bridge_truss.force_visualization import build_force_display
from bridge_truss.truss_analysis import analyze_default_central_load
from bridge_truss.truss_geometry import build_warren_truss


class ForceVisualizationTests(unittest.TestCase):
    def test_each_member_has_display_data(self) -> None:
        _, members = build_warren_truss()
        displays = build_force_display(members, analyze_default_central_load())

        self.assertEqual(len(displays), len(members))
        self.assertTrue(all(display.line_width > 0 for display in displays))

    def test_known_members_have_expected_force_states(self) -> None:
        _, members = build_warren_truss()
        displays = {display.member_name: display for display in build_force_display(members, analyze_default_central_load())}

        self.assertEqual(displays["bottom_1"].state, "tension")
        self.assertEqual(displays["top_1"].state, "compression")
        self.assertEqual(displays["bottom_1"].color, "tab:blue")
        self.assertEqual(displays["top_1"].color, "tab:red")


if __name__ == "__main__":
    unittest.main()
