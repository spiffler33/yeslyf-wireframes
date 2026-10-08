# Handoff - 8 Oct 2026 (unit closed: PLAN_logic_panel_v03.md made run-ready; Vatsal said "go")

State: the logic panel plan (PLAN_logic_panel_v03.md: the side wireframes as data, the Logic tab, the Tech, Access,
Walkthroughs and Ops pages, the checks, the board links) is in the repo. Committed as written (0b2334c), then rebuilt
for /run-plan (f593131): phases A0 to C2 carry touches, steps, done-criteria as commands and the metadata line; D is
Vatsal's look (HUMAN-GATED). Vatsal said "go" on 8 Oct 2026 in the plan-ready session. Nothing of the plan is built.
The five calls the plan-ready pass made are in the plan's section 12.0 under the cause "logic plan, 8 Oct 2026";
Vatsal did not veto any.

Everything else is as the 7 Oct 2026 handoff left it: W12 delivered (the admin brief with Kajal's six M03 answers went
to Spinach on 7 Oct 2026); phase G (PLAN_zoho_live_v01.md) waits on a person for G1 (users) and G6 (Campaigns); gaps
G18, G20, G23 open. Owed by people: Kajal's team check on anything M03 misses; Spinach's reply and estimate on the
brief; the 1 Oct meeting notes.

Untracked on purpose in the tree (never commit): inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/, the
two inputs/meeting/ files, inputs/spinach/2026-09-25/, the two seed CSV zips at the repo root.

## Next action
`/run-plan PLAN_logic_panel_v03.md` - runs A0 to C2 unattended and stops at D (Vatsal's visual pass, the nav fold,
the two seat questions, the push). One commit per phase, no push by the executor.

## Read first
1. PLAN_logic_panel_v03.md section 12 (12.0 the calls made, 12.1 to 12.13 the phases); sections 5, 6 and 7 to 10
   are the content the phases transcribe.
2. Memory project_state (one paragraph on this unit) and spinach-admin-split for the admin side it must not touch.

## Verify before coding
- `git status --short`: clean apart from the untracked items above.
- `python3 scripts/build_site.py` (about 2 minutes), then `python3 scripts/check_phase9.py` 19 PASS and
  `python3 scripts/check_site.py` 3 PASS.

## Gotchas (the plan's section 12.0 has the rest)
- The board's wireframes builder cannot draw a second file; the Logic tab comes from a stripped copy of
  scripts/build_admin_wireframes.py (plan 12.0, A0).
- data/gaps.json's v02 list feeds docs/admin_brief.html section 5, the pack Spinach has; the LQ items go to
  data/logic_gaps.json and never to gaps.json.
- Content phases rebuild with their own builder only; the full build_site.py runs in A0, C1 and C2.
- Data formats: data/admin_crm.json, data/admin_split.json and data/gaps.json round-trip with json.dumps(indent=1)
  plus a newline; data/admin_screens.json, data/seats.json and data/integrations.json with indent=2; data/tracker.json,
  data/admin_pack.json and data/operator.json are hand-formatted.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends. No message reaches a seeded
  contact. No vendor call, no Zoho change in this plan.
- No regex or phrase rules; stdlib only; ASCII; Rs; first names; a cause on every change; "to be verified: <item>"
  and "to be decided: <item>" with no name attached. Secrets never in the repo; the seed CSV zips never in a commit.
- No edit to data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json,
  data/tracker.json, docs/review/, docs/audiences/, data/seed/, docs/seed/ or inputs/.
- Commits: "logic <phase>: ..." for this plan; "board: ..." and "zoho live G<N>: ..." stay separate; no AI
  attribution trailer.
