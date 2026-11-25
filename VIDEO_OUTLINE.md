# Bridge Truss Analyzer Video Outline

Aim for about three minutes. Screen-record the project folder, the two figures,
and optionally a short terminal run. Speak in your own words; this is a guide,
not a script you need to memorize exactly.

## 0:00–0:20 — Question and project

“My project analyzes a Warren truss bridge in Python. I wanted to find out how
the location of a downward point load changes the internal member forces and
which member is predicted to fail first.”

Show `README.md` and the basic truss-geometry figure.

## 0:20–0:50 — Model

“The model has four panels and a 16 m span. The left support is pinned and the
right support is a roller. I treat the joints as pins, so members carry axial
tension or compression. This is an educational linear-elastic model, not a
real bridge design.”

Show `truss_geometry.py` briefly, then point out the supports and joint labels
on the geometry figure.

## 0:50–1:30 — Calculations

“The code uses the direct stiffness method. It assembles the stiffness of each
member, applies the support conditions and a load, solves for joint movement,
and then calculates the axial force in every member.”

“For a 100 kN center load, each support carries 50 kN upward. This is a useful
sanity check because the model and loading are symmetric.”

Show `truss_analysis.py` and the terminal output or force diagram.

## 1:30–2:10 — Force and failure results

“In the force diagram, blue members are in tension and red members are in
compression. Thicker members carry more force. The center top chord has the
largest compressive force: about 133 kN.”

“I compare tension with steel yielding and compression with Euler buckling. The
center top chord is predicted to buckle first.”

Show `force_diagram.png` and then `failure_analysis.py` or its terminal output.

## 2:10–2:40 — Numerical sweep and conclusion

“I repeated the analysis with the point load at B1, B2, and B3. A center load
is the most critical: it is predicted to cause first failure at about 184 kN.
Loads at B1 and B3 each give about 245 kN because the bridge is symmetric.”

Show `load_position_sweep.png` and point to the low middle point.

## 2:40–3:00 — Limitations and takeaway

“The main takeaway is that a centered point load produces the largest
compression in the center top chord, making buckling the controlling failure
mode in this model. A real bridge analysis would need more details, including
connection behavior, distributed and dynamic loads, member imperfections, and
code-based safety factors.”

End by showing the GitHub repository and the test files, if you want to
emphasize reproducibility.
