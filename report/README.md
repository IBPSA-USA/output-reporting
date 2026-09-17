# Energy Performance Report (draft)

Generates a static HTML report from a single Building Performance Output Report JSON file: summary figures, energy by source and end use, end-use detail, monthly energy, regulated vs. unregulated energy, and a few data checks.

## Run

```console
uv sync
uv run python report/src/report.py examples/courthouse_proposed.json
uv run python report/src/report.py examples/courthouse_proposed.json --units kBtu
```

Reports are written to `report/output/`. Git ignores that folder except for the published example reports (listed in `.gitignore`). With no input file, the courthouse example is used.

## Supported input

- Any file that is valid against the schema, including custom energy sources, end uses, and on-site production.
- One year of results on one shared time grid: a regular time step of one day or less (e.g., 15 min or 1 h), 12 monthly intervals, or one annual interval. Annual results skip the monthly section.

Files outside these limits exit with an error message.

## Files

| Path | Contents |
| --- | --- |
| `src/report.py` | Loads the file into pandas tables, summarizes it, draws the charts, and renders the page |
| `src/template.html` | Jinja2 page template |
