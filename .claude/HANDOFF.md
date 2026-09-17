# Handoff - 17 Sep 2026 (light close: mandatory and optional inputs; phase 11 Supabase write-back before it)

State: live. Every comment, verdict and field edit on every page is one row in the Supabase table board_entries;
the review link (https://spiffler33.github.io/yeslyf-wireframes/review/) shows "live, last write <time>" and every
device sees every row after a reload. Commits 0dd4af0 to the closure commit are pushed; GitHub Pages serves them.
No build work is pending; the next unit is the second review round.

## Read first
1. PLAN.md section 15 (what shipped, the row conventions per page, the known limitations, the live checks).
2. scripts/board_store.js (the shared layer; its header comment explains init, write, history, attach, the outbox
   and the pill) and supabase/migrations/20260916120000_board_entries.sql (table, policies, revokes).
3. Memory project_state, review-transport-preferences (why Supabase, what is recorded) and supabase-project (the
   project and its database password; the site never uses the password).

## Verify before coding
- `git status --short` is empty; HEAD is 628b6d3 or later (mandatory and optional inputs; PLAN.md section 16).
- `python3 scripts/apply_decisions.py` rebuilds data/screens_v02.json unchanged: 193 live, 79 screens with spec.forward.
- `python3 scripts/build_site.py` leaves docs/ and data/ unchanged and never touches docs/config.js.
- `python3 scripts/check_phase9.py` prints 17 PASS lines and no FAIL.
- `python3 scripts/pull_board.py` prints "wrote data/board_entries.json: N rows, ..." (N >= 3: the setup TEST probe
  and the A02 test rows by Kajal are in the table by design; it is append-only).

## What to do next
- 17 Sep 2026: every input screen carries a "Moving forward" block and field tags (required, optional, default,
  system); rule set in plan_v2.md section 11. The developers have the note. Any new input screen needs both or
  validate_v02.py fails the build; a new number screen gets them from gen_spine.py, anything else via op "forward"
  in an after_generation edit group that sorts after phase9_edits.json.
- Second review round: spiff shares the review link; reviewers pick an identity and comment; their rows land as they
  type. Owners set status and dates on the Integrations tab and the Owed to Spinach rows (W07, W08, W03, W04 due
  19 Sep 2026). Export comments and Export brief stay as the offline record only.
- When the round is done: `python3 scripts/pull_board.py`, then parse data/board_entries.json (the "latest" block:
  last row per page, item and field) into data (never docs/) with causes ("<first name>, <date>" or "row N"), a new
  edit group under data/v02, then apply_decisions, build_site, check_phase9; commit per phase and push. Skip item
  TEST; treat the A02 Keep by Kajal as a test unless Kajal confirms it.
- Then the CRM planning session (Admin and CRM v0.2 tab, CRM backlog section).

## Constraints carried forward
- The word "assumed" is banned outside D07b (check 12) and the execution vendor is always "smallcase Gateway",
  never bare "smallcase" (Vatsal, 16 Sep 2026); frozen tabs and v0.1 records keep their original wording.
- inputs/ is read-only; docs/ is generated except docs/config.js (hand-filled, never overwritten); docs/v01/ stays
  byte-identical to inputs/v01/. build_site.py calls build_integrations.py, then build_events.py, at the end.
- Every new editable control on any page calls yeslyfBoard.write (spiff, 16 Sep 2026: any manual input is recorded);
  filters, sorting and the identity picker are not rows. Rows are never updated or deleted; a correction is a new row.
- The layer sends the key in the apikey header only (a publishable key is refused in Authorization). The anon key in
  docs/config.js is public by design; RLS is the guard. No service key, no database password in the repo.
- Values saved in a browser before phase 11 show until a remote row exists for that field; they are not uploaded by
  themselves. The outbox is sent on the next page load only.
- v0.2 rules: causes only ("brief X", "row N", "<first name>, <date>"); no adviser named; "yeslyf" lowercase; "Rs";
  no "recommendation" or "founders"; ASCII only; no em dashes. Owed rows W01.. never renumbered; statuses live in
  the table, not in data. Vendor facts stay "to be verified: <item>"; every new number stays a placeholder.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026). Page density: a board page reads as a calm list
  first, editing behind a click. Setup guidance for spiff: one small step at a time.
