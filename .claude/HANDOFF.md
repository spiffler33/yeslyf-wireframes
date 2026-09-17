# Handoff - 17 Sep 2026 (phase 12: corrections, frozen and final markers, tracker)

State: live. Three commits (pass 1 corrections, pass 2 markers, pass 3 tracker) on main; GitHub Pages serves them
once pushed. The review link (https://spiffler33.github.io/yeslyf-wireframes/review/) carries the Tracker tab, the
frozen marker on every screen, final or open on every integrations row, and Spinach's questions with answers.
19 checks pass. No build work is pending; the next unit is Spinach's questions session (21 Sep 2026) and the admin
session (about 30 Sep 2026, Phase 13).

## Read first
1. PLAN.md section 17 and plan_v2.md section 12 (the rules that hold from here on); reports/phase12_pass1.md,
   pass2.md, pass3.md (what shipped, the contradictions found in the brief and what was done about each).
2. data/v02/freeze.json (the freeze register: open screens with causes, the blocking items, the unfreeze log) and
   data/tracker.json (the W rows, the milestones, the board link).
3. scripts/board_store.js header (identity rule, the ignore list, read() and init({also})).
4. Memory: project_state, board-page-density (never restyle the wireframes page), review-transport-preferences,
   kajal-integration-stack, supabase-project.

## Verify before coding
- `git status --short` shows only the two untracked files in inputs/meeting/ (the docx and the Zoom transcript,
  left untracked on purpose).
- `python3 scripts/apply_decisions.py`: 194 live, 27 states, to be verified 30, to be decided 6; freeze register
  160 frozen, 34 open, 21 templates.
- `python3 scripts/build_site.py`: cross-check 25 rows clean; docs/ unchanged on a rebuild; docs/config.js untouched.
- `python3 scripts/check_phase9.py`: 19 PASS, no FAIL.
- `python3 scripts/pull_board.py`: 12 rows (4 test rows ignored) until the second round writes more.

## Waiting on spiff (one question each, from the reports)
- Pass 0: append section 7 to inputs/meeting/yeslyf_minutes_2026-09-16_spinach_walkthrough.md? inputs/ is read-only
  by CLAUDE.md; the text is ready in reports/phase12_pass1.md.
- L00 to L09: if the drawn table shapes are the W04 delivery, drop the ten L entries from data/v02/freeze.json open
  and rebuild (24 open, 170 frozen); log it as a cause, not as an unfreeze (they were never frozen).
- Owners not named by the brief: I24 (video vendor), W27, W28 are empty; I00 Harish and I23 Vatsal were taken from
  W19 and W11.

## What to do next
- Spinach's questions: when Ankur's Excel arrives, `python3 scripts/import_questions.py <file.xlsx>` (dry run),
  then `--send`; then `python3 scripts/pull_board.py`. Answers are typed in the Answer box on the screen (any
  identity but Spinach) and show on the Tracker.
- The daily update: open the Tracker, pick an identity, press "Copy today's update", paste into WhatsApp. Anyone
  can press it; the text is also shown on the page.
- A freeze status changes only by a commit: edit data/v02/freeze.json (move a screen between open and frozen, add
  an unfreeze_log entry with date, screen, cause, what changed), then apply_decisions, build_site, check_phase9.
- Phase 13 after the admin session: the Admin and CRM v0.2 page rebuilt against Zoho One (I14), the tool over the
  app database, lead stages and the fulfilment percentage (W26), the website brief. The CAS decision (W11) applied
  to A10, A10c, D02c, G12a when it closes.

## Constraints carried forward
- Every screen cites integrations by I-number; a vendor name on a screen fails the build (validate_v02.VENDOR_NAMES).
  The M01 Tool column and the spec panel's Integrations line are rendered from data/integrations.json.
- Every field entry carries a tag (required, optional, default, system, read); validate_v02 fails the build otherwise.
  Op "tags" for screens without inputs; op "forward" for screens with a Moving forward block.
- "to be decided: <item>" is the grammar for an open product decision on a screen; the item runs to the first ), ;
  or full stop outside its own brackets. A screen with such a line is open unless freeze.json lists the line under
  tbd_owed (X00's session rule, W21).
- No write to the board table without an identity. A write without a name is held in the browser (board_store.write
  returns false; the pill reads "N edits waiting for a name") and sent, stamped, once a name is picked (named(who);
  init({who, local}) also sends what the page shows and the table lacks; 17 Sep 2026). Test rows are keyed in
  data/board_ignore.json and dropped from every fetch, export and count.
- Costs stay off the board (the Integrations page is public); the field's hint says so and a value in the data is an
  error.
- Causes only ("brief X", "row N", "minutes 16 Sep 2026, item N", "<first name>, <date>"); no adviser named;
  "yeslyf" lowercase; "Rs"; no "recommendation" or "founders"; ASCII only; no em dashes. Owed rows W01.. never
  renumbered; statuses live in the table. Vendor facts stay "to be verified: <item>". Subagents: Opus is the floor.
- The wireframes page keeps its layout: the marks are words (open in the list, frozen or open in the header, the
  line in the marker box, a Frozen filter); reviewers have adjusted to the page (spiff, 17 Sep 2026).
