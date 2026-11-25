# Bridge Truss Force Analyzer

This Python project models a two-dimensional Warren truss bridge. It calculates
member forces, estimates the first member to fail, and studies how the location
of a point load changes the result.

> **Educational scope:** This is a linear-elastic, pin-jointed model for a
> computational physics and engineering course. It is not a real bridge-design
> or safety tool.

## Project question

How does the position of a downward point load affect the internal forces and
the predicted first-failure load of a Warren truss bridge?

## Model assumptions

- The bridge is a 16 m, four-panel Warren truss.
- Joints are ideal pins; members carry only axial tension or compression.
- The left support is a pin and the right support is a roller.
- Members are modeled as solid circular structural-steel bars.
- The model uses 250 MPa steel yield strength and a 0.005 m² member area.
- Tension members are checked for yielding; compression members are checked for
  Euler buckling.

## Main results

For a 100 kN downward load at the center joint (`B2`), the solver finds equal
50 kN upward reactions at the two supports. The middle top chord (`top_1`) has
the largest compression force and is predicted to buckle first.

| Point-load location | Predicted first-failure load | First-failure member | Mode |
|---|---:|---|---|
| B1 (4 m) | 245.44 kN | `top_0` | Euler buckling |
| B2 (8 m, center) | **184.08 kN** | `top_1` | Euler buckling |
| B3 (12 m) | 245.44 kN | `top_2` | Euler buckling |

The center load is most critical because it produces the largest compression in
the center top chord. The equal B1/B3 results are expected because the bridge
geometry is symmetric.

## Generated figures

- `results/truss_geometry.png`: bridge shape, joint labels, and supports.
- `results/force_diagram.png`: blue tension members, red compression members,
  and member-force magnitudes.
- `results/load_position_sweep.png`: first-failure load versus load location.
- `results/load_position_sweep.csv`: numerical data behind the sweep graph.

These files are generated locally and are intentionally not committed; rerun
the commands below to recreate them.

## Setup and run

Open a terminal in the repository folder and run the following once:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

Run an individual part of the project with one of these commands:

```powershell
.\.venv\Scripts\python.exe -m bridge_truss.truss_geometry
.\.venv\Scripts\python.exe -m bridge_truss.truss_analysis
.\.venv\Scripts\python.exe -m bridge_truss.failure_analysis
.\.venv\Scripts\python.exe -m bridge_truss.load_position_sweep
.\.venv\Scripts\python.exe -m bridge_truss.force_visualization
```

Run all automated checks:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Plain-language guide to the Python files

| File | What it does |
|---|---|
| `src/bridge_truss/__init__.py` | Marks `bridge_truss` as a Python package. |
| `src/bridge_truss/truss_geometry.py` | Creates the locations of the bridge joints and the list of members connecting them. It also draws the basic bridge shape. |
| `src/bridge_truss/truss_analysis.py` | Uses the direct stiffness method to calculate support reactions, joint movements, and axial force in every member. Positive force is tension; negative force is compression. |
| `src/bridge_truss/failure_analysis.py` | Compares member forces with yield and buckling capacities to estimate which member fails first. |
| `src/bridge_truss/load_position_sweep.py` | Repeats the analysis for loads at B1, B2, and B3, then saves the numerical table and graph. |
| `src/bridge_truss/force_visualization.py` | Turns the calculated forces into a presentation-ready diagram with color and line width. |
| `tests/test_truss_geometry.py` | Checks the number and layout of nodes and members. |
| `tests/test_truss_analysis.py` | Checks force equilibrium, equal reactions for a centered load, and downward deflection. |
| `tests/test_failure_analysis.py` | Checks the material/section calculations and first-failure prediction. |
| `tests/test_load_position_sweep.py` | Checks that the sweep includes all three load locations and preserves symmetry. |
| `tests/test_force_visualization.py` | Checks that known members receive the correct tension/compression display colors. |

## Repository layout

```text
src/bridge_truss/  Python model, calculations, and plotting code
tests/             Automated numerical checks
data/              Small input data files, if needed
results/           Locally generated figures and CSV tables
VIDEO_OUTLINE.md   Short presentation plan
```

See [VIDEO_OUTLINE.md](VIDEO_OUTLINE.md) for a concise script for the final
video.
