# Handoff - 16 Sep 2026 (phase closed: 11, Supabase write-back, append-only, no login)

State: commit 0dd4af0 "Phase 11: Supabase write-back, append-only, no login" (not pushed; spiff decides, because the
live review link would show "offline, saved locally" until docs/config.js is filled). The Apps Script endpoint is gone
from every page. The table does not exist yet: spiff runs the migration and fills docs/config.js (three steps on
docs/setup.html). Everything was verified against a local mock of the REST endpoint; the live checks below are pending.

## Read first
1. PLAN.md section 15 (what shipped, the row conventions, the known limitations, what changed outside the script tags).
2. scripts/board_store.js (the shared layer; the header comment explains init, write, history, attach, the outbox and
   the pill) and supabase/migrations/20260916120000_board_entries.sql (the table, the policies, the revokes).
3. Memory project_state and review-transport-preferences (spiff chose Supabase on 16 Sep 2026; every human input on
   every page is recorded; the anon key is public by design; no service key anywhere).

## Verify before coding
- `git status --short` is empty; HEAD is 0dd4af0 or the closure commit after it.
- `python3 scripts/build_site.py` leaves docs/ and data/ unchanged and does not touch docs/config.js.
- `python3 scripts/check_phase9.py` prints 17 PASS lines and no FAIL.

## Live checks once docs/config.js is filled (read URL and KEY from it; the probe row stays in the table, page "setup")
    URL=...; KEY=...
    # insert: expect HTTP 201 and the row back with id and created_at
    curl -s -X POST "$URL/rest/v1/board_entries" -H "apikey: $KEY" -H "Content-Type: application/json" \
      -H "Prefer: return=representation" \
      -d '{"page":"setup","item_id":"TEST","field":"probe","value":"hello","who":"Vatsal","kind":"comment"}' -w " %{http_code}\n"
    # select: expect the row
    curl -s "$URL/rest/v1/board_entries?page=eq.setup&order=id.asc" -H "apikey: $KEY" -w " %{http_code}\n"
    # update and delete with the anon key: expect 401 or 403 with code 42501 (permission denied), never 204
    curl -s -X PATCH "$URL/rest/v1/board_entries?item_id=eq.TEST" -H "apikey: $KEY" -H "Content-Type: application/json" \
      -d '{"value":"x"}' -w " %{http_code}\n"
    curl -s -X DELETE "$URL/rest/v1/board_entries?item_id=eq.TEST" -H "apikey: $KEY" -w " %{http_code}\n"
    # then: python3 scripts/pull_board.py  (expect "wrote data/board_entries.json: 1 rows, 1 pages (setup)")
- Cross-browser: open the review link in two browsers (or one plus a private window), pick an identity, give a verdict
  and a comment on a screen in one; reload the other: the same verdict and comment show, the pill reads "live, last
  write <time>", History under the comment box lists both rows.
- If the insert returns 401 "No API key found" or 403, the key or the URL in docs/config.js is wrong; if PATCH returns
  204, the revoke in the migration did not run.

## What to do next
- After the live checks pass: push, then the second review round on the review link with the pill live. Reviewers no
  longer need Export comments for spiff to see their rows, but the export stays the offline record.
- Pending one-liner for spiff's yes: the Integrations lead still reads "Edits save in this browser and reach the sheet
  when the endpoint is set" (kept byte-identical on purpose); the fix is one sentence in scripts/build_integrations.py.
- Before any v0.3 build: `python3 scripts/pull_board.py`, then the edit group from data/board_entries.json (latest per
  page, item and field), never from docs/.

## Constraints carried forward
- inputs/ is read-only; docs/ is generated except docs/config.js (hand-filled, never overwritten); docs/v01/ stays
  byte-identical to inputs/v01/.
- Every new editable control on any page calls yeslyfBoard.write (spiff, 16 Sep 2026: any manual input is recorded);
  filters, sorting and the identity picker are not rows.
- The layer sends the key in the apikey header only (a publishable key is refused in Authorization).
- Rows are never updated or deleted from the site; corrections are new rows. pull_board.py needs no secret.
- v0.2 rules unchanged: causes only, no adviser named, "yeslyf" lowercase, "Rs", no "recommendation" or "founders",
  ASCII only, no em dashes. Subagents: Opus is the floor, never Sonnet. Page density: calm list first, editing behind
  a click.
