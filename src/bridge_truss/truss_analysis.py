"""Solve axial forces in a two-dimensional pin-jointed truss.

The solver uses the direct stiffness method with small displacements and
linear-elastic members.  Positive member force means tension; negative member
force means compression.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bridge_truss.truss_geometry import Member, Node, build_warren_truss


@dataclass(frozen=True)
class AnalysisResult:
    """Numerical results for one load case."""

    displacements_m: dict[str, tuple[float, float]]
    reactions_n: dict[str, tuple[float, float]]
    member_forces_n: dict[str, float]


def _dof_indices(nodes: dict[str, Node]) -> dict[str, tuple[int, int]]:
    """Assign horizontal and vertical displacement indices to each joint."""
    return {name: (2 * index, 2 * index + 1) for index, name in enumerate(nodes)}


def solve_truss(
    nodes: dict[str, Node],
    members: list[Member],
    loads_n: dict[str, tuple[float, float]],
    constrained_dofs: dict[str, tuple[str, ...]],
    youngs_modulus_pa: float,
    area_m2: float,
) -> AnalysisResult:
    """Solve a planar truss for nodal loads, displacements, and member forces.

    Parameters use SI units: metres, newtons, pascals, and square metres.
    ``constrained_dofs`` uses ``"x"`` and ``"y"`` to mark fixed displacement
    directions. A pin support fixes both; a roller fixes only ``"y"``.
    """
    if youngs_modulus_pa <= 0 or area_m2 <= 0:
        raise ValueError("young's modulus and member area must be positive")

    dofs = _dof_indices(nodes)
    total_dofs = 2 * len(nodes)
    stiffness = np.zeros((total_dofs, total_dofs), dtype=float)
    external_loads = np.zeros(total_dofs, dtype=float)

    for node_name, (force_x, force_y) in loads_n.items():
        if node_name not in nodes:
            raise ValueError(f"load references unknown node {node_name!r}")
        x_dof, y_dof = dofs[node_name]
        external_loads[x_dof] += force_x
        external_loads[y_dof] += force_y

    for member in members:
        start = nodes[member.start]
        end = nodes[member.end]
        delta_x = end.x - start.x
        delta_y = end.y - start.y
        length_m = float(np.hypot(delta_x, delta_y))
        if length_m == 0:
            raise ValueError(f"member {member.name!r} has zero length")

        cosine = delta_x / length_m
        sine = delta_y / length_m
        member_stiffness = youngs_modulus_pa * area_m2 / length_m
        local_matrix = member_stiffness * np.array(
            [
                [cosine**2, cosine * sine, -cosine**2, -cosine * sine],
                [cosine * sine, sine**2, -cosine * sine, -sine**2],
                [-cosine**2, -cosine * sine, cosine**2, cosine * sine],
                [-cosine * sine, -sine**2, cosine * sine, sine**2],
            ]
        )
        member_dofs = (*dofs[member.start], *dofs[member.end])
        stiffness[np.ix_(member_dofs, member_dofs)] += local_matrix

    fixed_dofs: list[int] = []
    for node_name, directions in constrained_dofs.items():
        if node_name not in nodes:
            raise ValueError(f"support references unknown node {node_name!r}")
        for direction in directions:
            if direction == "x":
                fixed_dofs.append(dofs[node_name][0])
            elif direction == "y":
                fixed_dofs.append(dofs[node_name][1])
            else:
                raise ValueError("support directions must be 'x' or 'y'")

    fixed_dofs = sorted(set(fixed_dofs))
    free_dofs = [dof for dof in range(total_dofs) if dof not in fixed_dofs]
    displacements = np.zeros(total_dofs, dtype=float)
    stiffness_free = stiffness[np.ix_(free_dofs, free_dofs)]
    displacements[free_dofs] = np.linalg.solve(stiffness_free, external_loads[free_dofs])
    reactions = stiffness @ displacements - external_loads

    member_forces_n: dict[str, float] = {}
    for member in members:
        start = nodes[member.start]
        end = nodes[member.end]
        delta_x = end.x - start.x
        delta_y = end.y - start.y
        length_m = float(np.hypot(delta_x, delta_y))
        cosine = delta_x / length_m
        sine = delta_y / length_m
        extension_m = np.dot(
            [
                -cosine,
                -sine,
                cosine,
                sine,
            ],
            displacements[[*dofs[member.start], *dofs[member.end]]],
        )
        member_forces_n[member.name] = youngs_modulus_pa * area_m2 * extension_m / length_m

    displacement_by_node = {
        name: (float(displacements[x_dof]), float(displacements[y_dof]))
        for name, (x_dof, y_dof) in dofs.items()
    }
    reaction_by_node = {
        name: (float(reactions[x_dof]), float(reactions[y_dof]))
        for name, (x_dof, y_dof) in dofs.items()
        if name in constrained_dofs
    }
    return AnalysisResult(displacement_by_node, reaction_by_node, member_forces_n)


def analyze_single_deck_load(
    load_node: str, load_n: float = 100_000.0
) -> AnalysisResult:
    """Analyze the project truss under one downward load at a deck joint.

    The left support is a pin and the right support is a vertical roller.
    ``load_node`` must be one of the bottom-joint identifiers, such as ``B2``.
    """
    nodes, members = build_warren_truss()
    if load_node not in nodes or not load_node.startswith("B"):
        raise ValueError("load_node must name a bottom truss joint, such as 'B2'")
    return solve_truss(
        nodes=nodes,
        members=members,
        loads_n={load_node: (0.0, -load_n)},
        constrained_dofs={"B0": ("x", "y"), "B4": ("y",)},
        youngs_modulus_pa=200e9,
        area_m2=0.005,
    )


def analyze_default_central_load(load_n: float = 100_000.0) -> AnalysisResult:
    """Analyze the project truss under a downward central deck load at B2."""
    return analyze_single_deck_load(load_node="B2", load_n=load_n)


if __name__ == "__main__":
    result = analyze_default_central_load()
    print("Support reactions for a 100 kN central downward load:")
    for node_name, (reaction_x, reaction_y) in result.reactions_n.items():
        print(f"  {node_name}: Rx = {reaction_x / 1_000:.2f} kN, Ry = {reaction_y / 1_000:.2f} kN")

    print("\nMember axial forces (positive = tension):")
    for member_name, force_n in result.member_forces_n.items():
        state = "tension" if force_n >= 0 else "compression"
        print(f"  {member_name}: {abs(force_n) / 1_000:.2f} kN {state}")
