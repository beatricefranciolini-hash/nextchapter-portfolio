# NextChapter · portfolio

Portfolio site for the DSC502 Coding individual project: how I built **NextChapter**, an AI outplacement platform
(live app: https://www.my-nextchapter.app, private and invite-only). The app's code is in a separate private repository.

- `src/*.html` — page content · `build.py` — shared layout → the `*.html` pages at the root
- `assets/` — style, script, screenshots (fictitious test data, passwords blurred) and charts
- `analysis/index.html` — the executed pandas/SQL notebook (anonymous data only)
- `scripts/check_site.py` — word count, drafts and to-dos left, broken links, sensitive text

```
python3 build.py && python3 scripts/check_site.py
```

Published with GitHub Pages from the `main` branch.
