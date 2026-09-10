# plan_v2.md - yeslyf wireframes v0.2

Owner of this plan: spiff (Vatsal). Executor: Claude Code in the yeslyf-wireframes repo.
Read CLAUDE.md first; its rules override this file. Read PLAN.md sections 1 to 6 for the repo, the data layer,
the ownership map and the attribution rules; they still hold. This file supersedes PLAN.md sections 7 to 11.

What v0.2 is: the accepted v0.1 skeleton (87 screens, IDs permanent) regenerated from the data layer with
(a) the 9 Sep 2026 meeting decisions applied, (b) section D (data collection) rebuilt around one spine that
serves both the Account Aggregator path and the manual path, (c) section N (returning-user states) completed
into a contract per state, (d) the admin and CRM spec updated for the new states and channels. Not a redraw.
The v0.1 files stay under docs/v01/ untouched.

Voice of this file: decisions marked "Vatsal, 10 Sep 2026" are product decisions taken by Vatsal in chat after
the meeting. Where such a decision touches another person's workstream (ownership map, PLAN.md section 2), it
enters v0.2 as a working draft with the owner's name on it and appears in the "open for owner" list (appendix E).
Nothing in this file is written as a decision taken on anyone else's behalf.

## 0. Two defaults Vatsal confirms by editing this file before running it

By running this plan unedited, these two defaults become Vatsal's decisions.

- DEFAULT-1 Investment plan for users whose holdings are not AA-fed or CAS-verified: G11 (allocation) renders;
  G12 (existing holdings: hold or exit) renders as one locked card with two unlock actions (connect AA, upload
  CAS); G13 (what to buy) renders with buy advice for new money only and one line saying existing holdings were
  not assessed. This is the v0.1 G12 rule ("manual entries get buy advice only") drawn as screens. Harish owns
  the compliance wording of the locked card.
- DEFAULT-2 One-time SKU (T1 card c) and the day-7 stall: if a one-time user has not met the build gate by day 7,
  the 45-minute session can be brought forward and used as an assisted-completion call. Who takes it follows
  S1 (Priya) unless Bhuvanaa and Harish decide otherwise (adviser-staffing workstream).

## 1. Inputs and precedence

1. inputs/meeting/yeslyf_meeting_brief_2026-09-09.md (spiff drops this; the export of the meeting sheet). If the
   sheet is reachable, scripts/pull_sheet.py runs first and the md is the cross-check; the two must agree, else stop
   and ask.
2. data/inputs.json statuses and the review-log dispositions already in the repo.
3. inputs/hoa/ documents, in this order where they conflict: the FP React component; the V5 journey script
   (App_Complete_Journey_without_community); Bhuvanaa's V2 deck; backend_m2_data_collection. Where V5 and M2
   conflict (band tables), V5 wins because it is later and it is the question owner's own script.
4. This file for everything the decisions do not cover (sections 4 and 5).

Attribution references used below: "brief T1" means the meeting brief item T1; "row 59" means review row 59;
"V5 Stage 3" means the V5 journey script; "deck slide 11" means Bhuvanaa's V2 deck; "spec v0.1 <ID>" means the
v0.1 wireframe screen; "Vatsal, 10 Sep 2026" means the post-meeting chat.

## 2. CLAUDE.md additions (append verbatim as a new section "v0.2 rules"; do not change existing lines)

- Dropped screens keep their ID and stay in data with status "dropped" and a pointer to where their content went.
  They are listed on the Changelog tab under "dropped" and never render in the flow. Every branch that pointed
  at a dropped screen is rerouted and the reroute is a changelog line.
- Returning-user state IDs S1 to S15 are permanent. New states get the next free number (S16 onward).
- A working draft on another owner's workstream is allowed only when Vatsal instructs it in writing. It carries the
  owner's name, the text "working draft, <owner> to confirm", and a line in the "open for owner" list. It is
  never labelled decided.
- A link whose target is its own screen is an in-place action (expander, download, upload). Its spec logic must say
  what it does. A self-link standing in for a screen that must exist is a bug.
- Conditions to verify are written as "<Name> to verify: <condition>". Never as facts.
- Every screen carries at least one event name in spec.events (appendix C). No screen without events.
- Meeting notes with no recorded speaker are written "meeting note, speaker not recorded (brief <item>)".

## 3. Phase 3 - apply the 9 Sep 2026 meeting decisions

Mechanics: extend data/decision_effects.json so scripts/apply_decisions.py produces these edits in
data/screens_v02.json with the cause on each. Where an item is a note rather than a recorded choice, the edit is a
working draft and the cause says so. Commit: "v0.2 phase 3: meeting decisions applied".

### 3.1 Team items

- T1 SKU set (brief T1, decided): P01 shows three cards: (a) Yeslyf Membership with adviser calls (DIWM),
  Rs ___ / month; (b) Yeslyf Membership, app only, no calls (DIY), Rs ___ / month; (c) Yeslyf Plan, one time,
  Rs ___, with a 45-minute session. Card (c) keeps the 60-day credit line (deck slide 11, Bhuvanaa). Since there
  are more than two cards, add a "video" element above the cards: explainer of the three options (brief T1 d;
  content owner Bhuvanaa, G08 content list). P01 spec.logic: remove the v0.1 "open point 1" and "Recommendation"
  text entirely; replace with "SKU set decided in the meeting, brief T1". Prices stay "Rs ___".
- T2 Calls model (brief T2: no choice recorded; meeting note applied as working draft, Team to confirm):
  DIY: no included calls; a la carte only (K04 stays for DIY, "Book and pay"). DIWM: the plan call (K01) plus four
  quarterly review calls included; K04 for DIWM becomes "Book your quarterly call" with no payment step; Q01 gains
  a DIWM line "Book your quarterly call" linking to K04. H07 DIY help card: remove "a human call is available
  whenever you want one" from O01's DIY card and H07; replace with "Calls are available a la carte from the Help
  tab". Mark every touched screen "working draft, Team to confirm (brief T2 note)".

### 3.2 Bhuvanaa and Harish

- S1 Plan call (brief S1, decided): K01 and O01 name Priya (CFP) as the DIWM adviser; K01 spec.logic replaces the
  "where spiff landed on calls" line with "Priya takes the DIWM plan call, brief S1". Capacity number stays gap G04.

### 3.3 Bhuvanaa

- B1 Pre-paywall sequence (brief B1, decided): reveal (R09) -> one video (R10) -> sample plan (R12) -> paywall
  (P01). R11 is dropped; its bridge content folds into the single R10 video script (copy owner Bhuvanaa; two edits
  of the video, with and without the call line, moves from R11 spec.logic to R10 spec.logic). R10 branches:
  Continue -> R12, Skip -> R12. R12: keep Bhuvanaa's accepted change (real plan screens in the sample; optional
  carousel of plan screens, rows 16 to 18 disposition).
- B2 Clarity picture (brief B2, decided): G02 dropped. G03 gains three rows in its ledger: realisable vs locked
  corpus, current allocation by class, current weighted return (dependency block, brief B2 "follows"). K01 dev
  note "Adviser sees G02 plus the plan" becomes "Adviser sees G03 plus the plan". All branches to G02 -> G03.
- B3 Retirement model (brief B3, decided): depletion to life expectancy as the FP React does. Add to L02
  assumptions: LIFE_EXPECTANCY 85, user-overridable to 90 or 100 (M2 registry). Add a line to G09 and G10 spec.logic:
  "Work-optional projection uses depletion to life expectancy, brief B3". Remove WITHDRAWAL_RATE from L02 if
  present; keep it in the M2 reference only.
- B4 Tax section (brief B4, decided): G08 dropped. G03 tab strip loses "Tax". G07 branches -> G09. Any tax line the
  FP React prints inside other sections stays where the React puts it (Bhuvanaa owns FP logic).
- Quick-accepts (brief, quick-accepts list): apply exactly as ticked in data/inputs.json: row 3 A01 declined;
  row 7 R01 declined; row 8 R02 declined with Bhuvanaa's note "Add pets" (see 4.6 D01 for placement); row 9 R02
  accepted; row 10 R04 accepted; row 11 R07 not ticked, stays quick-accept; row 15 R10 not ticked, stays; row 23
  O01 not ticked, stays; row 26 O02 (Kajal's wording) declined; row 31 G01 accepted; row 59 D03 and row 60 D04
  accepted with "additional screens needed" (D03a, D04a in section 4).

### 3.4 Harish

- H1 Asset classes (brief H1, decided): L03 grid columns become debt / hybrid / commodities / equity / REITs and
  InvITs. No cash class; the shortest bucket is liquid debt (label the short-term column "liquid debt"). Each row
  still sums to 100. G11 cards and the G11 chart use the same five classes; the short-term card reads "Liquid
  debt 100". Vatsal's earlier five-class position (brief H1, Vatsal, brief) is superseded; note it in the changelog.
- H2 Constraints (brief H2, decided): new L09 "Portfolio constraints", desktop frame: max weight per product; max
  direct shares within equity; category tag per instrument with manual override; validated in L05 before publish
  (L05 spec.logic adds "constraint breaches block publish"). L04 gains a link to L09.
- H3 Risk profiling (brief H3, decided): D08 stays HoA's eight questions verbatim; D09 band from the score.
  D08 spec.dev keeps "scoring map needed from HoA" (gap G06). Remove the tolerance-plus-capacity option text.
- H4 Aggregator links (brief H4, decided): E01 and E05 carry no aggregator links; E05 guided action stands.
  Remove any "link through aggregators" text.
- H5 Refund policy (brief H5: Harish to decide; note: per compliance, come back later): Q03 keeps its refund
  line as "per the agreement (Harish to confirm, brief H5)". No screen change.
- H6 Records for audit (brief H6: Harish to decide; note: data formats to be checked): L08 keeps the nine-record
  list from the admin spec with "Harish and Kajal to confirm formats (brief H6)".

### 3.5 Gaurav

- G1 Execution rails (brief G1: default, Gaurav's position, not confirmed in the meeting; note: new screens for
  BSE StAR onboarding, transactions, reporting): E02, E03, E04 stay as drawn. Add three screens as Gaurav's default,
  each marked "not confirmed in the meeting (brief G1)": E07 "BSE StAR MF onboarding" (UCC creation, FATCA, bank
  mandate, eNACH), E08 "BSE StAR MF transactions" (order status, mandate status, SIP calendar), E09 "BSE StAR MF
  reporting" (holdings and transaction statements into the Vault H06). Condition on all three: "Harish to verify:
  direct plans and the RIA code hold on this rail" (PLAN.md section 9, G1 condition).
- G2 Admin tool (brief G2: Gaurav to decide; note: ask Spinach to make a front end pulling the external admin
  tools): M01 adds a line "meeting note, speaker not recorded (brief G2): a Spinach-built front end over the
  bought tools is under consideration; Gaurav to decide with Kajal". No other change.

### 3.6 Vatsal

- V1 Community placement (brief V1, decided): H01 community card becomes a one-line strip; H08 reachable from
  the menu (H00 navigation map). H08 itself unchanged.
- V2 Human call as a nudge channel (brief V2, decided): N01 gains a channel value "human call"; the CRM creates a
  task for the caller (brief V2 "follows"). Section 5 carries the detail.

### 3.7 Kajal

- K1 Payment methods and GST (brief K1, decided): P04 shows UPI and netbanking only; no cards. GST split logic
  on the invoice: IGST, or CGST plus SGST, or no GST, by Kajal's rule (Kajal to supply the rule; placeholder
  text on P04). Gaurav's coupon field (row 21) accepted on P04. Remove "UPI autopay, card" from P04; keep UPI
  autopay for the monthly SKUs (Kajal to verify: mandate type for recurring UPI).

### 3.8 Gaps (brief, gaps list)

- G01 Brand name: "Yeslyf" (agreed, date set). In user-facing copy in screens_v02.json replace "yeslyf" with
  "Yeslyf". Repo, site title and file names unchanged.
- G02 SEBI advertisement code review, G03 DPDP notice and deletion: agreed with dates; no screen change beyond
  H09's existing delete-account line. Add to H09 spec.dev: "DPDP notice text pending (gap G03, Harish)".
- G04 to G13: no status recorded; no screen change. G07 (every screen ID is an event) is applied as a spec
  convention in v0.2 (appendix C) because the wireframe is the place the event names live; Gaurav owns the
  implementation and the gap stays open on the Gaps tab.

## 4. Phase 4 - rebuild section D: one spine for both paths

Commit: "v0.2 phase 4: data spine rebuilt". Owner of D01 to D10 questions, order and fields: Bhuvanaa. Everything
in this section that changes a question, its order or its fields is a working draft on Vatsal's instruction
(10 Sep 2026) and is listed in appendix E for Bhuvanaa. Screen mechanics (steps, autosave, ladders, filters) are
product and tech and carry no such marker.

### 4.1 Why (for the changelog and X00)

- v0.1 bug, found by Spinach: the manual path (A05 "Do it manually instead" -> D02) never asks a manual user for
  bank balances, deposits, mutual funds or stocks, and skips D01. A09's "Upload a CAS statement" button links to
  itself; no upload screen exists.
- Roughly 60 percent of the fields the plan needs are manual for every user, AA or not (family, expenses split,
  EPF, property, gold, insurance details, loans, goals, RPQ). The manual path is the main road; AA is a prefill.

### 4.2 First task: the FP React and missing inputs (do this before drawing anything)

Read the FP React in inputs/hoa/. For each field in appendix A, record whether the component tolerates a null or
undefined value (renders a section with a stated assumption) or breaks. Write the result to
data/fp_react_inputs.json: [{field, gate, tolerates_null, note}]. Then pick the branch and say which in the report:

- Branch A (the React tolerates unknowns): the build gate is the appendix A gate list; unknown gate fields are
  not allowed; unknown sharpen fields pass through as unknown and the plan copy says "you have not told me X yet".
- Branch B (the React needs a value for every field it reads): the build gate is every field the React reads.
  "Not sure" on any such field maps to a stated assumption from L02 (appendix A gives the source per field),
  tagged "assumed" in the profile, and the plan shows a verify action for it. The sharpen loop then works on
  assumptions instead of unknowns. Blindspot copy still reads the tri-state (4.3 rule 6).

Either way the data model rule in 4.3 rule 6 holds. Do not remove the gate concept under branch B; the gate list
just gets longer.

### 4.3 Standing rules for every D screen (put them on X00 as "baked into v0.2" and in each screen's spec)

1. One spine, both paths. AA users arrive with fields prefilled and tagged "AA-fed"; CAS users with holdings
   tagged "CAS-verified"; manual users with empty fields. No screen is bypassed on any path. Order (Vatsal, 10 Sep
   2026, working draft for Bhuvanaa): D01 -> D08 -> D09 -> D05 -> D06 -> D02 -> D03 -> D04 -> D07 -> D10.
2. Question sets render as one screen ID with a step counter (the D08 precedent in v0.1: "Question 5 of 8").
   The spec panel lists every step, its fields, its gate flag and its ladder. Number questions are one per step;
   tap questions may auto-advance. List items (family members, loans, policies, goals) are cards with a detail
   step behind each (D03a, D04a).
3. Band rule (V5 standing rule, Bhuvanaa): every band question shows a visible exact input; a tapped band prefills
   the exact field with the midpoint; exact removes the approx tag. Dynamic bands by income tier (V5 Stage 3,
   Bhuvanaa) replace the fixed M2 tables 9.1 to 9.5; midpoints are generated from L02 (new L02 rows: income tier
   boundaries and band multipliers). Per field the spec says which mode is primary: "exact-first" for numbers
   people know (take-home, EMI, premium, SIP amount) and "band-first" for numbers nobody knows (property value,
   gold, expenses split, goal cost).
4. Readback and units: every amount input shows a readback in words ("seventeen and a half lakh a year, about
   Rs 1.46 L a month"), a per-month / per-year toggle where the field can be either, L and Cr quick multipliers,
   and the numeric keypad (spec.dev). Plausibility checks against the reveal: take-home vs R03, corpus vs R04,
   EMI vs 30 percent of take-home; a large mismatch prompts a check, never a block.
5. Hesitation detection (V5 Stage 3, Bhuvanaa; restored): per step, at 45 seconds a warm line, at 90 seconds the
   "why this matters" line, at 120 seconds or on a second return the skip offer. Copy slots only; copy is
   Bhuvanaa's (gap G08).
6. Tri-state fields (Vatsal, 10 Sep 2026): every data field is one of value / explicit none / not sure. "None of
   these" chips set explicit none. "Not sure yet, skip" sets not sure. Not sure is never stored as zero. Blindspot
   and concern copy fires on explicit none only; not sure produces a verify action ("tell me your cover to check
   it") in G05, G07 and the action queue H04. Dev note for Spinach and the backend: M2's COALESCE(exact, band, 0)
   rule is superseded for not-sure fields.
7. Gate and sharpen (Vatsal, 10 Sep 2026): each field carries gate: true or false (appendix A). The plan builds when
   every gate field is value or explicit none. Sharpen fields appear inside the plan section they improve as
   "Sharpen this" links that reopen the single step and re-run (H05 shows the diff). Sharpen items that decide a
   verdict (ULIP years completed, loan rate) are also action-queue items.
8. Capture ladder (Vatsal, 10 Sep 2026): on every number step, below the exact input and bands, the lower-friction
   sources that exist for that item, in this order where they apply: AA (already fetched or "connect now" link to
   A05), CAS upload (A10), guided lookup (exact steps or an SMS or missed-call deep link), document to the Vault
   (H06, "drop it here and it gets read"), then "Not sure yet, skip". No partner ask (Vatsal, 10 Sep 2026: too
   intrusive at this stage; adds logic; removed everywhere). Appendix B lists the ladder per item.
9. Source and precision tags: every field stores source (aa, cas, manual, assumed) and precision (exact, approx,
   unknown). D10 and every G screen show them. A manual override locks the field against AA refresh (spec v0.1 A08,
   kept).
10. Section micro-feedback (V5 Stage 3, Bhuvanaa; restored): each spine screen ends on a one-card qualitative
    insight in the adviser's voice, chosen by the answers, before the Continue. No numbers in these cards. Copy
    slots only.
11. Endowed progress (spec v0.1 O02, kept): the ring starts at 20 percent after the reveal and is weighted by gate
    fields first, sharpen fields second. Per-screen minute estimates are placeholders "about N minutes" until the
    January beta measures them (gap G13).
12. Exit from any D screen: autosave (kept), then O03 "When will you finish?" (4.5). The chosen time schedules the
    first nudge; the standard ladder (section 5) follows.
13. Events: appendix C.

### 4.4 A05 to A10 - source choice and AA (the continuation sauce)

A05 "How should I get your numbers?" (rebuilt; sec D; tier ALL)
- purpose: make AA the obvious default by showing what it does now and what it keeps doing, while keeping the other
  three ways visible and honest. Vatsal, 10 Sep 2026: AA is not only faster capture; it is what keeps the plan
  alive (net worth on H02, the quarterly review Q01, the switch advice on G12). Present it as that.
- ui:
  - h: "Two ways to do this. One takes a minute and then keeps itself current. The other takes about N minutes and
    you keep it current by hand."
  - card (the default option, drawn larger than the others): "Connect via Account Aggregator": "Banks, deposits, mutual funds and stocks,
    fetched in about a minute"; "Your net worth and your quarterly review update themselves"; "Switch advice on what
    you already hold"; "Read-only. You pick the accounts. Revoke any time."
  - card: "What it cannot see (I will ask you either way)": "EPF, PPF, property, gold, insurance details, loans"
  - card: "Is +91 98xxx xxx21 the number your bank accounts know?": "Yes" / "Use another number" (kept)
  - card: "Which bank is your salary account with?": eight chips (top banks) plus "Other" - feeds the FIP health
    check (spec.dev)
  - btn: "Connect via Account Aggregator" -> A06
  - btn2: "Upload a CAS statement instead (holdings only)" -> A10
  - btn2: "Type it in (about N minutes)" -> D01
  - link: "Not now. I will type today and connect later" -> D01
- spec.logic: "Not now" and "Type it in" both set aa_status = not_connected and schedule two re-asks: the G12
  locked card and Q01. Neither path is penalised in copy. Minutes are placeholders measured in beta.
- spec.states: FIP degraded (Gaurav to verify: the TSP's FIP health API can be read before consent): the AA card
  shows "Your bank is slow right now. Upload a statement or type it in; I will fetch from the bank later" and the
  CAS and manual buttons move up.
- spec.dev: consent template asks for a periodic consent (fetch now plus quarterly for the review; validity as long
  as the TSP allows). Gaurav to verify with the TSP: maximum consent validity and fetch frequency permitted under
  the wealth-management purpose code. Store consent_status, consent_valid_till, fetch_frequency, last_fetch_at
  per FIP. Events: source_choice {aa, cas, manual, later}.

A06 (kept; add framing copy): the consent period and frequency are stated in plain words above the webview ("I am
asking for 12 months, fetched every quarter, read-only"). Numbers depend on the TSP verification above.

A07, A08 (kept). A08 branches: Continue -> D01 (both paths now start at D01). "Something is missing, add it
manually" -> D02.

A09 "AA partial or failed" (kept; fix): the CAS button -> A10. "Enter these manually" -> D02. "Continue with what
we have" -> D01.

A10 "Upload your CAS" (new; sec D; tier ALL)
- purpose: the best manual source for mutual funds and stocks, as a guided task with a reminder, not a bare upload.
- ui:
  - h: "Your CAS lists every fund and share you hold. Two minutes to request, it arrives by email."
  - card: "Request it": "CAMS or KFintech CAS (mutual funds)"; "NSDL or CDSL CAS (shares and funds)"; links open the
    request pages outside the app
  - p: "Look for the email subject 'Consolidated Account Statement'. I will remind you in an hour."
  - btn2: "Upload the PDF" -> A10 (in-place: file picker; password prompt: the password you set when requesting,
    or your PAN)
  - rows: parse result: fund or share, units, value, SIP detected
  - chips: "Looks right" / "Something is off"
  - btn: "Continue" -> D01 (or back to the step that sent the user here)
- spec.logic: parsed holdings are tagged cas-verified and count as verified for G12 sell and switch advice (spec
  v0.1 A09 rule, kept). Reminder in one hour and at 24 hours if not uploaded (state S17).
- spec.dev: casparser or a vendor (spec v0.1 A09). Vatsal, 10 Sep 2026: A10 is in V1; Gaurav to confirm whether
  parsing is additional effort and say so in the report.

### 4.5 D00 and O03 - before and between

D00 "Before you start" (new; sec D; tier ALL; reached from O02 step 2 and from A05 before the source choice on
first entry)
- ui:
  - h: "Have these open and it takes about N minutes. Without them, about 2N. You can skip anything and come back."
  - rows: "Salary slip or your bank app" / "Latest CAS, or I fetch it" / "Loan statement, or just the EMI" /
    "Term and health policy PDFs" / "EPF passbook (UMANG app)"
  - rows: per section, "about N minutes" (placeholders)
  - btn: "Start" -> A05 on first entry, else the first incomplete step
- spec.logic: shown once; a "What to have ready" link on O02 reopens it.

O03 "When will you finish?" (new; sec O; tier ALL; a sheet over any D screen on exit)
- ui: chips "Tonight" / "Tomorrow morning" / "This weekend" / "I will come back on my own"; btn "Save and exit" -> O02
- spec.logic: the chosen slot schedules the first push (WhatsApp if opted in) and skips the 24-hour default. "On
  my own" uses the standard ladder. Event: return_time_picked.

O02 "Your next steps (hub)" (rebuilt)
- ui: progress ring (endowed 20 percent); card 1 "Get your numbers in" with source status (AA connected on <date> /
  CAS uploaded / typing it in / not connected - connect for a live plan) and "Continue where you left off:
  <step>"; card 2 "Review and build" (enabled when the gate is met); card 3 "Book your plan call" (DIWM, after G01);
  link "What to have ready" -> D00; video "30-second walkthrough" (kept)
- spec.states: S3, S4, S5, S16, S17, S19 (section 5). Wording is a working draft (row 26 declined Kajal's; Bhuvanaa
  to confirm the new lines).

### 4.6 The spine

D01 "Family circle" (kept; entry for both paths; A08 and A05 manual both land here)
- Add a "Pets" card (yes or no; feeds a recurring expense line on D06) as Bhuvanaa's note "Add pets" (row 8,
  brief quick-accepts); placement is a working draft for Bhuvanaa.
- Partner card: name, age, earns yes or no (kept). Partner's own numbers are typed by the user on D05 and D02;
  there is no partner ask.
- gate: members[], has_dependants.

D08 "Risk profile (8 questions)" and D09 "Your risk profile" (moved early; working draft for Bhuvanaa)
- D08 unchanged in content (brief H3). D09 loses the declaration card and the "I confirm" chip; those move to D10.
  D09 keeps the band result and the retake line. Branch: D09 Continue -> D05.
- gate: rpq_answers[8], risk_band. No fallback: the gate cannot be met without the RPQ (SEBI suitability), which
  is why it sits early.

D05 "Income" (rebuilt as a question set; two states)
- steps: (1) your monthly take-home, exact-first, prefilled from AA salary detection when present, else the
  suggestion line "You said about Rs 17.5 L a year earlier; roughly Rs 1.2 L a month after tax?" from R03; hint
  "take-home, not CTC"; (2) partner's take-home, band-first, shown only if D01 partner earns; (3) rental income,
  exact-first, shown only if D02 investment property (or asked here with a yes/no gate); (4) business or other
  income, band-first, regular or lumpy.
- states: AA-fed (the v0.1 "here is what your money did" rows appear above step 1) / manual (rows absent; no "as
  best I can see" copy).
- gate: take-home. sharpen: the rest.

D06 "Expenses and existing investing" (rebuilt as a question set)
- steps: (1) total monthly outgoings, prefilled from R05 savings rate times income as a suggestion ("about Rs 1.3 L
  goes out each month?"), exact or band; (2) the three-bucket split (fixed / variable / guilt-free) as a three-way
  slider summing to the total, band-first, sharpen; (3) "how does the month typically end" (V5 Q1.4 four options)
  as the check; (4) already investing every month: SIPs and RDs, prefilled from AA debits when present, else
  exact-first.
- EMIs stay read-only, carried from D03 (M2 rule; kept). Surplus updates live (kept). Deficit state kept.
- gate: total outgoings. sharpen: split, month-end pattern, current SIP.

D02 "Your investments, by type" (rebuilt as a question set; replaces "Assets AA cannot see"; both paths)
- steps, one per item, each with its ladder (appendix B): bank balances and deposits; mutual funds; stocks and
  ETFs; NPS; EPF; PPF and post-office schemes; physical gold and silver (grams or value); property (home you live
  in: value, excluded from investable; investment property: value and rent); ULIP or endowment (surrender value,
  premium, years completed); anything else (crypto, international, business stake, other). Chips "None" per step.
- AA-fed steps show the fetched value with the tag and an "edit or add" affordance; CAS-verified steps likewise.
- gate: a value or explicit none on bank, mutual funds, stocks, EPF (the four the projection and allocation need).
  sharpen: the rest, and every detail behind a total.
- Under branch B (4.2), an unknown gate item maps to the R04 corpus band split by a default mix in L02 (new L02
  row "default asset mix for unknown split", Bhuvanaa and Harish to set) and is tagged assumed.

D03 "Loans and dues" (kept as the list; D03a new detail step)
- D03 asks per loan: type; EMI (exact-first, people know it); outstanding (band-first); years left (band-first).
  Rate is derived from the three and shown as "about N percent, correct it if you know it" (sharpen). Credit card
  carried balance: amount. Loans to or from friends and family (rows 59 disposition, Bhuvanaa and Harish). Chips
  "No loans" (explicit none).
- D03a: the detail step per loan (tax-deductible flag for home loans, prepayment allowed, lender).
- gate: has_loans, total EMI. sharpen: outstanding, tenure, rate, detail.

D04 "Insurance" (kept as the list; D04a new detail step)
- Step 1 per policy type (term, health, ULIP or endowment, other): "Have it and know the amount" / "Have it, not
  sure of the amount" / "Do not have it". Only the first opens the amount step; the second sets not sure and
  offers the ladder (find the policy schedule PDF in email; drop it in the Vault); the third sets explicit none.
- Health: employer only / personal / both / none (kept), sum insured band-first, family floater.
- D04a: per policy detail (insurer, premium, cover until age, years completed for ULIP).
- gate: term status, health status. sharpen: amounts, detail.

D07 "Goals and key life events" (kept)
- Suggested goals from the family circle (kept). Per goal: name, year, cost today band-first with "I am not sure
  yet" mapping to the persona estimate (V5 Q4.4b option F, Bhuvanaa), priority. Work-optional age default 60 (kept).
  Yes list (kept). Chips "No goals for now" (explicit none; plan covers emergency, protection, cashflow, debt and
  the work-optional projection, spec v0.1 D07 state).
- gate: at least one goal or explicit none, work-optional age. sharpen: costs, years.

D10 "Review, build, and what would sharpen it" (rebuilt)
- ui: rows per section with value, source tag and precision tag, each linking back to its step; card "Ready to
  build" listing gate status (met, or the missing fields with minutes); card "These would sharpen it" listing not-sure
  and approx fields with the plan section each improves; card "Your two paths, updated" (the R09 numbers re-run on
  what is now known, with the R06 tone variant; the only place numbers update during data entry, Vatsal, 10 Sep
  2026); card "Declaration" (moved from D09: the details furnished are true and correct; full text per HoA) with
  chip "I confirm"; btn "Build my plan" -> G01 (enabled when the gate is met and the declaration is confirmed);
  link "Edit a section" -> O02.
- spec.dev: snapshot of inputs as plan_input_version with source and precision per field (advice record).

### 4.7 G screens: the sharpen loop and the locked card

- Every G03 to G14 screen lists in spec.fields the fields it reads. Where a field is approx, not sure or assumed,
  the screen shows a "Sharpen this" link (in-place list) that opens the single D step and, on save, re-runs the
  engine and lands on H05 with the diff.
- G05 (protection), G07 (debt) and H04 (action queue): not-sure fields produce verify actions, never gap
  diagnoses (4.3 rule 6).
- G12 under DEFAULT-1: locked card "Switch and sell advice needs holdings I can verify" with btn2 "Connect via
  Account Aggregator" -> A05 and btn2 "Upload your CAS" -> A10. G13 buy advice only, with the one line. Harish owns
  the compliance wording; mark "Harish to confirm wording".
- G01 "Building your plan": add state "built on what we have (day 7)" with copy that names the number of assumed or
  not-sure fields.
- After delivery (S6 -> S18 in section 5): the "Sunday sharpen" ask - "Want me to ask you for the N numbers I am
  still missing on Sunday?" - as a card on H01 and a nudge slot.

## 5. Phase 5 - complete section N: a contract per returning-user state

Commit: "v0.2 phase 5: returning-user states completed". Owner: Vatsal (product); nudge structure Vatsal and
Kajal; nudge copy Bhuvanaa (gap G08); human-call channel per brief V2.

### 5.1 The contract

N01 (rebuilt as the master table, desktop frame) gets these columns per state: state ID; who; lands on (screen ID
and, for H01, the hero card variant); primary action; nudge ladder (day, channel, copy slot ID); human escalation by
tier (DIWM: CRM task for the caller per brief V2; one-time: the session under DEFAULT-2; DIY: none, a la carte offer
only); exit condition (the next state). Two new desktop screens hold the detail: N02 "Onboarding ladder (paid, before
the plan)" for S2b, S3, S4, S5, S16, S17, S19; N03 "Post-plan ladder" for S6 to S13, S18, S20 to S26.

Rules (Vatsal, 10 Sep 2026):
- One nudge per week maximum across layers (spec v0.1, kept) applies from day 14 after payment. Before day 14 the
  onboarding states may nudge at 24 hours, 72 hours and day 7 (spec v0.1 S3, S4 cadence, kept).
- Every nudge deep-links to the primary action and names the specific next step and its minutes; never "continue
  your journey".
- O03's chosen time replaces the first scheduled nudge when it exists.
- Human escalation creates a CRM task with the state ID, the missing fields and the tier; the caller enters inputs
  during the call and the engine re-runs; nobody edits outputs by hand (spec v0.1 rule, kept).
- Nudge copy slots are IDs (for example N-S4-72h); copy is Bhuvanaa's and lives in the CRM templates (M01).

### 5.2 States

Kept, with changes noted:
- S1 signed up, no reveal (kept). S2 reveal seen, not paid (kept; ladder day 1, 3, 7, 21, 82, stop).
  S2b paid, eSign incomplete (kept; refund path at day 14 per H5, Harish).
- S3 paid, nothing else: lands on O02 with D00 offered; ladder 24h, 72h, day 7 -> S19.
- S4 data partial: lands on O02 "continue where you left off: <step>"; ladder 24h, 72h, day 7 -> S19; O03 time
  first when set.
- S5 redefined (RPQ is now early, so "data done, RPQ pending" cannot occur): gate met, D10 not confirmed. Lands on
  D10; ladder 24h "two minutes to build"; exit to S6 on build, or to S18 at day 7 (rule 7 of 4.3, Vatsal).
- S6 plan built, not read (kept; 48h). S7 DIWM call booked (kept). S8 plan read, no action (kept; 48h, 7d, 14d).
  S9 executing (kept). S10 all actions done (kept). S11 plan updated (kept; 3d). S12 payment failed (kept; grace 7
  days; Kajal billing states). S13 lapsed (kept; 30d, 90d). S14 DIFM (kept). S15 AA consent expired (kept; lands
  on Q01 with re-consent first).

New:
- S16 AA not connected, manual in progress or done: lands on the spine or on H01 with the source line "last updated
  by you N days ago; connect Account Aggregator to keep this live" (H02 shows the same line). Re-asks at G12 (locked
  card) and Q01. Ladder as S4 while before the plan; after the plan, one line in the quarterly review only.
- S17 CAS requested, awaiting the email: lands on A10 "check your inbox"; reminder at 1 hour and 24 hours; exit on
  upload or on "type it instead".
- S18 plan built on partial data (day-7 build, or built with not-sure fields): lands on H01 with the sharpen strip
  and the Sunday sharpen card; ladder: the chosen Sunday, day 7, day 21; exit when no sharpen items remain.
- S19 stalled below the gate at day 7: lands on O02 with the exact missing fields and minutes; DIWM: CRM task for
  Priya to call (brief V2); one-time: session offer (DEFAULT-2); DIY: a la carte 15-minute call offer on K04 with
  "Rs ___". Ladder: day 7 (human where it applies), day 10, day 14, then monthly; exit when the gate is met.
- S20 call booked, no-show: lands on K01 rebook; 1 hour after, 24 hours; second no-show -> CRM task.
- S21 call done, no action started (DIWM): lands on K03 with the first action; 48h, 7d; exit on first action.
- S22 quarterly review ignored (Q01 not opened 14 days after generation): lands on H01 review card; 7d, 14d; DIWM:
  the quarterly call reminder (T2 working draft).
- S23 annual confirmation overdue (risk profile and agreement, Q04): 7 days before, day of, 7 days after. What
  happens to advice if not confirmed: Harish to decide (compliance); the wireframe shows the slot.
- S24 refund requested: Q03 path; slot only; H5 pending (Harish).
- S25 account deletion requested (H09): DPDP flow; regulated records retained; text pending gap G03 (Harish).
- S26 one-time plan delivered, 60-day credit window (deck slide 11, Bhuvanaa): lands on H01 with the credit card
  and countdown; day 30, 50, 58; exit on membership start or expiry.

Removed from the earlier draft (Vatsal, 10 Sep 2026): a "partner asked, awaiting" state. Do not add it.

### 5.3 Screens touched

- H01: spec.states lists every state that lands on H01 with its hero card variant (S6, S8, S9, S10, S11, S12, S14,
  S16, S18, S22, S26). H02: source and freshness line under the number. H04: verify actions from not-sure fields.
- Q01: manual state - for S16 users the first card is "Update N numbers" with the ladder (A10 again, exact entry)
  instead of the AA diff; the "Keep my manual number" chip stays for mixed users. DIWM line "Book your quarterly
  call" -> K04 (T2 working draft).
- K01: no-show state (S20). K03: S21 state. K04: tier states per 3.1. Q03: S24 slot. Q04: S23 slot. H09: S25 line.

## 6. Phase 6 - admin and CRM spec

Commit: "v0.2 phase 6: admin and CRM updated". Owner: Vatsal and Kajal (crm-and-nudges), Kajal (admin).

- PLACEMENT: the CRM platform name is "pending Kajal (one platform)". Where the v0.1 spec or brief V2 says Zoho, keep
  the text and add "(platform pending Kajal; the object model and the matrix are platform-neutral)". No other
  vendor name changes.
- NUDGES matrix: one row per state S1 to S26 per ladder step, columns: state, day, channel (push, WhatsApp, email,
  human call), copy slot ID, deep link screen, tier rule, CRM task (yes or no, task fields). Structure by Vatsal and
  Kajal; copy slots for Bhuvanaa (unchanged from v0.1's "for Bhuvanaa to fill").
- EVENTS: add every new screen event (appendix C) and the state_enter events.
- DEAL_FIELDS: payment_method (upi, netbanking), gst_type (igst, cgst_sgst, none), coupon (row 21), sku (three
  values from T1), credit_window_end (one-time SKU).
- CONTACT_FIELDS: aa_status, consent_valid_till, source_completeness (gate met yes or no; sharpen count),
  last_manual_update.
- COMPLIANCE records: unchanged; "Harish and Kajal to confirm formats (brief H6)".
- DECISIONS list in the admin spec: append the meeting items that touch admin (K1, V2, G2 note, H5 and H6 pending)
  with their attribution.

## 7. Phase 7 - the site, the renderer, the changelog, the checks

Commit: "v0.2 phase 7: site rebuilt". Never hand-edit docs/.

Renderer features (extend the v0.1 renderer; keep the grey low-fi style, Spinach owns visual design):
- Tier filter (kept) plus a path filter: AA / manual / both. A screen or step declares which paths show it; the
  filter walks each path end to end. Spinach asked for the manual path to be visible; this is how.
- State filter for section N and for H01: pick a state, see the landing screen and hero variant.
- "Changed in v0.2" marker on every touched screen with the cause (decision ID, input row, or plan_v2 section) and,
  where it applies, "working draft, <owner> to confirm".
- Spec panel gains: events; gate and sharpen flags per field; ladder per step; source and precision tags.
- Verdict and comment controls (kept) writing to a new sheet tab "v02_comments" through the existing endpoint;
  export still produces a markdown build brief. This is how the second review round runs.
- Tabs after the rebuild: Meeting (frozen as of 9 Sep, read-only with the recorded decisions), Gaps, Inputs,
  Wireframes v0.1, Admin and CRM v0.1, Wireframes v0.2, Admin and CRM v0.2, Changelog. Changelog tab sections:
  changed, added, dropped, rerouted branches, open for owner (appendix E, by name), conditions to verify (appendix
  D, by name).
- noindex on every page (kept). No personal data beyond first names (kept).

Acceptance checks before publishing (all must pass; print the results in the report):
1. Every branch target exists in screens_v02.json; no branch points at a dropped screen.
2. No self-link stands in for a missing screen; every in-place self-link has a logic line.
3. The manual path reaches every gate field in appendix A; the AA path reaches every D screen; neither path skips
   D01.
4. Every state S1 to S26 has a landing screen, a primary action, a ladder and an exit.
5. Every screen has at least one event name. Every D field has gate, source and precision.
6. Every touched screen shows its cause; every working draft shows its owner; no page contains "founders" or the
   word "recommendation" outside gaps and dependency blocks.
7. Team items show nothing decided beyond the brief; T2 and G1 read as working drafts.
8. The tier filter and the path filter both walk end to end without a dead end.
9. Export works with the sheet endpoint blank. Pages loads over HTTPS. noindex present.
10. docs/v01/ files are byte-identical to inputs/v01/.

## 8. Phase 8 - report and handover

Commit: "v0.2 from meeting decisions 2026-09-09 plus data spine and states, <date>". Then report to spiff, in this
order: the URL; the branch taken in 4.2 with the fp_react_inputs.json summary; changelog counts (changed, added,
dropped, rerouted); appendix E (open for owner, by name); appendix D (conditions to verify, by name); anything in
this file that CLAUDE.md would not allow and was therefore not done. Do not ask spiff anything that this file
answers. If blocked, batch at most three questions.

## Appendix A - gate and sharpen fields (working draft for Bhuvanaa on fields; Harish on the holdings rule)

Gate (the plan builds when each is value or explicit none). Branch B fallback in brackets.
- family: members, has_dependants [from R02 household type; partner earns assumed no]
- risk: rpq_answers, risk_band [no fallback; mandatory]
- income: take_home [R03 band midpoint, approx]
- expenses: total_outgoings [income times (1 minus R05 savings rate), approx]
- assets: bank_and_deposits, mutual_funds, stocks, epf [R04 corpus band split by the L02 default mix, assumed]
- loans: has_loans, total_emi [assumed none, verify action]
- protection: term_status, health_status [assumed none, verify action]
- goals: at least one goal or explicit none, work_optional_age [work_optional_age 60; goals none]

Sharpen (inside the plan section named):
- income: partner take-home, rental, other (G06)
- expenses: three-bucket split, month-end pattern, current SIP (G06)
- assets: NPS, PPF, gold, property values, ULIP detail, other (G03, G09, G11)
- loans: outstanding, years left, rate, D03a detail (G07)
- protection: sum assured, sum insured, floater, D04a detail (G05)
- goals: cost today, year (G09)

## Appendix B - capture ladder by item (order shown on the step, only the sources that exist for the item)

- bank balances, deposits: AA; bank app balance typed exact; band
- mutual funds: AA; CAS upload (A10); total typed; band
- stocks and ETFs: AA; NSDL or CDSL CAS (A10); total typed; band
- NPS: AA where the CRA is live (Gaurav to verify with the TSP); CRA statement to the Vault; band
- EPF: guided lookup - UMANG passbook, or the EPFO balance SMS and missed-call services (deep link with the message
  prefilled on Android; Gaurav to verify the current numbers and that the deep link works on both platforms);
  passbook PDF to the Vault; band
- PPF and post office: passbook or net banking; band
- physical gold and silver: grams (the app prices it from L07) or value; band
- property: what it would sell for, band; rent exact
- insurance amounts: policy schedule PDF in email, to the Vault; premium from the bank debit; band
- loans: EMI exact; outstanding and years left bands; rate derived
- ULIP or endowment: surrender value from the insurer app or the policy statement to the Vault; premium exact
- crypto, international, business stake, informal loans: typed; band
- Documents dropped in the Vault are read by the app (Gaurav to verify: V1 for CAS only via A10; other document
  extraction is V1.5 and the Vault drop stores the file until then)

No partner ask on any item (Vatsal, 10 Sep 2026).

## Appendix C - events (gap G07 applied as a convention; implementation is Gaurav's)

- every screen: <id>_view
- D steps: <id>_<field>_set {source, precision}, <id>_<field>_skip, <id>_hesitation_45, _90, _120,
  <id>_ladder_<source>, <id>_band_tapped, <id>_exact_entered
- A05: source_choice {aa, cas, manual, later}; A10: cas_requested, cas_uploaded, cas_parsed; O03: return_time_picked
- D10: gate_met, plan_built {assumed_count, unknown_count}; G screens: sharpen_opened {field}, sharpen_saved
- N: state_enter_<S>, nudge_sent {slot, channel}, nudge_opened, crm_task_created {state}
- Beta rule to record on X00 (Vatsal, 10 Sep 2026): if fewer than 70 percent of paid users in the January beta
  reach the gate within 7 days, the gate list is cut again before Spinach starts screens.

## Appendix D - conditions to verify, by name (print on the Changelog tab)

- Gaurav: A10 CAS parsing effort in V1; TSP FIP health API readable before consent; TSP maximum consent validity
  and fetch frequency under the wealth-management purpose; NPS CRA live on AA; EPFO SMS and missed-call numbers
  and the SMS deep link on both platforms; recurring UPI mandate type for monthly SKUs; document extraction scope.
- Harish: direct plans and the RIA code on the BSE StAR rail (E07 to E09); G12 locked-card wording; S23 outcome if
  the annual confirmation is not given; H5 refund policy; H6 record formats (with Kajal); DPDP notice text (G03).
- Kajal: the one CRM platform name; the GST split rule; billing states in Q03 unchanged.
- Bhuvanaa: everything in appendix E.

## Appendix E - open for owner confirmation, by name (print on the Changelog tab)

- Bhuvanaa: D order (D01, D08, D09, D05, D06, D02, D03, D04, D07, D10); the gate and sharpen split of fields;
  dynamic bands over M2 tables; restored hesitation copy and micro-feedback slots; D01 pets placement; O02 wording;
  the single R10 video script; P01 explainer video content; all nudge copy slots.
- Harish (with Somil): G12 and G13 rendering for unverified holdings (DEFAULT-1); L02 default asset mix for
  unknown splits (with Bhuvanaa); L09 fields.
- Team: T2 calls model working draft; G1 rail default.
- Kajal: DEAL_FIELDS additions; the platform name.
- Bhuvanaa and Harish: who takes the one-time session (DEFAULT-2).
