# Handoff - 17 Sep 2026, afternoon (closed: held edits, the folded spec panel, the ask, Raafiya)

State: live. Phase 12 closed at 12:24; four commits on top the same afternoon (080e6e2 held edits, 12b196e the
folded spec panel, a66e5df the rule text, e800ed9 the ask beside the name control, the sync fix, Raafiya). All
pushed; GitHub Pages serves them. 19 phase 9 checks and 3 site checks pass. No build work is pending; the next unit
is Spinach's questions session (21 Sep 2026) and the admin session (about 30 Sep 2026, Phase 13).

## Read first
1. PLAN.md section 18 (this afternoon) and section 17 (phase 12); plan_v2.md section 12 (the rules that hold).
2. scripts/board_store.js header: held edits, named(who), init({who, local}), the ask beside the name control.
3. Memory: project_state, board-page-density (the panel: depth is the lever, never the skin), supabase-project.

## Verify before coding
- `git status --short` shows only the two untracked files in inputs/meeting/ (the docx and the Zoom transcript).
- `python3 scripts/build_site.py`: docs/ unchanged on a rebuild; docs/config.js untouched.
- `python3 scripts/check_phase9.py`: 19 PASS. `python3 scripts/check_site.py`: 3 PASS.
- `python3 scripts/pull_board.py`: 29 rows, 16 test rows ignored (data/board_ignore.json has 11 entries), then
  `git checkout -- data/board_entries.json` (the pull rewrites the tracked file).

## Waiting on others
- Kajal: reload the Integrations tab and pick "Editing as Kajal"; the held edits then land. Check with pull_board.py
  that rows under page integrations carry who Kajal before treating the fix as proven with a real user.
- Rows 15 to 17 (I00 SEBI status "in talks" and choice "final", I01 Finvu status "in talks", who Vatsal, 13:50) were
  spiff's own unrecorded edits re-sent by the first sync; spiff to say if any is wrong.
- Should the review link (docs/review/) run the lighter Spinach panel (no causes, no compliance flag)? Today it runs
  the full panel; only docs/audiences/yeslyf_v02_spinach.html hides both.
- Still open from phase 12: the minutes append (Pass 0, inputs/ is read-only), the L00 to L09 freeze with W04, the
  CAS decision (W11) for A10, A10c, D02c, G12a, owners for I24, W27, W28.

## What to do next
- Spinach's questions: `python3 scripts/import_questions.py <file.xlsx>` (dry run), then `--send`; then pull_board.
- Phase 13 after the admin session: the Admin and CRM v0.2 page against Zoho One (I14), the tool over the app
  database, lead stages and the fulfilment percentage (W26), the website brief.

## Constraints carried forward
- Never type into a live board page from spiff's Chrome to test: a held or named edit there is a real row. Test on a
  local copy (serve docs/ on a free port; 8765 belongs to another process on this machine, 8791 worked) and clear
  that origin's localStorage after.
- A write without a name is held, never dropped; the sync on name compares against every fetched row, test rows
  included, and only after the table is read. Test rows are keyed by page, item and UTC minute in
  data/board_ignore.json; the table is append-only, so an unwanted row is ignored, never deleted.
- The wireframes page keeps its skin and layout; what changes is depth: words in existing places, folds with a
  count, the marker box, one more select in the bar (spiff, 17 Sep 2026).
- Reviewer identities: Bhuvanaa, Harish, Gaurav, Kajal, Somil, Raafiya, Vatsal, Spinach, Compliance (the team
  audience file lists eight, without Vatsal). Causes only; no adviser named; "yeslyf" lowercase; "Rs"; ASCII; no
  em dashes; vendor facts stay "to be verified: <item>". Every screen cites integrations by I-number.
- The node tests for the store (hold, named, sync, the ask) lived in the session scratchpad and are not in the repo.
