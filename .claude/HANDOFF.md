# Handoff - 9 Oct 2026 (phase closed: logic panel language - plain words, the cut, one glossary; pushed)

State: the logic panel speaks one set of words (data/logic_glossary.json) on every screen, page, open question and
code name; it is pushed and live by direct link, its tab hidden until the merge. Vatsal's verdict: simple now, but far
too big, "word vomit". The next job is a crisper pass, and where the complexity line sits is not decided yet.

## Read first
1. Memory crisp-not-word-vomit (the next job and how to start it), then memory glossary-in-their-words.
2. PLAN.md section 28 (what closed, the known limits, the firm rules carried forward).
3. The map artifact https://claude.ai/artifact/4Pvm3fga2vJzSj8udHLsYS (version 8). Artifact action "read" returns its
   full HTML with the map content (TREE), the screens (SCREENS) and the pages (PAGES) embedded; to republish from a new
   session, pass its url.

## Verify before changing anything
- `git status --short`: only the seven untracked items listed under constraints; `git status -sb`: main level with
  origin (pushed 9 Oct 2026, last commit the close of this phase).
- `python3 scripts/build_site.py`, then `python3 scripts/check_phase9.py` 19 PASS, `check_site.py` 3 PASS,
  `check_logic.py` 9 PASS.
- Live: https://spiffler33.github.io/yeslyf-wireframes/logic_wireframes.html loads and shows "Allocation matrix".

## Next: the crisper pass
1. Do not rewrite everything first. With Vatsal, find the complexity line on a pilot: L05 and L08 (the heaviest
   screens) and one page. For each, agree what the people who run the panel (Harish and Somil, full time) must see,
   what moves to the builders' notes, and what goes. Show the pilot, measure the sizes, ask before rolling out.
2. Then roll out as the earlier passes did: a brief, a checker, helpers on opus, one merge, the board's checks. The
   scratch briefs and checkers of 9 Oct are gone with the session; rebuild the checker from these invariants: fixed
   fields unchanged; every link, button and branch kept in order with its target; a self-link named word for word in a
   spec.logic line; spec.logic[0] (seats) and [1] (writes) generated, [1] rebuilt from the writes; field count and
   tags kept; mix cells (digits and slashes) sum to 100; L15, L15a, L15b instalment cells exact; every LQ id in
   spec.dev kept; the first ui note starts "Example only:"; ASCII; no names, vendors or banned words. Pages: section
   ids and order, open_items, derived, table and row counts, link cells, and the story tables' columns
   ["n", "at", "seat", "screen", "action and result"] with their n, at, seat and screen cells exact.
3. Rebuild and republish the map artifact after the pass.

## Still open
- Owed by Vatsal: the role names (Principal officer 01, Logic analyst 01); whether a state is missing from the 39;
  vetoes of each screen's "Calls made while building (logic plan, 8 Oct 2026)" line; an explicit OK on check_logic.py's
  "LQ" plus digits scan (the no-pattern rule); the logic panel review date; word changes from Harish and Somil (a
  changed word goes into the glossary first, then one pass).
- At the merge into Wireframes v0.2: un-hide the Logic panel tab and its Changelog rows in scripts/build_site.py (TABS
  and the changelog sources).
- Small leftovers: W03 on the main board (the plan JSON contract) may still say cohort and portfolio; L05 keeps 10
  side-note lines.
- Later, not now: the architecture breakdown skill (memory architecture-breakdown-skill), built with a Workflow when
  Vatsal says.

## Constraints carried forward
- No edit to data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json, data/tracker.json,
  data/seed/, docs/seed/, docs/review/, docs/audiences/, inputs/, docs/config.js, docs/v01/.
- The glossary's words only; no regex or phrase rules in shipped code; stdlib only; ASCII; Rs; first names only;
  "to be decided: <item>", "to be verified: <item>", "gap, to be decided: <item>".
- Commits carry no AI attribution line; never push without Vatsal's word; keep the logic work off Spinach's review
  link until the merge.
- Untracked on purpose (never commit): inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/,
  inputs/spinach/2026-09-25/, the two inputs/meeting/ files, the two seed CSV zips at the repo root.
- Coding helpers run on opus at the least (memory opus-floor-for-coding). Replies: three bullets, plain words,
  top-down first (memory plain-words-first).
