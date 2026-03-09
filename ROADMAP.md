# ROADMAP

Legend: Priority **P0–P3** (P0 highest), Complexity **S/M/L/XL**

Last discovery refresh: **2026-03-09 (cron `quant-discovery-2h`, 18:04 UTC)**

## Recommended Focus (next 48 hours)

**Theme:** Make runs fail early, degrade gracefully, and emit decision-ready outputs.

1. **Preflight + timeline guardrail**: semantic date checks and `--dry-run` env probe before expensive work.
2. **Resilience path**: typed errors + partial artifact export when recorder objects are missing.
3. **Decision pack + comparability**: one report, one run index, one naming scheme for clean run-to-run comparisons.

Success condition: a first-time operator can run preflight + one backtest and receive a clear pass/fail verdict, reproducibility metadata, and baseline-comparable metrics without reading strategy source.

## Discovery Backlog (reprioritized)

### P0 — UX Gaps + Reliability Risks

- [ ] **P0 · M** Add semantic date-window validation (ISO parse, start<=end, train/valid/test ordering + non-overlap, backtest fully inside test segment, handler range coverage).
- [ ] **P0 · M** Add `--dry-run` mode to validate imports/deps, provider path existence, output-dir writability, config shape, and optional qlib init probe without fitting.
- [ ] **P0 · S** Add typed error taxonomy + exit codes (`ConfigError`, `EnvError`, `DataError`, `RuntimeError`) with concise remediation hints.
- [ ] **P0 · S** Harden recorder/artifact path (`sig_analysis`, `portfolio_analysis`) to export partial results + explicit warnings instead of traceback-only failure.
- [ ] **P0 · S** Fix metric safety edge cases: ICIR divide-by-zero guard and explicit `NaN/inf` handling in console + artifacts.
- [ ] **P0 · S** Remove in-place mutation in `_apply_overrides` (copy config before applying overrides) to prevent hidden state coupling in tests and repeated runs.

### P1 — Missing Features for Decision Quality

- [ ] **P1 · M** Produce consolidated run report (`results/report.md` + `report.csv`) with IC/ICIR, annual return, Sharpe, max drawdown, turnover, benchmark delta, and fee assumptions used.
- [ ] **P1 · M** Add transaction-cost sensitivity presets (`low/base/high`) and output side-by-side delta table.
- [ ] **P1 · S** Add run manifest/index (`results/index.csv`) containing run id, run label, config hash, git SHA, python/package versions, date windows, and headline metrics.
- [ ] **P1 · S** Parameterize experiment/run naming (remove hardcoded `lgbm_alpha158`) and include run labels in artifact paths.
- [ ] **P1 · S** Add benchmark block (SPY buy/hold + equal-weight baseline) in same report path for immediate relative judgment.

### P2 — Tech Debt + Maintainability

- [ ] **P2 · L** Split `strategies/lgbm_alpha158.py` into focused modules (`validation.py`, `runner.py`, `artifacts.py`, `cli.py`) to reduce monolith coupling.
- [ ] **P2 · M** Expand tests for semantic date validation, dry-run behavior, override non-mutation, recorder fallback, and metric edge paths (`std=0`, missing columns).
- [ ] **P2 · M** Pin/lock full dependency set (not only `pyqlib`) and document reproducible env setup for local + notebook workflows.
- [ ] **P2 · M** Add CI quality gates (`ruff`, `black`, unit tests, smoke CLI run) with fail-fast checks on PRs.
- [ ] **P2 · S** Add runtime portability guardrails (`num_threads` sanity vs host CPU; warn/auto-cap when oversized).

### P3 — Growth Ideas

- [ ] **P3 · M** Add experiment template notebook with hypothesis/result/decision sections and artifact export hook.
- [ ] **P3 · L** Add lightweight performance-drift notebook using run index history.
- [ ] **P3 · L** Add multi-strategy scaffold/interface so additional models reuse the same evaluation/reporting pipeline.
- [ ] **P3 · M** Add one-command tear-sheet export for review sharing.

## Discovery Notes (2026-03-09, 18:04 UTC)

- Core validation is still structural; semantic timeline bugs remain the highest-cost failure mode.
- Runner still assumes recorder artifacts exist; this is the biggest source of brittle operator experience.
- `ICIR = mean/std` is currently unguarded and can emit inf/NaN or fail presentation quality.
- `_apply_overrides` mutates input config in place; this is subtle tech debt that can leak state across flows/tests.
- Comparability has improved via artifact export, but run-to-run decision velocity is still blocked by missing consolidated report + run index + baseline block.
- `num_threads: 20` in config remains a portability rough edge on smaller hosts and notebooks.
