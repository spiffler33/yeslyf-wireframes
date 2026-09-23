# Seed and admin discovery: progress

Plan: PLAN_admin_seed_v01.md (the spec; CLAUDE.md wins on a conflict). Resume from this file plus the plan.

## State (23 Sep 2026)

- Phase A done: config, generator, run-500 and run-3000, report.md per run. Committed as "seed A: generator and
  two runs" (446099f); closed at a phase boundary the same day (dead code swept, PLAN.md section 20, handoff,
  pushed). Stopped for Vatsal's go before phase B (his instruction, 23 Sep 2026).
- The phase A summary went to Vatsal in chat on 23 Sep 2026: layers, the state by tier grid, topups, the N01
  multi-predicate list, every phase A assumption, the CLAUDE.md conflicts and the three questions below. Silence
  after it is consent for the seed plan decisions (plan, cause labels); his go starts phase B.
- 23 Sep 2026, afternoon: Vatsal's go ("go"); his answers to the three questions and two readings followed the
  same afternoon (below). Phases B to E ran in sequence, one commit per phase (plan section 18
  messages); the one-line tracker update goes in the phase report (the tracker's update is composed on its page
  from board rows; there is no data slot for it).
- Seed regenerated (55607b2): tier mix 60/36/4 and the S16 line (Vatsal, 23 Sep 2026); run-3000 has 126
  DIWM, 76 DIY, 8 DIFM, 72,398 events; run-500 507 people, 16,272 events. The S24 payment_reference and the
  paid event's razorpay_ids hold real synthetic ids (were placeholder strings).
- Phase B done ("seed B: exports and operator page"): seed/export_schema.json (147 columns plus Days Unsigned),
  scripts/seed_export.py (exports, the private fixtures zip, the scan), data/seed/<run>/exports/,
  docs/admin_operator.html (data/operator.json, scripts/build_operator.py; 12 steps, 94 checkboxes, a notes box
  per step). Rows run-3000: leads 1,400, contacts 1,640, deals 206, a la carte 9, calls 84, tasks 114,
  app_events 12,464 (plan guessed about 20,000; not padded), tickets 73, landing 940, 27 campaign lists.
  Regenerate: `python3 scripts/seed_gen.py --anchor 2026-09-23`, then `python3 scripts/seed_export.py`, then
  `python3 scripts/build_site.py` (it runs the scan and fails on a breach).
- Phase C's foundation was built in a separate git worktree and merged: renderer hooks (five pages render
  identically, checked screen by screen), data/admin_screens.json, scripts/admin_core.js,
  scripts/build_admin_wireframes.py (masked bundles in docs/seed/<run>/admin/: run-3000 35 files, 18.8 MB;
  run-500 10 files, 3.9 MB; no PAN, no full phone; plus a sip table for M13).
- Phase C done ("admin wireframes v0.1"): docs/admin_wireframes.html draws M02 to M14 over the masked bundle
  with the run switch (500 or 3,000) and the Admin Link deep link; scripts/admin_screens_1.js (M02 to M04),
  _2.js (M05 to M09), _3.js (M10 to M14). Checks: the screen agents' own counts against the bundle (170, 97
  and all of M10 to M14), a smoke test drawing every screen on both runs (42 draws, 0 problems), a visual pass
  on an offline copy; admin_core's dates read the IST clock face with UTC getters (a +08:00 viewer saw times
  2.5 hours late).
- Gaps the screens found (for data/seats.json): no SLA per ops item type (M06); no call script text in any state
  (M04); the CAS source has no integrations row (M03); "who is on an old version" is always the S11 list (M08:
  a publish rebuilds every plan pending acceptance); M13: no app-open or active-user event, kyc_status never
  failed, no one-time SKU, data_complete has day precision, no CMS content, no paywall_viewed aggregate, no
  per-D-screen completion flags, no week-N retention cohort.
- Phase D done ("admin brief skeleton"): data/seats.json (8 seats, 99 questions: 38 answered from the seed,
  61 gaps: T1 5, T2 2, T3 3, T4 4, T5 42, T6 5; the principal officer seat carries the 35 N01 state pairs and
  the six PLAN.md section 20 gaps), docs/admin_seats.html (answered select and a comment box per question,
  board page admin_seats), docs/admin_brief.html (T1 399, T2 500, T3 13, T4 203, T5 25, T6 62 rows; gap rows
  from the data and, live, from the seats page), operator step 11 lists each seat's Zoho views. The seats
  judgment dropped four M13 "not in the seed" claims (the data exists); M13 now computes active users and the
  KYC failure rate from the seed and says "in the event log, not on this tab" where only the event log holds
  it. seed/export_schema.json columns carry an exact "field" path (T1's "where mirrored" matches on it).
- Nav (landed with D): one "Admin seed" tab on every page and a sub-nav across its four pages (four tabs would
  grow the header from 93 to 128 px at 1,512 px and cut into the wireframes layout).

## Vatsal's answers (23 Sep 2026, afternoon)

1. The board is public: the admin tab loads a masked variant only (phones "+91 9xxxx xx123", last three digits
   kept; no PAN; emails unchanged). Full phones and PAN live only in data/seed/ and exports/, never in docs/. No
   CSV is linked from the board; Kajal gets the CSVs from Vatsal via Drive.
2. Fixtures ship as a private zip named by run date and run size (yeslyf_seed_<anchor>_<run>.zip, gitignored,
   built by seed_export.py). Nothing seed-related on the board beyond the masked admin bundle.
3. The operator page gets one notes box per step (board_entries, like the checkboxes).
4. Progress ring (settled after one round: the v0.2 O02 logic line, frozen, also says "the ring starts at 20
   percent after the reveal"): follow v0.2. The ring starts after the reveal; S1 people show 0; the endowed 20
   lands at reveal_seen. Item 4's gaps row is dropped; nothing frozen changes. DIFM people, provisioned without a
   reveal, get no endowment (their ring reads 68 to 75 instead of 88 to 95).
5. DIFM stays 8. seed/config.json tier_mix becomes DIWM 60, DIY 36, DIFM 4 (cause "Vatsal, 23 Sep 2026"); the
   mix drives the DIWM:DIY quota, so the seed regenerates (DIWM 123 -> 126, DIY 79 -> 76). DIFM prospects stay
   15; run-500 keeps its floor of 2.
6. S16 stays 37 percent; the assumption line reads "S16 flag follows from the path mix: manual 30% plus
   AA-failed" (config s16_flag and the report row).
7. Synthetic customer names are the point; the no-invented-names rule covers the team and any real person.
   Staff stay role labels except Harish.
8. Harish as the DIFM relationship owner on admin screens is right (the no-named-adviser rule is app copy only);
   first name only.

## Phase B and C decisions (23 Sep 2026)

- Scan: no regex (Vatsal's standing rule). seed/export_schema.json declares every column's type; the scan
  checks types with stdlib parsers and leaks by exact membership against the seed's own PANs, ISINs, holding
  names and rupee numbers (the exports come only from the seed, so this is complete). The site build fails on a
  breach (build_operator runs `seed_export.py --scan-only`).
- Deals Amount: "Rs ___" as a single-line text field; to be verified: whether the standard Amount currency field
  can stay blank on import.
- One AA Status column on contacts (it is both a mirror and a field in the plan's list).
- fixtures/: README.md plus the private zip (Vatsal's answer 2); the canonical JSON is not copied into the repo
  twice.
- The repo is private (spiffler33 the only collaborator), but no CSV goes on the board (Vatsal's answer 1): the
  operator page names each file by path and the CSVs reach Kajal via Drive. Nothing copies exports into docs/.
- Seats and roles are named by role on the new pages (CLAUDE.md: no owner markers), not "(Harish)" or
  "(Kajal's seat)" as in plan section 15.
- Admin Link contract: admin_wireframes.html?run=3000&screen=M03&person=P00001 (run=500 for run-500).
- Admin tab: data/admin_screens.json (M02 to M14; M01 stays on the wireframes tab), template T-table, compliance
  internal (plan_v2 appendix G), freeze open with its own marker (data/v02/freeze.json untouched: it registers the
  194 v0.2 screens), events <id>_view plus <id>_<action> per mock write.
- Renderer: four inert hooks in WIRE_OPTS (version, specTop, drawScreen; "v0.2" strings read VERSION). Proof:
  every screen of the five pages that inline the renderer renders identically before and after
  (scratchpad render_dump.js against dumps of the committed pages).
- Seed bundle for the page: docs/seed/<run>/admin/ (meta, people without pan, dob and legal_name, tables with
  assets and the derived audit log, integration_events, person/NNNN.json chunks of 100 with events).
  admin_core.js exposes window.ADMIN (load, detail, select, open, draw registry, h helpers); three screen files
  admin_screens_1.js to _3.js register ADMIN.draw.MXX.

## Files

- seed/config.json: every count, ratio, floor, band placeholder, archetype and rule; each block carries a cause
  ("Vatsal, 22 Sep 2026", "assumption", "seed plan, 22 Sep 2026"); blocks with "added": "phase A" are decisions
  taken where the plan was silent (report.md section 8 lists them).
- seed/names.json: synthetic name lists by region (team names, retired personas and the wireframe example name left out).
- scripts/seed_gen.py: generator, state resolver, validation and report. `python3 scripts/seed_gen.py` builds both
  runs with the anchor = the run date; `--run run-500`; `--anchor YYYY-MM-DD`. About 1 s for both runs.
  Output is fixed by seed and anchor (checked: identical hashes on a rerun).
- data/seed/<run>/: one JSON per table keyed by person_id (people, households, reveal, financial_records, loans,
  covers, goals, rpq, holdings, aa_consents, cas_uploads, plan_versions, actions, subscriptions, payments,
  a_la_carte, calls, tickets, ops_queue, integration_events, tasks, nudges_sent), state_flags.json (what the
  resolver reads), staff.json, config.json (the app config table), events.jsonl, report.md.
- Inspect with scripts and counts; never load a full seed JSON or events.jsonl into context.
- seed/export_schema.json and scripts/seed_export.py: data/seed/<run>/exports/ (zoho, desk, campaigns, landing,
  mixpanel, fixtures README and the gitignored zip, README with the scan line); `--scan-only`, `--run`.
- data/operator.json and scripts/build_operator.py: docs/admin_operator.html (board page admin_operator).
- data/admin_screens.json, scripts/admin_core.js, scripts/admin_screens_1.js to _3.js and
  scripts/build_admin_wireframes.py: docs/admin_wireframes.html and the masked docs/seed/<run>/admin/ bundles.
- data/seats.json and scripts/build_seats.py: docs/admin_seats.html (board page admin_seats);
  scripts/build_brief.py: docs/admin_brief.html; data/changelog_seed.json: the changelog's seed section.
- All of them run from `python3 scripts/build_site.py` (about 18 s; most of it the admin bundles).

## How the generator works

- Each paid person gets a target state; overlay states (S7, S11, S12, S13, S15, S17, S20, S22, S23, S24, S25)
  sit on an underlying state (config overlay_bases). The timeline is drawn from the time model until the target
  holds at the anchor; the resolver then derives the state and the state_enter history from state_flags only.
- report.md checks: targets vs resolved (none differ), coherence (0 violations), gate (0 unknown gate or React
  fields on built plans), event order (0 before signed_up, 0 plan_read before plan_built), names (all on the board).
- Money: every amount on a deal, payment or a la carte purchase is "Rs ___" with a price key (CLAUDE.md: prices are
  never invented). Included calls "N". Minutes "about N minutes".
- Vendors: integration_events carry the vendor key of plan section 11 and the I-number; screens must cite the
  I-number only (CLAUDE.md).

## Phase A results (run-3000; run-500 in its report)

- 3,040 people: 1,400 leads, 400 S1, 990 S2, 25 S2b, 15 S2c, 210 paid; topups 0 (run-500: 507, topups 7).
- Every ugly case at its count. 86 people with more than one predicate (the N01 gap list). 3 engine-failure people
  match no state (kept at S5). 72,371 events (the plan estimated about 150,000).

## Open questions

- None from the seed plan: the three phase A questions and the two readings were answered on 23 Sep 2026 (see
  "Vatsal's answers" above).
- For Vatsal when he reads the seats page: fi-01's Zoho view names the export's own column labels "Razorpay Customer
  Id" and "Razorpay Subscription or Txn Id" (plan section 12); the I-number rule covers screens, so they stay.

## Next

- Phase 13, the admin session (about 30 Sep 2026): walk admin_seats.html and admin_brief.html with the team; Kajal
  runs admin_operator.html on a Zoho One trial with the CSVs from data/seed/<run>/exports/ (Vatsal sends them via
  Drive). Nothing goes to Spinach now: the fixtures zip waits until they build from the final brief (Vatsal's call).
- Demo morning: regenerate on purpose (seed_gen.py without --anchor, then seed_export.py, then build_site.py) and
  commit the result; every date moves.
