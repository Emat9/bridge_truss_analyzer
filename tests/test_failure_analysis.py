"""Checks for the idealized member-failure model."""

import unittest

from bridge_truss.failure_analysis import CircularSection, analyze_default_failure


class FailureAnalysisTests(unittest.TestCase):
    def test_circular_section_properties_are_positive(self) -> None:
        section = CircularSection(area_m2=0.005)

        self.assertGreater(section.diameter_m, 0.0)
        self.assertGreater(section.second_moment_m4, 0.0)

    def test_default_center_load_first_fails_in_compression(self) -> None:
        result = analyze_default_failure()

        self.assertEqual(result.first_failure.member_name, "top_1")
        self.assertEqual(result.first_failure.state, "compression")
        self.assertEqual(result.first_failure.failure_mode, "Euler buckling")

    def test_first_failure_load_exceeds_the_starting_load(self) -> None:
        result = analyze_default_failure(load_n=100_000.0)

        self.assertGreater(result.predicted_failure_load_n, 100_000.0)
        self.assertLess(result.first_failure.utilization, 1.0)


if __name__ == "__main__":
    unittest.main()
