"""Basic numerical checks for the Warren truss geometry."""

import unittest

from bridge_truss.truss_geometry import build_warren_truss


class WarrenTrussGeometryTests(unittest.TestCase):
    def test_default_truss_has_expected_node_and_member_counts(self) -> None:
        nodes, members = build_warren_truss()

        self.assertEqual(len(nodes), 9)
        self.assertEqual(len(members), 15)

    def test_every_member_references_existing_nodes(self) -> None:
        nodes, members = build_warren_truss()

        for member in members:
            self.assertIn(member.start, nodes)
            self.assertIn(member.end, nodes)

    def test_default_span_and_height_are_in_metres(self) -> None:
        nodes, _ = build_warren_truss()

        self.assertEqual(nodes["B4"].x, 16.0)
        self.assertEqual(nodes["T0"].y, 3.0)


if __name__ == "__main__":
    unittest.main()
