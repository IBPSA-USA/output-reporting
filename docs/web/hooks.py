"""MkDocs hooks for this project's generated web documentation."""

import sys
from pathlib import Path

from mkdocs.structure.files import File

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "report" / "src"))
import report  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"


def _supported_examples():
    for example_path in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            data = report.load(example_path)
        except report.UnsupportedFile:
            continue
        yield example_path, data


def lattice_example_columns(example_path, content):  # pylint: disable=unused-argument
    """Adds a "Report" column to lattice's generated Examples table.

    Links to the example's report page (added to docs_dir by `on_files`, below), for examples
    the report tool supports. Written as a plain sibling reference - `{stem}.md`, next to
    examples.md itself - so MkDocs resolves and rewrites it like any other internal link, and
    lattice styles it as a button along with the table's other links.
    """
    try:
        report.load(example_path)
    except report.UnsupportedFile:
        return {}
    return {"Report": f"[View Report]({example_path.stem}.md){{: .md-button .md-button--small }}"}


def on_files(files, config, **kwargs):  # pylint: disable=unused-argument
    """Generates each example's report, plus a page embedding it, as real tracked doc files.

    Making these real `Files` - rather than writing them straight into the built site, outside
    docs_dir, the way this used to work - means they render correctly under `mkdocs serve` too,
    not just a one-shot `mkdocs build`. The report itself keeps its own full-page styling and is
    added as a plain file; the wrapper page embeds it in an iframe so it still reads as part of
    the site, with the site's own nav and header around it.
    """
    for example_path, data in _supported_examples():
        stem = example_path.stem
        html = report.render(report.summarize(*data), example_path.name)
        report_uri = f"reports/{stem}.html"
        files.append(File.generated(config, report_uri, content=html))

        wrapper = (
            f"# {stem}\n\n"
            "[← Back to examples](examples.md)\n\n"
            f'<iframe src="../../{report_uri}" style="width: 100%; height: 85vh; border: none;"></iframe>\n'
        )
        files.append(File.generated(config, f"examples/{stem}.md", content=wrapper))

    return files
