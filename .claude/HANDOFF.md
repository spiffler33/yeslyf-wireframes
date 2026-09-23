# Handoff - 23 Sep 2026 (phase closed: seed phase A)

State: PLAN_admin_seed_v01.md phase A (seed/config.json, scripts/seed_gen.py, data/seed/run-500 and run-3000 with
report.md each) is committed and pushed; phases B to E wait for Vatsal's go.

## Read first
1. seed/PROGRESS.md: state, files, how the generator works, the open questions, what phase B needs.
2. PLAN_admin_seed_v01.md sections 12 to 18 (phase B onwards) and PLAN.md section 20.
3. data/seed/run-3000/report.md (read with head or sed; never load a full seed JSON or events.jsonl).

## Verify before coding
- `git status --short`: only the two untracked files in inputs/meeting/ (the docx and the Zoom transcript,
  untracked on purpose).
- `python3 scripts/seed_gen.py --anchor 2026-09-23`: "run-500: 507 people, 16272 events" and "run-3000: 3040
  people, 72371 events", and `git status` stays clean. Without --anchor the anchor is the run date: every date
  moves and every seed file changes. Regenerate on a new date only on purpose (demo morning), then commit it.
- `python3 scripts/check_phase9.py`: 19 PASS. `python3 scripts/check_site.py`: 3 PASS. `python3 scripts/build_site.py`
  leaves docs/ unchanged.

## Waiting on Vatsal
- The go for phase B. Silence on the phase A summary is consent for the seed plan decisions.
- Three questions: where the progress ring starts (at OTP per the seed plan, implemented; after the reveal per
  plan_v2 4.3 rule 11); DIFM = the S14 count, 8 people (3.8 percent), or raise S14 to 21 for 10 percent; the S16
  flag on the manual path plus the AA-failed fallback (37 percent) against the plan's about 30 percent.
- Two CLAUDE.md readings to confirm: synthetic customer names are allowed ("never invent a person's name" read as
  the team and reviewers); admin screens may show Harish as the DIFM owner ("no adviser named" read as app copy).

## Next, after the go
- Run B, C, D and E in sequence without stopping; one commit per phase with the plan section 18 messages; the
  one-line Tracker update at the end of each phase; seed/PROGRESS.md at every boundary and every subagent return.
- B: data/seed/<run>/exports/ (zoho/*.csv, desk/tickets.csv, campaigns/<stage>.csv, landing/landing_sheet.csv,
  fixtures/ with README.md), the minimisation scan (fails on a PAN pattern, a rupee value that is not a band label,
  a holding, an email outside example.com), docs/admin_operator.html with checkboxes on scripts/board_store.js.
  One subagent per export file, each given plan section 12, seed/config.json and data/seed/<run>/; check their
  files yourself.
- C: docs/admin_wireframes.html, M02 to M14 on the wireframes_v02 renderer (scripts/renderer_v02.js and .css),
  run switch 500 or 3,000, freeze marker open on every new screen; subagents in batches of three or four screens.
  GitHub Pages serves docs/ only, so the page needs the seed data copied into docs/ by build_site.py.
- D: docs/admin_seats.html and docs/admin_brief.html (two subagents). E: nav rows, changelog rows, tracker W12 and
  W13 lands_at, mixpanel JSONL.

## Constraints carried forward
- Money is "Rs ___" with a price key; included calls "N"; minutes "about N minutes" (CLAUDE.md wins over the plan's
  Amount columns). A Zoho currency field will not take "Rs ___" (to be verified): settle the Deals Amount column in B.
- Screens cite integrations by I-number; vendor names live in the data only.
- Do not touch existing pages except the nav rows in phase E; reuse the wireframes_v02 renderer and the
  board_entries write-back; standard library Python only; no network; seed 20260922.
- Never type into a live board page from spiff's Chrome; test on a local copy (port 8791; 8765 is taken).
- Events are 72,371 against the plan's estimate of about 150,000; not padded.
