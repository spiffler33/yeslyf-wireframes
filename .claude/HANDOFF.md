# Handoff - 9 Oct 2026 (the logic screens are in plain words; the zoomable map links them)

State: PLAN_logic_panel_v03.md phases A0 to C2 are built (c0011a7 to e320e9e). On 9 Oct 2026 the 39 logic screens
were rewritten in plain words (b1454d7), then cut harder: L02 and L05 first as the pattern Vatsal approved (79cc4ae),
then the other 37 the same way (b850320). A fact shared by every row is said once; bookkeeping columns and id lists
left the drawings; side notes keep only what happens on the screen; every moved fact sits in the screen's dev notes.
Nothing is pushed. The artifact "Logic panel in plain words" (https://claude.ai/artifact/4Pvm3fga2vJzSj8udHLsYS,
version 4) is the zoomable map: one line, six parts, rooms, details. Every screen id on it opens its drawing.

## Next action
Vatsal reads the map and the screens. Then, as he picks:
1. A further cut on any screen he names.
2. The same plain words on the four other pages (tech, access, walkthroughs, ops), which still use the old words.
3. Phase D: his look, the nav fold, the two questions, the push.
To rebuild the map: Artifact action "read" returns its full HTML, with the map content (TREE) and the screens
(SCREENS) embedded. Take TREE from it, rebuild SCREENS from data/logic_screens.json, and publish to the same URL.
The word list the screens now use is the map's "Word decoder" room.

## The map, in plain words (use this to explain; check details in the files only when asked)
- What it is: the logic panel is the back-office screen where two staff seats change the rules the app uses to build
  every client's plan (expected returns, which funds, which mix a goal gets) and send those changes out safely: a
  second person checks, clients are told the right amount, and every plan a client was shown is kept.
- Where it lives: a new "Logic panel" tab on the main board, with five pages linked to each other:
  1. Logic tab (docs/logic_wireframes.html): the drawings. 39 screens: 33 staff screens and 6 phone screens showing
     what a client sees. The main piece.
  2. Tech page (docs/logic_tech.html): what the engineers must build and store.
  3. Access page (docs/logic_access.html): who may do what, in one table.
  4. Walkthroughs page (docs/logic_walk.html): four example jobs told step by step (a yearly update; an urgent stop on
     a fund; a new client group; a mistake that is caught and fixed).
  5. Ops page (docs/logic_ops.html): what ops, the call centre and support do when a change goes out.
- Behind the pages: one data file per page (data/logic_screens.json, data/logic_tech.json, data/logic_access.json,
  data/logic_walk.json, data/logic_ops.json), two small builders that turn data into pages
  (scripts/build_logic_wireframes.py, scripts/build_logic_pages.py), and a check script (scripts/check_logic.py)
  that confirms the numbers add up and nothing is missing. Open questions: 46 numbered items (data/logic_gaps.json)
  plus 14 found while building.
- Every value on the pages is a made-up example, and the whole design is "proposed, to be confirmed".
- Where the complexity comes from (the simplification targets): coined terms (lanes, cohorts, releases REL01 to
  REL12, version ids like fu-2, rehearsal values, update sizes note/outlook/review/urgent, routes quiet/push,
  snapshots, sleeves, model portfolios MP1 to MP9, seats, LQ ids), the "(logic plan, 8 Oct 2026)" markers, long
  sentences, and no page that says what the five pages are and how they connect.

## Read first
1. Memory plain-words-first (how Vatsal wants this explained) and project_state.
2. PLAN.md section 27 only when asked for detail (status, conventions, the phase D list).

## Verify before changing anything
- `git status --short`: only the seven untracked items listed below.
- `python3 scripts/build_site.py`, then check_phase9.py 19 PASS, check_site.py 3 PASS, check_logic.py 9 PASS.

## Still open from the run (do not lose)
- Before any push: the review link's tracker links to three board pages that now carry the Logic panel tab, so a
  review-link reader would be two clicks from the logic work.
- Owed by Vatsal: whether the seats stay "Principal officer 01" and "Logic analyst 01"; whether a state is missing
  from the 39; vetoes of the "logic plan, 8 Oct 2026" calls; an explicit OK on check_logic.py's "LQ" plus digits scan
  (the no-pattern rule); the logic panel review date. Full list: PLAN.md section 27.

## Constraints carried forward
- No edit to data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json,
  data/tracker.json, data/seed/, docs/seed/, docs/review/, docs/audiences/, inputs/, docs/config.js, docs/v01/.
- No regex or phrase rules; stdlib only; ASCII; Rs; first names only; "to be verified: <item>" and
  "to be decided: <item>" with no name. Commits carry no AI attribution line; never push without Vatsal's word.
- Untracked on purpose (never commit): inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/,
  inputs/spinach/2026-09-25/, the two inputs/meeting/ files, the two seed CSV zips at the repo root.

## Later, not now: the architecture breakdown skill (Vatsal, 9 Oct 2026)
Vatsal wants the zoomable plain-words map (artifact "Logic panel in plain words",
https://claude.ai/artifact/4Pvm3fga2vJzSj8udHLsYS) turned into a reusable skill for learning any repo. He opted in to
building it with a Workflow, later: not before the logic panel language work is done and he confirms the timing.
Design notes: memory architecture-breakdown-skill.
