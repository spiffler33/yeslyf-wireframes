# Phase 14, pass 1: data/questions.json (24 to 26 Sep 2026)

Source: yeslyf_phase14_brief.md, pass 1. Phase 14 is free (PLAN.md numbers phases up to 13, the admin session).

## State

scripts/import_sq.py reads the three files and the answer set and wrote data/questions.json: 231 rows, every id on
exactly one sheet row and every sheet row that carries a question on exactly one id, every ref resolving (24 waited
on the Part F tracker rows until pass 2). The write happened on 26 Sep 2026 after Vatsal's decision to match the
journey rows by order (below); on 24 Sep 2026 the dry run had stopped on 11 quotes, as the brief's rule said.
Nothing in the answer set was changed. Rebuild: no page changed (nothing reads questions.json before pass 3);
check_phase9 19 PASS, check_site 3 PASS.

## Quotes that differ from the sheet (brief 1.2; matched by order, Vatsal, 26 Sep 2026)

The check: lower case, every character that is not a letter or a digit separates words, the first three words of
the answer set's "row" cell against the sheet row's cells joined (for the M row the Recommendation cell; for the
H1 block the "Entry criteria" row). Sheet row numbers are 1-based rows of the sheet.

| id | sheet, row | the sheet row begins | the answer set quotes |
|---|---|---|---|
| JD-REVEAL-M1 | Reveal, row 34 | if a04 a05 are both intro | A04/A05 merge; keep R10 |
| JD-AA-M1 | Account Aggreviator, row 40 | a06 a07 account discovery consent explanation | A06/A07 and A08/A09 merges |
| JD-ONB-H1 | Onboarding, row 4 | entry criteria o01 o03 | Header block |
| JD-ONB-W1 | Onboarding, row 13 | o01 select preferred onboarding service mode | O01 Select service mode |
| JD-ONB-E1 | Onboarding, row 18 | user selects diy then immediately switches | Selects DIY then switches to DIWM/DIFM |
| JD-ONB-E2 | Onboarding, row 19 | user s plan tier changes in | Plan/tier changes in another session |
| JD-ONB-E4 | Onboarding, row 21 | o02 is not applicable to one | O02 not applicable to a mode |
| JD-ONB-E5 | Onboarding, row 22 | user partially completes o02 and exits | Partially completes O02 and exits |
| JD-ONB-E6 | Onboarding, row 23 | o01 mode changes and only some | O01 change invalidates some O02 fields |
| JD-ONB-E8 | Onboarding, row 25 | user chooses later but no reminder | Chooses later but no reminder channel |
| JD-ONB-E10 | Onboarding, row 27 | user chooses continue now after a | Continue now after a reminder exists |

What the sheets show: the two M rows and the H1 block are found by their labels (the one "Recommendation" row of a
sheet; the Onboarding header block from "Entry criteria" to "Source status"), and their quotes are summaries, not
opening words. The eight Onboarding rows are in the same order and number as the answer set (W1 to W3 are O01, O02,
O03; E1 to E10 are the ten edge rows), and each quote shortens the sheet's label (the sheet writes "User selects
DIY then immediately switches to DIWM/DIFM"; the quote reads "Selects DIY then switches to DIWM/DIFM"). Every other
journey row passes the check: Login 16 of 16, Reveal 14 of 15, Paywall 20 of 20, Account Aggreviator 16 of 17,
Onboarding 5 of 14.

Decision (Vatsal, 26 Sep 2026): match by order. The importer matches every journey row by its position within its
block (the M row by its label, H1 by its bounds) and reports a differing quote as a note instead of stopping; the
11 rows above are those notes. Their answers were read against the sheet rows: each names the row's content (W1
corrects O01 as built, E1 says a tier change is Q02, the M rows decline the merges the Recommendation cells propose).

## What the dry run found

231 rows across the three files.

| file | rows | frozen | open | owed |
|---|---|---|---|---|
| 2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx | 129 | 124 | 3 | 2 |
| Yesly Backend Clarifications Questionaire.xlsx | 15 | 14 | 1 | 0 |
| 2026_Sep_22nd_Yesly_Journey_Description.xlsx | 87 | 84 | 2 | 1 |
| total | 231 | 222 | 6 | 3 |

Per sheet (sheet names as Spinach wrote them, two with padding spaces):

| file | sheet | rows | ids | frozen | open | owed |
|---|---|---|---|---|---|---|
| Frontend | Frontend Technical | 80 | FE-01 to FE-80 | 75 | 3 | 2 |
| Frontend | React Native Foundation & Archi | 6 | FE-F1 to FE-F6 | 6 | 0 | 0 |
| Frontend | Navigation & Routing | 6 | FE-N1 to FE-N6 | 6 | 0 | 0 |
| Frontend | Conectivity | 2 | FE-C3, FE-C4 | 2 | 0 | 0 |
| Frontend | Performance & Optimization | 6 | FE-P1 to FE-P6 | 6 | 0 | 0 |
| Frontend | Security & Authentication | 6 | FE-S1 to FE-S6 | 6 | 0 | 0 |
| Frontend | " Native Device Features " | 5 | FE-D1 to FE-D5 | 5 | 0 | 0 |
| Frontend | CI_CD & Release Management | 5 | FE-R1 to FE-R5 | 5 | 0 | 0 |
| Frontend | Analytics & Monitoring | 4 | FE-M1 to FE-M4 | 4 | 0 | 0 |
| Frontend | Integrations (App-Specific) | 5 | FE-X1 to FE-X5 (by order; the sheet numbers rows 1, 2, 3, 5, 5) | 5 | 0 | 0 |
| Frontend | "Open Decisions from Wireframes " | 4 | FE-O1 to FE-O4 | 4 | 0 | 0 |
| Backend | Sheet1 | 15 | BE-01 to BE-15 | 14 | 1 | 0 |
| Journey | Journey Summary | 5 | JD-SUM-1 to JD-SUM-5 | 5 | 0 | 0 |
| Journey | Login | 16 | W1 to W3, E1 to E12, M1 | 15 | 1 | 0 |
| Journey | Reveal | 15 | W1 to W3, E1 to E11, M1 | 15 | 0 | 0 |
| Journey | Paywall | 20 | W1 to W4, E1 to E15, M1 | 19 | 1 | 0 |
| Journey | Onboarding | 14 | H1, W1 to W3, E1 to E10 | 13 | 0 | 1 |
| Journey | Account Aggreviator | 17 | W1 to W7, E1 to E5, API1 to API4, M1 | 17 | 0 | 0 |

The open and owed rows (owner, due, the item):

| id | status | owner | due (proposed) | item |
|---|---|---|---|---|
| FE-01 | owed | Spinach | 28 Sep 2026 | the exact Expo SDK and React Native versions, pinned by Spinach before development starts and stated in the project plan |
| FE-17 | owed | Spinach | no date | there is no Figma yet |
| FE-74 | open | Tech | 30 Sep 2026 | the iOS bundle ID and the Android package name, the reverse of HoA's domain once the domain is confirmed (W35) |
| FE-75 | open | Tech and Compliance | 30 Sep 2026 | the Apple Developer and Google Play Console accounts in HoA's legal name; the registration is in, so they can be opened now (W35) |
| FE-78 | open | Copy and Compliance | no date | the store listing copy (owner: Copy) and the financial-app declarations (owner: Compliance, W06) |
| BE-14 | open | Compliance | 30 Sep 2026 | the cancellation and refund rule (brief H5), owner Compliance with Harish (W05) |
| JD-LOGIN-E12 | open | Compliance | 30 Sep 2026 | owner Compliance (W29) |
| JD-PAY-E14 | open | Compliance | 30 Sep 2026 | (none: the answer reads "... the rule is BE-14 (to be decided, Compliance, W05)", without the "to be decided:" opening) |
| JD-ONB-H1 | owed | Spinach | 28 Sep 2026 | the sheet is rebuilt by Spinach against O01 to O03 as built (W38) |

Refs: 134 distinct refs; every one resolves to a live screen, a state, an I row, a W row, a question id or a
listed literal. 24 refs on 22 rows point at W30 to W40, which pass 2 adds from Part F; the importer lists them as
pending and the second run after pass 2 must show none. No ref failed.

Part D: 19 template rows, 190 of the 194 live screens placed (147 on the 18 explicit rows; the T-table, T-msg row
covers the 43 N, L and M screens by their board template). Live screens missing from Part D, listed and not added: P04, X00, A01, R12.
The range "G03 to G10" spans G08, which is dropped; it is left out. Every screen named in Part D is live, none is
listed twice, and each one's Part D template equals its board template.

Part E: 4 route groups, stored as written (its screen lists are text, not validated; the brief validates Part D).

## Decisions taken in the importer (say if any is wrong)

- The backend file on disk is "Yesly Backend Clarifications Questionaire.xlsx" (spaces); the brief and the answer
  set write it with underscores. inputs/ is read-only, so the file keeps its name; questions.json records the name
  on disk and the export file is SQ1_Yesly_Backend_Clarifications_Questionaire.xlsx as the brief says.
- Sheet names are stored verbatim, padding spaces included (" Native Device Features ", "Open Decisions from
  Wireframes "); the tab will strip them for headings and the export writes them as they are.
- The Open Decisions sheet has no question column: area is its "Decision" cell, question its "Wireframe Note" cell,
  proposal its "Best Practice Proposal" cell, link empty.
- Journey rows: question holds the row's cells as "Header: cell" lines (proposal and comments cells left out), so
  the tab can show one line and the full row on tap; proposal is the row's Best Practise or Best Practice cell; a
  JD-SUM row's question is its "Key open area" cell and its area the journey name; the M row's question is the
  Recommendation cell; H1's question is the header block's eight lines.
- Fields beyond the brief's list, all needed by the tab or the export: row (the answer set's quote), item (the
  "to be decided:" or "to be verified:" sentence of an open or owed answer, for the export's Status column),
  header_row and comment_col (where the export writes the comment; -1 on the summary sheet, which has no Yesly
  Comments column: the export appends one).
- Spinach's cells hold non-ASCII characters (en dashes, arrows, curly quotes, middle dots). They are kept verbatim
  in the data; json.dump escapes them, so data/questions.json stays ASCII and the text does not change. The tab
  will write them as numeric entities so the page stays ASCII too; the export writes them back as they came.
- The cause rule is applied literally: an answer that begins "Accepted as proposed" gets the accepted cause;
  "Accepted.", "Accepted in principle", "Accepted with one rule" and "Accepted as written" get "Vatsal, 24 Sep 2026".
- Every due date is a proposal (the answer set's header), so due_about is true on every open and owed row with a
  date; "no date" gives an empty due with due_about true.

## Committed

- scripts/import_sq.py (dry run by default; --write after a clean run), data/questions.json (231 rows, ASCII,
  278 KB), this report. The importer runs again after pass 2 to confirm that no W ref is pending.

## Notes for passes 2 to 4 (from a read of the build scripts, 24 Sep 2026)

- Rebuild order: scripts/apply_decisions.py (regenerates data/screens_v02.json and data/changelog.json whole; needed
  after the X00 edits file and the I13 vendor change), then scripts/build_site.py (runs every other builder), then
  check_phase9.py, check_site.py, validate_v02.py.
- Deep links on the board: integrations.html#row/I05 and tracker.html#row/W35 (not #I05, #W35 as the brief writes);
  screens wireframes_v02.html#A01 (index.html#A01 in the review copy); states have no anchor of their own, the N01
  screen is the states table.
- X00 is frozen. Adding cards is copy, which the freeze does not cover; the new X00 edits file must sort after
  data/v02/spinach_markers_edits.json (a name such as sq1_edits.json), its text must not contain "to be decided:"
  with a colon (the register would read it as an open decision on a frozen screen; the brief's card has no colon),
  and the data-lifecycle line stays byte-identical because data/v02/freeze.json tbd_owed matches it by text; the
  W21 line is appended after it with card_add.
- I13 to Mixpanel: the M01 table reads the vendor from the row, and the vendor cross-check then flags M01 unless I13
  carries "mentions": ["M01"] as I09 and I12 do; add that field (build mechanics, not content) and say so.
- The banned-word check (recommendation, Recommendation; case-sensitive) runs over the v0.2 pages, the audience files,
  the Tracker and Integrations pages. Spinach's cells contain "Recommendation" and "recommendations". The tab is
  built by its own script (adding it to V02_PAGES would fail the build), keeps their text verbatim (non-ASCII as
  numeric entities) and checks the banned words over its own chrome only; the export writes their text as it came.
- check_phase9 fixes the nav string "Wireframes v0.2, Tracker" in that order: the new tab goes after Tracker as the
  brief says. The daily update composer is capped at 15 lines (8 today) and is run in a fake browser with no board
  rows, so the SQ1 line must work with none. Audience files may not contain "http://" or "https://": links to the
  tab are relative. The header wraps (flex-wrap) and the wireframes layout height assumes one header row.
- Board API: init({page, also, apply, who, local}), write({item_id, field, value, who, kind}), read({page, apply}),
  history(item_id) (rows newest first), attach(el, idFn); the identity select is id="reviewer"; the table accepts
  kinds comment, verdict and field_edit and any page name. BOARD.fmt has no year, so the tab formats "approved by
  Harish, 26 Sep 2026" itself. The Tracker's question list links only wireframes_v02, integrations and tracker;
  pass 3 adds spinach_questions to pageLink so Spinach's comments on the tab link back.
- In-page sub-tabs exist only in the audience files (VIEW_JS, a[data-view] and [data-viewpane]); the site's subtabs
  CSS is a link row across pages. The tab uses the audience files' pattern inside one page.
