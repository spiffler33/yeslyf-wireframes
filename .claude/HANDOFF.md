# Handoff - 10 Sep 2026 (phase closed: wireframes v0.2, plan_v2.md phases 3 to 8)

State: v0.2 is built, checked and live. The next unit of work is the second review round (the team, Spinach and
the compliance reviewers comment through the v0.2 tabs; rows land on the v02_comments sheet tab once spiff
redeploys the Apps Script) and the CRM planning session (Admin and CRM v0.2 tab, CRM backlog section).

## Read first
1. `plan_v2.md` (the brief that was run) and `CLAUDE.md` v2 (the rules; v0.2 pages carry causes, never owner
   markers or names on callouts).
2. `PLAN.md` section 13 (status) plus sections 1 to 6 (repo, data layer).
3. `data/changelog.json` for what changed and why; `docs/changelog.html` is its page.

## Verify before coding
- `git status --short` is empty; HEAD is the v0.2 final commit.
- `python3 scripts/apply_decisions.py` rebuilds `data/screens_v02.json` and `data/changelog.json` unchanged
  (188 live screens, 21 templates); `python3 scripts/validate_v02.py` prints seven PASS lines.
- `python3 scripts/build_site.py` rewrites docs/ byte-identical; `python3 scripts/check_site.py` prints three PASS
  lines; `git status --short` is still empty afterwards.
- `cmp inputs/v01/yeslyf_wireframes_v0.1.html docs/v01/yeslyf_wireframes_v0.1.html` is silent, same for the
  admin file.

## How the build is layered (edit data, never docs/)
- v0.1 skeleton (`data/screens_v01.json`, never edited) -> `data/screen_meta_v02.json` (template, path, compliance,
  events per carried screen) -> `data/decision_effects.json` groups in order (brief items, then the section 0
  overrides, then CLAUDE.md wording) -> `data/v02/*edits*.json` groups (phases 4 to 6) -> `data/v02/screens_*.json`
  full screens -> generated instances (`scripts/gen_spine.py` over `data/v02/spine.json`; `scripts/gen_states.py`
  over `data/v02/states.json`) -> `data/v02/flow.json` order -> events by template -> validation -> write.
- Every edit op matches an exact existing string and stops the build if it is not found. Every screen carries
  v02.status and v02.causes; the changelog derives from them.
- `UNTIL_PHASE=4 python3 scripts/apply_decisions.py` builds without the phase 5 files (used for the phase commits).

## Constraints carried forward
- inputs/ is read-only; docs/ is generated; docs/v01/ stays byte-identical to inputs/v01/.
- Screen IDs are permanent; dropped screens keep their ID with a pointer (R11, G02, G08, D05, D06, D08).
- No adviser is named on any screen; "yeslyf" lowercase; "Rs"; "N calls"; "about N minutes"; "Rs ___".
- The frozen Meeting, Gaps and Inputs tabs keep their v0.1 content; new gaps go under the v02 key of
  data/gaps.json; meeting outcomes sit on inputs.json rows as a "meeting" field, statuses untouched.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026).
- Secrets stay out of the repo (.local/sheet.json); the Pages site is noindex and shared by URL only.

## Open items
- spiff: redeploy the Apps Script web app once (Deploy, Manage deployments, edit, new version) so the
  v02_comments tab receives rows; until then v0.2 comments land on the "other" tab as JSON payloads.
- The to-be-verified list (24 items) and gaps G14 to G16 are on the Changelog tab.
- The FP React analysis found the component crashes on any missing money field; branch B is recorded in
  data/fp_react_inputs.json for the developers.
