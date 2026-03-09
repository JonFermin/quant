Looking at the changes to `setup.ipynb`, I can see there's a discrepancy that needs fixing in the documentation.

The updated `setup.ipynb` clearly downloads and uses **US market data** (`us_data`, `--region us`), but the current CLAUDE.md documentation shows a **CN data example** in the Notebooks section.

This inconsistency could confuse users because:
1. The actual updated setup.ipynb uses US data
2. The CLAUDE.md Reminders section already states to "Prefer US market data (`REG_US`)"
3. The example in Notebooks contradicts both of these

This is a factual documentation error that needs correcting.

---

# CLAUDE.md — /quant

## Project Overview

This is a quantitative trading research repo. We write strategy code locally in Cursor, then run experiments in Google Colab using Microsoft QLib as our core library.

**QLib is a pip dependency, not source code in this repo.** We import it like any other Python library. We never clone or vendor the QLib repo itself.

## Architecture

```
/quant
├── CLAUDE.md
├── requirements.txt          # pinned deps: pyqlib, lightgbm, torch, etc.
├── setup.ipynb               # Colab setup notebook (install deps, download data, mount drive)
├── strategies/               # our strategy code — the actual work
│   ├── __init__.py
│   └── lgbm_alpha158.py      # LightGBM alpha strategy
├── notebooks/                # Colab experiment notebooks
│   └── 01_first_backtest.ipynb
├── configs/                  # QLib YAML workflow configs
│   └── lgbm_alpha158.yaml
├── data/                     # local data scratch (gitignored)
└── results/                  # backtest outputs, charts, logs (gitignored)
```

## Workflow

1. **Write strategy code locally** in `strategies/` and `configs/` using Cursor
2. **Push to GitHub**
3. **Open Google Colab**, clone the repo, `pip install -r requirements.txt`
4. **Run experiments** — backtest, evaluate, iterate
5. **Review results** in Colab, then come back to step 1

## Key Conventions

### Strategy Code
- All strategy logic lives in `strategies/`. One file per strategy idea.
- Strategies should be importable modules, not standalone scripts.
- Keep strategies pure Python — no Colab-specific code (no `!` commands, no `drive.mount`).
- Colab-specific setup lives ONLY in `setup.ipynb` and `notebooks/`.

### Notebooks
- `setup.ipynb` is the universal first-run notebook. It handles:
  - `!pip install -r requirements.txt`
  - Downloading QLib data (`!python -m qlib.run.get_data qlib_data --target_dir ~/.qlib/qlib_data/us_data --region us`)
  - Initializing QLib
- Experiment notebooks in `notebooks/` should start with `%run ../setup.ipynb` or a setup cell.
- Notebooks are for running experiments and viewing results, NOT for core strategy logic.

### Configs
- QLib YAML configs go in `configs/`.
- Use relative paths where possible.
- Document what each config does in a comment block at the top.

### Data
- Never commit data files. The `data/` and `results/` dirs are gitignored.
- QLib data lives at `~/.qlib/qlib_data/` (standard QLib convention).
- For US market data: `--region us`. For CN market: `--region cn`.

## QLib Quick Reference

```python
# Initialize
import qlib
from qlib.constant import REG_US
qlib.init(provider_uri="~/.qlib/qlib_data/us_data", region=REG_US)

# Get data
from qlib.data import D
instruments = D.instruments("sp500")
features = D.features(instruments, ["$close", "$volume", "Ref($close,5)"], start_time="2020-01-01")

# Run a full workflow from YAML
# !qrun configs/your_config.yaml

# Or programmatically
from qlib.workflow import R
from qlib.utils import init_instance_by_config
```

## Dependencies

Core: `pyqlib`, `lightgbm`, `numpy`, `pandas`
Optional: `torch` (for deep learning models), `matplotlib`, `jupyter`

Always pin versions in `requirements.txt`. QLib's Cython compilation can break across versions.

## Reminders

- **QLib does NOT execute live trades.** It's research and backtesting only. Live execution requires a separate tool (Alpaca, IBKR, QuantConnect, etc.).
- **Colab sessions are ephemeral.** Every restart means re-running setup. Design for this.
- **This repo is the strategy code and configs.** QLib is just a dependency.
- When creating new strategies, always include a backtest config so results are reproducible.
- Prefer US market data (`REG_US`) unless explicitly working with Chinese markets.
