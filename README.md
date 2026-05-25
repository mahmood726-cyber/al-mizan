# Al-Mizan

[![ci](https://github.com/mahmood726-cyber/al-mizan/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/mahmood726-cyber/al-mizan/actions/workflows/ci.yml) [![codeql](https://github.com/mahmood726-cyber/al-mizan/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/mahmood726-cyber/al-mizan/actions/workflows/codeql.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

An evidence equipoise monitor: detects when accumulating trial evidence has tipped a question, and estimates how many participants were subsequently enrolled after equipoise ended.

**Live dashboard:** <https://mahmood726-cyber.github.io/almizan/>

## What it does

- Cumulative meta-analysis at each chronological study entry.
- Trial Sequential Analysis (TSA) with O'Brien-Fleming alpha-spending boundaries on the cumulative Z-statistic.
- Classifies evidence state as **tipped**, **trending**, or **in equipoise**.
- Leave-one-out fragility checks for the tipping point.
- Post-tipping waste estimate (participants enrolled after the boundary was crossed).

## Run

Open `al-mizan.html` (or `index.html`) in any modern browser. No build step.

For local development:

```bash
python -m http.server 8000
# then open http://localhost:8000/
```

## Test

```bash
python -m pytest -q
```

The suite includes a Selenium-driven end-to-end test (`test_al_mizan.py`) plus unit tests (`tests/`).

## Repo layout

| Path | Purpose |
|---|---|
| `al-mizan.html` | the dashboard (main artifact) |
| `index.html` | landing page |
| `test_al_mizan.py`, `tests/` | pytest + Selenium tests |
| `pytest.ini` | test configuration (registers `tests/` as a package) |
| `manuscript_bmj_ebm.md` | BMJ EBM submission manuscript |
| `cover_letter_bmj_ebm.md` | submission cover letter |
| `e156-submission/` | E156 micro-paper bundle |
| `E156-PROTOCOL.md` | project metadata (E156 entry #6) |

## Statistical methods

The TSA boundary follows the formulation in Wetterslev et al. 2008 (`doi:10.1016/j.jclinepi.2007.03.013`) using `z_k = z_alpha / sqrt(t_k)` for O'Brien-Fleming spending. Three clinical exemplars ship with the tool: corticosteroids in TBI (CRASH 2004, `doi:10.1016/S0140-6736(04)17188-2`), tranexamic acid, and intensive glucose control (NICE-SUGAR).

## License

See `LICENSE` (MIT).
