# Handoff - 8 Oct 2026 (run in flight: PLAN_logic_panel_v03.md under /run-plan; A0 to C1 closed)

State: /run-plan of PLAN_logic_panel_v03.md is in flight (Vatsal's go, 8 Oct 2026; paused twice at his ask and
resumed). Closed and committed, not pushed: A0 to A4 (39 screens, each after review fixes), B0 to B4 (the page
builder and the Tech, Access, Walkthroughs and Ops pages), C1 (scripts/check_logic.py, the nine section 11 checks,
9 PASS). Next: C2 (the Logic panel tab, the changelog rows, PLAN.md section 27), then the run stops before phase D,
Vatsal's look. The plan holds every push for phase D.

## Next action
If the session died: `/run-plan PLAN_logic_panel_v03.md` resumes at C2 (the only unticked phase before D).

## Read first
1. PLAN_logic_panel_v03.md section 12 (12.0 the binding calls; the ticks show what is closed).
2. scripts/build_logic_wireframes.py validate_logic_screens() and scripts/build_logic_pages.py's docstring: the two
   schemas every content phase must pass.

## Verify before coding
- `git status --short`: only the untracked items listed below, plus whatever an in-flight phase left.
- `python3 scripts/build_logic_wireframes.py` -> "... validation PASS"; `python3 scripts/build_logic_pages.py` ->
  "logic pages: 4 built".
- `python3 scripts/build_site.py` (about 19 seconds) only when no phase is in flight, then check_phase9.py 19 PASS and
  check_site.py 3 PASS.

## Gotchas
- The Access page's derived table reads data/logic_screens.json (roles and writes), so every A phase changes
  docs/logic_access.html: rebuild the pages and commit it with the A phase.
- Vendors only as {I..} tokens, and the check is a substring one: SEBI is I00, AWS I17, FCM I12; "Accordingly" trips
  I05 "Accord". The Access data file carries no first name, causes included (section 8).
- Walkthrough tables (B3): the "at" cell must parse as "10 Mar 2028" and the seat cell must be a seat or "-"
  (12.0, C1 checks 4 and 5); section 9 types times, "the system", clients and two seats in some cells.
- System python3 is 3.9.6: no 3.10+ syntax.

## Constraints carried forward
- No edit to data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json,
  data/tracker.json, data/seed/, docs/seed/, docs/review/, docs/audiences/, inputs/, docs/config.js, docs/v01/,
  scripts/build_admin_wireframes.py, scripts/renderer_v02.js or .css. Existing pages stay byte-identical (C2 alone
  changes the main nav).
- No regex or phrase rules; stdlib only; ASCII; Rs; seats as actors, never a team name; "to be verified: <item>" and
  "to be decided: <item>" with no name. No network, no vendor call, nothing sent.
- Commits "logic <phase>: ..."; no AI attribution line; never push (phase D is Vatsal's).
- Untracked on purpose (never commit): inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/,
  inputs/spinach/2026-09-25/, the two inputs/meeting/ files, the two seed CSV zips at the repo root.
