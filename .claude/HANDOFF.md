# Handoff - 8 Oct 2026 (run closed: PLAN_logic_panel_v03.md A0 to C2 built; stopped before phase D)

State: the logic panel side wireframes are built and committed on main, not pushed: the Logic tab (39 screens:
33 panel, 6 client views, data/logic_screens.json), the Tech, Access, Walkthroughs and Ops pages (data/logic_*.json,
scripts/build_logic_pages.py), the nine section 11 checks (scripts/check_logic.py, 9 PASS), the Logic panel tab on the
main board, the changelog rows and PLAN.md section 27. Every phase was reviewed and fixed before its commit. The plan
holds every push for phase D, Vatsal's look (PLAN_logic_panel_v03.md 12.13).

## Next action
Phase D is Vatsal's. The first decision, before any push: the review link's tracker links to three main-board
pages (admin_brief, admin_operator, spinach_questions) that now carry the Logic panel tab, so once pushed a
review-link reader is two clicks from the logic pages (PLAN.md section 27, "Open, phase D, before the push").

## Read first
1. PLAN.md section 27: what was built, the conventions the run pinned, the full phase D list, what people owe.
2. PLAN_logic_panel_v03.md 12.13 (phase D) and section 13 (the merge after acceptance).

## Verify before coding
- `git status --short`: only the seven untracked items listed below.
- `python3 scripts/build_site.py` (about 19 seconds), then `python3 scripts/check_phase9.py | grep -c PASS` -> 19,
  `python3 scripts/check_site.py | grep -c PASS` -> 3, `python3 scripts/check_logic.py | grep -c PASS` -> 9.

## Gotchas
- Logic content: a figure the plan does not type reads N or N% (no derived figure, ratio, formula or date); vendors
  only as {I..} tokens (the check is a substring one: SEBI is I00); the Access page and its data carry no first name.
- On L15, L15a and L15b cause tags take the colon form ("house view: REL02"): check 7 reads every bracketed cell there
  as an instalment.
- docs/logic_access.html's derived table reads data/logic_screens.json (roles and writes): rebuild the pages after any
  screen change. Run check_logic.py by hand after the build, like check_phase9.py.
- System python3 is 3.9.6.

## Constraints carried forward
- No edit to data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json,
  data/tracker.json, data/seed/, docs/seed/, docs/review/, docs/audiences/, inputs/, docs/config.js, docs/v01/.
  The logic work stays off the review link and the audience files until the merge (section 0).
- No regex or phrase rules (check_logic.py's "LQ" plus digits scan awaits Vatsal's explicit OK); stdlib only; ASCII;
  Rs; seats as actors, never a team name; "to be verified: <item>" and "to be decided: <item>" with no name.
- Commits "logic <phase>: ..."; no AI attribution line; never push without Vatsal's word.
- Untracked on purpose (never commit): inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/,
  inputs/spinach/2026-09-25/, the two inputs/meeting/ files, the two seed CSV zips at the repo root.
