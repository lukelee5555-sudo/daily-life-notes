#!/usr/bin/env python3
"""Publish one new post to daily-life-notes and push it.

Pipeline #20 of the daily automation calls this once per run:

    python3 tools/publish_daily.py \
        --title "..." --summary "..." --tags safety,home \
        --body /tmp/body.md --date 2026-11-21

It writes content/posts/<date>-<slug>.md, rebuilds the static site
(index.html, posts/*.html, sitemap.xml, feed.xml), commits, and pushes to
origin main. Add --no-push to build and commit locally only.

Exit codes: 0 published, 1 nothing to do, 2 error (message on stderr).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "posts"
KST = timezone(timedelta(hours=9))

STOPWORDS = {"a", "an", "the", "of", "and", "or", "to", "in", "on", "for", "with",
             "your", "you", "is", "are", "why", "how", "what", "that", "this"}


def slugify(title: str, max_words: int = 8) -> str:
    words = re.findall(r"[a-z0-9]+", title.lower())
    words = [w for w in words if w not in STOPWORDS] or words
    return "-".join(words[:max_words]) or "note"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--body", required=True, help="path to a Markdown file with the article body")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--slug", default=None)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    body_path = Path(args.body)
    if not body_path.is_absolute():
        body_path = ROOT / body_path
    if not body_path.exists():
        print(f"body file not found: {body_path}", file=sys.stderr)
        return 2

    body = body_path.read_text(encoding="utf-8").strip()
    words = len(re.findall(r"\w+", body))
    if words < 300:
        print(f"refusing to publish: body is only {words} words (minimum 300)", file=sys.stderr)
        return 2

    slug = f"{args.date}-{args.slug or slugify(args.title)}"
    target = CONTENT / f"{slug}.md"
    if target.exists():
        print(f"already published today: {target.name}", file=sys.stderr)
        return 1

    front = ["---", f'title: "{args.title}"', f"date: {args.date}",
             f'summary: "{args.summary}"', f"tags: {args.tags}", "---", ""]
    target.write_text("\n".join(front) + body + "\n", encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({words} words)")

    built = run([sys.executable, str(ROOT / "tools" / "site.py")])
    sys.stdout.write(built.stdout)
    if built.returncode != 0:
        print(built.stderr, file=sys.stderr)
        return 2

    stamp = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    msg = f"post: {args.title} ({args.date})"
    run(["git", "add", "-A"])
    commit = run(["git", "commit", "-m", f"{msg}\n\nPublished {stamp} KST."])
    print((commit.stdout or commit.stderr).strip())

    if args.no_push:
        print("skipped push (--no-push)")
        return 0

    push = run(["git", "push", "origin", "main"])
    sys.stdout.write(push.stdout or "")
    if push.returncode != 0:
        print(push.stderr, file=sys.stderr)
        print("push failed — the site was built and committed locally", file=sys.stderr)
        return 2
    print("pushed to origin/main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
