# Daily Life Notes

A small daily publication: one short page a day on home safety, everyday technology, and
the practical fixes that make a normal day go more smoothly.

Live site: <https://lukelee5555-sudo.github.io/daily-life-notes/>

## How it is built

Plain HTML, no build service. GitHub Pages serves the files on `main` directly
(`.nojekyll` is present so Jekyll stays out of the way). Sources live in `content/posts/`
as Markdown with a small front matter block; `tools/site.py` renders them into `posts/*.html`
and regenerates `index.html`, `sitemap.xml` and `feed.xml`.

```
content/posts/YYYY-MM-DD-slug.md   source article (front matter: title, date, summary, tags)
posts/YYYY-MM-DD-slug.html         published page (generated)
index.html                         home page with the latest notes (generated)
about.html, privacy.html, 404.html static pages (generated)
assets/style.css                   the whole design
tools/site.py                      static site generator (stdlib only)
tools/publish_daily.py             publish one article, build, commit, push
tools/config.json                  site name, tagline, base URL
```

## Publishing today's note

Write the article body to a Markdown file (300 words minimum), then:

```bash
python3 tools/publish_daily.py \
  --title "Title of the note" \
  --summary "One or two sentences for the home page, feed and search results." \
  --tags safety,home \
  --body /tmp/body.md
```

The script writes `content/posts/<date>-<slug>.md`, rebuilds the site, commits, and pushes
to `origin main`. `--no-push` stops after the local commit, `--date` sets a date other than
today.

## Rebuilding only

```bash
python3 tools/site.py           # build everything from content/posts/
python3 tools/site.py --list    # list the current posts
```

## Editorial rules

- One article a day, roughly 600–900 words, written to be useful on its own.
- Concrete numbers and named settings over general encouragement.
- No invented statistics, studies, or quotes. If a figure is not verifiable, it does not
  go in.
- Anything involving mains electricity, gas, structural work, or heights says plainly when
  a licensed professional is the right answer.
- Affiliate or sponsored links, if ever added, are labelled in the article itself.
