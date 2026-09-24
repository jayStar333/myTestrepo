# WCICLT Collection & Report utility

Local Python app for Winners Chapel International, Charlotte. It creates the next **Collection Analysis** tabs and a weekly **Collection Report** that is ready to attach to email.

Layouts follow the 2026 analysis workbook and the September 2026 weekly reports. Categories stay in one shared list.

## Install

```bash
cd wciclt-collection
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## GUI

```bash
python -m wciclt gui
```

Pick the week-ending date, add or remove services from the dropdown, edit categories, then **Generate week**.

## CLI

```bash
# Dropdown codes
python -m wciclt service-types

# Typical midweek + Sunday
python -m wciclt generate \
  --week-end 2026-09-27 \
  --service 2026-09-23:midweek \
  --service 2026-09-27:sunday \
  --analysis "./output/2026-Collection Analysis.xlsx" \
  --output-dir ./output \
  --recorded-by "Bro Ernest, Sis Sandra"

# WOSE / Other
python -m wciclt generate \
  --week-end 2026-09-06 \
  --service 2026-09-02:wose_day_1 \
  --service 2026-09-03:wose_day_2 \
  --service 2026-09-04:wose_day_3 \
  --service 2026-09-06:sunday \
  --service 2026-09-05:other:"Youth Night"

# Add or remove a category in both workbooks
python -m wciclt sync-categories \
  --analysis "./output/2026-Collection Analysis.xlsx" \
  --add "Mission Seed" \
  --remove "Chairs"
```

Point `--analysis` at your live `2026-Collection Analysis.xlsx` to append tabs. New files are created from `templates/analysis_tab_template.xlsx` (blanked copy of `Sun-09.20.2026`).

## Tests

```bash
pip install pytest
python -m pytest tests -q
```

## Sample output

`samples/` has workbooks produced by the generator (not hand-edited):

- `2026-Collection Analysis.sample.xlsx` — template plus midweek and Sunday tabs for 09/23 and 09/27/2026
- `Collection Report 09.27.2026.xlsx` — two service blocks
- `Collection Report 09.06.2026.xlsx` — WOSE Days 1–3 plus Sunday

## What gets created

- Analysis tab name: `Wed-09.23.2026`, subtitle `09/23/2026 - Midweek Service`.
- Weekly file: `Collection Report 09.27.2026.xlsx`, sheet `09.27.26`, one 3-column block per service.
- Hidden `_Categories` sheet plus `data/categories.json`.
