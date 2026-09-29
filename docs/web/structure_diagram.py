"""
Build an HTML figure of the canonical end-use category tree, read from the schema itself.

Adapted from a structure diagram Greg Collins shared (covering energy sources, end uses, and
consumption fields); this keeps just the end-use tree, embedded inline in the specification page.
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "report" / "src"))
from report import END_USE_COLORS  # noqa: E402

FALLBACK_COLOR = "#9aa3ad"

CSS = """
  :root {
    color-scheme: light;
    --page: #ffffff; --ink: #10151c; --rule: #dbe1e8;
    --root-bg: #22303c;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--page); color: var(--ink);
    font: 15px/1.5 Inter, system-ui, sans-serif; -webkit-font-smoothing: antialiased;
  }
  main { padding: 16px; }
  .row { display: flex; align-items: center; height: 36px; }
  .pipe {
    font-family: "Cascadia Mono", Consolas, ui-monospace, monospace; font-size: 15px; line-height: 36px;
    color: #b6bfca; white-space: pre; user-select: none;
  }
  .node {
    display: inline-flex; align-items: center; gap: 10px;
    border: 1.5px solid var(--rule); border-radius: 999px; background: #ffffff; padding: 3px 15px 3px 12px;
    font-size: 14.5px;
  }
  .node.root {
    border-radius: 8px; background: var(--root-bg); border-color: var(--root-bg); color: #ffffff;
    font-weight: 600; padding: 4px 15px;
    font-family: "Cascadia Mono", Consolas, ui-monospace, monospace; font-size: 13.5px;
  }
  .node.parent { font-weight: 600; }
  .dot { width: 12px; height: 12px; border-radius: 50%; flex: none; }
"""


def load_schema(repo: Path) -> dict:
    return yaml.safe_load((repo / "schema" / "BuildingPerformanceOutputReport.schema.yaml").read_text(encoding="utf-8"))


def node(label, color=None, classes=""):
    dot = f'<span class="dot" style="background:{color}"></span>' if color else ""
    return f'<span class="node {classes}">{dot}{label}</span>'


def row(pipe, content):
    return f'    <div class="row"><span class="pipe">{pipe}</span>{content}</div>\n'


def build_end_uses(repo: Path) -> str:
    schema = load_schema(repo)
    end_uses = schema["EnergySource"]["Data Elements"]["end_uses"]["Canonical End Uses"]

    html = '<section>\n  <div class="tree">\n'
    html += row("", node("Canonical End Uses", classes="root"))
    for i, category in enumerate(end_uses):
        name = category["name"]
        subs = [s["name"] for s in category.get("subcategories", [])]
        last = i == len(end_uses) - 1
        color = END_USE_COLORS.get(name, FALLBACK_COLOR)
        html += row("└─ " if last else "├─ ", node(name, color, "parent"))
        for j, sub in enumerate(subs):
            sub_last = j == len(subs) - 1
            trunk = "   " if last else "│  "
            html += row(trunk + ("└─ " if sub_last else "├─ "), node(sub, color))
    html += "  </div>\n</section>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Canonical end uses — structure</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>

{html}
</main>
</body>
</html>
"""
