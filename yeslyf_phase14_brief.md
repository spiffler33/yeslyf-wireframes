# yeslyf board - Phase 14 brief: the Spinach Questions tab (SQ1)

Written 24 Sep 2026 for Claude Code. Sources: the three questionnaire files Spinach sent on 22 Sep 2026, the answer
set SQ1_answers.md (Vatsal, 24 Sep 2026), the board as built at commit 36b9ba0, the minutes of 16 Sep 2026 and
Vatsal's decisions of 24 Sep 2026. If the number 14 is already taken by the admin work, renumber this phase; the
content does not change.



Five passes, one commit each, in this order: Pass 0 inputs, Pass 1 data, Pass 2 board corrections, Pass 3 the tab,
Pass 4 the export. Pass 5 (applying approvals) is described here but runs later, on instruction.

## 0. Read me first

### Why this phase exists
Spinach sent three questionnaires (frontend, backend, journey description) with a "Yesly Comments" column and
asked for answers at the earliest, in their format, as the baseline for every questionnaire that follows. HoA
answers on the board so there is one copy: every row is on a new tab with a status (frozen, open, owed), the
team approves the open rows on the page, a commit freezes them, and the board exports the three files back in
Spinach's own layout with the comments column filled. The next questionnaire takes the same route as SQ2.

### Standing rules (unchanged, restated)
- Every change carries a cause and nothing else. Causes used in this phase:
  - "Vatsal, 24 Sep 2026"
  - "Spinach proposal SQ1, accepted, Vatsal, 24 Sep 2026"
  - "Vatsal, 17 Sep 2026 (vendor choices final); recorded 24 Sep 2026"
  - later, per approval: "approved by <first name>, <date>" or "delivered by <first name>, <date>"
- Status vocabulary is the board's three words: frozen, open ("to be decided: <item>"), owed ("to be verified:
  <item>"). No fourth word anywhere on the tab or in the export.
- Unconfirmed vendor or regulatory facts are written "to be verified: <item>", no name attached.
- First names only on the Tracker and in comment histories; function labels in the owner column of the tab
  (Product, Tech, Admin, Compliance, Financial planning, Investment advisory, Copy, Team session (30 Sep 2026),
  Spinach). ASCII only. The brand is yeslyf, lowercase. Rs, never the rupee symbol. Plain hyphens.
- Never write "recommend" or "recommendation" on a v0.2 page. The answer set does not use the word; keep it out
  of the page chrome too.
- inputs/ is read-only. data/*.json is the single source of truth; pages and exports are generated; never
  hand-edit docs/.
- Do not change the text of any answer, status, owner or date in the answer set. If something in it looks wrong
  (an id that does not exist, a ref that does not resolve), stop and report; do not fix it silently.
- Existing screen IDs, state IDs, event names and W numbers never change. New W rows continue the series.
- The board table (board_entries) is append only. This phase writes no rows to it by script.
- After each pass: rebuild the site, the /review/ copy and the three audience files; run the validation scripts.
- Commit after every pass; the message says what changed and why.

### Decisions this brief carries (Vatsal, 24 Sep 2026)
1. The answers in SQ1_answers.md stand as written. Frozen rows are final; open and owed rows carry the owner and
   the date given there. The cause per row follows the rule in that file's header.
2. Vendor choices declared final on 17 Sep 2026 that never reached the data: I05 Accord, I08 Gupshup, I09 Razorpay,
   I12 FCM are final since 17 Sep 2026.
3. I13 is Mixpanel, final since 24 Sep 2026 (FE-60). Journeys and nudges stay in Zoho Campaigns and Flow, FCM and
   WATI.
4. The corporate RIA registration with SEBI is granted. I00 and W19 are delivered.
5. Approval on the tab is a comment under a person's identity; the status changes only by a commit (the freeze
   register rule). The freezing commit writes "approved by <first name>, <date>" as the cause.
6. Exports go out in two batches: batch 1 the day this phase lands (open rows marked open), batch 2 after the open
   rows are frozen (expected after the 30 Sep 2026 session). Every re-export marks the rows changed since the
   previous export.
7. Vendor documentation is already with Spinach (Kajal and Raafiya). Nothing in this phase adds documentation
   tasks; W16 is not touched.

## Pass 0. Inputs

- Create inputs/spinach/2026-09-22/ and place, unchanged: the three xlsx files with their original names
  (2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx, Yesly_Backend_Clarifications_Questionaire.xlsx,
  2026_Sep_22nd_Yesly_Journey_Description.xlsx) and SQ1_answers.md. Vatsal supplies the four files; if any is
  missing, stop and say which.
- Add one line to inputs.json (or wherever the Inputs tab reads its list) for the batch: "Spinach questionnaire
  SQ1, received 22 Sep 2026, three files, answered 24 Sep 2026". The frozen Inputs tab content itself is not
  edited; if the Inputs tab is frozen at the data level too, put the line in the Changelog only and say so.
- Check every file's real type with `file` before parsing (standing discipline).

## Pass 1. Data: data/questions.json

### 1.1 The importer
scripts/import_sq.py reads the three xlsx files with the standard library, the way scripts/import_questions.py
does (zipfile plus XML; reuse its read_sheet), reads SQ1_answers.md, and writes data/questions.json. Dry run by
default (prints every row it would write and every problem); `--write` writes after a clean dry run only. No
new dependencies.

### 1.2 The id scheme (from the answer set; do not invent others)
- Frontend main sheet: FE-01 to FE-80, from the Sr No column.
- Frontend supplementary sheets, by sheet and Sr No: Foundation FE-F1 to FE-F6; Navigation FE-N1 to FE-N6;
  Conectivity FE-C3 and FE-C4 (the sheet starts at 3); Performance FE-P1 to FE-P6; Security FE-S1 to FE-S6;
  Native Device Features FE-D1 to FE-D5; CI_CD FE-R1 to FE-R5; Analytics & Monitoring FE-M1 to FE-M4;
  Integrations FE-X1 to FE-X5 (the sheet numbers two rows 5: the first, guided lookup, is FE-X4; the second, SES,
  is FE-X5; match by order); Open Decisions FE-O1 to FE-O4.
- Backend sheet: BE-01 to BE-15, in row order (the header row is "Question, Comments").
- Journey file: JD-SUM-1 to JD-SUM-5 (the five journey rows of the summary sheet; the answer applies to the
  "Key open area" cell); then per journey sheet: JD-LOGIN, JD-REVEAL, JD-PAY, JD-ONB, JD-AA, with blocks W
  (the rows after the "Screen / Step" header up to "Detailed Edge Cases"), E (the rows after the "Edge Case"
  header up to the screen-sequence or API block), API (the rows after "API ID", AA sheet only), M (the
  "Recommendation" row of the screen-sequence block), H1 (ONB only: the header block as one item).
- Every journey row in the answer set quotes its opening words in the "row" column. The importer asserts that
  the sheet row begins with the same first three words (case-insensitive, punctuation ignored). A mismatch stops
  the import with the sheet, the row number and both strings. Do not remap by guesswork.
- Two table layouts in the answer set: the FE, BE and JD-SUM tables have five columns (id, status, comment, refs,
  owner and due); the five journey tables (LOGIN, REVEAL, PAY, ONB, AA) have six (id, row, status, comment, refs,
  owner and due). JD-SUM rows match the summary sheet's journey rows by order (Login, Reveal, Paywall,
  Onboarding, Account Aggregator).

### 1.3 The row record
questions.json: {source, note, batches: [{id: "SQ1", received: "2026-09-22", answered: "2026-09-24", files:
[...]}], rows: [...], templates: [...], route_groups: [...]}.

Each row: id; batch; file (original file name); sheet (original sheet name); sheet_order (1-based sheet index
so the export rebuilds the workbook in order); block (main, W, E, API, M, H, or empty); row_no (1-based row in
the sheet, for the export); area (the sheet's Area or Decision column when it has one); question (their text,
verbatim); proposal (their Best Practise or Best Practice cell, verbatim; empty for the backend sheet); link
(their Link or Doc Link cell, verbatim); answer (the Yesly comment, verbatim from the answer set); status
(frozen, open, owed); refs (a list of ids, parsed from the refs column, comma separated; "Part D" and "Part E"
stay as written); owner (the function label, open and owed rows only); due (yyyy-mm-dd or empty); due_about
(true when the answer set says "no date" or a date is a proposal: all dates in SQ1 are proposals); cause (a
list; frozen rows get one entry by the header rule: an answer that begins "Accepted as proposed" gets the
accepted cause, every other frozen row gets "Vatsal, 24 Sep 2026"; open and owed rows get an empty list);
tracker (the W ids among the refs); changed (the date the row's answer or status last changed; "2026-09-24" for
every row now); exported (the date of the last export that carried the row's current state; empty until Pass
4 runs).

templates: Part D of the answer set as rows {template, screens, back, loading, keyboard, validation}.
route_groups: Part E as rows {group, screens, who, rule}.

### 1.4 Validation (the build fails on any of these)
- Every sheet row that carries a Sr No, a question or a journey row lands on exactly one id, and every id in the
  answer set matches exactly one sheet row. Report the counts per sheet.
- Every row has a status from the three words. An open or owed row has an owner. A frozen row has one cause.
- Every ref resolves: a screen id in data/screens_v02.json (live screens only), a state id in data/v02/states.json,
  an I row in data/integrations.json, a W row in data/tracker.json (after Pass 2 adds W30 to W40; run Pass 1's
  validation again after Pass 2), another question id, or one of these literals: X00, N01, N02, N03, N04, Events,
  Part D, Part E, Wireframes v0.2, D spine, L00 to L09, M01. Anything else fails.
- The screens named in Part D are live screens and every live screen appears in exactly one template row, except
  the T-table and T-msg rows, which list tabs. If a screen is missing from Part D, list it in the report; do not
  add it to a template row.

## Pass 2. Board corrections and Tracker rows

### 2.1 Integrations (data/integrations.json)
- I05 Accord, I08 Gupshup, I09 Razorpay, I12 FCM: choice "final", final_since "2026-09-17", cause appended
  "Vatsal, 17 Sep 2026 (vendor choices final); recorded 24 Sep 2026 (SQ1)". Nothing else on the row changes.
- I13: vendor "Mixpanel", choice "final", final_since "2026-09-24", cause appended "Vatsal, 24 Sep 2026 (SQ1
  FE-60)". The alternatives field keeps the names considered, prefixed "considered:". The role line gains
  "product analytics; journeys and nudges stay in Zoho Campaigns and Flow, FCM and WATI".
- I00 SEBI: status "production", notes prefixed "Registration granted (Vatsal, 24 Sep 2026). " The existing
  "to be verified" on the row stays unless it is now moot; if it is moot, say so in the report and leave it.
- The screens lists and everything else on every row stay as they are.

### 2.2 Tracker (data/tracker.json)
- Add W30 to W40 exactly as Part F of the answer set gives them: item, owner (first names on the Tracker), due
  date (all with due_about true, they are proposals), status "not started", direction (W30 to W35, W39, W40:
  HoA to Spinach; W36 to W38: Spinach to HoA), source "SQ1 <ids>", lands_at (W30: D09 and the logic panel; W31:
  K01, K05; W32: I24, K02, K06; W33: K06; W34: I06, I07; W35: I17, I21; W36: X00; W37: I01, A06; W38: the
  Spinach Questions tab; W39: the copy list; W40: the D spine).
- Update the existing rows as Part F's second table says: W05 notes appended; W06, W11, W27, W29 gain a note
  naming the SQ1 rows that link to them; W07 delivered with the note "Mixpanel (I13)"; W19 delivered; W21 in
  progress with the note "FE-O1 is the map; closes when Spinach posts it on X00"; W22 in progress; W24 delivered
  with the note "SQ1 received 22 Sep 2026, answered 24 Sep 2026".
- Milestones: add 28 Sep 2026 "Spinach owed items (W36 to W38)" and, about, 1 Oct 2026 "SQ1 batch 2 export"
  with rows W30 to W35 and W40.
- The daily update composer gains one line when the tab exists: "Spinach questions SQ1: N frozen, N open,
  N owed; changed since yesterday: <ids>" read from questions.json and the board table (Pass 3.5).

### 2.3 X00
- Add a card "Spinach Questions tab" with these lines, verbatim: "Every questionnaire Spinach sends lands on the
  Spinach Questions tab, one sub-tab per file, with its answer and one of three words: frozen, open (to be
  decided), owed (to be verified). An open row is approved on the page by a comment; a commit freezes it. The tab
  exports the files back in Spinach's own layout with the Yesly Comments column filled. The next questionnaire
  takes the same route."
- Add under the existing data-lifecycle line: "W21: the Open Decisions row 1 of SQ1 (FE-O1) is the map; posted
  here when Spinach shares it."

### 2.4 Changelog
Append entries for 2.1 to 2.3 with their causes, and one entry "SQ1 answered: <counts>" (Vatsal, 24 Sep 2026).

## Pass 3. The tab: docs/spinach_questions.html

### 3.1 Placement
- One tab, label "Spinach Questions", added to TABS in scripts/build_site.py after "Tracker", and to REVIEW_TABS
  in the same position. The Spinach audience file (docs/audiences/yeslyf_v02_spinach.html) gains a link to it in
  its header line. If adding a tab pushes the header to a third row at laptop width (the reason the Admin seed
  pages share one tab), shorten labels rather than drop the tab; say what you did.
- One page. Three sub-tabs inside it using the existing subtabs pattern: "Frontend", "Backend", "Journey", one per
  file, in that order. A sub-tab shows the rows of its file grouped by sheet, in sheet order, each sheet a section
  with the sheet's own name as the heading (so "React Native Foundation & Archi" reads as Spinach wrote it) and
  the sheet's row count. The Journey sub-tab shows the summary sheet first, then the five journeys; within a
  journey the blocks appear in the sheet's order (workflow, edge cases, API summary, merge) with the block name
  as a sub-heading. Part D and Part E render at the top of the Frontend sub-tab as two compact tables.

### 3.2 Filters
- Above the sub-tabs: status (all, frozen, open, owed), batch (SQ1; more later), and a text filter on id and
  text. The filter is carried in the URL hash so a link can open the tab on open rows only
  (spinach_questions.html#open). Default: all rows. The counts per status show next to the filter and per
  sub-tab.

### 3.3 The row
- Each row: the id (an anchor: #FE-34), the status pill in the board's existing colours, their question (one
  line; the full cell on tap), their proposal collapsed by default ("their proposal" expander), the Yesly comment
  in full, the refs as links (a screen id to wireframes_v02.html#<id>; a state id to the N tab anchor; an I row
  to integrations.html#<id>; a W row to tracker.html#<id>; another question id to its anchor; Part D and Part E to
  their tables), the owner and the due date on open and owed rows (with "(proposed)" while due_about is true),
  the cause line, and the changed date.
- Journey rows also show their block and the first words of the sheet row they answer, so a reader with the xlsx
  open can find the row.

### 3.4 Controls
- The identity picker and the comment box exactly as on the Wireframes v0.2 tab: page "spinach_questions",
  item_id the row id, field "comment", kind "comment". Free text.
- An "Approve" control on open and owed rows only: page "spinach_questions", item_id the row id, field "approve",
  kind "verdict", value "approved" or "disputed". A disputed verdict opens the comment box; the page asks for the
  position in words. Without an identity the write is held, as everywhere on the board.
- The page shows, under the row, the latest verdict per row from the board table as "approved by Harish, 26 Sep
  2026" or "disputed by Bhuvanaa, 26 Sep 2026: <comment>", plus the comment history. The status pill does not
  change on approval: that is Pass 5, by commit. Say so in one line of the tab's lead paragraph.

### 3.5 Back-links and the Tracker
- On the Wireframes v0.2 tab, every screen whose id appears in a row's refs gets one line in its spec panel:
  "Spinach questions: FE-34, BE-07" with links to the anchors. Rendered from questions.json at build time; no
  comment rows, no copies of the text.
- The Tracker's question list stays as it is (comments under the identity Spinach). Its daily update gains the
  SQ1 line from 2.2. The Tracker page links to the tab in its lead paragraph.

### 3.6 Copies
- The /review/ copy carries the tab. The three audience files: the Spinach file links to it; the team and
  compliance files link to it with the #open filter.

## Pass 4. The export: docs/exports/

### 4.1 Files
scripts/export_sq.py writes, on every build, one xlsx per file of the batch:
- docs/exports/SQ1_2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx
- docs/exports/SQ1_Yesly_Backend_Clarifications_Questionaire.xlsx
- docs/exports/SQ1_2026_Sep_22nd_Yesly_Journey_Description.xlsx
Each rebuilds the workbook sheet for sheet in the original sheet order with the original sheet names, the
original column headers in the original order, and the original cell text (question, proposal, link, area) as
Spinach wrote it. Then the Yesly Comments column filled with the answer, then three added columns: "Status"
(the word, plus the "to be decided:" or "to be verified:" item for open and owed rows), "Board ref" (the refs as
text, comma separated), "Changed since <date of the previous export>" ("yes" or blank; blank everywhere on the
first export). Journey sheets keep their blocks in order with the block headers as rows, so a reader sees the
same shape as the file they sent; merged cells and styling are not reproduced.

### 4.2 Mechanics
- Standard library only: an xlsx is a zip of XML; write xl/workbook.xml, xl/worksheets/sheetN.xml with inline
  strings, xl/styles.xml with one bold font for the header row and wrapped text for the answer column, the
  _rels and [Content_Types] entries. No openpyxl.
- Verify by reading every written file back with import_questions.read_sheet and comparing row and sheet counts
  to questions.json; the build fails on a mismatch.
- The tab shows a download link per file at the top of its sub-tab and the date of the export. The three files
  are also the email attachments; the cover note is written by Vatsal outside the board.
- On writing, set exported on every row to the export date and record the export date in the batch record.

## Pass 5. Applying approvals (later, on instruction; not part of this phase's commits)
- scripts/apply_sq_approvals.py reads the board table (as scripts/pull_board.py does) for page
  spinach_questions, field approve, and lists per row the latest verdict with who and when. Dry run by default.
- On Vatsal's instruction it sets status "frozen" on the approved rows, replaces the "to be decided:" or "to be
  verified:" item in the status with nothing (the answer text itself does not change), appends the cause
  "approved by <first name>, <date>" (or "delivered by <first name>, <date>" for an owed row), sets changed to the
  date, closes the linked W row where the approval closes it (status delivered, note "SQ1 <id> approved"), and
  rebuilds. The re-export then marks the rows as changed since the previous export.
- A disputed row stays open; the dispute shows on the tab and goes to the 30 Sep 2026 session.

## 6. Report back (one md file per pass)
reports/phase14_pass0.md to reports/phase14_pass4.md: what was done, the counts (rows per file and per sheet;
frozen, open, owed per file), every ref that did not resolve, every screen missing from Part D, and anything the
brief got wrong about the repo. The Pass 4 report ends with the three lines the cover note needs: the counts per
file, the export file names, and the tab URL.

## 7. Not in this phase
- No answer text changes. No screen changes beyond the back-link line and the X00 cards. No comment rows written
  by script. No freezing or unfreezing of screens. The Onboarding sheet is answered as the answer set says; it is
  not restructured here (W38 is Spinach's). No documentation or sandbox tasks (decision 7). Pass 5 does not run.
