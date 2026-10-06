"""Build index.html from box-shortlist.md.

Usage: python build.py <path to box-shortlist.md>

Handles the subset of Markdown the shortlist uses: headings, paragraphs,
bullet lists, pipe tables with alignment rows, `code` and **bold**.
"""

import html
import re
import sys
from pathlib import Path

OUT = Path(__file__).parent / "index.html"


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table(lines: list[str]) -> str:
    head, align, *body = lines
    right = [a.strip().endswith(":") for a in split_row(align)]
    cls = lambda i: ' class="num"' if right[i] else ""  # noqa: E731
    th = "".join(f"<th{cls(i)}>{inline(c)}</th>" for i, c in enumerate(split_row(head)))
    rows = "".join(
        "<tr>" + "".join(f"<td{cls(i)}>{inline(c)}</td>" for i, c in enumerate(split_row(r))) + "</tr>"
        for r in body
    )
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'


def convert(md: str) -> str:
    blocks: list[str] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif m := re.match(r"(#{1,3}) (.*)", line):
            level = len(m.group(1))
            blocks.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
        elif line.startswith("|"):
            start = i
            while i < len(lines) and lines[i].startswith("|"):
                i += 1
            blocks.append(table(lines[start:i]))
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            blocks.append(f"<ul>{''.join(items)}</ul>")
        else:
            blocks.append(f"<p>{inline(line)}</p>")
            i += 1
    return "\n".join(blocks)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Box Shortlist</title>
<meta name="description" content="Topps sealed boxes ranked by what their autographs resell for and how often those cards sell, from Topps's published odds and SportsCardsPro values.">
<style>
:root {
  --bg: #fbfaf8; --fg: #1d1d1f; --muted: #5f6368; --line: #e3e1dc;
  --head: #f1efea; --accent: #1f5fbf; --code: #efede8;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #141518; --fg: #e8e6e3; --muted: #a0a4ab; --line: #2c2e33;
          --head: #1d1f23; --accent: #7aa7ff; --code: #24262b; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 1200px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 2rem; margin: 0 0 8px; }
h2 { font-size: 1.4rem; margin: 40px 0 8px; padding-top: 8px; border-top: 1px solid var(--line); }
h3 { font-size: 1.1rem; margin: 28px 0 8px; }
p, ul { max-width: 75ch; }
li { margin: 4px 0; }
strong { color: var(--accent); }
code { background: var(--code); padding: 1px 5px; border-radius: 4px; font-size: 0.9em; }
.scroll { overflow-x: auto; margin: 12px 0 20px; border: 1px solid var(--line); border-radius: 8px; }
table { border-collapse: collapse; width: 100%; font-size: 0.875rem; }
th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { background: var(--head); position: sticky; top: 0; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover td { background: var(--head); }
footer { margin-top: 48px; color: var(--muted); font-size: 0.85rem; }
</style>
</head>
<body>
<main>
{body}
<footer>Built from box-shortlist.md. Odds from Topps's published odds sheets; auto values from SportsCardsPro; prices as labeled in the table.</footer>
</main>
</body>
</html>
"""

if __name__ == "__main__":
    md = Path(sys.argv[1]).read_text(encoding="utf-8")
    OUT.write_text(PAGE.replace("{body}", convert(md)), encoding="utf-8")
    print(OUT)
