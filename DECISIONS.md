# DECISIONS

## Open Questions / Needs Owner Input

- **Data posture:** Keep default universe as S&P 500 only, or expand to broader US equities after reliability gate?
  - Recommendation: **Keep S&P 500 for now** until baseline/cost-sensitivity are in place.
- **Primary optimization target for next 4 weeks:** prioritize IC/RankIC quality or portfolio-level Sharpe after costs?
  - Recommendation: **Sharpe after costs** as primary, IC as diagnostic.
- **Execution realism floor:** what default fee/slippage assumptions should define the “base” preset?
  - Recommendation: decide and lock `low/base/high` assumptions this week.
- **Minimum acceptance bar to promote a strategy iteration:** define go/no-go thresholds (e.g., min Sharpe, max drawdown, turnover cap).
  - Recommendation: set explicit thresholds before adding new model families.

## Decision Log

- 2026-03-09: Start autonomous build loop with roadmap-first workflow and cron-driven discovery/recap cadence.
- 2026-03-09: Keep US-market (`REG_US`) as default posture unless explicitly changed.
- 2026-03-09 (weekly strategy review): Reprioritized roadmap around reliability and decision-grade evaluation before feature expansion.
- 2026-03-09 (weekly strategy review): Adopted strategic pivots:
  1) trustworthiness before breadth,
  2) comparability before novelty,
  3) operator UX before architecture refactor.
