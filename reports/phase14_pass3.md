# Phase 14, pass 3: the Spinach Questions tab (26 Sep 2026)

Source: yeslyf_phase14_brief.md, pass 3 (3.1 to 3.6), with one change of scope from Vatsal on 26 Sep 2026: the tab is
HoA's working view (what is done, what is pending, which 5 to 10 questions the team must take), and Spinach never
sees it; Spinach receives only the filled questionnaire files (pass 4). Where that changes the brief, the line says so.

## What was built

- scripts/build_questions.py writes docs/spinach_questions.html from data/questions.json; scripts/build_site.py calls
  it after build_tracker, so every rebuild carries it. One page, 505 KB, 231 rows.
- The tab "Spinach Questions" sits after "Tracker" in TABS (the check that fixes "Wireframes v0.2, Tracker" in that
  order still passes). Not in REVIEW_TABS and no docs/review/ copy (brief 3.1 and 3.6 said both; Vatsal, 26 Sep 2026:
  the review link is Spinach's view).
- Lead: what the three words mean, that approval is a comment under a name and the status word changes only by a
  commit, that Spinach receives the files, never the tab. Then "Open and owed: what the team decides or verifies",
  the 9 rows with their item, owner and proposed date, each a link to its row (added for Vatsal's purpose: the
  pending list is the first thing on the page).
- Filters above the sub-tabs: status chips (all 231, frozen 222, open 6, owed 3), batch (SQ1), a text filter on id
  and text, and "N of 231 rows shown". The status word travels in the URL hash: spinach_questions.html#open opens
  the tab on the six open rows; #frozen, #owed and #all likewise; a row id in the hash (#FE-34) opens its sub-tab,
  scrolls to it and highlights it, clearing the filter if the row was hidden. Default: all rows.
- Sub-tabs Frontend, Backend, Journey (the audience files' in-page tab pattern: a[data-view] and [data-viewpane]),
  each with its count and "frozen, open, owed" breakdown. A sub-tab shows its sheets in sheet order, each a section
  headed with the sheet's own name (padding spaces stripped for display) and "N of N rows; frozen, open, owed".
  The Journey sub-tab: Journey Summary, then Login, Reveal, Paywall, Onboarding, Account Aggreviator, each with its
  blocks as sub-headings in sheet order (Header block, Workflow, Edge cases, API summary, Merge suggestion). Part D
  (19 template rows) and Part E (4 route groups) open the Frontend sub-tab as two tables (anchors #part-d, #part-e).
- A row: the id (anchor and link), the status word as a text tag (frozen dark, open yellow, owed dashed; text, never
  colour alone), Spinach's question as one clipped line that opens to the full cell, "their proposal" folded, their
  link as a meta line, the Yesly comment in full, the refs as links, owner and due "(proposed)" on open and owed rows,
  the cause line ("cause: none until the row is frozen; the freezing commit writes approved by (first name),
  (date)" on open and owed rows), the changed date. Journey rows add "Workflow, sheet row 15: A02-A03 Enter OTP"
  (the block, the sheet row number and the answer set's quote), so a reader with the xlsx open finds the row.
- Ref links, in the forms the board actually uses (the brief's #I05 and #W35 do not open a row): a screen to
  wireframes_v02.html#A01; a state to wireframes_v02.html#N01 (the states table; no state has an anchor of its own);
  an I row to integrations.html#row/I05; a W row to tracker.html#row/W35; a question id to its anchor; Part D and
  Part E to their tables; Events to events.html; "Wireframes v0.2" to the tab; "D spine" to D01.
- Controls: the identity picker (Bhuvanaa, Harish, Gaurav, Kajal, Somil, Raafiya, Vatsal, Compliance; no Spinach,
  since Spinach never sees the tab) and a comment box on every row (page spinach_questions, item_id the row id,
  field comment, kind comment, written 1.5 s after typing stops, as on the Wireframes v0.2 tab; a History toggle
  under each box). Approve and Dispute on the 9 open and owed rows only (field approve, kind verdict, value approved
  or disputed); Dispute focuses the row's comment box and asks for the position in words. Without a name the write
  is held and the store's "Who is this?" line appears beside the picker, as everywhere on the board. Under the row:
  the latest verdict from the board table ("approved by Harish, 26 Sep 2026" or "disputed by Bhuvanaa,
  26 Sep 2026: <the comment posted with it>") and the comment history, newest first. The status word does not move
  on approval; the lead says so.
- Back-links (3.5): the Wireframes v0.2 spec panel gains a block "Spinach questions" with links to the rows whose
  refs name the screen (data blob SQ_REFS rendered by renderer_v02.js; 63 screens carry one). The review copy and
  the audience files get an empty blob, so nothing shows there. No comment rows, no copies of the text.
- Tracker (3.5): the lead paragraph links to the tab (site copy only); the question list links a Spinach comment
  on the tab back to its row (there will be none: Spinach never sees it); the daily update composer gains
  "Spinach questions SQ1: 222 frozen, 6 open, 3 owed; changed since yesterday: <ids or none>", read from the
  build data (rows whose changed date is yesterday or today) and the board table (rows written on the tab in the last
  24 hours); it composes in the check harness with no board rows and stays under the 15-line cap (6 lines today).
- Copies (3.6): the team and compliance audience files link to the tab on the open rows (relative link, since an
  audience file may carry no absolute URL); the Spinach file does not (Vatsal, 26 Sep 2026); no review copy.
- The Changelog row of pass 0 now names the tab under Where.

## Text rules

- Spinach's cells (question, proposal, link, area, the row quote) are verbatim: non-ASCII characters are written as
  numeric entities, so the page is ASCII and the text is theirs. The banned-word check runs over the page with
  Spinach's cells blanked ("Recommendation" is the label of their merge rows, "recommendations" is in BE-06's
  question); HoA's chrome, the answers and Part D and E carry none of the words, and the check passed. The page is
  built by its own script and is not in V02_PAGES.

## Header width

At a 1,512 px screen the header keeps two rows: the brand and the 14 tabs need 1,475 px on the first row (the new
tab adds 108 px) against 1,494 px available inside the padding, and the name control, the saved line and the pill
wrap to the second row as they did before. Measured on a local copy of docs/ with config.js blank (port 8791); the
browser window in this session could not be widened past 1,200 px, so the 1,512 px figure is the sum of the
measured widths, not a screenshot at that width. Nineteen pixels to spare; a wider system font would wrap the tabs
into a third row, and the labels would then be shortened rather than the tab dropped.

## Checks

- check_phase9 19 PASS, check_site 3 PASS, validate_v02 7 PASS; the page's own checks: ASCII, noindex, 231 rows drawn,
  no banned word outside Spinach's cells.
- In the browser (local copy, board offline): #open shows 6 rows and lights the open chip, #owed 3, #JD-ONB-H1 opens
  the Journey sub-tab and highlights the row; 231 comment boxes and History toggles, 18 Approve and Dispute buttons
  on the 9 open and owed rows; the journey sheets and blocks appear in sheet order; FE-42's refs link to P02, P03, E02,
  I06, I07 and W34 in the working forms.

## Counts (unchanged)

| file | rows | frozen | open | owed |
|---|---|---|---|---|
| 2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx | 129 | 124 | 3 | 2 |
| Yesly Backend Clarifications Questionaire.xlsx | 15 | 14 | 1 | 0 |
| 2026_Sep_22nd_Yesly_Journey_Description.xlsx | 87 | 84 | 2 | 1 |
| total | 231 | 222 | 6 | 3 |

## For Vatsal

- X00 carries the card "Spinach Questions tab" (pass 2, the brief's text) and X00 is on Spinach's copy of the
  wireframes; it describes the process, not the page, and stays as written unless you want it reworded.
- Approvals write board rows only; scripts/apply_sq_approvals.py (pass 5) freezes approved rows on your instruction.
