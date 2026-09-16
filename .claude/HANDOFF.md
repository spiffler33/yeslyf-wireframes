# Handoff - 16 Sep 2026 (phase closed: E10 and E11 on the execution screens)

State: wireframes v0.2 is live with 193 screens and 21 templates. E10 SIP mandate registration and E11 Set up monthly
SIPs were added on 16 Sep 2026 (cause "Kajal, 16 Sep 2026"; commit 232a15c), E01, E02 and E03 wired to them, pushed
and confirmed on the review link. No build work is pending; the next unit is the second review round.

## Read first
1. plan_v2.md section 10 (what E10 and E11 are, the wiring, the flow order), then PLAN.md section 14 (status bullets
   of 11 and 16 Sep 2026).
2. data/v02/sip_mandate_edits.json: the pattern for adding screens (one edit group in a data/v02 file with "edits" in
   its name; new ids also go into data/v02/flow.json or the build stops with "flow.json lacks").
3. Memory project_state (constraints the repo does not state: Opus floor, no Apps Script change, M2 absent, causes can
   name Kajal when spiff says so).

## Verify before coding
- `git status --short` is empty; HEAD is the closure commit after 232a15c.
- `python3 scripts/apply_decisions.py` prints "screens: 193 live ... templates: 21" and leaves data/screens_v02.json
  and data/changelog.json unchanged; `python3 scripts/build_site.py` leaves docs/ unchanged; `git status --short`
  is still empty afterwards.
- `python3 scripts/check_phase9.py` prints 17 PASS lines and no FAIL.

## What to do next
- Second review round on the review link (https://spiffler33.github.io/yeslyf-wireframes/review/): reviewers press
  Export comments and the markdown goes to spiff. No Apps Script change; do not raise the v02_comments tab.
- When the exported comments arrive: parse them into data (never docs/), dispositions with causes ("<first name>,
  <date>" or "row N"), a new edit group under data/v02 (groups with "stage": "after_generation" may touch generated
  screens), then rerun apply_decisions, build_site and check_phase9; commit per phase and push.
- Then the CRM planning session: the Admin and CRM v0.2 tab, CRM backlog section.

## Constraints carried forward
- inputs/ is read-only; docs/ is generated; docs/v01/ stays byte-identical to inputs/v01/.
- Screen IDs are permanent; the next free id in section E is E12. Dropped: R11, G02, G08. Split: D05, D06, D08.
- v0.2 pages carry causes only ("brief X", "row N", "<first name>, <date>"); no adviser named; "yeslyf" lowercase;
  "Rs"; "N calls"; "about N minutes"; "Rs ___"; no "recommendation" or "founders"; "assumed" on D07b only.
- No client-data fallback assumptions: bands are fixed per field; a missing number is asked for (D13), never assumed.
- Unverified vendor facts are written "to be verified: <item>" (E10 and E11 carry three; plan_v2.md appendix E lists
  them). A product gap is "gap, to be decided" under the v02 key of data/gaps.json.
- Every edit op matches an exact existing string and stops the build if it is not found.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026).
- Secrets stay out of the repo (.local/); the Pages site is noindex and shared by URL only.
