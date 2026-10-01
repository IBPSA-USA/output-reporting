"""MkDocs hooks for this project's generated web documentation."""

import sys
from pathlib import Path

from mkdocs.structure.files import File

sys.path.insert(0, str(Path(__file__).resolve().parent))
import structure_diagram  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "report" / "src"))
import report  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"
EXAMPLES_PAGE_URI = "examples/examples.md"

EXAMPLE_REPORT_NOTE = (
    "This is an example report, generated from the example file by a draft tool in this repository. "
    "It illustrates one way a conforming file can be presented. The specification does not define "
    "a report format, and the report's layout and contents are not part of the specification."
)


def _supported_examples():
    for example_path in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            data = report.load(example_path)
        except report.UnsupportedFile:
            continue
        yield example_path, data


def lattice_example_columns(example_path, content):  # pylint: disable=unused-argument
    """Adds an "Example Report" column to lattice's generated Examples table.

    Links to the example's report page (added to docs_dir by `on_files`, below), for examples
    the report tool supports. Written as a plain sibling reference - `{stem}.md`, next to
    examples.md itself - so MkDocs resolves and rewrites it like any other internal link, and
    lattice styles it as a button along with the table's other links.
    """
    try:
        report.load(example_path)
    except report.UnsupportedFile:
        return {}
    return {"Example Report": f"[View Example Report]({example_path.stem}.md){{: .md-button .md-button--small }}"}


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
            f"# Example Report: {stem}\n\n"
            "[← Back to examples](examples.md)\n\n"
            f"{EXAMPLE_REPORT_NOTE}\n\n"
            f"[Print to PDF](../../{report_uri}#print){{: .md-button .md-button--small target=_blank }}\n\n"
            f'<iframe src="../../{report_uri}" style="width: 100%; height: 85vh; border: none;"></iframe>\n'
        )
        files.append(File.generated(config, f"examples/{stem}.md", content=wrapper))

    files.append(
        File.generated(
            config, "assets/end_use_structure.html", content=structure_diagram.build_end_uses(REPO_ROOT)
        )
    )

    return files


def on_page_markdown(markdown, page, **kwargs):  # pylint: disable=unused-argument
    """Adds an introduction below the heading of lattice's generated Examples page.

    lattice writes that page's heading and table itself, with no option for introductory text, so
    the introduction is inserted after its first line here.
    """
    if page.file.src_uri != EXAMPLES_PAGE_URI:
        return markdown
    heading, _, rest = markdown.partition("\n")
    introduction = (
        "Each file below conforms to the schema and can be downloaded as YAML, JSON, or CBOR. "
        "Where available, the **View Example Report** button opens an example report generated "
        "from that file. The example reports illustrate one way a conforming file can be "
        "presented. The specification does not define a report format, and the reports' layout "
        "and contents are not part of the specification."
    )
    return f"{heading}\n\n{introduction}\n{rest}"
