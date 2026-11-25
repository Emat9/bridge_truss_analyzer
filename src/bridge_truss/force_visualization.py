"""Create a color-coded axial-force diagram for the default bridge truss."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bridge_truss.truss_analysis import AnalysisResult, analyze_default_central_load
from bridge_truss.truss_geometry import Member, Node, build_warren_truss


@dataclass(frozen=True)
class ForceDisplay:
    """Plotting information for one member's axial force."""

    member_name: str
    force_n: float
    state: str
    color: str
    line_width: float


def build_force_display(
    members: list[Member], force_result: AnalysisResult
) -> list[ForceDisplay]:
    """Convert axial forces to tension/compression colors and line widths."""
    maximum_force_n = max(abs(force_result.member_forces_n[member.name]) for member in members)
    displays: list[ForceDisplay] = []
    for member in members:
        force_n = force_result.member_forces_n[member.name]
        state = "tension" if force_n >= 0 else "compression"
        color = "tab:blue" if state == "tension" else "tab:red"
        line_width = 1.5 + 5.0 * abs(force_n) / maximum_force_n
        displays.append(ForceDisplay(member.name, force_n, state, color, line_width))
    return displays


def plot_force_diagram(
    nodes: dict[str, Node],
    members: list[Member],
    force_result: AnalysisResult,
    output: Path,
    applied_load_n: float = 100_000.0,
) -> None:
    """Save a labelled force diagram for one centered downward point load."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    displays = {display.member_name: display for display in build_force_display(members, force_result)}
    figure, axes = plt.subplots(figsize=(11, 5))

    for member in members:
        start = nodes[member.start]
        end = nodes[member.end]
        display = displays[member.name]
        axes.plot(
            [start.x, end.x],
            [start.y, end.y],
            color=display.color,
            linewidth=display.line_width,
            solid_capstyle="round",
            zorder=2,
        )
        midpoint_x = (start.x + end.x) / 2
        midpoint_y = (start.y + end.y) / 2
        axes.annotate(
            f"{abs(display.force_n) / 1_000:.0f}",
            (midpoint_x, midpoint_y),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color=display.color,
            zorder=4,
        )

    for node in nodes.values():
        axes.scatter(node.x, node.y, color="black", s=24, zorder=3)
        axes.annotate(node.name, (node.x, node.y), xytext=(4, -16), textcoords="offset points", fontsize=8)

    # Green triangles mark the pin (left) and roller (right) supports.
    axes.scatter([nodes["B0"].x, nodes["B4"].x], [0, 0], marker="v", color="tab:green", s=85, zorder=3)

    # Draw the 100 kN applied point load at the middle deck joint.
    center_node = nodes["B2"]
    axes.annotate(
        "",
        xy=(center_node.x, center_node.y + 0.05),
        xytext=(center_node.x, center_node.y + 1.25),
        arrowprops={"arrowstyle": "->", "color": "black", "linewidth": 2},
    )
    axes.text(center_node.x + 0.15, 1.15, f"{applied_load_n / 1_000:.0f} kN", va="center")

    legend_handles = [
        Line2D([0], [0], color="tab:blue", linewidth=3, label="Tension"),
        Line2D([0], [0], color="tab:red", linewidth=3, label="Compression"),
        Line2D([0], [0], color="tab:green", marker="v", linestyle="", label="Support"),
    ]
    axes.legend(handles=legend_handles, loc="upper right")
    axes.text(0.01, 0.01, "Member labels: axial force magnitude (kN)", transform=axes.transAxes, fontsize=9)
    axes.set_aspect("equal")
    axes.set_xlabel("Horizontal position (m)")
    axes.set_ylabel("Vertical position (m)")
    axes.set_title("Member Forces: 100 kN Center Point Load")
    axes.grid(alpha=0.2)
    axes.margins(x=0.05, y=0.25)
    figure.subplots_adjust(left=0.10, right=0.985, top=0.88, bottom=0.16)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    truss_nodes, truss_members = build_warren_truss()
    central_load_result = analyze_default_central_load()
    output_path = Path("results/force_diagram.png")
    plot_force_diagram(truss_nodes, truss_members, central_load_result, output_path)
    print(f"Saved force diagram to {output_path}")
