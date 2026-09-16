# PLAN.md - yeslyf product board and wireframes

Owner of this plan: spiff (Vatsal). Executor: Claude Code (Fable) in this folder.
Purpose: one private repo, one live GitHub Pages site, one JSON data layer. The site runs the team meeting
(in about 2 hours from kickoff), captures decisions to a Google Sheet, and is then regenerated as
wireframes v0.2 plus an updated admin/CRM spec for the developers and Spinach (UI/UX studio).

Read CLAUDE.md first. Its rules override anything here.

## 0. Time budget

- T+0 to T+15: Phase 0 (repo, Pages, inventory).
- T+15 to T+75: Phase 1 (data layer and the meeting site). Must ship before the meeting.
- T+75 to T+100: Phase 2 (sheet write-back). Ship if possible; the site works without it (local save + export).
- Meeting.
- After: Phase 3 (pull decisions, build v0.2, changelog, CRM updates), Phase 4 (handover URL).

If something in Phase 1 is at risk, cut in this order: Inputs tab, Gaps tab, dependency blocks. Never cut the Open items tab.

## 1. What is in inputs/ (spiff drops these; do not edit them, ever)

inputs/v01/            the four v0.1 HTML files: yeslyf_wireframes_v0.1.html, yeslyf_admin_crm_spec_v0.1.html,
                       yeslyf_review_log_v0.1.html, yeslyf_v0.2_decision_board.html
                       Each embeds its data as JS arrays inside a script tag: SCREENS/SECTIONS, STACK/PLACEMENT/
                       CONTACT_FIELDS/DEAL_FIELDS/EVENTS/INBOUND/NUDGES/NUDGE_EXAMPLES/COMPLIANCE/DECISIONS,
                       ROWS (73 review rows), DECISIONS/CONFIRM/CHANGES/ANSWERED/GAPS/HARISH_ROWS.
                       Extract by loading the script text into a Node vm context; do not regex-parse.
inputs/reviews/        five markdown exports: Gaurav, Kajal, Somil, Bhuvanaa, Harish. Format: "## Section" then
                       "- **ID Title** [Verdict]" then indented comment lines.
inputs/hoa/            Client_Journey_Version_2_0.pptx (Bhuvanaa's journey deck; the paywall position comes from it),
                       Admin_Panel_-_Yeslyf.docx (HoA admin needs), Risk_Profiling__1_.pdf (HoA's 8-question RPQ),
                       2025-12-29_ria_agreement.pdf (current advisory agreement, AUA mode),
                       New_User_Flow_03-06-2026.xlsx (June screen review), yeslyf FP React component (.jsx or .txt;
                       the financial plan output spec), and the earlier project documents (App_Complete_Journey...,
                       backend_m1..m6, gtm_content_v4.md, yeslifers_community_plan.md, hell_yes spec, profile cards).
                       Note: several files named .docx in that set are plain text, not Office XML. Check with `file`
                       before choosing a reader.

## 2. Ownership map (drives every default on the site; first names only, no titles)

workstream                  owner(s)              screens / topics
journey-to-paywall          Bhuvanaa              A01-A04, R01-R12, X01, all pre-paywall questions and copy
data-collection             Bhuvanaa              O01-O02, A05-A09, D01-D10 (questions, order, fields)
financial-plan-logic        Bhuvanaa              G01-G10, all FP calculations and assumptions used by them
investment-advisory         Harish (with Somil)   G11-G14, risk profiling method and its use, instrument logic
logic-panel                 Harish (with Somil)   L00-L09
compliance                  Harish                anything regulatory: advertisement code, refunds, records,
                                                  direct-plan rules, aggregator links, agreement, KYC
tech                        Gaurav                how anything is built or integrated: A02-A04 mechanics,
                                                  AA vendor flow, E01-E06 integrations, analytics events, hosting,
                                                  video delivery, OTP handling
product                     Vatsal                H00-H11, Q01-Q04, K01-K04 screens, tier rules, dates, cut line
admin                       Kajal                 M01, P02-P04 payment methods and GST, billing states in Q03,
                                                  support operations, records operations
crm-and-nudges              Vatsal and Kajal      N01, nudge matrix, Zoho, channel policy
sku-set                     Team                  P01 cards; decided in the meeting by everyone
calls-model                 Team                  what calls exist per tier; decided in the meeting
adviser-staffing            Bhuvanaa and Harish   who takes DIWM calls, certification, capacity

Rules of the map:
- A screen belongs to one workstream. A topic can override a screen (a compliance question on any screen is Harish's).
- "Team" items have no default and no preselection.
- Never write the word "founders". Never write "recommendation" on an open item.

## 3. Attribution rules (the reason this rebuild exists)

- Every position is shown with the first name of the person who said it and a reference (review row, deck slide,
  brief, or spec v0.1). Paraphrase is allowed; authorship is not transferable.
- The owner's stated position is the default and is preselected. If the owner has not spoken, the item reads
  "<Owner> to decide" with the inputs listed. Nothing is preselected.
- Options may be synthesized from positions, but each option lists who holds it. An option nobody holds is
  labelled "possible form" with no name.
- Earlier statements by Vatsal (the product brief, answers in chat, the v0.1 spec) are positions attributed to Vatsal,
  same as anyone else's.
- "Vatsal recommendation" appears in exactly two places: the Gaps tab (items nobody raised) and dependency blocks
  ("if X is decided, Y follows", because Vatsal owns product).
- Accepted items are not shown on the meeting page. Accepted means: the owner of the workstream said it, or it is a
  factual question the v0.1 spec already answers. Non-owner suggestions inside a workstream are not accepted by
  anyone but the owner; they appear on the meeting page as quick-accepts under that owner's section.
- Everything is in the open. No private notes, no hidden tabs.

## 4. Data layer (data/*.json is the single source of truth; every page is generated from it)

data/ownership.json      the map in section 2, machine-readable: [{id, owner:[names], screens:[ids], topics:[...]}]
data/screens_v01.json    SCREENS from the wireframe file, unchanged, plus SECTIONS.
data/inputs.json         the 73 review comments: {n, reviewer, screen, verdict, text, workstream, owner, status}
                         status in {open, quick-accept, accepted, answered}. Assign by rule:
                           reviewer is the owner -> accepted (unless it contradicts another named position -> open)
                           factual question the spec answers -> answered, with answer text credited to "spec v0.1"
                           suggestion by a non-owner with no counter-position -> quick-accept (owner ticks in the meeting)
                           anything with two or more named positions, or a Team topic -> open (attach to an open item)
data/open_items.json     [{id, workstream, owner, title, context, positions:[{who, position, ref}],
                           default:{who, key} or null, options:[{key, text, held_by:[names]}],
                           dependencies:[{if_key, then, recommended_by:"Vatsal"}], screens:[ids], impact}]
data/gaps.json           [{id, title, why, recommendation, suggested_owner, impact}]  (the only Vatsal-voice file)
data/admin_crm.json      STACK, PLACEMENT, CONTACT_FIELDS, DEAL_FIELDS, EVENTS, INBOUND, NUDGES, NUDGE_EXAMPLES,
                         COMPLIANCE, and the admin-spec DECISIONS re-attributed (they were written by Vatsal and Kajal's
                         CRM workstream; label them so).
data/decisions.json      written by Phase 3 from the sheet: [{item_id, choice, decided_by, note, ts}]
data/screens_v02.json    written by Phase 3.
data/changelog.json      written by Phase 3 by diffing v01 and v02 screens, with the decision or input row that caused each change.

## 5. The site (docs/ is the Pages root; generated by scripts/build_site.py; never hand-edit docs/)

Tabs, in this order:
1. Meeting        open items grouped by workstream, owner name on the section header, Team items first.
                  Per item: context, positions by name, options with holders, default preselected when it exists,
                  a decision control (choice, note), a "decided by" name field at page top, dependency blocks.
                  Quick-accepts per owner section: one line each, accept/decline, from inputs.json.
2. Gaps           gaps.json with "Vatsal recommendation", suggested owner, impact; owner and date fields.
3. Inputs         inputs.json, filterable by reviewer, workstream, status; raw text, names, row numbers. No dispositions
                  in anyone's voice; status labels only.
4. Wireframes v0.1   the v0.1 wireframe file served as-is from docs/v01/ in an iframe (or a link on mobile).
5. Admin and CRM     the v0.1 admin/CRM spec served as-is from docs/v01/.
After Phase 3 add: 6. Wireframes v0.2 (generated from screens_v02.json using the v0.1 renderer, with a "changed in v0.2"
marker and the causing row on each touched screen) and 7. Changelog.

Behaviour:
- Choices and notes save in the browser (localStorage in try/catch) and post to the sheet endpoint if configured.
- Export button downloads a markdown build brief and copies it; this is the fallback if the sheet is not live.
- Deep links: #item/T1, #screen/R09.
- Add <meta name="robots" content="noindex"> on every page.
- Style: reuse the v0.1 tokens (paper #EEF0F3, ink #1B1F27, accent #FFDA00, system font stack). Low-key. No new design work.

## 6. Sheet write-back (Phase 2)

Superseded on 16 Sep 2026 by the Supabase write-back (phase 11, section 15); kept as the record of the v0.1 path.

- Create one Google Sheet "yeslyf decisions" with tabs: decisions (ts, who, item_id, choice, note), gaps (ts, who, gap_id,
  status, owner_date, note), quick_accepts (ts, who, input_n, accept, note). Use the Google MCP if connected; otherwise
  create data/sheet_template.csv and ask spiff to create the sheet.
- Write path: Google Apps Script web app (doPost appends a row; execute as spiff; access: anyone). spiff deploys it in the
  browser (three minutes); the script and steps go in docs/setup.html. The page stores the endpoint URL in localStorage
  and in a config field, so no rebuild is needed to switch it on.
- Read path (Phase 3): the sheet published as CSV (File, Share, Publish to web) fetched by scripts/pull_sheet.py, or the
  Google MCP. Last write per item wins; keep all rows in data/decisions_raw.json.

## 7. Phase 3: from decisions to v0.2

- scripts/apply_decisions.py reads decisions.json and data/decision_effects.json (seeded from the dependencies and the
  quick-accepts: each effect is {when: item_id=key, edit: {screen, field, op, value, cause}}), produces screens_v02.json.
- scripts/diff_screens.py writes changelog.json: per screen, added / removed / changed with the cause (decision id or
  input row).
- Rebuild the site with the v0.2 tab and the Changelog tab. Update admin_crm.json where a decision touches it (payment
  methods, nudge channels, admin tool choice, records list) and note the cause on the row.
- Commit with the message "v0.2 from meeting decisions <date>"; report the URL.

## 8. Phase 0 commands (adjust for what is installed)

- gh auth status; gh repo create yeslyf-wireframes --private --source=. --push (or init and create separately).
- Enable Pages from main, folder /docs: gh api -X POST repos/<user>/yeslyf-wireframes/pages -f build_type=legacy
  -f source[branch]=main -f source[path]=/docs. The site URL is https://<user>.github.io/yeslyf-wireframes/.
- Warning to surface to spiff verbatim: on GitHub Pro or Team, a Pages site built from a private repository is still
  publicly reachable by URL; access-controlled Pages exist only on Enterprise Cloud. Keep no personal data on the site
  (there is none in these files beyond first names), keep noindex on, and share the URL only with the team.
- Python 3 for scripts; Node for extracting the v0.1 data (vm context). No frameworks, no build tools beyond that.

## 9. Seed: open items (starting list; refine from inputs.json, keep the attribution exact)

Team
- T1 SKU set at launch. Positions: Bhuvanaa (deck slide 11): one-time plan with a 45-minute session, and a monthly
  membership with quarterly reviews; Bhuvanaa (review P01): drop the one-time, at most two options, maybe an explainer
  video; Kajal (review X00): a no-call SKU on day one at a different price; Vatsal (brief): DIY at a low monthly price,
  DIWM is DIY plus calls, same app. Options: cards proposed as checkboxes with holders.
- T2 Calls model per tier. Positions: Bhuvanaa (message): 45-minute plan call plus 15-minute quarterly check-ins for DIWM;
  Vatsal (chat): one plan call at delivery, quarterly review automated in-app, extra calls paid; Gaurav (K04): no one-off
  calls for DIY; Kajal (K04, H07): planner call, not advisory; only Harish can discuss investments; bandwidth; Somil
  (K04): a review call only after execution.

Bhuvanaa and Harish
- S1 Who takes the DIWM plan call, certification, capacity. Inputs: Kajal (K01); Vatsal (chat): about 3 adviser-hours per
  client-year, one person tops out near 450 clients a year. Default: Bhuvanaa and Harish to decide.

Bhuvanaa
- B1 Pre-paywall sequence. Default Bhuvanaa (deck): reveal, two videos, sample plan, paywall. Positions: Gaurav (R12):
  convinced users go to the paywall, the sample is for the unconvinced; Kajal (R11): one video; Somil (R11): two videos
  back to back feels off; Bhuvanaa (R12): show real plan screens in the sample; Bhuvanaa (R09): more descriptive.
- B2 Clarity picture (G02). Default Bhuvanaa (G02): drop, it delays the plan. Position: Vatsal (chat): keep post-paywall as
  the first output and the adviser's call brief. Fact from spec v0.1: G03 already carries the snapshot and the concerns.
- B3 Retirement model. Bhuvanaa (L02): withdrawal rate, decide how. Fact: the FP React uses depletion to life expectancy.
  Default: Bhuvanaa to decide.
- B4 Tax section (G08). Somil (G08): drop or modify; needs Bhuvanaa and Harish. Default: Bhuvanaa to decide.
- Quick-accepts for Bhuvanaa: Gaurav's copy and selector suggestions (A01, R01, R02 two-row selector, R02 city, R04
  callout, R07 type-your-own); Harish's D03/D04 detail screens; Gaurav's O01 adviser weight; Kajal's O02 step wording.

Harish
- H1 Asset classes in the grid. Default Harish (L03, L02): no cash in recommendations, liquid debt is the shortest bucket;
  add a bucket for REITs and InvITs. Position: Vatsal (brief): five classes, cash, debt, hybrid, commodities, equity.
- H2 Where portfolio constraints live (L04): max per product, max direct shares within equity, category tagging.
  Harish to decide; possible form: a constraints screen L09 validated at staging.
- H3 Risk profiling method. Default Harish: the HoA 8-question RPQ band (his questionnaire). Position: Bhuvanaa (D09):
  tolerance plus capacity plus need, logic available. Somil works with Harish.
- H4 Insurance aggregator links (E01). Position: Bhuvanaa (E01): link through aggregators like PolicyBazaar. Harish to
  decide (compliance).
- H5 Refund policy (Q03). Harish (Q03): check RIA refund rules. Fact: the current agreement refunds the unexpired period
  less a breakage fee of at most one quarter's fee. Harish to decide with Kajal.
- H6 Records for audit (L08). Harish (L08): check what must be saved. Fact: the admin/CRM spec (Vatsal and Kajal) lists
  nine records. Harish to confirm with Kajal.
- Quick-accepts for Harish: none pending beyond his own accepted items (rationale storage, emergency months).

Gaurav
- G1 Execution rails. Default Gaurav (X00): all execution via smallcase Gateway only. Positions: Vatsal (brief): BSE StAR
  MF for mutual funds, smallcase for ETFs; Harish (E03, E04): unsure how either integration looks. Condition attached
  (Harish, compliance): direct plans and the RIA code must hold on whichever rail.
- G2 Admin tool over the database. Gaurav (M01): Appsmith? Fact: the admin/CRM spec (Vatsal and Kajal) proposes Directus
  with a two-day trial. Gaurav to decide with Kajal.
- Quick-accepts for Gaurav: none; his own tech notes (OTP backoff, captions, bundling, AA OTPs) are accepted.

Vatsal
- V1 Community placement (H08). Positions: Gaurav (H08): menu only; Bhuvanaa (deck slide 25): on the returning-client
  home; Harish (H08): asks where. Vatsal's position: a one-line strip on home, community from the menu.
- V2 Human-call as a nudge channel (N01). Position: Harish (N01): more nudges, offline calls too. Vatsal and Kajal to decide.
- Accepted (not shown): Kajal's H10 goals progress and H11 portfolio; Somil's H00 navigation map; Gaurav's H05 banner,
  H06 entry, H09 rebuild rule; Bhuvanaa's Q02 wording and Q04 referral.

Kajal
- K1 Payment methods and GST. Default Kajal (P04): UPI and netbanking only, no cards; GST split logic. Position: Harish
  (P04): subject to regulatory approval on payment types. Fact: v0.1 (Vatsal) drew UPI autopay, card, netbanking.
- Quick-accepts for Kajal: Gaurav's coupon field (P04).

Dependency blocks (Vatsal recommendation allowed here):
- If T2 removes one-off calls for DIY: K04 becomes an upgrade prompt; H07 DIY card changes.
- If T1 has no one-time card: P01 two cards, the 60-day credit rule goes, subscription-conversion KPI goes.
- If G1 is smallcase only: E02 and E03 collapse into E04; the one-time setup becomes a broker login.
- If B2 drops G02: fold realisable-vs-locked, allocation and current return into G03.
- If H2 wants constraints: new L09 validated in L05.
- If V2 adds human calls: nudge policy gains a channel value and Zoho creates tasks.

## 10. Seed: gaps (Vatsal recommendation; suggested owner by first name)

G01 Brand name lock (yeslyf vs Yesly vs Yalpho) - Team - High.
G02 SEBI advertisement code review of reveal, sample plan, testimonials, listing, nudges - Harish - High.
G03 DPDP consent notice and deletion - Harish - Med.
G04 Adviser capacity number and slot design - Bhuvanaa and Harish - High.
G05 Vendor onboarding critical path with owner and dates (AA TSP and FIU, Digio, Razorpay, smallcase or BSE, WhatsApp,
    Zoho) - Kajal - High.
G06 Documents owed: RPQ scoring map, fixed-fee agreement with the app as a channel, risk logic - Harish, Bhuvanaa - Med.
G07 Analytics instrumentation rule: every screen ID is an event - Gaurav - Low.
G08 Content production list with screen IDs - Bhuvanaa - Med.
G09 App store financial-app requirements - Gaurav - Low.
G10 Date protection: define V1 without in-app execution - Vatsal - High.
G11 Existing HoA clients into the app after launch via assisted onboarding - Harish - Low.
G12 Support staffing on day one - Kajal - Med.
G13 Closed beta with thirty community members in January - Vatsal - Med.

## 11. Acceptance checks before sharing the URL

- Every open item shows at least one name; no item shows the word recommendation; no page contains "founders".
- Team items have nothing preselected; owner items preselect the owner's position only.
- Every input row (73) has a status and appears on the Inputs tab with its author.
- The wireframe and admin tabs load from docs/v01/ and their screen IDs deep-link.
- Export works with the sheet endpoint blank.
- noindex present; Pages URL loads over HTTPS; spiff has reviewed the defaults before anyone else sees the page.

## 12. Status, 10 Sep 2026

Closed. Phases 0, 1a, 1b, 1c and 2 shipped and the meeting ran on the live site on 9 Sep 2026.
- Repo spiffler33/yeslyf-wireframes, private, Pages from main /docs: https://spiffler33.github.io/yeslyf-wireframes/
- Data layer complete: screens_v01, admin_crm, review_rows_v01, decision_board_v01, inputs (73 rows, every row with
  a status), ownership, open_items (18), gaps (13).
- Sheet write-back live and tested end to end: the Google Sheet "yeslyf decisions" with tabs decisions, gaps and
  quick_accepts, written by the Apps Script web app. The sheet id and endpoint are in .local/sheet.json, gitignored.
- The meeting brief is at inputs/meeting/yeslyf_meeting_brief_2026-09-09.md.

Superseded. Sections 7 to 11 of this file are replaced by plan_v2.md; do not run Phase 3 from here.
Sections 1 to 6 still hold: the repo, the data layer, the ownership map and the attribution rules are unchanged.

Known limitations carried into v0.2.
- The header date on the generated site is pinned to the meeting date in scripts/build_site.py; change it there,
  not in docs/.
- Two items in the meeting brief need resolving before they can be applied: T1 carries all four SKU options
  ticked, including the one-time card whose dependency block removes the 60-day credit rule; T2 records no
  choice, only the note "DIY no calls at all only a la carte, DIWM - 4 qtrly review calls".
- Every sheet row and the brief header carry the name of whoever ran the meeting screen, not the owner of the
  item. The owner of each position is fixed by data/open_items.json and the ownership map, not by that field.
- plan_v2.md section 0 holds two defaults that become Vatsal's decisions if the plan is run unedited.

## 13. Status, 10 Sep 2026 (v0.2 shipped)

plan_v2.md ran end to end (phases 3 to 8). The live site carries the v0.2 tabs: Wireframes v0.2 (188 screens,
21 templates, filters for tier, path, state, compliance and template, comment controls writing to the
v02_comments sheet tab), Admin and CRM v0.2 (with the CRM backlog and the v0.2 nudge matrix) and Changelog.
The Meeting, Gaps and Inputs tabs are frozen with the decisions shown; docs/v01/ stays byte-identical.
- Data layer: data/decisions.json (from the sheet export in inputs/meeting/, cross-checked against the brief),
  data/decision_effects.json (section 3 edits with causes), data/screen_meta_v02.json, data/compliance_reasons.json,
  data/fp_react_inputs.json (branch B), data/v02/ (spine.json, states.json, flow.json, the hand-drawn screens and
  the per-phase edit files), data/screens_v02.json and data/changelog.json (generated by scripts/apply_decisions.py).
- Scripts: pull_sheet.py, apply_decisions.py (with gen_spine.py and gen_states.py), validate_v02.py (checks 1 to 7),
  build_site.py (with renderer_v02.js and renderer_v02.css), check_site.py (checks 8 to 10).
- Open: the to-be-verified list (24 items) and the three build gaps (G14 to G16, data/gaps.json v02 key) are on
  the Changelog tab.
- 11 Sep 2026 (spiff): no Apps Script redeploy. Reviewers comment on the Wireframes v0.2 tab and press Export
  comments; the markdown file goes to spiff. The sheet write path stays as deployed for the meeting tabs.
- Next: the second review round through the v0.2 tabs, then the CRM planning session off the CRM backlog.

## 14. Status, 11 Sep 2026 (phase 9 shipped)

Phase 9 ran from a chat brief (Vatsal, 11 Sep 2026; recorded in plan_v2.md section 9) in four commits: 9a no
client-data assumptions, 9b data-capture improvements, 9c split status, 9d audience files. Live at the Pages URL.
- Closed: every number in a plan is the client's own, exact or a band they chose; bands are fixed per field (M2
  tables 9.1 to 9.5 where a table exists, else "Rs ___" chips); a not-sure field blocks the build and D13 Quick
  ranges collects a band for it; L02 keeps engine assumptions only; the word "assumed" survives on D07b alone
  (default accepted). D02 and D04 are multi-selects; confirm or correct on every prefilled screen; Q06 and Q06a
  (life events) reachable from H01, H07, H09, Q01 and N04; AA fetches in the background (A05, A06, then D01;
  A07, A08, A09 are states); "Why this one matters" on every number and detail screen; section strip, relief cards
  (D12a to D12h), section map on O02, silent autosave on exit, O03 as the reminder picker. D05, D06 and D08 carry
  status "split"; dropped is R11, G02, G08. Three audience files under docs/audiences/ (team, Spinach,
  compliance), self-contained, listed on the Changelog tab with sizes and linked from index.html.
- Counts: 191 live screens (D13, Q06, Q06a added), 21 templates; changed 63, added 110, dropped 3, split 3,
  rerouted 4, superseded 4, to be verified 23. Gaps: G14 done, G15 and G16 not needed, G17 new (which fields have
  an M2 band table; M2 is not in inputs/).
- Data layer additions: data/v02/phase9_edits.json (edit groups; groups with "stage": "after_generation" apply
  after the spine and states are generated), spine.json "strip", "prefill" and "multi_parent" keys,
  fp_react_inputs.json "fallback": "band required" on every field. Scripts: build_audiences.py, check_phase9.py
  (checks 1 to 10, then 11 to 17), new ops in apply_decisions.py (table_remove_row, field_replace, status, split).
- Known limitations: the relief cards draw Keep going as a button and Remind me later as a link (the spec calls
  them chips); the prefilled state exists on the six number screens that can arrive prefilled and on Q05 only; the
  site's Wireframes v0.2 tab offers eight identities, the team file the seven asked for; the A screens that sit in
  the Data section (A05 to A10c) are not spine screens and carry no exit line.
- Review link (Vatsal, 11 Sep 2026): docs/review/ holds the same Wireframes v0.2 and Admin and CRM v0.2 pages
  with only their two tabs and no setup link, at https://spiffler33.github.io/yeslyf-wireframes/review/. One
  link for the team, Spinach and Compliance; everyone picks an identity, gives verdicts and presses Export
  comments. The audience files stay as built and are not the review channel.
- 16 Sep 2026 (cause Kajal, 16 Sep 2026; plan_v2.md section 10): E10 SIP mandate registration and E11 Set up monthly
  SIPs added to section E; E01, E02 and E03 wired to them (data/v02/sip_mandate_edits.json, flow.json). Counts: 193
  live screens, 21 templates; added 112, to be verified 26. Checks 1 to 17 pass. Pushed; confirmed on the review link (spiff, 16 Sep 2026).
- 16 Sep 2026, phase 10b (Vatsal): the Integrations tab. data/integrations.json (22 rows I01 to I22 from Kajal's
  integration list and admin/CRM v0.2; owner, status, the three dates, docs, cost, notes and a comment editable in
  the page, saved per browser and posted to the v02_integrations sheet tab when the endpoint is set; screens, gates,
  fallback and cause generated), scripts/build_integrations.py (called at the end of build_site.py; writes
  docs/integrations.html and docs/review/integrations.html; cross-checks every vendor name against the live v0.2
  screens and marks I01, I02 and I09 "to be verified: screens"), the tab on every page and on the three review pages.
  Layout: one line per row, a click opens the panel (facts left, edits right); counts and the long pole as chips.
  Owners (Vatsal, 16 Sep 2026): Kajal, Vatsal or Spinach; Gaurav on DevOps; Gaurav and Raafiya on the HoA Core
  Platform; Compliance and Harish on the store declarations. One vendor per row; alternatives only on I13 (journey
  tool, decision by 19 Sep 2026) and I15 (Directus). Google and Apple sign-in are later in the journey (P02, where
  the email is asked), not later in dev; entry is always mobile OTP. Known limitations: the P02 sign-in step is not
  drawn in v0.2; every status starts at "not started" until its owner sets it; edits live in each reviewer's
  browser unless the endpoint is set (Export brief is the record). Commits f3896a2 and 99de140, pushed.
- 16 Sep 2026, phase 10b-2 (Vatsal): "Owed to Spinach" under the integrations table, and the Events tab.
  data/dependencies.json (W01 to W09, the nine items of the team message of 16 Sep 2026, in message order; cause on every
  row "Vatsal, 16 Sep 2026, Spinach agenda item 7"; owner, due date, status (not started | in progress | delivered), notes
  and a comment editable in the page, saved like the integrations rows; posted sheet rows carry a trailing type column,
  integration or owed, with the item in the vendor column for owed rows). docs/events.html and docs/review/events.html
  (scripts/build_events.py, called after build_integrations): 540 rows = 193 screen_view (one per live screen) + 339 named
  events (one row per event per screen, the screen's own _view excluded; 246 unique names) + 8 core actions from
  data/events_extra.json (action_started, action_done with verification aa_verified or self_reported, review_opened,
  review_accepted, life_event_reported, nudge_sent, nudge_opened, open_organic); the standard properties user_id,
  screen_id, tier, state, sku, source_choice, timestamp on every event; the appendix D properties per named event; a
  section filter; markdown export; no comment control. "Events" tab on every page and on the four review pages. Known
  limitations: nudge_sent, nudge_opened and life_event_reported appear both as named rows and as core actions by design;
  W03 and W04 carry two dates each, the earlier in due_date and both in notes; the header nav (11 tabs) wraps to two lines
  at 1280. Commit a3d902e, pushed; both pages checked at 1280 and phone width.
- Next: the second review round on the review link (reviewers press Export comments; the markdown goes to
  spiff; owners set status and dates on the Integrations tab and the Owed to Spinach rows), then parse the comments into data with causes,
  rerun the scripts, commit per phase; then the CRM planning session off the CRM backlog.

## 15. Status, 16 Sep 2026 (phase 11: Supabase write-back, append-only, no login)

- The Apps Script endpoint is gone. Every comment, verdict and field edit on every page inserts one row in the
  Supabase table board_entries (id, page, item_id, field, value, who, kind, created_at); nothing is ever updated or
  deleted. supabase/migrations/20260916120000_board_entries.sql creates it: RLS on, policies anon insert and anon
  select, no update or delete policy, and the update, delete and truncate privileges revoked so a client attempt is
  refused with 42501 instead of matching zero rows; the insert grant names the columns, so a client cannot set id or
  created_at. Run once in the dashboard SQL editor (the steps are on docs/setup.html).
- docs/config.js holds SUPABASE_URL and SUPABASE_ANON_KEY; every page loads it from the head (the review copies as
  ../config.js; the audience files do not load it and stay local only). It is the one hand-filled file in docs/:
  build_site.py creates it blank when it is missing and never overwrites it. The key is the public client key (RLS is
  the guard); no secret or service key anywhere in the repo.
- scripts/board_store.js is the shared save layer, inlined in every page as window.yeslyfBoard. init({page, apply})
  sends the outbox, fetches the page's rows (1000 at a time, id order), hands the latest value per item and field to
  the page and paints the top bar pill: "live, last write <time>" (the last write on that page by anyone) or
  "offline, saved locally". write({item_id, field, value, who, kind}) inserts a row; when the insert fails the row
  is queued in localStorage ("yeslyf_entries_v1") and sent on the next load. A History toggle under each comment box
  lists every row of the item, newest first, queued rows on top. Requests carry the key in the apikey header only
  (a publishable key is refused in Authorization; the legacy anon key works the same way).
- Row conventions. page "board" (Meeting, Gaps and Inputs share it): item_id item:T1, qa:12 or gap:G03; choice and
  accept are verdicts, note is a comment, decided, status, owner and date are field edits. page "wireframes_v02":
  item_id the screen id; verdict (verdict), reason (field_edit), text (comment). page "integrations": item_id I01 or
  W01; owner, status, the dates, docs_url, cost, notes, due_date (field_edit) and comment (comment). admin_v02,
  changelog and events write nothing; the pill only. Every editable control on every page writes a row; filters,
  sorting and the identity picker do not (the identity rides on every row as who).
- Each page's localStorage store stays as the offline cache. On load a remote row wins over the local value unless a
  queued (unsent) local row exists for the same field. Values saved in a browser before phase 11 are shown until a
  remote row for that field exists; they are not uploaded by themselves (touch the field again to record it).
- Read path: scripts/pull_board.py exports every row to data/board_entries.json (rows in id order plus the latest
  row per page, item and field). It reads the config from docs/config.js through a Node vm, or from the environment
  variables of the same names. Run it before any v0.3 build; data/board_entries.json is the input to the next edit
  group, never docs/.
- Verified 16 Sep 2026: the body of wireframes_v02.html, admin_v02.html, integrations.html and events.html (and of
  the review copies, index, gaps, inputs and the two v0.1 frame pages) is byte-identical outside the script tags to
  the build before phase 11; checks 1 to 17 pass. Against a local mock of the REST endpoint: a verdict and a comment
  written in one browser appear in a second browser (fresh storage) after a reload, with the pill live and the last
  write time; a comment written while the insert fails shows "offline, saved locally" and is sent on the next load;
  PATCH and DELETE with the anon key are refused. The same checks run against the real project once docs/config.js
  is filled (the curl lines are in the handoff).
- Changed outside the script tags, on purpose: docs/setup.html (the Apps Script instructions replaced by the
  Supabase steps), the three audience files (the Sheet endpoint field removed from the header) and the one sentence
  on the Changelog tab that described that field, and (6e72ef3, Vatsal, 16 Sep 2026) the Integrations lead, now
  "Every edit is recorded as it happens and shows on every device".
- Known limitations: the outbox is sent on the next load only (no retry while the tab stays open); the latest value
  per field follows insertion order (id), not the client clock; a row the server rejects (a wrong key, a missing
  policy) stays queued and the pill stays offline until a later load succeeds; the Meeting page's frozen controls
  (choices, quick-accepts, gap fields) are disabled, so only the item notes write rows there; docs/sheet_template.csv,
  data/sheet_template.csv and scripts/pull_sheet.py stay as the record of the v0.1 sheet path.
- 16 Sep 2026, later: project created, migration run, docs/config.js filled and pushed (cdfbce8). Live checks passed
  against the real table (insert, select, update and delete refused with 42501, bad kind refused, pull_board.py) and
  on the review link (a verdict and a comment on A02 seen from a second browser after a reload). Test rows stay in the
  table: page setup item TEST, and A02 Keep by Kajal.
- Phase 11 closed 16 Sep 2026 (commits 0dd4af0 to 6e72ef3, pushed). Next: the second review round on the review
  link with the pill live; reviewers' rows reach the table as they type; scripts/pull_board.py copies them into
  data/board_entries.json when the next edit group is built.
