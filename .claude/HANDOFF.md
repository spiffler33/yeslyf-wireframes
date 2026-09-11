# Handoff - 11 Sep 2026 (phase closed: wireframes v0.2 phase 9)

State: phase 9 (no client-data assumptions, seven data-capture improvements, split status, three audience files)
is built, checked, committed, pushed and live; the next unit of work is the second review round on the audience
files, then the CRM planning session. No build work is pending.

## Read first
1. `PLAN.md` section 14 (status, 11 Sep 2026), then section 13 and sections 1 to 6 (repo, data layer).
2. `plan_v2.md` section 9 (what phase 9 superseded in 4.2 and 4.3) and `data/changelog.json` (what changed and
   why; `docs/changelog.html` is its page, with the split section and the audience files).
3. Memory `project_state` (constraints the repo does not state: Opus floor, no Apps Script change, M2 absent).

## Verify before coding
- `git status --short` is empty; HEAD is the phase 9 closure commit of 11 Sep 2026.
- `python3 scripts/apply_decisions.py` rewrites `data/screens_v02.json` and `data/changelog.json` unchanged
  (191 live screens, 21 templates, dropped 3, split 3); `python3 scripts/build_site.py` rewrites docs/ and
  docs/audiences/ unchanged; `git status --short` is still empty afterwards.
- `python3 scripts/check_phase9.py` prints 17 PASS lines (checks 1 to 10 of plan_v2.md section 7, then 11 to 17).

## What to do next
- Second review round: send the audience files (docs/audiences/yeslyf_v02_team.html for the team, seven
  identities; yeslyf_v02_spinach.html locked to Spinach; yeslyf_v02_compliance.html locked to Compliance, 107
  flagged screens). Each opens from disk; reviewers press Export comments and the markdown goes to spiff. No Apps
  Script change (spiff, 11 Sep 2026); do not raise the v02_comments tab again.
- When the exported comments arrive: parse them into data (never docs/), dispositions with causes
  ("Vatsal, <date>" or "row N"), a new edit group in data/v02 (groups with "stage": "after_generation" may touch
  generated screens), then rerun apply_decisions, build_site and check_phase9 and commit per phase.
- CRM planning session: the Admin and CRM v0.2 tab, CRM backlog section.

## Constraints carried forward
- inputs/ is read-only; docs/ is generated; docs/v01/ stays byte-identical to inputs/v01/.
- Screen IDs are permanent. Dropped: R11, G02, G08 (pointer each). Split: D05, D06, D08 (instances listed).
- v0.2 pages carry causes only (brief item, review row, "Vatsal, 10 Sep 2026" or "Vatsal, 11 Sep 2026"); no adviser
  named; "yeslyf" lowercase; "Rs"; "N calls"; "about N minutes"; "Rs ___"; no "recommendation" or "founders".
- No client-data fallback assumptions: bands are fixed per field; a missing number is asked for (D13), never
  assumed; the word "assumed" lives on D07b only (CLAUDE.md, last line of What not to do).
- The frozen Meeting, Gaps and Inputs tabs keep their v0.1 content; new gaps go under the v02 key of
  data/gaps.json (G17 open: which fields have an M2 band table; M2 is not in inputs/).
- Every edit op matches an exact existing string and stops the build if it is not found.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026).
- Secrets stay out of the repo (.local/sheet.json); the Pages site is noindex and shared by URL only; no sheet
  endpoint string in any file (the audience files carry a blank endpoint field).
