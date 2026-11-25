"""Analyze how point-load position changes the first predicted truss failure."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from bridge_truss.failure_analysis import CircularSection, SteelMaterial, assess_members
from bridge_truss.truss_analysis import analyze_single_deck_load
from bridge_truss.truss_geometry import build_warren_truss


@dataclass(frozen=True)
class LoadPositionResult:
    """The governing predicted failure for one point-load position."""

    load_node: str
    position_m: float
    first_failure_member: str
    failure_mode: str
    predicted_failure_load_n: float


def run_load_position_sweep(
    starting_load_n: float = 100_000.0,
    load_nodes: tuple[str, ...] = ("B1", "B2", "B3"),
) -> list[LoadPositionResult]:
    """Return first-failure predictions for several deck-joint load positions.

    The force analysis is linear, so the predicted first-failure load is found
    by scaling the initial load until the highest member utilization reaches 1.
    """
    if starting_load_n <= 0:
        raise ValueError("starting_load_n must be positive")

    nodes, members = build_warren_truss()
    results: list[LoadPositionResult] = []
    for load_node in load_nodes:
        force_result = analyze_single_deck_load(load_node, starting_load_n)
        assessments = assess_members(
            nodes=nodes,
            members=members,
            force_result=force_result,
            material=SteelMaterial(),
            section=CircularSection(),
        )
        first_failure = max(assessments, key=lambda assessment: assessment.utilization)
        results.append(
            LoadPositionResult(
                load_node=load_node,
                position_m=nodes[load_node].x,
                first_failure_member=first_failure.member_name,
                failure_mode=first_failure.failure_mode,
                predicted_failure_load_n=starting_load_n / first_failure.utilization,
            )
        )
    return results


def save_sweep_csv(results: list[LoadPositionResult], output: Path) -> None:
    """Save the sweep results as a CSV table for inspection or reuse."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=(
                "load_node",
                "position_m",
                "first_failure_member",
                "failure_mode",
                "predicted_failure_load_kN",
            ),
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "load_node": result.load_node,
                    "position_m": result.position_m,
                    "first_failure_member": result.first_failure_member,
                    "failure_mode": result.failure_mode,
                    "predicted_failure_load_kN": result.predicted_failure_load_n / 1_000,
                }
            )


def plot_sweep(results: list[LoadPositionResult], output: Path) -> None:
    """Save a graph of predicted first-failure load versus load position."""
    import matplotlib.pyplot as plt

    positions_m = [result.position_m for result in results]
    failure_loads_kn = [result.predicted_failure_load_n / 1_000 for result in results]

    figure, axes = plt.subplots(figsize=(8, 4.5))
    axes.plot(positions_m, failure_loads_kn, marker="o", linewidth=2, color="tab:purple")
    for result, load_kn in zip(results, failure_loads_kn):
        axes.annotate(
            f"{result.load_node}\n{result.first_failure_member}",
            (result.position_m, load_kn),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
        )

    axes.set_xticks(positions_m, [result.load_node for result in results])
    axes.set_xlabel("Point-load location (deck joint)")
    axes.set_ylabel("Predicted first-failure load (kN)")
    axes.set_title("Effect of Point-Load Position on Truss Failure Load")
    axes.margins(y=0.15)
    axes.grid(alpha=0.25)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    sweep_results = run_load_position_sweep()
    save_sweep_csv(sweep_results, Path("results/load_position_sweep.csv"))
    plot_sweep(sweep_results, Path("results/load_position_sweep.png"))

    print("Predicted first-failure load by point-load location:")
    for result in sweep_results:
        print(
            f"  {result.load_node} ({result.position_m:.1f} m): "
            f"{result.predicted_failure_load_n / 1_000:.2f} kN; "
            f"{result.first_failure_member}, {result.failure_mode}"
        )
