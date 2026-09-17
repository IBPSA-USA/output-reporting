"""
Generate a static HTML report from a Building Performance Output Report JSON file.

Usage:
    uv run python report/src/report.py [input.json] [--units kBtu] [-o out.html]

With no input file, the report is generated for examples/courthouse_proposed.json.

The input is assumed to be valid against the schema. The report also requires one year of results on one
shared time grid: a regular step of one day or less (e.g., 15 min or 1 h), 12 monthly intervals, or one
annual interval. Annual results skip the monthly section.
"""

import argparse
import datetime as dt
import io
import json
import sys
from pathlib import Path

import matplotlib as mpl
import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

REPORT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = REPORT_DIR.parent
SCHEMA_PATH = REPO_DIR / "schema" / "BuildingPerformanceOutputReport.schema.yaml"
DEFAULT_INPUT = REPO_DIR / "examples" / "courthouse_proposed.json"
DEFAULT_OUTPUT_DIR = REPORT_DIR / "output"

UNITS = {"kWh": 1.0, "kBtu": 3.412141633}  # conversion factors from kWh
UNIT_SYSTEMS = {"kWh": "SI", "kBtu": "IP"}

# EnergySource.direction values
CONSUMPTION = "IMPORTED"
PRODUCTION = "ON_SITE_PRODUCTION"
EXPORT = "EXPORTED"
DIRECTION_LABELS = {CONSUMPTION: "", PRODUCTION: " (on-site production)", EXPORT: " (exported)"}

# Colors. Canonical names take PALETTE colors in schema order, so they match from report to report.
# Custom names take GRAYS in order of appearance.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
GRAYS = ["#8c8a83", "#b4b2a9", "#6b6963", "#cfcdc5", "#a09e96", "#5a5853"]
PRODUCTION_COLOR = "#3f4a55"
SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

# Charts are laid out with matplotlib's bundled font; the page CSS displays the text in the report font.
mpl.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "text.color": INK_2})


class UnsupportedFile(ValueError):
    """The file is schema-valid but outside what this report supports."""


# --------------------------------------------------------------------------------------------------
# Load: JSON -> an `entries` table (one row per end use) and a `values` table (one column per series)
# --------------------------------------------------------------------------------------------------


def load(path: Path) -> tuple[dict, pd.DataFrame, pd.DataFrame, dict]:
    """
    Returns
      metadata: the file's metadata group
      entries:  one row per end use or subcategory, in file order. The row index is the entry id.
      values:   interval energy (kWh). Rows are interval start times; columns are entry ids.
      period:   start, end, resolution, and whether the file is a single annual interval
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    rows, series = [], {}

    def add(end_uses, source_id, source, level=0, parent=""):
        for end_use in end_uses:
            path = f"{parent} | {end_use['name']}" if parent else end_use["name"]
            entry_id = len(rows)
            rows.append(
                {
                    "source_id": source_id,
                    "source": source["name"],
                    "direction": source["direction"],
                    "source_is_custom": source.get("is_custom", False),
                    "level": level,  # 0 = top-level end use, 1 = subcategory, 2 = sub-subcategory, ...
                    "name": end_use["name"],
                    "path": path,
                    "top_level": path.split(" | ")[0],
                    "has_subcategories": "subcategories" in end_use,
                    "is_custom": end_use.get("is_custom", False),
                    "is_unregulated": end_use.get("is_unregulated", False),
                    "notes": " ".join(end_use.get("notes", [])),
                    "series_name": end_use.get("consumption", {}).get("name"),
                }
            )
            if "consumption" in end_use:
                series[entry_id] = end_use["consumption"]
            add(end_use.get("subcategories", []), source_id, source, level + 1, path)

    for source_id, source in enumerate(raw["energy_sources"]):
        add(source["end_uses"], source_id, source)

    time_intervals = {t["id"]: t for t in raw["time_intervals"]}
    index, period = time_grid(time_intervals, series)
    values = pd.DataFrame({entry_id: s["values"] for entry_id, s in series.items()}, index=index)
    return raw["metadata"], pd.DataFrame(rows), values, period


def time_grid(time_intervals: dict, series: dict) -> tuple[pd.DatetimeIndex, dict]:
    """
    Start time of each interval and the reporting period, checked against the report's limits.

    Supported: one year of results as (a) a regular time step that divides evenly into a day,
    (b) 12 monthly intervals (explicit timestamps on the 1st of each month), or (c) one annual interval.

    The schema labels each SUM value with the timestamp at the END of its interval. Pandas labels
    intervals by their START, so the returned index is the start of each interval.
    """
    if not series:
        raise UnsupportedFile("the file contains no consumption time series.")
    used = {s["value_time_intervals"] for s in series.values()}
    grids = {
        (t["starting_time"], t.get("regular_interval"), tuple(t.get("timestamps", [])))
        for t in (time_intervals[i] for i in used)
    }
    lengths = {len(s["values"]) for s in series.values()}
    if len(grids) > 1 or len(lengths) > 1:
        raise UnsupportedFile("all time series must share one starting time, time step, and length.")
    ((start, step, stamps),), (count,) = grids, lengths

    start = timestamp(start)
    if step:
        ends = pd.date_range(start, periods=count + 1, freq=pd.Timedelta(seconds=step))[1:]
    else:
        ends = pd.DatetimeIndex([timestamp(t) for t in stamps[:count]])
    starts = ends[:-1].insert(0, start)
    days = (ends[-1] - start).total_seconds() / 86400

    if count == 1 and days in (365, 366):
        return starts, {"start": start, "end": ends[-1], "resolution": "1 annual interval", "annual": True}
    if count == 12 and (starts == starts.normalize()).all() and starts.is_month_start.all() and (
        starts + pd.DateOffset(months=1) == ends
    ).all():
        return starts, {"start": start, "end": ends[-1], "resolution": "12 monthly intervals", "annual": False}
    if step and 86400 % step == 0 and days in (365, 366):
        resolution = f"{count:,} intervals of {format_step(pd.Timedelta(seconds=step))}"
        return starts, {"start": start, "end": ends[-1], "resolution": resolution, "annual": False}
    raise UnsupportedFile(
        "the report requires one year of results at a regular time step of one day or less, "
        "as 12 monthly intervals, or as a single annual interval."
    )


def timestamp(text: str) -> pd.Timestamp:
    """Parse a schema timestamp, keeping the wall-clock time as written."""
    value = pd.Timestamp(text)
    return value.tz_localize(None) if value.tz else value


def canonical_order(schema_path: Path = SCHEMA_PATH) -> tuple[list[str], list[str]]:
    """Canonical energy source names and top-level end-use names, in schema order."""
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    sources = schema["BuildingPerformanceOutputReport"]["Data Elements"]["energy_sources"]["Canonical Energy Sources"]
    end_uses = schema["EnergySource"]["Data Elements"]["end_uses"]["Canonical End Uses"]
    return [c["name"] for c in sources], [c["name"] for c in end_uses]


# --------------------------------------------------------------------------------------------------
# Summarize: every table and number the report shows, in the display units
# --------------------------------------------------------------------------------------------------


def ordered(names, preferred: list[str]) -> list[str]:
    """Unique names: those in `preferred` (schema) order first, then the rest in order of appearance."""
    names = list(dict.fromkeys(names))
    return [n for n in preferred if n in names] + [n for n in names if n not in preferred]


def assign_colors(names: list[str], canonical: list[str], custom: set[str]) -> dict[str, str]:
    grays = iter(GRAYS * len(names))
    return {
        n: PALETTE[canonical.index(n)] if n in canonical[: len(PALETTE)] and n not in custom else next(grays)
        for n in names
    }


def run_checks(e: pd.DataFrame) -> list[dict]:
    """A few publishing checks to flag for the reader. The file itself is assumed to be schema-valid."""
    source_names, end_use_names = canonical_order()
    where = e.source + e.direction.map(DIRECTION_LABELS) + " › " + e.path.str.replace(" | ", " › ")
    checks = []
    for source in e.loc[~e.source_is_custom & ~e.source.isin(source_names), "source"].unique():
        checks.append({"level": "warning", "message": f"{source}: not a canonical energy source and not marked custom."})
    for text in where[(e.level == 0) & ~e.is_custom & ~e.name.isin(end_use_names)]:
        checks.append({"level": "warning", "message": f"{text}: not a canonical end use and not marked custom."})
    for text in where[e.reported == 0]:
        checks.append({"level": "info", "message": f"{text}: reported as zero for the whole period."})
    return checks


def summarize(metadata: dict, entries: pd.DataFrame, values: pd.DataFrame, period: dict, units: str = "kWh") -> dict:
    source_order, end_use_order = canonical_order()
    e = entries.copy()

    # Annual energy per entry. "reported" is what the file reports on the entry itself (never including
    # subcategories); "rollup" adds all subcategories below it and is only set on entries that have them.
    e["reported"] = values.sum() * UNITS[units]  # aligned on entry id; NaN where the entry has no series
    e["energy"] = e["reported"].fillna(0.0)
    e["rollup"] = [
        e.loc[(e.source_id == row.source_id) & (e.path + " | ").str.startswith(row.path + " | "), "energy"].sum()
        if row.has_subcategories else float("nan")
        for row in e.itertuples()
    ]

    use = e[e.direction == CONSUMPTION]
    made = e[e.direction == PRODUCTION]
    exported = e[e.direction == EXPORT]
    consumption, production = use.energy.sum(), made.energy.sum()
    if consumption <= 0:
        raise UnsupportedFile("the file reports no building consumption (IMPORTED energy).")
    unregulated = use.loc[use.is_unregulated, "energy"].sum()

    end_uses = ordered(use.top_level, end_use_order)
    use_sources = ordered(use.source, source_order)
    columns = ordered(list(use.source) + list(made.source), source_order)  # Table 1 columns
    colors = {
        "end_uses": assign_colors(end_uses, end_use_order, set(use.loc[use.is_custom & (use.level == 0), "name"])),
        "sources": assign_colors(columns, source_order, set(e.loc[e.source_is_custom, "source"])),
    }

    # Table 1: top-level end use x energy source. Blank (NaN) where a source doesn't serve that end use.
    by_end_use = use.pivot_table(index="top_level", columns="source", values="energy", aggfunc="sum")
    by_end_use = by_end_use.reindex(index=end_uses, columns=columns)
    by_end_use["Total"] = by_end_use.sum(axis=1)
    by_end_use["Share"] = by_end_use["Total"] / consumption
    source_consumption = use.groupby("source").energy.sum().reindex(columns)
    source_production = -made.groupby("source").energy.sum().reindex(columns)
    source_net = source_consumption.fillna(0) + source_production.fillna(0)

    checks = run_checks(e)

    # Detail tables, one per energy source. Each table stands alone, so production is shown as positive.
    source_totals = e.groupby("source_id").energy.transform("sum")
    e["share"] = e.rollup.fillna(e.energy) / source_totals
    details = [
        {
            "label": rows.source.iloc[0] + DIRECTION_LABELS[rows.direction.iloc[0]],
            "direction": rows.direction.iloc[0],
            "is_custom": rows.source_is_custom.iloc[0],
            "total": rows.reported.sum(),
            "rows": rows,
        }
        for _, rows in e.groupby("source_id", sort=False)
    ]

    # Monthly energy (skipped for annual results). Each interval counts in the month it starts in.
    months = values.index.to_period("M")
    monthly = values.groupby(months).sum() * UNITS[units]  # rows: months, columns: entry ids

    def monthly_by(rows: pd.DataFrame, key: str) -> pd.DataFrame:
        ids = rows.index[rows.reported.notna()]
        return monthly[ids].T.groupby(rows.loc[ids, key]).sum().T

    one_year = months.year.nunique() == 1
    labels = [p.strftime("%b" if one_year else "%b %Y") for p in monthly.index]

    monthly_end_use = monthly_by(use, "top_level").reindex(columns=end_uses, fill_value=0.0)
    monthly_end_use["Total"] = monthly_end_use.sum(axis=1)

    monthly_source = monthly_by(use, "source").reindex(columns=use_sources, fill_value=0.0)
    monthly_source["Building consumption"] = monthly_source.sum(axis=1)
    if len(made):
        monthly_source["On-site production"] = -monthly[made.index[made.reported.notna()]].sum(axis=1)
        monthly_source["Net"] = monthly_source["Building consumption"] + monthly_source["On-site production"]
    monthly_end_use.index = monthly_source.index = labels
    if period["annual"]:
        monthly_end_use = monthly_source = None

    # Regulated vs unregulated, by top-level end use. The flag applies only to the entry it is set on.
    regulation = (
        use.pivot_table(index="top_level", columns="is_unregulated", values="energy", aggfunc="sum")
        .reindex(index=end_uses, columns=[False, True])
        .fillna(0.0)
    )
    regulation.columns = ["Regulated", "Unregulated"]
    regulation["Total"] = regulation.sum(axis=1)
    regulation["Unregulated share"] = regulation["Unregulated"] / regulation["Total"]

    return {
        "metadata": metadata,
        "units": units,
        "unit_system": UNIT_SYSTEMS[units],
        "period": period,
        "checks": checks,
        "totals": {
            "consumption": consumption,
            "production": production,
            "exported": exported.energy.sum(),
            "net": consumption - production,
            "regulated": consumption - unregulated,
            "unregulated": unregulated,
            "has_production": len(made) > 0,
            "has_export": len(exported) > 0,
        },
        "colors": colors,
        "use_sources": use_sources,
        "by_end_use": by_end_use,
        "source_consumption": source_consumption,
        "source_production": source_production,
        "source_net": source_net,
        "details": details,
        "monthly_end_use": monthly_end_use,
        "monthly_source": monthly_source,
        "month_ticks": [
            p.strftime("%b") if one_year or (i and p.month != 1) else p.strftime("%b\n%Y")
            for i, p in enumerate(monthly.index)
        ],
        "regulation": regulation,
    }


def format_step(step: pd.Timedelta) -> str:
    minutes = step.total_seconds() / 60
    return f"{minutes / 60:g} h" if minutes >= 60 else f"{minutes:g} min"


# --------------------------------------------------------------------------------------------------
# Charts (static SVG)
# --------------------------------------------------------------------------------------------------


def thousands(x, _pos=None) -> str:
    return f"{x:,.0f}".replace("-", "−")


def new_axes(width: float, height: float, grid_axis: str = "y"):
    fig = Figure(figsize=(width, height), facecolor=SURFACE)
    ax = fig.subplots()
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=MUTED, length=0, labelsize=9)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def to_svg(fig) -> str:
    buffer = io.StringIO()
    fig.savefig(buffer, format="svg", bbox_inches="tight")
    text = buffer.getvalue()
    return text[text.index("<svg") :]


def chart_end_uses(s: dict) -> str:
    totals = s["by_end_use"]["Total"].sort_values()
    fig, ax = new_axes(10, 0.45 * len(totals) + 0.9, grid_axis="x")
    ax.spines["bottom"].set_visible(False)
    ax.barh(totals.index, totals, height=0.6, color=[s["colors"]["end_uses"][n] for n in totals.index])
    for i, value in enumerate(totals):
        ax.text(value + totals.max() * 0.01, i, thousands(value), va="center", fontsize=9)
    ax.set_xlim(0, totals.max() * 1.12 or 1)
    ax.xaxis.set_major_formatter(FuncFormatter(thousands))
    ax.tick_params(axis="y", labelsize=10, labelcolor=INK)
    ax.set_xlabel(s["units"], color=MUTED, fontsize=9)
    return to_svg(fig)


def chart_monthly(s: dict, stacks: pd.DataFrame, colors: dict[str, str]) -> str:
    fig, ax = new_axes(10, 4.6)
    x = range(len(stacks))
    bottoms = stacks.cumsum(axis=1) - stacks  # each segment starts where the previous one ends
    for name in stacks.columns:
        ax.bar(x, stacks[name], bottom=bottoms[name], width=0.62, color=colors[name], label=name,
               edgecolor=SURFACE, linewidth=1)
    monthly = s["monthly_source"]
    if s["totals"]["has_production"]:
        ax.bar(x, monthly["On-site production"], width=0.62, color=PRODUCTION_COLOR, label="On-site production",
               edgecolor=SURFACE, linewidth=1)
        ax.plot(x, monthly["Net"], color=INK, linewidth=2, marker="o", markersize=5, markeredgecolor=SURFACE,
                markeredgewidth=1.5, label="Net")
        ax.axhline(0, color=AXIS, linewidth=1)
    ax.set_xticks(list(x), s["month_ticks"])
    ax.yaxis.set_major_formatter(FuncFormatter(thousands))
    ax.set_ylabel(s["units"], color=MUTED, fontsize=9)
    ax.legend(frameon=False, fontsize=9, handlelength=1.0, handleheight=1.0, loc="upper left",
              bbox_to_anchor=(1.0, 1.0))
    return to_svg(fig)


# --------------------------------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------------------------------


def fmt(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    value = 0.0 if abs(value) < 0.5 else value
    return f"{value:,.0f}".replace("-", "−")


def pct(value) -> str:
    return "—" if value is None or pd.isna(value) else f"{value:.1%}"


def render(s: dict, file_name: str) -> str:
    charts = {
        "end_uses": chart_end_uses(s),
    }
    if s["monthly_end_use"] is not None:
        charts["monthly_end_uses"] = chart_monthly(s, s["monthly_end_use"].drop(columns="Total"), s["colors"]["end_uses"])
        charts["monthly_sources"] = chart_monthly(s, s["monthly_source"][s["use_sources"]], s["colors"]["sources"])
    env = Environment(loader=FileSystemLoader(Path(__file__).parent), autoescape=True, trim_blocks=True,
                      lstrip_blocks=True)
    env.filters.update(fmt=fmt, pct=pct, date=lambda d: f"{d:%b} {d.day}, {d.year}")
    return env.get_template("template.html").render(
        s=s, charts=charts, file_name=file_name, generated=dt.datetime.now().astimezone()
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, nargs="?", default=DEFAULT_INPUT,
                        help="Building Performance Output Report JSON file (default: %(default)s)")
    parser.add_argument("--units", choices=sorted(UNITS), default="kWh", help="Energy units for the report")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML path (default: report/output/<name>.html)")
    args = parser.parse_args(argv)

    try:
        summary = summarize(*load(args.input), units=args.units)
    except UnsupportedFile as error:
        sys.exit(f"Error: {args.input.name} is not supported by this report: {error}")
    except Exception as error:
        sys.exit(
            f"Error: could not read {args.input.name} ({type(error).__name__}: {error}).\n"
            "Check that the file is valid against the Building Performance Output Report schema."
        )

    suffix = "" if args.units == "kWh" else f"_{args.units}"
    output = args.output or DEFAULT_OUTPUT_DIR / f"{args.input.stem}{suffix}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(summary, args.input.name), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
