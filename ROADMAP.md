# ROADMAP

Legend: Priority **P0–P3** (P0 highest), Complexity **S/M/L/XL**

## Backlog

- [x] **P0 · M** Add reproducible runner CLI (`python -m strategies.lgbm_alpha158` + args for config path, date overrides, output dir).
  - Goal: one-command local/Colab execution with explicit artifacts.

- [x] **P0 · M** Add validation + smoke tests for config/strategy wiring.
  - Include checks for required config keys, date ranges, and provider URI sanity.

- [ ] **P1 · M** Add evaluation report export (IC stats, Sharpe, max drawdown, turnover) to Markdown/CSV in `results/`.

- [ ] **P1 · M** Add notebook template for experiment tracking (`notebooks/02_experiment_template.ipynb`) with standardized sections.

- [x] **P1 · S** Fix documentation drift in `CLAUDE.md` architecture tree (`example_lgbm.py` -> `lgbm_alpha158.py`).

- [ ] **P1 · M** Add strategy hyperparameter surface notes + safe defaults in config comments.

- [ ] **P2 · M** Add optional walk-forward split presets (short/medium/long horizon) via config variants.

- [ ] **P2 · L** Add baseline strategy comparison (buy-and-hold SPY, equal-weight factor-neutral subset).

- [ ] **P2 · M** Add lint/format tooling (`ruff` + `black`) and CI workflow for checks.

- [ ] **P3 · L** Add lightweight dashboard notebook for run history and metric drift.

## Discovery Notes

- Gaps: no tests/validation, no reproducible artifact output contract.
- Polish: docs mention old filename; limited onboarding guardrails.
- Depth: no baseline comparisons/walk-forward presets.
- Delight: no experiment template/report snapshots.
- Infra: no CI/linting.
- Growth: sharable dashboard/report exports missing.
