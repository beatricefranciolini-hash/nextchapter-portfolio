"""Builds the portfolio pages: src/<page>.html (content only) + one shared layout -> <page>.html at the root.

Run: python3 build.py   (then python3 scripts/check_site.py)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = [
    ("index", "Home"),
    ("problem", "Who & what problem"),
    ("building", "Building it"),
    ("data", "Data"),
    ("business", "Pay & reach"),
    ("reflection", "Do differently"),
    ("ai-log", "AI log & refs"),
]

LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="icon" href="assets/img/favicon.png">
<link rel="stylesheet" href="assets/style.css">
<script src="assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="top-inner">
    <a class="brand" href="index.html"><img src="assets/img/logo.png" alt="NextChapter" width="160" height="26"></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav id="nav" aria-label="Sections">
      <ol>
{nav}
      </ol>
    </nav>
  </div>
</header>
{hero}<main id="main">
{body}
</main>
<footer class="foot">
  <div class="foot-inner">
    <p><strong>NextChapter</strong> · portfolio for DSC502 Coding, Regent's University London · Beatrice Franciolini · 2026</p>
    <p>{pager}</p>
  </div>
</footer>
<dialog class="lightbox" aria-label="Enlarged image"><button class="lightbox-close" aria-label="Close">Close ✕</button><img alt=""></dialog>
</body>
</html>
"""


def main():
    for i, (slug, label) in enumerate(PAGES):
        src = (ROOT / "src" / f"{slug}.html").read_text()
        meta = dict(re.findall(r"<!--\s*(title|description):\s*(.*?)\s*-->", src))
        nav = "\n".join(
            f'        <li><a href="{s}.html"{" aria-current=\"page\"" if s == slug else ""}>{l}</a></li>'
            for s, l in PAGES
        )
        prev_link = f'<a href="{PAGES[i - 1][0]}.html">← {PAGES[i - 1][1]}</a>' if i > 0 else ""
        next_link = f'<a href="{PAGES[i + 1][0]}.html">{PAGES[i + 1][1]} →</a>' if i < len(PAGES) - 1 else ""
        hero = ""
        m = re.search(r"<!-- hero -->(.*?)<!-- /hero -->", src, re.S)
        if m:
            hero, src = m.group(1).strip() + "\n", src.replace(m.group(0), "")
        html = LAYOUT.format(
            hero=hero,
            title=meta.get("title", "NextChapter"),
            description=meta.get("description", ""),
            nav=nav,
            body=src.strip(),
            pager=" · ".join(x for x in [prev_link, next_link] if x),
        )
        (ROOT / f"{slug}.html").write_text(html)
        print("built", f"{slug}.html")


if __name__ == "__main__":
    main()
