"""
Build an example report for each example file, plus an index page, into one folder.

Used by the `publish_example_reports` doit task to add the reports to the generated web
documentation, so they can be read in a browser on the published site:

    uv run python report/src/publish.py .lattice/docs/web/public/reports

Example files the report does not support (see report.py) are skipped with a note.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import report  # noqa: E402

EXAMPLES = report.REPO_DIR / "examples"

INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Example Energy Performance Reports</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{ color-scheme: light; --page: #f4f3ef; --paper: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e;
           --muted: #898781; --rule: #e1e0d9; --accent: #184f95; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--page); color: var(--ink);
          font: 15px/1.55 Inter, system-ui, sans-serif; }}
  main {{ max-width: 820px; margin: 32px auto; padding: 48px 56px 56px; background: var(--paper);
          border: 1px solid var(--rule); border-radius: 6px; }}
  h1 {{ font-size: 30px; font-weight: 700; letter-spacing: -.02em; margin: 0 0 8px; color: var(--accent); }}
  p.lede {{ color: var(--ink-2); margin: 0 0 32px; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li {{ padding: 16px 0; border-top: 1px solid var(--rule); }}
  a {{ color: var(--accent); font-weight: 600; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .file {{ font-family: ui-monospace, monospace; font-size: 13px; color: var(--muted); }}
  .note {{ color: var(--ink-2); font-size: 13.5px; margin: 6px 0 0; }}
  footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--rule);
            font-size: 12px; color: var(--muted); }}
  @media (max-width: 760px) {{ main {{ margin: 0; padding: 24px 16px; border: 0; border-radius: 0; }} }}
</style>
</head>
<body>
<main>
  <h1>Example Energy Performance Reports</h1>
  <p class="lede">Reports generated from the example files in this repository, to show what a
  Building Performance Output Report file can be turned into. Each page is a static HTML report.</p>
  <ul>
{items}  </ul>
  <footer>Building Performance Output Report · Example Report v{version} · generated from the
  <a href="https://github.com/IBPSA-USA/output-reporting">repository</a>'s example files</footer>
</main>
</body>
</html>
"""

ITEM = """    <li>
      <a href="{name}.html">{title}</a> <span class="file">{name}.json</span>
      <p class="note">{description}</p>
    </li>
"""


def build(out_dir: Path, units: str = "kWh") -> list[Path]:
    """Write a report for every supported example file, plus an index page. Returns the files written."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written, items = [], ""
    for path in sorted(EXAMPLES.glob("*.json")):
        try:
            summary = report.summarize(*report.load(path), units=units)
        except report.UnsupportedFile as error:
            print(f"Skipping {path.name}: {error}")
            continue
        page = out_dir / f"{path.stem}.html"
        page.write_text(report.render(summary, path.name), encoding="utf-8")
        written.append(page)
        metadata = summary["metadata"]
        items += ITEM.format(
            name=path.stem,
            title=path.stem.replace("_", " ").title(),
            description=metadata.get("description", ""),
        )
    index = out_dir / "index.html"
    index.write_text(INDEX.format(items=items, version=report.REPORT_VERSION), encoding="utf-8")
    written.append(index)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output", type=Path, help="Folder to write the reports and index page into")
    parser.add_argument("--units", choices=sorted(report.UNITS), default="kWh", help="Energy units for the reports")
    args = parser.parse_args(argv)
    written = build(args.output, args.units)
    print(f"Wrote {len(written)} files to {args.output}")


if __name__ == "__main__":
    main()
