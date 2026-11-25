# Bridge Truss Force Analyzer

A Python project that models a two-dimensional pin-jointed Warren truss bridge,
calculates its member forces under deck loads, and estimates which member reaches
its failure limit first.

> **Scope:** This is an educational, linear-elastic model. It is not suitable for
> real bridge design or safety decisions.

## Project question

How do load magnitude and load position affect the internal forces and predicted
first-failure member of a simple bridge truss?

## Planned features

- Define a 2D Warren truss with pin and roller supports.
- Calculate axial member forces with the direct stiffness method.
- Classify members as in tension or compression.
- Compare axial forces against tensile yield and Euler buckling capacities.
- Visualize force magnitude and tension/compression in a truss diagram.
- Sweep load location and magnitude to identify predicted failure patterns.

## Setup

This project will use Python 3.11+ and the packages listed in
`requirements.txt`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Repository layout

```text
src/bridge_truss/  # Model, analysis, and plotting code
tests/             # Automated checks and numerical sanity tests
data/              # Small input data files, if needed
results/           # Locally generated charts and tables (not committed)
```

## Status

The first milestone, truss geometry, is implemented. To generate its drawing:

```powershell
$env:PYTHONPATH = "src"
python src/bridge_truss/truss_geometry.py
```

The program saves `results/truss_geometry.png`. The next milestone is a solver
that calculates support reactions and axial member forces.

## Run the first force analysis

The default case applies a 100 kN downward load to the center deck joint (`B2`).
It uses a pin support at `B0` and a roller support at `B4`.

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m bridge_truss.truss_analysis
```

The program reports reactions and member axial forces in kilonewtons. Positive
force means tension; negative force means compression.

## Estimate first failure

The failure model assumes solid circular structural-steel members. Tension
members are compared with yielding; compression members are compared with Euler
buckling. This is an educational approximation, not a real bridge design.

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m bridge_truss.failure_analysis
```

For the default 100 kN centered load, the output reports the member with the
largest utilization and predicts the deck load at which that member would first
reach its modeled capacity.

## Analyze load position

The numerical sweep compares a point load at the three interior deck joints
(`B1`, `B2`, and `B3`). It saves a reusable CSV table and a graph in `results/`.

```powershell
.\.venv\Scripts\python.exe -m bridge_truss.load_position_sweep
```

The graph answers the project question: how does point-load position affect the
load at which the first truss member is predicted to fail?
