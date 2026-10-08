# Handoff - 8 Oct 2026 (phase closed: A0 of PLAN_logic_panel_v03.md)

State: the /run-plan run of PLAN_logic_panel_v03.md is in flight (Vatsal's go, 8 Oct 2026). A0 is closed in the
commit "logic A0: the Logic tab builder, 39 stub screens and the open items file", not pushed (the plan holds every
push for phase D). The Logic tab exists: scripts/build_logic_wireframes.py, a stripped copy of the admin wireframes
builder, validates data/logic_screens.json (39 stubs, every ui []) and draws docs/logic_wireframes.html;
build_site.main() calls it after build_admin_split. data/logic_gaps.json holds LQ1 to LQ46. Next wave: A1 + B0,
under the orchestrator.

## Next action
The orchestrator runs the next wave: A1 (the start and logic groups, 14 screens, plan 12.2) and B0 (the page builder
and four skeleton pages, plan 12.6). Nobody starts a phase by hand while the run is in flight.

## Read first
1. PLAN_logic_panel_v03.md section 12 (12.0 the binding calls, 12.2 A1, 12.6 B0); sections 5 and 6 are the content.
2. scripts/build_logic_wireframes.py, validate_logic_screens(): the schema every A phase must pass (C1 calls it).

## Verify before coding
- `git status --short`: only the untracked items listed below.
- `python3 scripts/build_logic_wireframes.py` -> "logic wireframes: 39 screens (33 panel, 6 client views),
  validation PASS".
- `python3 scripts/build_site.py` (about 19 seconds), then `python3 scripts/check_phase9.py | grep -c PASS` -> 19 and
  `python3 scripts/check_site.py | grep -c PASS` -> 3.

## Gotchas
- spec.logic[0] and spec.logic[1] are derived lines: "Seats: ..." from role over the ten seats, "Writes: ..." from
  writes ("Writes: none" when empty). The builder rejects a stale line; add each write's event to events.
- The team-name check skips only the two cause fields (v02.causes, freeze.cause), which carry "Vatsal, 8 Oct 2026";
  a team name anywhere else fails the build.
- Every btn, btn2 and link in ui needs a target that is a logic or board screen id; a btn with no target fails.
- LQ22 lands on L14 as well (4.10), though 5.3 names it only in L14's checks line; LQ31 sits in L11's 5.3 open line
  but 4.10 lands it on L04 only.
- The renderer labels a "kept" screen "Kept from v0.1" (fixed text; no renderer change is allowed): L09, L07, L00.
- The subnav links to logic_tech.html, logic_access.html, logic_walk.html and logic_ops.html go nowhere until B0.

## Constraints carried forward
- No edit to data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json,
  data/tracker.json, data/seed/, docs/seed/, docs/review/, docs/audiences/, inputs/, docs/config.js, docs/v01/,
  scripts/build_admin_wireframes.py, scripts/renderer_v02.js or .css. Existing pages stay byte-identical (C2 alone
  changes the main nav).
- No regex or phrase rules; stdlib only; ASCII; Rs; seats as actors, never a team name; "to be verified: <item>" and
  "to be decided: <item>" with no name; vendors only as {I..} tokens. No network, no vendor call, nothing sent.
- Commits "logic <phase>: ..."; no AI attribution line; never push (phase D is Vatsal's).
- Untracked on purpose (never commit): inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/,
  inputs/spinach/2026-09-25/, the two inputs/meeting/ files, the two seed CSV zips at the repo root.
