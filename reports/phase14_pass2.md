# Phase 14, pass 2: board corrections and Tracker rows (26 Sep 2026)

Source: yeslyf_phase14_brief.md, pass 2 (2.1 to 2.4) and Part F of SQ1_answers.md. Every change carries the cause
the brief gives; the Changelog rows are dated 26 Sep 2026, the day they landed on the board.

## 2.1 Integrations (data/integrations.json)

| row | change | cause |
|---|---|---|
| I05 Accord, I08 Gupshup, I09 Razorpay, I12 FCM | choice final, final_since 2026-09-17; nothing else on the row | appended "Vatsal, 17 Sep 2026 (vendor choices final); recorded 24 Sep 2026 (SQ1)" |
| I13 | vendor Mixpanel, choice final, final_since 2026-09-24; alternatives "considered: CleverTap, MoEngage, WebEngage"; the role line gains "; product analytics; journeys and nudges stay in Zoho Campaigns and Flow, FCM and WATI" | appended "Vatsal, 24 Sep 2026 (SQ1 FE-60)" |
| I00 SEBI | status production; notes prefixed "Registration granted (Vatsal, 24 Sep 2026). " | in the prefix |

Notes on these rows:
- I13 also gains "mentions": ["M01"], as I09 and I12 carry. The M01 table names the vendor from this row ("I13
  Mixpanel" once the vendor is set), and without the field the vendor cross-check would have marked I13 "to be
  verified: screens" on the next build. Build mechanics, not content; the build confirms I13 carries no mark.
- I13's role line now opens "Journey orchestration and product analytics ..." and closes "... journeys and nudges
  stay in Zoho Campaigns and Flow, FCM and WATI": the brief says the line gains the clause, so the opening words
  stay; trimming them is a later commit if wanted. I13's notes still read "Decision by 19 Sep 2026." (stale; not in
  the brief, left).
- I00's "to be verified: which rows need the registration document before a sandbox" is moot now that the
  registration is granted; left on the row as the brief says.
- I09's cause now carries "Vatsal, 17 Sep 2026" twice (once from phase 12, once in the appended phrase); appended
  as written.

## 2.2 Tracker (data/tracker.json)

New rows, all status "not started", every date a proposal (due_about true):

| W | owner | due | direction | source | lands at |
|---|---|---|---|---|---|
| W30 RPQ scoring map (gap G06) | Harish, Somil | 30 Sep 2026 | HoA to Spinach | SQ1 BE-05 | D09 and the logic panel |
| W31 The calls recipe (gap G04) | Bhuvanaa, Harish | 30 Sep 2026 | HoA to Spinach | SQ1 BE-08, BE-10, BE-12 | K01, K05 |
| W32 Meeting tool for calls (I24) | Kajal | 30 Sep 2026 | HoA to Spinach | SQ1 BE-07, BE-13 | I24, K02, K06 |
| W33 Recording consent and retention rule | Compliance | 30 Sep 2026 | HoA to Spinach | SQ1 BE-07, BE-15 | K06 |
| W34 Close the KYC vendor (I06) and the eSign vendor (I07) | Kajal, Harish | 30 Sep 2026 | HoA to Spinach | SQ1 FE-42, JD-PAY-W3 | I06, I07 |
| W35 Accounts in HoA's legal name; bundle ID and package name; the domain | Gaurav, Kajal | 30 Sep 2026 | HoA to Spinach | SQ1 FE-73, FE-74, FE-75, FE-08, FE-N4 | I17, I21 |
| W36 Expo SDK and React Native versions; React Compiler status | Spinach | 28 Sep 2026 | Spinach to HoA | SQ1 FE-01, FE-F2, FE-F3, FE-P5 | X00 |
| W37 Finvu's integration mode | Spinach | 28 Sep 2026 | Spinach to HoA | SQ1 FE-38, FE-X1 | I01, A06 |
| W38 The Onboarding sheet rebuilt against O01 to O03 | Spinach | 28 Sep 2026 | Spinach to HoA | SQ1 JD-ONB-H1 | spinach_questions.html |
| W39 Validation and error copy for the reusable inputs | Bhuvanaa | no date (not a blocker) | HoA to Spinach | SQ1 FE-26 | the copy list |
| W40 The bands and validation ranges table | Bhuvanaa, Vatsal | 30 Sep 2026 | HoA to Spinach | SQ1 FE-27 | the D spine |

- W38's lands_at is the tab's page name: the Tracker renders a lands_at that names a site page as a link to it
  (the rule W12 and W13 use), so it reads "Spinach Questions" once the tab exists in pass 3; until then it shows the
  file name as text.
- W39 has no date; the page shows "-" for it (the about flag has nothing to qualify).
- Existing rows: W05 notes gain the SQ1 items (the refund and cancellation rule BE-14 and JD-PAY-E14, the deletion
  retention period and the retained-record list BE-02, the DPDP notice text JD-SUM-4); W06, W11, W27 and W29 note
  the SQ1 rows that link to them; W07 delivered ("Mixpanel (I13); Vatsal, 24 Sep 2026"); W19 delivered (the
  registration is in); W21 in progress ("FE-O1 is the map; closes when Spinach posts it on X00"); W22 in progress
  (the journey description is the first output); W24 delivered ("SQ1 received 22 Sep 2026, answered 24 Sep 2026").
  Owners, dates and directions of existing rows are unchanged.
- Milestones added: 28 Sep 2026 "Spinach owed items (W36 to W38)"; about 1 Oct 2026 "SQ1 batch 2 export" (W30 to
  W35, W40). The Tracker's validation passes (39 rows, W01 to W40 in order, 1 folded).
- The daily update composer is not touched here; its SQ1 line comes with the tab (pass 3, brief 3.5).

## 2.3 X00 (data/v02/sq1_edits.json, applied by scripts/apply_decisions.py)

- A card "Spinach Questions tab" with the brief's four lines, verbatim, inserted after "How Spinach works from this
  board" (before the Start button). The edits file sorts after spinach_markers_edits.json so its anchor card exists.
- The W21 line "W21: the Open Decisions row 1 of SQ1 (FE-O1) is the map; posted here when Spinach shares it."
  appended to the card "Saving and coming back", directly under the data-lifecycle line (its line 4), which stays
  byte-identical (the freeze register matches it by text).
- X00's causes gain "Vatsal, 24 Sep 2026"; the freeze register is unchanged (160 frozen, 34 open, 21 templates);
  cards are copy, which the freeze does not cover, and the new text carries no "to be decided:" marker.

## 2.4 Changelog (data/changelog_sq.json)

Six rows dated 26 Sep 2026 under "Spinach questionnaires": the four vendor finals (17 Sep 2026 cause), I13 Mixpanel
(SQ1 FE-60 cause), I00 granted and W19 delivered, the Tracker changes, the X00 card and line, and "SQ1 answered:
231 rows, frozen 222, open 6, owed 3 (frontend 129: 124, 3, 2; backend 15: 14, 1, 0; journey 87: 84, 2, 1)". X00
also appears in the Changed table with the new cause, through changelog.json.

## Validation

- scripts/import_sq.py run again after the Tracker rows: 0 refs pending, 0 problems; data/questions.json rewritten
  (the tracker field of each row now resolves against real rows). Found and fixed in this pass: the Part D lists
  were built from a set and their order varied between runs; they now follow the board's screen order, and two
  consecutive writes are byte-identical.
- scripts/apply_decisions.py: 194 live screens, 21 templates, 160 frozen, 34 open. scripts/build_site.py: every
  page rebuilt (the integrations, tracker, wireframes, changelog and audience pages changed; the admin pages embed
  the integrations rows and changed with I13). check_phase9 19 PASS, check_site 3 PASS, validate_v02 7 PASS.

## Counts (unchanged from pass 1)

| file | rows | frozen | open | owed |
|---|---|---|---|---|
| 2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx | 129 | 124 | 3 | 2 |
| Yesly Backend Clarifications Questionaire.xlsx | 15 | 14 | 1 | 0 |
| 2026_Sep_22nd_Yesly_Journey_Description.xlsx | 87 | 84 | 2 | 1 |
| total | 231 | 222 | 6 | 3 |
