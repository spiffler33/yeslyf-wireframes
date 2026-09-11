# Handoff - 11 Sep 2026 (phase closed: wireframes v0.2, plan_v2.md phases 3 to 8)

State: v0.2 is built, checked, live and closed; the next unit of work is the second review round (comments
exported to spiff from the v0.2 tab) and the CRM planning session off the CRM backlog. No build work is pending.

## Read first
1. `PLAN.md` section 13 (status, 10 and 11 Sep 2026) plus sections 1 to 6 (repo, data layer).
2. `plan_v2.md` (the brief that ran) for the rules every v0.2 screen follows; `data/changelog.json` for what
   changed and why (`docs/changelog.html` is its page).
3. Memory `yeslyf-product-board` (build layering, decisions, open items).

## Verify before coding
- `git status --short` is empty; HEAD is the closure commit of 11 Sep 2026.
- `python3 scripts/apply_decisions.py` rewrites `data/screens_v02.json` and `data/changelog.json` unchanged
  (188 live screens, 21 templates); `python3 scripts/validate_v02.py` prints seven PASS lines.
- `python3 scripts/build_site.py` rewrites docs/ unchanged; `python3 scripts/check_site.py` prints three PASS
  lines; `git status --short` is still empty afterwards.

## What to do next
- Second review round: the team, Spinach and the compliance reviewers comment on the Wireframes v0.2 tab
  (identity select: the five first names, Spinach, Compliance) and press Export comments; spiff receives the
  markdown. No Apps Script change (spiff, 11 Sep 2026); do not raise the v02_comments tab again.
- When the exported comments arrive: parse them into data (never docs/), dispositions with causes, then rerun
  the four scripts and commit per phase.
- CRM planning session: the Admin and CRM v0.2 tab, CRM backlog section.

## Constraints carried forward
- inputs/ is read-only; docs/ is generated; docs/v01/ stays byte-identical to inputs/v01/.
- Screen IDs are permanent; dropped screens keep their ID with a pointer (R11, G02, G08, D05, D06, D08).
- v0.2 pages carry causes only (brief item, review row, or "Vatsal, 10 Sep 2026"); no adviser named on any
  screen; "yeslyf" lowercase; "Rs"; "N calls"; "about N minutes"; "Rs ___"; no "recommendation" or "founders".
- The frozen Meeting, Gaps and Inputs tabs keep their v0.1 content; new gaps go under the v02 key of
  data/gaps.json; meeting outcomes sit on inputs.json rows as a "meeting" field, statuses untouched.
- Every edit op in the data layer matches an exact existing string and stops the build if it is not found;
  `UNTIL_PHASE=4 python3 scripts/apply_decisions.py` builds without the phase 5 files.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026).
- Secrets stay out of the repo (.local/sheet.json); the Pages site is noindex and shared by URL only.
