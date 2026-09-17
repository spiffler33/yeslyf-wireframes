# Phase 12, pass 3: the Tracker (17 Sep 2026)

Source: yeslyf_phase12_brief.md, pass 3 (3.1 to 3.5). Cause: minutes 16 Sep 2026, item 21; Vatsal, 17 Sep 2026.

## What changed

- 3.1 New tab "Tracker" after "Wireframes v0.2" on the site and on the review link (docs/tracker.html,
  docs/review/tracker.html; scripts/build_tracker.py from data/tracker.json). The "Owed to Spinach" table (W01 to
  W09) moved there with its saved rows: the Tracker writes under page "tracker" and reads the W rows written under
  page "integrations" as well (scripts/board_store.js init also), so the latest value and the History are whole.
  data/dependencies.json is removed; the Integrations tab keeps a one-line link. Fields: id, item, direction (HoA to
  Spinach, Spinach to HoA, HoA internal), owner, due date (with an "about" flag), status (not started, in progress,
  delivered, blocked), blocked by, source, lands at, notes. Edited on the page: owner, due, status, blocked by,
  notes; History under each row. Filters: direction, owner, status (plus overdue). Overdue rows read "overdue by N
  days" under the date; "due today" on the day.
- Milestone strip on top: 19 Sep 2026 (W03 and W04 due), 21 Sep 2026 (Spinach's questions session), about 23 Sep
  2026 (I00), about 30 Sep 2026 (admin panel, CRM and website session), every integrations row final (the date from
  the Integrations tab, "date not set" until it is). Past milestones read "(passed)"; the next one is outlined.
- 3.2 Seed rows W10 to W29 as in the brief; W01 owner Kajal, Raafiya with the note; W06 blocked by W19; W15 and W25
  delivered. Owners not named in the brief: W21 to W24 carry "Spinach" (the direction's sender); W27 and W28 stay
  empty as the brief says.
- 3.3 "Copy today's update": plain text from the last 24 hours of the board table plus the build data, copied to the
  clipboard and shown on the page (copy by hand where the clipboard is blocked). Sections, each dropped when empty:
  Delivered (status rows set to delivered in the last 24 hours), Now final (choice rows set to final in the last
  24 hours, or a seed whose final_since is within a day), Frozen and open (from the build; unfrozen screens from the
  log), Spinach questions (new and answered, with IDs), Overdue (owner and days; "none"), Next milestone, the board
  link. At most about 15 lines; check 19 fails the build past 15.
- 3.4 Spinach's questions: a list on the Tracker of every comment written under the identity Spinach (or "Spinach
  (name)") on any page, newest first: screen or row ID (linked), age, open or answered, the text, the answers under
  it. On the Wireframes v0.2 tab the same questions show under the comment box of their screen with an Answer box
  for every other identity; an answer is a new row on the screen (field "answer", kind comment, with who) and a
  question is answered once an answer row follows it. scripts/import_questions.py reads Ankur's Excel (screen ID,
  field, question; standard library only), dry run first, then --send writes one row per line under "Spinach
  (Ankur)" with field "question".
- 3.5 Identity: no write on any page without an identity; the page says "Pick who you are at the top first; nothing
  is recorded without a name." (in place since pass 1). Old rows show "(no identity)".
- Check 19: the Tracker validates (W01 to W29 in order, blocked_by resolves, milestone dates), renders on both navs
  after Wireframes v0.2, the daily update composes from the build data, the questions box is on the wireframes page,
  the owed table is gone from Integrations. 19 PASS.

## Counts

- Tracker rows: 29 (W01 to W29); 2 delivered, 1 in progress, 26 not started; overdue today: W09 (due 16 Sep 2026)
  and every row due 19 Sep 2026 once that passes.
- Board table: 12 rows, 4 ignored; no question from Spinach yet, so the list is empty and says so.

## Judgment calls

- Field names on the tracker rows are due_date, blocked_by, lands_at and source (the brief's prose names, in the
  repo's style).
- The question list treats a comment as a question by identity, not by wording: every comment under Spinach counts.
  Imported questions carry field "question" so the comment box is not overwritten by an import.
- The Tracker's pill reads the last write on the Tracker itself; the W rows written under the Integrations tab
  before the move show in History with their original time.
- The daily update names a delivered row by the first clause of its item (up to the first colon or semicolon),
  so the text stays short.
