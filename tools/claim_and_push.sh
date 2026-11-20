#!/usr/bin/env bash
# Push the prepared site to GitHub and turn on Pages.
#
# Run this once the empty public repo exists and Pickle has access to it:
#     bash tools/claim_and_push.sh
#
# Exit codes:
#   0  pushed, Pages enabled (or already on) — URL printed
#   3  repo does not exist yet
#   4  repo exists but this credential cannot push to it (app access missing)
#   5  push failed
#   6  push ok, Pages could not be enabled
set -uo pipefail

REPO="lukelee5555-sudo/daily-life-notes"
BRANCH="main"
cd "$(dirname "$0")/.." || exit 2

say() { printf '%s\n' "$*"; }

# 1. does the repository exist?
if ! gh repo view "$REPO" --json name >/dev/null 2>&1; then
  say "MISSING REPO: $REPO does not exist yet."
  say "Create it once at https://github.com/new — name daily-life-notes, Public, no template,"
  say "no README — then grant it to the Pickle app at"
  say "https://github.com/apps/pickle/installations/new and run this script again."
  exit 3
fi
say "repo exists: https://github.com/$REPO"

# 2. can this credential push?
push_ok=$(gh api "/repos/$REPO" --jq '.permissions.push // false' 2>/dev/null)
if [ "$push_ok" != "true" ]; then
  say "NO PUSH PERMISSION on $REPO."
  say "Add this repository to the Pickle GitHub app installation:"
  say "https://github.com/apps/pickle/installations/new"
  exit 4
fi

# 3. make sure the local branch is main and the remote is set
git remote get-url origin >/dev/null 2>&1 || \
  git remote add origin "https://github.com/$REPO.git"
git branch -M "$BRANCH"

# 4. push
if ! git push -u origin "$BRANCH"; then
  say "PUSH FAILED — see the git output above."
  exit 5
fi
say "pushed $BRANCH to https://github.com/$REPO"

# 5. enable Pages from the branch root (skip quietly if already on)
status=$(gh api "/repos/$REPO/pages" --jq '.html_url' 2>/dev/null)
if [ -z "$status" ]; then
  gh api -X POST "/repos/$REPO/pages" \
      -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1
  status=$(gh api "/repos/$REPO/pages" --jq '.html_url' 2>/dev/null)
fi
if [ -n "$status" ]; then
  say "Pages: $status"
  say "first build takes 1–3 minutes; check with: gh api /repos/$REPO/pages --jq '.status'"
  exit 0
fi

say "PUSH OK, but Pages could not be enabled with this credential (Pages write permission)."
say "Turn it on once at https://github.com/$REPO/settings/pages —"
say "Source: Deploy from a branch · Branch: main · Folder: / (root)."
exit 6
