# Phase 14, pass 4: the export (26 Sep 2026)

Source: yeslyf_phase14_brief.md, pass 4 (4.1, 4.2) and decision 6 (two batches; every re-export marks the rows changed
since the previous one). Batch 1 is written: the day this phase lands, with the open and owed rows marked as such.

## What was built

- scripts/export_sq.py writes, on every build (scripts/build_site.py calls it before build_questions), one xlsx per
  file of the batch under docs/exports/:
  - SQ1_2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx (37,582 bytes, 11 sheets, 129 comments)
  - SQ1_Yesly_Backend_Clarifications_Questionaire.xlsx (11,931 bytes, 1 sheet, 15 comments)
  - SQ1_2026_Sep_22nd_Yesly_Journey_Description.xlsx (36,161 bytes, 6 sheets, 87 comments)
- Each workbook is rebuilt from the original file in inputs/spinach/2026-09-22/: the sheets in the original order
  with the original names (padding spaces included), every original row and cell as Spinach wrote it (title rows,
  header rows, block headers, the journey header blocks, the screen-sequence blocks, the empty rows, so the row
  numbers are the same as in the file they sent), then the Yesly Comments column filled with the answer of each
  question row, then three added columns after the sheet's last column, on every header row and question row:
  "Status", "Board ref" and "Changed since ...". The Journey Summary sheet has no Yesly Comments column: it gets one
  after "Key open area", then the three. The Onboarding header block's answer (JD-ONB-H1) sits on its "Entry
  criteria" row in the sheet's Yesly Comments column.
- Status reads "frozen", or "open - to be decided: <item>" and "owed - to be verified: <item>" (the item is the
  opening sentence of the answer; JD-PAY-E14, whose answer names the rule instead, reads "open - to be decided").
  Board ref is the refs, comma separated. The last column is blank everywhere on this first export and its header
  reads "Changed since previous export (first export 26 Sep 2026)"; from the next stamp on it reads "Changed since
  <date>" with "yes" on the rows whose changed date is later.
- Mechanics: standard library only; inline strings; one styles part with a bold font (header rows) and wrapped text
  (the comments and Status cells), the comment column 60 wide and Status 44 so the text reads; the rels and content
  types. Merged cells and Spinach's styling are not reproduced. Every zip entry carries the export date as its time,
  so a rebuild with nothing changed produces byte-identical files (checked twice today).
- Verification on every run: each written file is read back with import_questions.read_sheet; the sheet names in
  order, the row count of every sheet, every answer cell and every Status cell must match the data; a mismatch fails
  the build. The first run caught one: empty rows were dropped by the reader and shifted the rows below them; an
  empty row now keeps its place with one empty cell.
- The export date: stamped on the batch (exported, with the previous stamp in exported_previous) and on every row
  (exported) only when a row's changed date is later than the last stamp, so a quiet rebuild keeps the date and the
  marks; on a new stamp the previous date becomes the "Changed since" column. A row changed on the day of a stamp,
  after it, is carried by the next day's build. Today's stamp: 2026-09-26, first export.
- The tab shows, at the top of each sub-tab, "Export of 26 Sep 2026" with the download link of that file. The three
  files are the attachments of the cover note; the tab itself is HoA's and is not sent.
- Changelog: one row for the batch 1 export.

## Checks

check_phase9 19 PASS, check_site 3 PASS, validate_v02 7 PASS; the export's own read-back on all three files passes;
the tab rebuilt with the links (506 KB).

## For the cover note

Counts per file (frozen, open, owed):

| file | rows | frozen | open | owed |
|---|---|---|---|---|
| 2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx | 129 | 124 | 3 | 2 |
| Yesly Backend Clarifications Questionaire.xlsx | 15 | 14 | 1 | 0 |
| 2026_Sep_22nd_Yesly_Journey_Description.xlsx | 87 | 84 | 2 | 1 |
| total | 231 | 222 | 6 | 3 |

Per sheet: Frontend Technical 80 (75, 3, 2); React Native Foundation & Archi 6; Navigation & Routing 6; Conectivity 2;
Performance & Optimization 6; Security & Authentication 6; Native Device Features 5; CI_CD & Release Management 5;
Analytics & Monitoring 4; Integrations (App-Specific) 5; Open Decisions from Wireframes 4 (all frozen); Backend Sheet1
15 (14, 1, 0); Journey Summary 5 (frozen); Login 16 (15, 1, 0); Reveal 15 (frozen); Paywall 20 (19, 1, 0); Onboarding
14 (13, 0, 1); Account Aggreviator 17 (frozen).

Export file names: SQ1_2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx, SQ1_Yesly_Backend_Clarifications_Questionaire.xlsx,
SQ1_2026_Sep_22nd_Yesly_Journey_Description.xlsx (docs/exports/).

Tab URL (HoA only, not for the note): https://spiffler33.github.io/yeslyf-wireframes/spinach_questions.html

## Not in this phase

Pass 5 (applying approvals by commit) runs later on instruction; batch 2 exports after the open rows are frozen; the
sending is Vatsal's.
