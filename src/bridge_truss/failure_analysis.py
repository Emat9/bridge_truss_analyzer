"""Estimate which truss member reaches an idealized failure limit first.

This educational model compares tensile force with material yielding and
compressive force with Euler buckling. It assumes pin-connected, straight,
solid circular steel members and does not replace real bridge design checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

from bridge_truss.truss_analysis import AnalysisResult, analyze_default_central_load
from bridge_truss.truss_geometry import Member, Node, build_warren_truss


@dataclass(frozen=True)
class SteelMaterial:
    """Linear-elastic steel properties in SI units."""

    youngs_modulus_pa: float = 200e9
    yield_strength_pa: float = 250e6


@dataclass(frozen=True)
class CircularSection:
    """A solid circular member cross-section specified by its area."""

    area_m2: float = 0.005

    @property
    def diameter_m(self) -> float:
        """Diameter of an equivalent solid circular cross-section."""
        return sqrt(4.0 * self.area_m2 / pi)

    @property
    def second_moment_m4(self) -> float:
        """Second moment of area about either centroidal bending axis."""
        return pi * self.diameter_m**4 / 64.0


@dataclass(frozen=True)
class MemberAssessment:
    """Force, governing capacity, and failure margin for one member."""

    member_name: str
    force_n: float
    state: str
    capacity_n: float
    failure_mode: str
    utilization: float
    safety_factor: float


@dataclass(frozen=True)
class FailureAnalysisResult:
    """Member assessments and the first predicted failure for a load case."""

    assessments: list[MemberAssessment]
    first_failure: MemberAssessment
    predicted_failure_load_n: float


def _member_length_m(member: Member, nodes: dict[str, Node]) -> float:
    """Return the straight-line length of a member."""
    start = nodes[member.start]
    end = nodes[member.end]
    return ((end.x - start.x) ** 2 + (end.y - start.y) ** 2) ** 0.5


def assess_members(
    nodes: dict[str, Node],
    members: list[Member],
    force_result: AnalysisResult,
    material: SteelMaterial,
    section: CircularSection,
    effective_length_factor: float = 1.0,
) -> list[MemberAssessment]:
    """Compare member forces to tensile-yield or Euler-buckling capacity.

    ``effective_length_factor`` is 1.0 for the ideal pin-connected members
    modeled here. A higher value would reduce the predicted buckling capacity.
    """
    if material.youngs_modulus_pa <= 0 or material.yield_strength_pa <= 0:
        raise ValueError("material properties must be positive")
    if section.area_m2 <= 0 or effective_length_factor <= 0:
        raise ValueError("section area and effective length factor must be positive")

    tensile_yield_capacity_n = material.yield_strength_pa * section.area_m2
    assessments: list[MemberAssessment] = []
    for member in members:
        force_n = force_result.member_forces_n[member.name]
        if force_n >= 0:
            capacity_n = tensile_yield_capacity_n
            state = "tension"
            failure_mode = "tensile yielding"
        else:
            length_m = _member_length_m(member, nodes)
            euler_capacity_n = (
                pi**2
                * material.youngs_modulus_pa
                * section.second_moment_m4
                / (effective_length_factor * length_m) ** 2
            )
            capacity_n = min(tensile_yield_capacity_n, euler_capacity_n)
            state = "compression"
            failure_mode = "Euler buckling" if euler_capacity_n < tensile_yield_capacity_n else "compressive yielding"

        utilization = abs(force_n) / capacity_n
        safety_factor = float("inf") if force_n == 0 else capacity_n / abs(force_n)
        assessments.append(
            MemberAssessment(
                member_name=member.name,
                force_n=force_n,
                state=state,
                capacity_n=capacity_n,
                failure_mode=failure_mode,
                utilization=utilization,
                safety_factor=safety_factor,
            )
        )
    return assessments


def analyze_default_failure(load_n: float = 100_000.0) -> FailureAnalysisResult:
    """Estimate the first failure for the default centered-load configuration."""
    nodes, members = build_warren_truss()
    force_result = analyze_default_central_load(load_n=load_n)
    assessments = assess_members(
        nodes=nodes,
        members=members,
        force_result=force_result,
        material=SteelMaterial(),
        section=CircularSection(),
    )
    first_failure = max(assessments, key=lambda assessment: assessment.utilization)

    # With this linear model, every force scales proportionally with load.
    predicted_failure_load_n = load_n / first_failure.utilization
    return FailureAnalysisResult(assessments, first_failure, predicted_failure_load_n)


if __name__ == "__main__":
    result = analyze_default_failure()
    first = result.first_failure
    print("Default material: structural steel, 250 MPa yield strength")
    print("Default section: solid circular members, area = 0.005 m^2")
    print(f"Predicted first failure: {first.member_name}")
    print(f"  State: {first.state}; governing mode: {first.failure_mode}")
    print(f"  Force: {abs(first.force_n) / 1_000:.2f} kN")
    print(f"  Capacity: {first.capacity_n / 1_000:.2f} kN")
    print(f"  Utilization at 100 kN deck load: {first.utilization:.3f}")
    print(f"  Predicted deck load at first failure: {result.predicted_failure_load_n / 1_000:.2f} kN")
