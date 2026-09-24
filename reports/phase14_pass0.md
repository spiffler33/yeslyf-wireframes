# Phase 14, pass 0: inputs (24 Sep 2026)

Source: yeslyf_phase14_brief.md, pass 0. Phase 14 is free: PLAN.md's phases run to 13 (the admin session) and the
seed plan uses letters A to F, so nothing is renumbered. The brief is committed at the repo root next to
yeslyf_phase12_brief.md.

## What was done

- inputs/spinach/2026-09-22/ holds the four files Vatsal placed; nothing in it was changed or renamed. Real types
  by `file`: the three xlsx files are "Microsoft Excel 2007+" (zip of XML, read with the standard library);
  SQ1_answers.md is ASCII text.

| file | bytes | sheets |
|---|---|---|
| 2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx | 41851 | 11 |
| Yesly Backend Clarifications Questionaire.xlsx | 52061 | 1 |
| 2026_Sep_22nd_Yesly_Journey_Description.xlsx | 36408 | 6 |
| SQ1_answers.md | 61244 | - |

- The batch line. The Inputs tab is frozen at the data level: data/inputs.json is the v0.1 review log, rows 1 to 73
  in the log's record shape (reviewer, screen, text), and a "batch received" line has no place in it. So, as the
  brief's fallback says, the line is on the Changelog only. It lives in a new hand-authored file
  data/changelog_sq.json (source, note, rows of date, change, pages, cause), rendered as its own section "Spinach
  questionnaires" (id c-sq) on docs/changelog.html, the same mechanism as the seed rows in data/changelog_seed.json:
  scripts/apply_decisions.py regenerates data/changelog.json whole, so rows written there would not survive.
  scripts/build_site.py changelog_parts now loops over the two files (the seed section is unchanged). The row:
  24 Sep 2026, "Spinach questionnaire SQ1, received 22 Sep 2026, three files, answered 24 Sep 2026", where "-"
  (the tab lands in pass 3 and is added to the row's pages then), cause "Vatsal, 24 Sep 2026".
- Rebuild: `python3 scripts/build_site.py`; only docs/changelog.html changed. `python3 scripts/check_phase9.py`
  19 PASS, `python3 scripts/check_site.py` 3 PASS, `python3 scripts/validate_v02.py` 7 PASS.

## The files as received

Rows as the reader sees them (title and header rows included); the question rows are counted in pass 1.

| file | sheet (as named, padding kept) | rows | question rows |
|---|---|---|---|
| Frontend | Frontend Technical | 83 | 80 |
| Frontend | React Native Foundation & Archi | 33 | 6 |
| Frontend | Navigation & Routing | 11 | 6 |
| Frontend | Conectivity | 4 | 2 |
| Frontend | Performance & Optimization | 8 | 6 |
| Frontend | Security & Authentication | 11 | 6 |
| Frontend | " Native Device Features " | 11 | 5 |
| Frontend | CI_CD & Release Management | 7 | 5 |
| Frontend | Analytics & Monitoring | 6 | 4 |
| Frontend | Integrations (App-Specific) | 7 | 5 |
| Frontend | "Open Decisions from Wireframes " | 6 | 4 |
| Backend | Sheet1 | 998 (16 with text) | 15 |
| Journey | Journey Summary | 9 | 5 |
| Journey | Login | 37 | 16 |
| Journey | Reveal | 37 | 15 |
| Journey | Paywall | 43 | 20 |
| Journey | Onboarding | 27 | 14 |
| Journey | Account Aggreviator | 42 | 17 |

## Where the brief and the repo or the files differ

- The backend file is "Yesly Backend Clarifications Questionaire.xlsx" on disk (spaces); the brief and the answer
  set write it with underscores. inputs/ is read-only, so it keeps its name; the export file will be named as the
  brief says (SQ1_Yesly_Backend_Clarifications_Questionaire.xlsx).
- "inputs.json (or wherever the Inputs tab reads its list)": data/inputs.json is the frozen review log, so the line
  went to the Changelog (above).
- Two sheet names carry padding spaces (" Native Device Features ", "Open Decisions from Wireframes "). They are
  kept verbatim in the data and written back as they are; the tab strips them for headings.
- The Onboarding sheet's workflow header reads "Screen/Step" (no spaces, unlike the other four sheets), the sheet
  has no screen-sequence block and no API block, and its header block is scrambled (as JD-ONB-H1 says). The
  Journey Summary sheet has no Yesly Comments column. The Account Aggreviator sheet has an empty row (28) before
  its API block. The importer (pass 1) handles each of these by label, not by position.
- Spinach's cells hold non-ASCII characters (en dashes, arrows, curly quotes, middle dots) and the words
  "Recommendation" (the journey sheets' merge rows) and "recommendations" (BE-06's question). The ASCII rule and
  the banned-word check are for HoA's own writing; how the data, the tab and the export carry Spinach's text
  verbatim without breaking either is set out in the pass 1 report.

## Counts

No rows are counted in this pass; pass 1 reads them (231 across the three files, see reports/phase14_pass1.md).
