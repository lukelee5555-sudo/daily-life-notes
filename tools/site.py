#!/usr/bin/env python3
"""Static site builder for daily-life-notes.

Reads Markdown posts from content/posts/, writes HTML into posts/, and rebuilds
index.html, about.html, privacy.html, 404.html, sitemap.xml, feed.xml and
robots.txt. No third-party packages and no build service: the output is plain
HTML, so GitHub Pages can serve it straight from the main branch.

    python3 tools/site.py            # build everything
    python3 tools/site.py --list     # print post titles and dates only
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))
CONTENT = ROOT / "content" / "posts"
OUT_POSTS = ROOT / "posts"
CONFIG = json.loads((ROOT / "tools" / "config.json").read_text(encoding="utf-8"))

BASE_URL = CONFIG["base_url"].rstrip("/")
PREFIX = urlparse(BASE_URL).path.rstrip("/")  # "" or "/daily-life-notes"
SITE = CONFIG["site_name"]
TAGLINE = CONFIG["tagline"]
DESCRIPTION = CONFIG["description"]
AUTHOR = CONFIG["author"]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# ---------------------------------------------------------------- helpers

def esc(text: str) -> str:
    return html.escape(text, quote=False)


def url_for(path: str) -> str:
    """Root-relative link that respects the project-page prefix."""
    if path.startswith(("http://", "https://", "mailto:", "#")):
        return path
    return f"{PREFIX}/{path.lstrip('/')}"


def pretty_date(d: str) -> str:
    y, m, day = (int(x) for x in d.split("-"))
    return f"{MONTHS[m - 1]} {day}, {y}"


def inline(text: str) -> str:
    """Inline markdown: code, bold, italic, links."""
    placeholders: list[str] = []

    def stash(snippet: str) -> str:
        placeholders.append(snippet)
        return f"\x00{len(placeholders) - 1}\x00"

    text = re.sub(r"`([^`]+)`",
                  lambda m: stash(f"<code>{esc(m.group(1))}</code>"), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: stash(f'<a href="{esc(m.group(2))}">{esc(m.group(1))}</a>'), text)
    text = esc(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    for i, snippet in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", snippet)
    return text


def render_markdown(md: str) -> str:
    """A deliberately small Markdown subset: headings, lists, quotes, code, rules."""
    out: list[str] = []
    lines = md.split("\n")
    i = 0
    para: list[str] = []
    list_kind: str | None = None
    in_code = False
    code_buf: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para).strip())}</p>")
            para = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                out.append("<pre><code>" + esc("\n".join(code_buf)) + "</code></pre>")
                code_buf, in_code = [], False
            else:
                code_buf.append(line)
            i += 1
            continue

        if stripped.startswith("```"):
            flush_para(); close_list()
            in_code = True
            i += 1
            continue

        if not stripped:
            flush_para(); close_list()
            i += 1
            continue

        m = re.match(r"^(#{2,4})\s+(.*)$", stripped)
        if m:
            flush_para(); close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            flush_para(); close_list()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith("> "):
            flush_para(); close_list()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
            continue

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            flush_para()
            if list_kind != "ul":
                close_list()
                out.append("<ul>")
                list_kind = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        m = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m:
            flush_para()
            if list_kind != "ol":
                close_list()
                out.append("<ol>")
                list_kind = "ol"
            out.append(f"<li>{inline(m.group(1))}</li>")
            i += 1
            continue

        para.append(stripped)
        i += 1

    if in_code and code_buf:
        out.append("<pre><code>" + esc("\n".join(code_buf)) + "</code></pre>")
    flush_para()
    close_list()
    return "\n".join(out)


# ---------------------------------------------------------------- templates

def layout(title: str, body: str, description: str = DESCRIPTION,
           canonical: str = "", body_class: str = "") -> str:
    full_title = f"{title} · {SITE}" if title and title != SITE else SITE
    canonical_tag = f'\n  <link rel="canonical" href="{esc(canonical)}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="{CONFIG['language']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(full_title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="{esc(AUTHOR)}">
  <meta property="og:site_name" content="{esc(SITE)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">{canonical_tag}
  <link rel="stylesheet" href="{url_for('assets/style.css')}">
  <link rel="alternate" type="application/rss+xml" title="{esc(SITE)}" href="{url_for('feed.xml')}">
</head>
<body{(' class="' + body_class + '"') if body_class else ''}>
  <header class="site-head">
    <a class="brand" href="{url_for('')}">{esc(SITE)}</a>
    <nav><a href="{url_for('')}">Home</a><a href="{url_for('about.html')}">About</a><a href="{url_for('feed.xml')}">RSS</a></nav>
  </header>
  <main>
{body}
  </main>
  <footer class="site-foot">
    <p>{esc(SITE)} — {esc(TAGLINE)}</p>
    <p><a href="{url_for('about.html')}">About</a> · <a href="{url_for('privacy.html')}">Privacy</a> · <a href="{url_for('feed.xml')}">RSS</a></p>
    <p class="tiny">© {date.today().year} {esc(AUTHOR)}. Written and published by a small automation every day.</p>
  </footer>
</body>
</html>
"""


def parse_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    body = raw
    if raw.startswith("---"):
        _, front, rest = raw.split("---", 2)
        body = rest
        for line in front.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip().strip('"')
    slug = path.stem
    title = meta.get("title") or slug.replace("-", " ").title()
    d = meta.get("date") or slug[:10]
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    return {
        "slug": slug,
        "path": path,
        "title": title,
        "date": d,
        "summary": meta.get("summary", ""),
        "tags": tags,
        "body_md": body.strip(),
    }


# ---------------------------------------------------------------- builders

def build_post(post: dict) -> None:
    content = render_markdown(post["body_md"])
    tag_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in post["tags"])
    canonical = f"{BASE_URL}/posts/{post['slug']}.html"
    body = f"""    <article class="post">
      <p class="crumb"><a href="{url_for('')}">Home</a> / {esc(pretty_date(post['date']))}</p>
      <h1>{esc(post['title'])}</h1>
      <p class="meta"><time datetime="{esc(post['date'])}">{esc(pretty_date(post['date']))}</time> · {esc(AUTHOR)} {tag_html}</p>
      <div class="prose">
{content}
      </div>
      <p class="back"><a href="{url_for('')}">← All notes</a></p>
    </article>
"""
    (OUT_POSTS / f"{post['slug']}.html").write_text(
        layout(post["title"], body, post["summary"] or DESCRIPTION, canonical),
        encoding="utf-8")


def build_index(posts: list[dict]) -> None:
    posts = sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)
    cards = []
    for p in posts:
        tags = " ".join(f'<span class="tag">{esc(t)}</span>' for t in p["tags"])
        cards.append(f"""      <li class="card">
        <a href="{url_for('posts/' + p['slug'] + '.html')}">
          <time datetime="{esc(p['date'])}">{esc(pretty_date(p['date']))}</time>
          <h2>{esc(p['title'])}</h2>
          <p>{esc(p['summary'])}</p>
        </a>
        <p class="tags">{tags}</p>
      </li>""")
    body = f"""    <section class="hero">
      <h1>{esc(SITE)}</h1>
      <p class="lede">{esc(TAGLINE)}</p>
      <p class="sub">{esc(DESCRIPTION)}</p>
    </section>
    <section>
      <h2 class="section-title">Latest notes</h2>
      <ul class="cards">
{chr(10).join(cards)}
      </ul>
    </section>
"""
    (ROOT / "index.html").write_text(
        layout(SITE, body, DESCRIPTION, f"{BASE_URL}/"), encoding="utf-8")


def build_static_pages(posts: list[dict]) -> None:
    about_body = f"""    <article class="post">
      <h1>About</h1>
      <div class="prose">
<p>{esc(SITE)} is a small, daily publication. One short page a day on home safety, everyday technology, and the practical fixes that make a normal day go more smoothly.</p>
<h2>How it works</h2>
<p>Each entry is prepared in the evening, kept to a single sitting's read, and checked against the source material it draws on: manufacturer guidance, standards bodies, and public safety agencies. The aim is not to cover everything, but to leave you with a short list you can act on today.</p>
<h2>What you will find</h2>
<ul>
<li><strong>Safety at home</strong> — heating, electricity, and the seasonal problems that arrive with cold weather.</li>
<li><strong>Everyday technology</strong> — phones, batteries, networks, and settings worth changing.</li>
<li><strong>Small life fixes</strong> — the ten-minute jobs that save an hour later.</li>
</ul>
<h2>Editorial note</h2>
<p>Nothing here is professional advice for your particular wiring, appliance, or building. Where a job involves mains electricity, gas, or heights, the right move is a licensed professional — the notes say so when it matters.</p>
<h2>Contact</h2>
<p>Corrections and suggestions are welcome through the repository linked in the footer of each page.</p>
      </div>
    </article>
"""
    (ROOT / "about.html").write_text(
        layout("About", about_body, f"About {SITE}", f"{BASE_URL}/about.html"), encoding="utf-8")

    privacy_body = """    <article class="post">
      <h1>Privacy policy</h1>
      <div class="prose">
<p>Last updated: 2026-11-20</p>
<p>This site is a static publication. It does not ask you to create an account, and it does not have a comment section or a contact form.</p>
<h2>What is collected</h2>
<p>Like nearly every website, the hosting provider records standard technical request logs (IP address, browser type, the page requested, and the time). These logs are used to keep the site available and to understand which pages are read.</p>
<p>If advertising or analytics services are enabled on this site, those third parties may set cookies or read device identifiers in order to measure and personalise advertising. Where required by law, a consent notice is shown before any non-essential cookie is set, and you can decline it.</p>
<h2>What is not collected</h2>
<ul>
<li>No names, email addresses, or phone numbers are requested or stored by this site.</li>
<li>No accounts, passwords, or payment details pass through this site.</li>
<li>No reading history is tied to an identity by the publisher.</li>
</ul>
<h2>Your choices</h2>
<p>You can block cookies in your browser settings at any time; the pages remain readable. You can also use your browser's private mode to avoid persistent cookies entirely.</p>
<h2>Third-party links</h2>
<p>Some notes link to manufacturers, public agencies, or shops. Those sites have their own privacy policies, which apply once you follow a link.</p>
<h2>Changes</h2>
<p>If this policy changes, the date at the top of this page changes with it.</p>
      </div>
    </article>
"""
    (ROOT / "privacy.html").write_text(
        layout("Privacy policy", privacy_body, f"Privacy policy for {SITE}",
               f"{BASE_URL}/privacy.html"), encoding="utf-8")

    not_found = """    <article class="post">
      <h1>Page not found</h1>
      <div class="prose">
<p>That page is not here. It may have been renamed, or the link may have a typo.</p>
<p><a href="/daily-life-notes/">Go to the latest notes →</a></p>
      </div>
    </article>
"""
    (ROOT / "404.html").write_text(
        layout("Page not found", not_found.replace("/daily-life-notes/", url_for(""))),
        encoding="utf-8")


def build_feeds(posts: list[dict]) -> None:
    posts = sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)
    urls = [f"{BASE_URL}/", f"{BASE_URL}/about.html", f"{BASE_URL}/privacy.html"]
    urls += [f"{BASE_URL}/posts/{p['slug']}.html" for p in posts]
    today = date.today().isoformat()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")

    items = []
    for p in posts[:20]:
        link = f"{BASE_URL}/posts/{p['slug']}.html"
        pub = datetime.fromisoformat(p["date"] + "T09:00:00+09:00").strftime(
            "%a, %d %b %Y %H:%M:%S %z")
        items.append(f"""    <item>
      <title>{esc(p['title'])}</title>
      <link>{esc(link)}</link>
      <guid isPermaLink="true">{esc(link)}</guid>
      <pubDate>{pub}</pubDate>
      <description>{esc(p['summary'])}</description>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{esc(SITE)}</title>
    <link>{esc(BASE_URL)}/</link>
    <description>{esc(DESCRIPTION)}</description>
    <language>{CONFIG['language']}</language>
    <lastBuildDate>{datetime.now(KST).strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")

    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")


def build() -> list[dict]:
    OUT_POSTS.mkdir(exist_ok=True)
    for stale in OUT_POSTS.glob("*.html"):
        stale.unlink()
    posts = [parse_post(p) for p in sorted(CONTENT.glob("*.md"))]
    if not posts:
        raise SystemExit("no posts found in content/posts/")
    for post in posts:
        build_post(post)
    build_index(posts)
    build_static_pages(posts)
    build_feeds(posts)
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    return posts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="list posts and exit")
    args = ap.parse_args()
    if args.list:
        for p in sorted((parse_post(x) for x in CONTENT.glob("*.md")),
                        key=lambda x: x["date"], reverse=True):
            print(f"{p['date']}  {p['slug']}  {p['title']}")
        return
    posts = build()
    print(f"built {len(posts)} post(s) → index.html, posts/, sitemap.xml, feed.xml")


if __name__ == "__main__":
    main()
