# Project guidance

## Goal

Build a clear, reproducible computational physics or engineering project that
generates numerical results, analyzes them, and can be explained in a short
video.

## Working style

- Prefer Python and small, readable modules unless the project specifically
  benefits from a web interface.
- Make the smallest useful change; do not add packages or features without a
  clear project need.
- Explain unfamiliar commands briefly before asking the user to run them.
- Keep generated plots, videos, large data files, virtual environments, and
  secret configuration out of Git.
- Never commit passwords, API keys, access tokens, or private class material.

## Reproducibility

- Keep dependencies in `requirements.txt` once external packages are used.
- Use a fixed random seed for any stochastic simulation.
- Label plots with units, include legends where needed, and save the code that
  generates every reported numerical result.
- Update `README.md` with setup, run, and interpretation instructions.

## Git workflow

- Check `git status` before and after meaningful work.
- Make small commits with imperative messages after a focused change is tested.
- Push the current branch after each meaningful milestone once GitHub is
  connected.
- Do not rewrite published history or use destructive Git commands unless the
  user explicitly asks.

## Verification

- Run the relevant script or tests after code changes.
- For numerical work, include a simple sanity check against an analytical,
  limiting, or hand-calculated result when possible.
