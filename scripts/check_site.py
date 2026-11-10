"""Checks the built site before publishing.

- Word count of the main text (the brief allows about 1500 words): figure captions, code, the references/AI log page,
  and draft/to-do markers are reported separately.
- Lists every DRAFT (reflection to rewrite) and TO FILL IN marker: both must be gone before submission.
- Broken local links and images.
- Sensitive text: email addresses, API keys, the Supabase project id, local paths, ".env".

Run: python3 scripts/check_site.py   (exit code 1 if there are broken links or sensitive text)
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index", "problem", "building", "data", "business", "reflection", "ai-log"]
NOT_COUNTED = {"ai-log"}  # references and AI log are outside the word count
SENSITIVE = [
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
    (r"sb_(publishable|secret)_[A-Za-z0-9_-]+", "Supabase key"),
    (r"sk-ant-[A-Za-z0-9_-]+", "Anthropic key"),
    (r"twzpnyqoiwqscoqwkmzs", "Supabase project id"),
    (r"/Users/[A-Za-z]+", "local path"),
    (r"(?<![A-Za-z])\.env(\.local)?\b", ".env file"),
]
MONTHS = "January|February|March|April|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
DATES = [
    rf"\b\d{{1,2}}(?:–\d{{1,2}})?\s+(?:{MONTHS}|May)\b",
    rf"\b(?:{MONTHS})\s+\d{{1,2}}\b",
    rf"\b(?:January|February|March|April|June|July|August|September|October|November|December)\b",
    r"\b\d{1,2}:\d{2}\b", r"\b\d{4}-\d{2}-\d{2}\b", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", r"\blast week\b",
]


def dates_in(text):
    """Dates or times in visible text; Harvard "(Accessed: …)" dates are allowed."""
    text = re.sub(r"\(Accessed: [^)]*\)", "", text)
    text = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "", text)
    return sorted({m.group(0) for p in DATES for m in re.finditer(p, text, re.I)})


class Text(HTMLParser):
    SKIP = {"script", "style", "pre", "code", "figcaption", "header", "footer", "nav", "dialog"}

    def __init__(self):
        super().__init__()
        self.stack, self.main, self.words, self.draft_words = [], False, [], []
        self.drafts, self.todos, self.links = [], [], []
        self.marker_depth = None
        self.struct_depth = None
        self.hero_depth = None
        self.struct_words = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("br", "img", "meta", "link", "input", "hr"):
            if tag == "img":
                self.links.append(a.get("src", ""))
            return
        self.stack.append(tag)
        cls0 = (a.get("class") or "").split()
        if tag == "main":
            self.main = True
        if "hero" in cls0:
            self.main, self.hero_depth = True, len(self.stack)
        if self.struct_depth is None and (tag == "table" or set(cls0) & {"products", "vtimeline", "tiles", "cards", "badges", "legend-tags"}):
            self.struct_depth = len(self.stack)
        if tag == "a":
            self.links.append(a.get("href", ""))
        cls = (a.get("class") or "").split()
        if self.marker_depth is None and ("draft" in cls or "todo" in cls):
            self.marker_depth = len(self.stack)
            (self.drafts if "draft" in cls else self.todos).append("")
            self.marker_kind = "draft" if "draft" in cls else "todo"

    def handle_endtag(self, tag):
        if tag not in self.stack:
            return
        while self.stack:
            if self.marker_depth is not None and len(self.stack) == self.marker_depth:
                self.marker_depth = None
            if self.struct_depth is not None and len(self.stack) == self.struct_depth:
                self.struct_depth = None
            if self.hero_depth is not None and len(self.stack) == self.hero_depth:
                self.hero_depth = None
                self.main = False
            top = self.stack.pop()
            if top == "main":
                self.main = False
            if top == tag:
                break

    def handle_data(self, data):
        if not self.main or any(t in self.SKIP for t in self.stack):
            return
        words = re.findall(r"[A-Za-z0-9$£€%'’.,-]+", data)
        words = [w for w in words if re.search(r"[A-Za-z0-9]", w)]
        if self.marker_depth is not None:
            target = self.drafts if self.marker_kind == "draft" else self.todos
            target[-1] += " " + " ".join(words)
            self.draft_words += words
        elif self.struct_depth is not None:
            self.struct_words += words
        else:
            self.words += words


def main():
    problems, total, total_marked = [], 0, 0
    print(f"{'page':12} {'prose':>6} {'cards/timeline/tables':>22} {'drafts/todos':>13}")
    total_struct = 0
    all_drafts, all_todos = [], []
    for slug in PAGES:
        path = ROOT / f"{slug}.html"
        html = path.read_text()
        p = Text()
        p.feed(html)
        counted = slug not in NOT_COUNTED
        if counted:
            total += len(p.words)
            total_marked += len(p.draft_words)
            total_struct += len(p.struct_words)
        print(f"{slug:12} {len(p.words):6} {len(p.struct_words):22} {len(p.draft_words):13}{'' if counted else '   (not counted)'}")
        all_drafts += [(slug, d.strip()) for d in p.drafts]
        all_todos += [(slug, t.strip()) for t in p.todos]
        for link in p.links:
            if not link or link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = (ROOT / link.split("#")[0]).resolve()
            if not target.exists():
                problems.append(f"{slug}.html: broken link or image {link}")
        visible = re.sub(r"<[^>]+>", " ", html)
        for d in dates_in(re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", "", html, flags=re.S))):
            problems.append(f"{slug}.html: date or time found ({d})")
        for pattern, label in SENSITIVE:
            for m in set(re.findall(pattern, visible)):
                problems.append(f"{slug}.html: {label} found ({str(m)[:12]}…)")
    nb = (ROOT / "analysis" / "index.html").read_text()
    nb_text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", nb, flags=re.S)
    for d in dates_in(re.sub(r"<[^>]+>", " ", nb_text)):
        problems.append(f"analysis/index.html: date or time found ({d})")
    print(f"{'TOTAL':12} {total:6} {total_struct:22} {total_marked:13}")
    print(f"Prose + drafts/to-dos: {total + total_marked} words · everything: {total + total_marked + total_struct} words")
    print(f"\nDRAFT sentences to rewrite: {len(all_drafts)}")
    for slug, d in all_drafts:
        print(f"  - {slug}: {d[:90]}…")
    print(f"TO FILL IN: {len(all_todos)}")
    for slug, t in all_todos:
        print(f"  - {slug}: {t[:90]}…")
    if problems:
        print("\nPROBLEMS:")
        for pr in problems:
            print("  -", pr)
        return 1
    print("\nOK: no broken links or images, no sensitive text found.")
    if all_drafts or all_todos:
        print("Not ready to submit yet: drafts or to-dos remain.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
