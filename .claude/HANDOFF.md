# Handoff - 23 Sep 2026 (phase closed: seed plan phases B to E)

State: PLAN_admin_seed_v01.md is done (phases A to E, pushed). The board has one "Admin seed" tab leading to four
pages: admin_wireframes.html (M02 to M14 over a masked seed), admin_seats.html (99 questions: 38 answered, 61 gaps),
admin_brief.html (T1 to T6 plus the gap rows), admin_operator.html (the Zoho afternoon checklist).

## Read first
1. seed/PROGRESS.md: state, Vatsal's answers of 23 Sep 2026, decisions, files, how to regenerate.
2. PLAN.md section 21 (and section 20 for phase A).
3. data/seats.json when working on the brief (the seats judgment: surface, answered, gap, brief table).

## Verify before coding
- `git status --short`: only the two untracked files in inputs/meeting/ (the docx and the Zoom transcript,
  untracked on purpose).
- `python3 scripts/seed_gen.py --anchor 2026-09-23` then `python3 scripts/seed_export.py` then
  `python3 scripts/build_site.py`: "run-3000: 3040 people, 72398 events", both scans PASS, and `git status` stays
  clean (without --anchor every date moves; regenerate on a new date only on purpose, then commit it).
- `python3 scripts/check_phase9.py`: 19 PASS. `python3 scripts/check_site.py`: 3 PASS.

## Next
- Phase 13, the admin session (about 30 Sep 2026): walk the seats page and the brief with the team. Kajal runs the
  operator page on a Zoho One trial with the CSVs Vatsal sends via Drive (data/seed/<run>/exports/).
- Nothing goes to Spinach now. The fixtures zip (data/seed/<run>/exports/fixtures/yeslyf_seed_<anchor>_<run>.zip,
  gitignored, rebuilt by seed_export.py) is for Spinach's dev and staging databases once they build from the final
  brief; how and when it is sent is Vatsal's call.
- Seats answers and comments come back as board rows (pages admin_seats, admin_operator, admin_wireframes); read
  them with scripts/pull_board.py before changing data/seats.json.

## Constraints carried forward
- Nothing seed-related on the board beyond the masked admin bundle (phones "+91 9xxxx xx123", no PAN, dob or
  legal name); the build asserts it. No CSV linked from the board.
- The site build runs the minimisation scan and fails on a breach. No regex in shipped checks: exact membership
  against the seed's own values, stdlib parsers for types.
- Screens cite integrations by I-number (vendor names rendered from data/integrations.json); money "Rs ___";
  seats and roles by role, never people's names; CLAUDE.md wins over the plan.
- The header fits one more tab at 1,512 px; a second new tab pushes it to three rows and cuts into the wireframes
  layout (calc(100vh - 128px)).
- Test board pages only on a local copy of docs/ with config.js blanked (port 8791; 8765 is taken); docs/config.js
  holds the live key.
- data/changelog_seed.json holds the seed rows of the changelog (apply_decisions.py rewrites changelog.json whole).
