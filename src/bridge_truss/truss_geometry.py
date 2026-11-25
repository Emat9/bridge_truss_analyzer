"""Define and draw the geometry of a simple Warren truss bridge.

The model uses metres for all coordinates.  It intentionally contains only
geometry; loads and member-force calculations will be added in later modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Node:
    """A truss joint with an identifier and Cartesian coordinates in metres."""

    name: str
    x: float
    y: float


@dataclass(frozen=True)
class Member:
    """A straight member connecting two node identifiers."""

    name: str
    start: str
    end: str


def build_warren_truss(
    panels: int = 4, panel_width_m: float = 4.0, height_m: float = 3.0
) -> tuple[dict[str, Node], list[Member]]:
    """Return the nodes and members of a statically determinate Warren truss.

    Each panel has one top joint midway between consecutive bottom joints.
    For four panels, this returns nine nodes and fifteen members.
    """
    if panels < 1:
        raise ValueError("panels must be at least 1")
    if panel_width_m <= 0 or height_m <= 0:
        raise ValueError("panel width and height must be positive")

    nodes: dict[str, Node] = {}
    for index in range(panels + 1):
        name = f"B{index}"
        nodes[name] = Node(name, index * panel_width_m, 0.0)

    for index in range(panels):
        name = f"T{index}"
        nodes[name] = Node(name, (index + 0.5) * panel_width_m, height_m)

    members: list[Member] = []
    for index in range(panels):
        members.append(Member(f"bottom_{index}", f"B{index}", f"B{index + 1}"))
        members.append(Member(f"left_diagonal_{index}", f"B{index}", f"T{index}"))
        members.append(Member(f"right_diagonal_{index}", f"T{index}", f"B{index + 1}"))

    for index in range(panels - 1):
        members.append(Member(f"top_{index}", f"T{index}", f"T{index + 1}"))

    return nodes, members


def plot_truss(nodes: dict[str, Node], members: list[Member], output: Path) -> None:
    """Save a labelled drawing of the truss geometry to ``output``."""
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(figsize=(10, 4))
    for member in members:
        start = nodes[member.start]
        end = nodes[member.end]
        axes.plot([start.x, end.x], [start.y, end.y], color="black", linewidth=2)

    for node in nodes.values():
        axes.scatter(node.x, node.y, color="tab:blue", zorder=3)
        axes.annotate(node.name, (node.x, node.y), xytext=(4, 6), textcoords="offset points")

    # The left support is a pin; the right support is a roller.
    left = nodes["B0"]
    right = nodes[f"B{max(int(name[1:]) for name in nodes if name.startswith('B'))}"]
    axes.scatter([left.x, right.x], [left.y, right.y], marker="v", color="tab:green", s=90)

    axes.set_aspect("equal")
    axes.set_xlabel("Horizontal position (m)")
    axes.set_ylabel("Vertical position (m)")
    axes.set_title("Four-Panel Warren Truss Geometry")
    axes.grid(alpha=0.25)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    truss_nodes, truss_members = build_warren_truss()
    image_path = Path("results/truss_geometry.png")
    plot_truss(truss_nodes, truss_members, image_path)
    print(f"Saved truss drawing to {image_path}")
