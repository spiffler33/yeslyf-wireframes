# plan_v2.md - yeslyf wireframes v0.2 (rewrite of 10 Sep 2026)

Owner of this plan: spiff (Vatsal). Executor: Claude Code in the yeslyf-wireframes repo.
Read CLAUDE.md (v2) first; its rules override this file. PLAN.md sections 1 to 6 still describe the repo, the data
layer and how the meeting site was built; sections 7 to 11 of PLAN.md are superseded by this file.

What v0.2 is: the accepted v0.1 skeleton regenerated from the data layer with (a) the 9 Sep 2026 meeting
decisions applied and the post-meeting product decisions layered on top, (b) section D (data collection) rebuilt
around one spine that serves both the Account Aggregator path and the manual path, drawn at instance level, (c)
section N (returning-user states) completed into a contract per state with a message-plus-landing mock per state,
(d) a compliance layer so the compliance reviewers can walk the flagged screens and comment on language, (e) the
admin and CRM spec updated, plus a CRM backlog for the later CRM planning session. The v0.1 files stay under
docs/v01/ untouched. Screen count goes from 87 to about 185 (appendix A); Spinach quotes off this set.

Who decides what in this file: the meeting brief is the team's record; post-meeting product decisions are Vatsal's
and are written "Vatsal, 10 Sep 2026". There are no owner markers and no working drafts. Everyone reviews v0.2
through the comment controls in the second round.

## 0. Decisions taken on 10 Sep 2026 that override the meeting brief (cause: "Vatsal, 10 Sep 2026 (supersedes brief X)")

- SKU set: two SKUs, DIY (app only) and DIWM (app plus adviser calls). No one-time plan card, no 60-day credit rule,
  no state S26. Each SKU is billed monthly or quarterly; the paywall carries a period toggle. Supersedes brief T1.
- Calls: the number of included calls per SKU per period is config ("N calls included this <period>"), never a drawn
  number or a drawn length. There is no "plan call" as a type; a call is a call, with a topic. Any adviser from the
  call centre takes any call. Calls explain (using the app, the plan, the investments and why the instruments and
  cohorts are what they are, what changed); nobody plans separately for a user; the app does not change per SKU.
  A la carte calls can be bought by anyone on any SKU. Calls can be booked at any time, before or after the plan.
  Supersedes brief T2 and the v0.1 K01 rule "bookable only after G01".
- Adviser: no named adviser on any screen. A config flag "adviser continuity" (off by default) lets the same adviser
  be offered again later without redrawing. Supersedes brief S1 in the wireframe only; the staffing discussion is
  not touched by this file.
- DIFM: not a shown SKU, no in-app upsell. DIFM clients exist in the app for tracking only (state S14, O01's DIFM
  card, dashboard without engine advice). Prospects are flagged in the CRM and called by the call centre; the rule is
  "total investable assets from D02 over Rs ___" plus a manual flag any adviser can set after a call. Goes to the
  CRM backlog (section 6).
- Investment plan for holdings that are not AA-fed or CAS-verified: G11 renders; G12 renders as a locked card with
  two unlock actions (connect AA, upload CAS); G13 renders buy advice for new money with one line saying existing
  holdings were not assessed. Compliance flag on the wording.
- Brand: "yeslyf", lowercase, everywhere. Brief gap G01 recorded "Yeslyf"; that was the sheet capitalising a cell.

## 1. Inputs and precedence

1. inputs/meeting/yeslyf_meeting_brief_2026-09-09.md (spiff drops it). If the sheet is reachable, scripts/pull_sheet.py
   runs first and the md is the cross-check; if they disagree, stop and ask.
2. Section 0 of this file, which overrides the brief on T1, T2, S1 and gap G01.
3. data/inputs.json statuses and the review-log dispositions already in the repo.
4. inputs/hoa/ documents, in this order where they conflict: the FP React component (now a .jsx in inputs/hoa/);
   the V5 journey script (App_Complete_Journey_without_community); Bhuvanaa's V2 deck; backend_m2_data_collection.
   Where V5 and M2 conflict (band tables), V5 wins because it is later.
5. This file for everything else.

Reference shorthand: "brief T1" = meeting brief item; "row 59" = review row; "V5 Stage 3" = the V5 script;
"deck slide 11" = Bhuvanaa's V2 deck; "spec v0.1 <ID>" = the v0.1 screen; "Vatsal, 10 Sep 2026" = post-meeting.

## 2. Rules that apply to every v0.2 screen (CLAUDE.md v2 carries them; repeated here for the builder)

- Cause on every change; no owner markers; "to be verified: <item>" without names; "yeslyf" lowercase.
- Every screen: ID, title, template tag (appendix F), tier set, path set (aa, manual, both), events (appendix D),
  compliance flag with reason category (appendix G), spec panel with fields, logic, branches, states, dev.
- Instances are drawn, not collapsed; template tagged.
- Placeholders: "Rs ___", "N calls", "about N minutes". Minutes get measured in the January beta (gap G13).

## 3. Phase 3 - meeting decisions and the section 0 overrides

Mechanics: extend data/decision_effects.json so scripts/apply_decisions.py produces every edit below in
data/screens_v02.json with its cause. Apply the brief first, then the section 0 overrides on top so the changelog
shows both. Commit: "v0.2 phase 3: meeting decisions and post-meeting overrides applied".

### 3.1 Paywall, payment, subscription (brief T1 superseded; brief K1; deck slide 11)

- P01 Paywall: two cards. Card 1 "yeslyf DIY, app only": your full plan on your numbers; refreshed every quarter; your
  progress and next action always visible; investment plan with exact instruments; a la carte calls whenever you want
  one; cancel any time. Card 2 "yeslyf DIWM, app plus adviser calls": everything in DIY; N calls included this
  <period> with the yeslyf advisers to walk you through the plan, the app and the investments; extra calls a la
  carte. Period toggle above the cards: monthly / quarterly, "Rs ___ / month" and "Rs ___ / quarter" on each card,
  shown inclusive of GST. No video (two cards; brief T1 d applied only for more than two). "Not sure yet" line and
  "Save and decide later" -> X01 kept. Remove every v0.1 "open point" and "Recommendation" line from spec.logic.
- P02 KYC (kept). P03 Agreement and eSign (kept; the agreement must reflect two SKUs and the period; compliance flag:
  fees and disclosures).
- P04 Payment (brief K1; row 21): UPI and netbanking only, no cards; recurring UPI mandate for the chosen period
  (to be verified: mandate type and limits for monthly and quarterly recurring UPI); GST split on the invoice
  (IGST, or CGST plus SGST, or no GST) by a rule to be supplied (to be verified: the GST split rule); coupon field.
- Q02 Change plan: switch SKU and period; proration line "to be verified: proration and refund on a period switch".
- Q03 Subscription states: split into instances Q03a cancel (reason, pause offer, confirm), Q03b payment failed (retry,
  grace 7 days), Q03c lapsed (read-only plan, refresh stopped, resubscribe restores). Refund line "per the agreement
  (brief H5: to be decided)".
- X01 Save and decide later (kept). The 60-day credit line is removed wherever it appears.

### 3.2 Calls (section 0; brief V2)

Rebuild section K as a generic call system, tier differences limited to entitlements:
- K01 "Talk to an adviser": entitlement line ("N calls included this <period>; Rs ___ per extra call" for DIWM;
  "Rs ___ per call" for DIY); topic picker chips: my plan / using the app / the investments and why they were chosen /
  something changed / my numbers; free-text "anything specific"; btn "Pick a slot" -> K05. Reachable from H07, H01
  cards, O02, D-section stalls (S19) and G screens.
- K05 "Pick a slot" (new): call-centre calendar, any available adviser; "adviser continuity" flag when on shows
  "Talk to the same adviser as last time" as a chip; length is config (to be verified: call lengths in the recipe).
- K02 "Call confirmed" (kept; no name; add-to-calendar; what to have open).
- K03 "After the call" (kept): summary, the first action, "book another" -> K01.
- K04 "Buy an extra call" (changed): payment for one a la carte call through P04's flow; "Rs ___".
- K06 "Your calls" (new): history, calls left this period, recordings or notes if the CRM keeps them (to be verified:
  recording consent and retention).
- O01 "Meet yeslyf" (changed): DIY card as drawn minus "a human call is available whenever you want one" (replace
  with "Calls are available a la carte from the Help tab"); DIWM card: "Your calls with the yeslyf advisers: N this
  <period>, book them whenever you want a walk-through"; DIFM card kept ("Your adviser: Harish"; this app tracks your
  progress; advice comes from your adviser directly).
- H07 Help: "Talk to an adviser" entry -> K01 for every tier.
- Q01 Quarterly review: for DIWM a line "Book a call to walk through this review" -> K01.
- Remove the name Priya from every screen (K01, O01, spec.logic lines). Remove every "45-minute" and "15-minute"
  mention; call length is config.

### 3.3 Bhuvanaa's items in the brief (brief B1 to B4; quick-accepts)

- B1: reveal (R09) -> one video (R10) -> sample plan (R12) -> paywall (P01). R11 dropped; its bridge content folds
  into the single R10 script (content owner per gap G08); the "two edits of the video, with and without the calls
  line" rule moves to R10 spec.logic. R10 branches Continue -> R12, Skip -> R12. R12 keeps the accepted change (real
  plan screens in the sample, optional carousel; rows 16 to 18).
- B2: G02 dropped; G03 gains three ledger rows (realisable vs locked corpus, current allocation by class, current
  weighted return; brief B2 "follows"). Every branch to G02 -> G03. K-screen dev notes that mention G02 -> G03.
- B3: depletion to life expectancy as the FP React does. L02 gains LIFE_EXPECTANCY 85, user-overridable to 90 or
  100 (M2 registry); G09 and G10 spec.logic say so; WITHDRAWAL_RATE removed from L02 if present.
- B4: G08 dropped; G03 tab strip loses "Tax"; G07 branches -> G09.
- Quick-accepts, exactly as ticked (brief quick-accepts list, into data/inputs.json): row 3 A01 declined; row 7 R01
  declined; row 8 R02 declined with the note "Add pets" (a Pets card on D01, feeding a recurring expense line on
  D06a); row 9 R02 accepted; row 10 R04 accepted; row 11 R07 not ticked, stays quick-accept; row 15 R10 not ticked,
  stays; row 21 P04 accepted; row 23 O01 not ticked, stays; row 26 O02 declined; row 31 G01 accepted; row 51 L04
  accepted; row 59 D03 and row 60 D04 accepted with additional screens (D03a, D04a to D04c).

### 3.4 Harish's items in the brief (brief H1 to H6)

- H1: L03 grid columns become liquid debt / debt / hybrid / commodities / equity / REITs and InvITs; no cash class;
  the shortest bucket is liquid debt; every row still sums to 100. G11 cards and the G11 chart use the same classes;
  the short-term card reads "Liquid debt 100". The v0.1 five-class line is noted in the changelog as superseded.
- H2: new L09 "Portfolio constraints" (desktop): max weight per product; max direct shares within equity; category
  tag per instrument with manual override; L05 validation blocks publish on a constraint breach; L04 links to L09.
- H3: D08 stays the eight HoA questions verbatim, one screen per question (D08a to D08h); D09 band from the score;
  "to be verified: the RPQ scoring map" stays in D08 spec.dev (gap G06).
- H4: E01 and E05 carry no aggregator links; E05 guided action stands.
- H5: Q03 refund line reads "per the agreement (brief H5: to be decided)". No other change.
- H6: L08 keeps the nine-record list with "to be verified: record formats (brief H6)".

### 3.5 Gaurav's items in the brief (brief G1, G2)

- G1 (default, not confirmed in the meeting): E02, E03, E04 as drawn. Add E07 "BSE StAR MF onboarding" (UCC, FATCA,
  bank mandate, eNACH), E08 "BSE StAR MF transactions" (order status, mandate status, SIP calendar), E09 "BSE StAR MF
  reporting" (holdings and transaction statements into the Vault). All three carry "brief G1: default, not confirmed
  in the meeting" and "to be verified: direct plans and the RIA code hold on this rail".
- G2: M01 adds "meeting note, speaker not recorded (brief G2): a Spinach-built front end over the bought admin tools
  is under consideration; to be decided". Goes to the CRM backlog too.

### 3.6 Vatsal's and Kajal's items in the brief (brief V1, V2, K1)

- V1: H01 community card becomes a one-line strip; H08 from the menu (H00). H08 unchanged.
- V2: "human call" becomes a nudge channel in N01; the CRM creates a task for the caller. Detail in section 5.
- K1: see 3.1 P04.

### 3.7 Gaps (brief gaps list)

- G01 brand: "yeslyf" lowercase, see section 0. G02 advertisement code review and G03 DPDP notice: agreed with dates;
  the compliance layer (section 7) is how the review happens on the screens; H09 spec.dev notes "to be verified: DPDP
  notice text (gap G03)". G04 to G13: no status recorded; no screen change. G07 (every screen ID is an event) is
  applied as the events convention (appendix D); the gap stays open for the implementation.

## 4. Phase 4 - rebuild section D: one spine for both paths, at instance level

Commit: "v0.2 phase 4: data spine rebuilt at instance level".

### 4.1 Why (write on X00 and in the changelog)

- v0.1 bug, flagged by Spinach: the manual branch (A05 "Do it manually instead" -> D02) never asked a manual user for
  bank balances, deposits, mutual funds or stocks, and skipped D01. A09's CAS button linked to itself; no upload
  screen existed.
- About 60 percent of the fields the plan needs are manual for every user, AA or not. The manual path is the main
  road; AA prefills one lane and, more importantly, keeps the plan current afterwards.

### 4.2 First task: the FP React and missing inputs (before drawing anything)

Read the FP React .jsx in inputs/hoa/. For each field in appendix B, record whether the component tolerates a null or
undefined value (renders the section with a stated assumption) or breaks. Write data/fp_react_inputs.json:
[{field, gate, tolerates_null, note}]. Pick the branch and name it in the report:
- Branch A (tolerates unknowns): the build gate is the appendix B gate list; unknown gate fields are not allowed;
  unknown sharpen fields pass through and the plan copy says "you have not told me X yet".
- Branch B (needs a value for every field it reads): the build gate is every field the React reads. "Not sure" on any
  such field maps to a stated assumption from L02 (appendix B gives the source per field), tagged "assumed", with a
  verify action in the plan. The sharpen loop then works on assumptions instead of unknowns.
Either way the tri-state rule (4.3 rule 6) holds and the gate concept stays.

### 4.3 Standing rules for every D screen (on X00 as "baked into v0.2" and in each spec)

1. One spine, both paths. AA users arrive with fields prefilled and tagged "AA-fed"; CAS users with holdings tagged
   "CAS-verified"; manual users with empty fields. No screen is bypassed on any path. Order: D01 -> D08 -> D09 -> D05
   -> D06 -> D02 -> D03 -> D04 -> D07 -> D10 (Vatsal, 10 Sep 2026).
2. One question per screen for numbers; taps may auto-advance. List items (family members, loans, policies, goals)
   are a list screen plus a detail screen per item type. Every instance is its own screen ID with a template tag.
3. Band rule (V5 standing rule): every band question shows a visible exact input; a tapped band prefills the exact
   field with the midpoint; exact removes the approx tag. Dynamic bands by income tier (V5 Stage 3) replace the fixed
   M2 tables 9.1 to 9.5; midpoints come from L02 (new rows: income tier boundaries, band multipliers). Per field the
   spec says "exact-first" (take-home, EMI, premium, SIP amount) or "band-first" (property value, gold, expense
   split, goal cost).
4. Readback and units: every amount input shows a readback in words ("seventeen and a half lakh a year, about
   Rs 1.46 L a month"), a per-month / per-year toggle where the field can be either, L and Cr quick multipliers, the
   numeric keypad. Plausibility checks against the reveal (take-home vs R03, corpus vs R04, EMI vs 30 percent of
   take-home): a mismatch prompts a check, never a block.
5. Hesitation detection (V5 Stage 3, restored): per number screen, at 45 seconds a warm line (sheet D11a), at 90
   seconds the "why this matters" line (D11b), at 120 seconds or on a second return the skip offer (D11c). Copy slots
   only (gap G08).
6. Tri-state fields (Vatsal, 10 Sep 2026): every field is value / explicit none / not sure. "None" chips set explicit
   none; "Not sure yet, skip" sets not sure; not sure is never stored as zero. Blindspot and concern copy fires on
   explicit none only; not sure produces a verify action ("tell me your cover to check it") in G05, G07 and H04. Dev
   note: M2's COALESCE(exact, band, 0) is superseded for not-sure fields.
7. Gate and sharpen (Vatsal, 10 Sep 2026): each field carries gate true or false (appendix B). The plan builds when
   every gate field is value or explicit none. Sharpen fields appear inside the plan section they improve as "Sharpen
   this" links that reopen the single screen and re-run (H05 shows the diff). Sharpen items that decide a verdict
   (ULIP years completed, loan rate) are also action-queue items on H04.
8. Capture ladder (Vatsal, 10 Sep 2026): on every number screen, under the exact input and the bands, the
   lower-friction sources that exist for that item, in this order where they apply: AA (fetched, or "connect now" ->
   A05); CAS upload (A10); guided lookup (exact steps, an SMS or missed-call deep link where one exists); document to
   the Vault (H06, "drop it here and it gets read"); then "Not sure yet, skip". No partner ask anywhere. Appendix C
   lists the ladder per item.
9. Source and precision tags on every field: source (aa, cas, manual, assumed), precision (exact, approx, unknown).
   D10 and every G screen show them. A manual override locks the field against AA refresh (spec v0.1 A08, kept).
10. Section micro-feedback (V5 Stage 3, restored): after the last screen of each spine section, one card in the
    adviser voice, chosen by the answers, no numbers (D12a to D12h). Copy slots only.
11. Endowed progress (spec v0.1 O02, kept): the ring starts at 20 percent after the reveal, weighted gate fields
    first. Minutes are "about N minutes" placeholders.
12. Exit from any D screen: autosave, then O03 "When will you finish?". The chosen time replaces the first scheduled
    nudge; the standard ladder (section 5) follows.
13. Events (appendix D) and compliance flags (appendix G) on every screen.

### 4.4 Source choice, AA and CAS (A05 to A10; the continuation sauce)

A05 "How should I get your numbers?" (rebuilt)
- purpose (Vatsal, 10 Sep 2026): make AA the obvious default by showing what it does now and what it keeps doing:
  the net worth on H02 stays live, the quarterly review runs itself, the switch advice on G12 unlocks. Keep the other
  three ways visible and honest; penalise none of them in copy.
- ui: h "Two ways to do this. One takes a minute and then keeps itself current. The other takes about N minutes and
  you keep it current by hand." Card (the default option, drawn larger) "Connect via Account Aggregator": banks,
  deposits, mutual funds and stocks fetched in about a minute; your net worth and your quarterly review update
  themselves; switch advice on what you already hold; read-only, you pick the accounts, revoke any time. Card "What it
  cannot see (I ask you either way)": EPF, PPF, property, gold, insurance details, loans. Card "Is +91 98xxx xxx21 the
  number your bank accounts know?" Yes / Use another number (kept). Card "Which bank is your salary account with?"
  eight chips plus Other (feeds the FIP health check). btn "Connect via Account Aggregator" -> A06. btn2 "Upload a CAS
  statement instead (holdings only)" -> A10. btn2 "Type it in (about N minutes)" -> D01. link "Not now. I will type
  today and connect later" -> D01.
- logic: "Not now" and "Type it in" set aa_status = not_connected and schedule two re-asks, at G12a and at Q01.
- states: A05a "Your bank is slow right now" (instance): the AA card shows the message and the CAS and manual buttons
  move up (to be verified: the TSP's FIP health API can be read before consent).
- dev: consent template asks for a periodic consent (fetch now plus quarterly for the review; validity as long as the
  rails allow; to be verified: maximum consent validity and fetch frequency under the wealth-management purpose code).
  Store consent_status, consent_valid_till, fetch_frequency, last_fetch_at per FIP. Events: source_choice.
A06 Consent framing (kept; plus the consent period in plain words above the webview: "I am asking for 12 months,
  fetched every quarter, read-only"; number subject to the verification above). Compliance flag: consent.
A07 Fetching (kept). A08 Here is what I found (kept; Continue -> D01; "Something is missing" -> D02).
A09 AA partial or failed (kept; CAS button -> A10; "Enter these manually" -> D02; "Continue with what we have" -> D01).
A10 "Your CAS" (new, four instances): A10 request it (CAMS or KFintech for mutual funds; NSDL or CDSL for shares and
  funds; links open outside the app; "look for the email subject Consolidated Account Statement; I will remind you in
  an hour"); A10a waiting for the email (state S17 landing; "Upload it" / "Type it instead"); A10b upload and
  password (the password you set when requesting, or your PAN); A10c parse result and confirm (rows: fund or share,
  units, value, SIP detected; chips "Looks right" / "Something is off"; Continue -> the screen that sent the user
  here, else D01). Parsed holdings are CAS-verified and count as verified for G12 (spec v0.1 A09 rule). Reminder at
  one hour and 24 hours. In V1 (Vatsal, 10 Sep 2026); "to be verified: CAS parsing effort in V1".

### 4.5 Before and between (D00, O02, O03)

D00 "Before you start" (new): "Have these open and it takes about N minutes. Without them, about 2N. You can skip
  anything and come back." Rows: salary slip or your bank app; latest CAS, or I fetch it; loan statement, or just the
  EMI; term and health policy PDFs; EPF passbook (UMANG app). Rows: per section, about N minutes. btn "Start" -> A05
  on first entry, else the first incomplete screen. Shown once; "What to have ready" on O02 reopens it.
O02 "Your next steps (hub)" (rebuilt): progress ring (endowed 20 percent); card 1 "Get your numbers in" with source
  status (connected on <date> / CAS uploaded / typing it in / not connected: connect for a live plan) and "Continue
  where you left off: <screen>"; card 2 "Review and build" (enabled when the gate is met); card 3 "Book a call"
  (any tier) -> K01; link "What to have ready" -> D00; video "30-second walkthrough" (kept). States: S3, S4, S5, S16,
  S17, S19.
O03 "When will you finish?" (new; sheet over any D screen on exit): chips Tonight / Tomorrow morning / This weekend /
  I will come back on my own; btn "Save and exit" -> O02. The slot schedules the first push (WhatsApp if opted in)
  and skips the 24-hour default. Event return_time_picked.

### 4.6 The spine, screen by screen (register in appendix A)

- D01 Family circle (kept; entry for both paths): cards per member from R02, "Pets" card (row 8 note), chips "Just
  me". D01a Member detail (new): partner (name, age, earns yes or no); child (name, age); dependant parent (age,
  lives with you). Gate: members, has_dependants.
- D08a to D08h Risk profile questions (one per HoA question, tap, auto-advance); D09 Your risk profile (band result,
  what it changes, retake; the declaration card removed to D10; Continue -> D05a). Gate: rpq_answers, risk_band; no
  fallback (SEBI suitability), which is why it sits early.
- D05a Your monthly take-home (exact-first; prefilled from AA salary detection when present, else the suggestion
  "You said about Rs 17.5 L a year earlier; roughly Rs 1.2 L a month after tax?" from R03; hint "take-home, not
  CTC"). D05b Partner's take-home (band-first; only if D01 partner earns). D05c Rental income (exact-first; only if
  D02h investment property). D05d Other income (band-first; regular or lumpy). States on D05a: AA-fed (the v0.1 "here
  is what your money did" rows above the question) / manual (rows absent). Gate: take_home.
- D06a Total monthly outgoings (suggestion from R05 times income; exact or band; EMIs shown read-only from D03; live
  surplus; deficit state). D06b The three buckets (fixed / variable / guilt-free; three-way slider summing to the
  total; band-first; sharpen). D06c How does the month typically end (V5 Q1.4 four options; check). D06d Already
  investing every month (SIPs and RDs; prefilled from AA debits when present; exact-first). Gate: total_outgoings.
- D02 Your investments, by type (overview list: one row per type with status and tag; AA-fed rows show value and
  "edit or add"). D02a Bank balances and deposits. D02b Mutual funds. D02c Stocks and ETFs. D02d NPS. D02e EPF. D02f
  PPF and post-office schemes. D02g Physical gold and silver (grams or value; the app prices grams from L07). D02h
  Property (home you live in: value, excluded from investable; investment property: value and rent). D02i ULIP or
  endowment (surrender value, premium, years completed). D02j Anything else (crypto, international, business stake,
  other). Each with its ladder (appendix C) and a "None" chip. Gate: bank_and_deposits, mutual_funds, stocks, epf.
  Branch B: an unknown gate item maps to the R04 corpus band split by the L02 default mix (new L02 row "default asset
  mix for unknown split"; "to be verified: the default mix").
- D03 Loans and dues (list; per loan: type, EMI exact-first, outstanding band-first, years left band-first; rate
  derived and shown "about N percent, correct it if you know it"; credit card carried balance; loans to or from
  friends and family; chips "No loans"). D03a Loan detail (new): lender, tax-deductible flag, prepayment allowed.
  Gate: has_loans, total_emi.
- D04 Insurance (list; per policy type: "Have it and know the amount" / "Have it, not sure of the amount" / "Do not
  have it"; only the first opens the amount screen; the second sets not sure and offers the ladder; the third sets
  explicit none). D04a Term cover detail (sum assured, premium, cover until age). D04b Health cover detail (employer
  only / personal / both; sum insured band-first; floater; premium). D04c Other policy detail (ULIP or endowment
  links to D02i; other). Gate: term_status, health_status.
- D07 Goals and key life events (list; suggested goals from D01; "No goals for now" chip; work-optional age default
  60). D07a Goal detail (name, year, cost today band-first with "I am not sure yet" mapping to the persona estimate,
  V5 Q4.4b, priority). D07b Work-optional age (kept as its own screen; slider 45 to 70; default 60). Gate: at least one
  goal or explicit none, work_optional_age.
- D10 Review, build, and what would sharpen it (rebuilt): rows per section with value, source tag and precision tag,
  each linking back to its screen; card "Ready to build" (gate met, or the missing fields with minutes); card "These
  would sharpen it" (not-sure and approx fields with the plan section each improves); card "Your two paths, updated"
  (the R09 numbers re-run on what is now known, R06 tone variant; the only place numbers update during data entry);
  card "Declaration" (moved from D09: the details furnished are true and correct; full text to be verified against
  HoA's current wording) with chip "I confirm"; btn "Build my plan" -> G01 (enabled when the gate is met and the
  declaration is confirmed); link "Edit a section" -> O02. dev: snapshot of inputs as plan_input_version with source
  and precision per field (advice record).
- D11a, D11b, D11c Hesitation sheets (rule 5). D12a to D12h Section micro-feedback cards (rule 10), one per spine
  section: family, risk profile, income, expenses, investments, loans, insurance, goals.

### 4.7 The plan screens: sharpen loop and the locked card

- Every G03 to G14 screen lists in spec.fields the fields it reads; where a field is approx, not sure or assumed the
  screen shows a "Sharpen this" link (in-place list) that opens the single D screen and, on save, re-runs and lands
  on H05 with the diff.
- G05, G07 and H04: not-sure fields produce verify actions, never gap diagnoses (rule 6).
- G12a Locked holdings (new instance; section 0): "Switch and sell advice needs holdings I can verify"; btn2 "Connect
  via Account Aggregator" -> A05; btn2 "Upload your CAS" -> A10. G13 gains the state "buy advice for new money only;
  existing holdings not assessed". Compliance flag: advice language.
- G01a Building your plan, built on what we have (new instance; day-7 build, section 5): copy names the count of
  assumed or not-sure fields and that each can be sharpened from the plan.
- After delivery (S6 -> S18): the "Sunday sharpen" card on H01: "Want me to ask you for the N numbers I am still
  missing on Sunday?" with a nudge slot.

## 5. Phase 5 - complete section N: a contract per returning-user state, with a mock per state

Commit: "v0.2 phase 5: returning-user states completed with message mocks".

### 5.1 The contract

N01 (rebuilt master table, desktop): per state: state ID; who; lands on (screen ID; for H01 the variant H01a to
H01k); primary action; nudge ladder (day, channel, copy slot ID); human escalation by tier; exit condition. N02
"Onboarding ladder (paid, before the plan)": S2b, S3, S4, S5, S16, S17, S19 day by day. N03 "Post-plan ladder": S6
to S13, S15, S18, S20 to S25. N04 "Message templates": every push, WhatsApp and email template with its copy slot
ID, deep link and the state it serves (WhatsApp templates need approval before launch; to be verified: template
approval lead time). N05 to N30: one phone mock per state (S1, S2, S2b, S3 ... S25 in order), each showing the push
and WhatsApp message on the left and the landing screen on the right.

Rules (Vatsal, 10 Sep 2026):
- One nudge per week maximum across layers (spec v0.1, kept) applies from day 14 after payment. Before day 14 the
  onboarding states may nudge at 24 hours, 72 hours and day 7 (spec v0.1 S3, S4 cadence, kept).
- Every nudge deep-links to the primary action and names the specific next screen and its minutes; never "continue
  your journey".
- O03's chosen time replaces the first scheduled nudge when it exists.
- Human escalation (brief V2): an outbound call from the call centre; the CRM creates a task carrying the state ID,
  the missing fields and the tier. It does not consume the user's included calls. During the call the adviser enters
  inputs and the engine re-runs; nobody edits outputs by hand (spec v0.1, kept).
- Escalation by tier: DIWM gets the outbound call at day 7 of a data stall and on a second no-show; DIY gets the
  a la carte offer (K04) at the same points; DIFM is handled by the adviser relationship, not the ladder.
- Nudge copy slots are IDs (N-S4-72h); copy is content (gap G08) and lives in the CRM templates.

### 5.2 States

Kept, with changes: S1 signed up, no reveal. S2 reveal seen, not paid (ladder day 1, 3, 7, 21, 82, stop). S2b paid,
eSign incomplete (refund path at day 14 per brief H5: to be decided). S3 paid, nothing else: lands O02 with D00
offered; 24h, 72h, day 7 -> S19. S4 data partial: lands O02 "continue where you left off"; 24h, 72h, day 7 -> S19; O03
time first when set. S5 redefined (RPQ is early now): gate met, D10 not confirmed; lands D10; 24h "two minutes to
build"; exit S6 on build or S18 at day 7. S6 plan built, not read (48h). S7 call booked (any tier). S8 plan read, no
action (48h, 7d, 14d). S9 executing. S10 all actions done. S11 plan updated (3d). S12 payment failed (grace 7 days).
S13 lapsed (30d, 90d). S14 DIFM (dashboard without engine advice). S15 AA consent expired (lands Q01 with re-consent
first).

New: S16 AA not connected, manual in progress or done (lands the spine, or H01 with "last updated by you N days ago;
connect Account Aggregator to keep this live"; H02 shows the same line; re-asks at G12a and Q05). S17 CAS requested,
awaiting the email (lands A10a; 1h, 24h; exit on upload or "type it instead"). S18 plan built on partial data (lands
H01j with the sharpen strip and the Sunday card; the chosen Sunday, day 7, day 21; exit when no sharpen items
remain). S19 stalled below the gate at day 7 (lands O02 with the missing fields and minutes; DIWM outbound call task;
DIY a la carte offer; day 7, 10, 14, then monthly; exit when the gate is met). S20 call booked, no-show (lands K01
rebook; 1h after, 24h; second no-show -> task). S21 call done, no action started (lands K03 with the first action; 48h,
7d). S22 quarterly review ignored, Q01 not opened 14 days after generation (lands H01 review card; 7d, 14d; DIWM call
line). S23 annual confirmation overdue, Q04 (7 days before, day of, 7 days after; "to be verified: what happens to
advice if not confirmed (brief compliance)"). S24 refund requested (Q03a path; brief H5: to be decided). S25 account
deletion requested (H09; DPDP flow; regulated records retained; "to be verified: DPDP notice and retention text").

Not used: S26. Not added: any partner state.

### 5.3 Screens touched

- H01 base plus H01a to H01k variants: a S6 plan ready; b S8 next action; c S9 executing; d S10 all done; e S11
  updated banner; f S12 payment failed banner; g S13 lapsed read-only; h S14 DIFM; i S16 not connected; j S18 built on
  partial data with sharpen strip; k S22 review overdue. H02: source and freshness line. H04: verify actions from
  not-sure fields.
- Q01 Quarterly review (AA users; kept; DIWM call line). Q05 "Update your numbers" (new; manual quarterly review for
  S16 users: the fields that move, with the ladder and A10 again; "Keep my manual number" stays for mixed users).
- K01 no-show state (S20). K03 S21 state. Q03a S24. Q04 S23. H09 S25.

## 6. Phase 6 - admin and CRM spec, plus the CRM backlog

Commit: "v0.2 phase 6: admin and CRM updated; CRM backlog added".

- PLACEMENT: the CRM platform name is "to be decided (one platform)". Where the v0.1 spec or brief V2 says Zoho, keep
  the text and add "(platform to be decided; the object model and the matrix are platform-neutral)".
- NUDGES matrix: one row per state S1 to S25 per ladder step: state, day, channel (push, WhatsApp, email, human call),
  copy slot ID, deep link screen, tier rule, CRM task (yes or no, task fields).
- EVENTS: every new screen event (appendix D) and state_enter events.
- DEAL_FIELDS: sku (diy, diwm), period (monthly, quarterly), payment_method (upi, netbanking), gst_type (igst,
  cgst_sgst, none), coupon, calls_included_per_period, calls_used, a_la_carte_purchases.
- CONTACT_FIELDS: aa_status, consent_valid_till, source_completeness (gate met; sharpen count), last_manual_update,
  difm_prospect_flag (rule or manual), adviser_continuity (on or off), last_adviser.
- COMPLIANCE records: unchanged; "to be verified: record formats (brief H6)".
- DECISIONS list in the admin spec: append K1, V2, the G2 note, H5 and H6 pending, with causes.
- CRM_BACKLOG (new list in admin_crm.json; rendered as its own section on the Admin and CRM v0.2 tab; items the team
  said to remember for the CRM planning session): DIFM prospect flag (rule "total investable assets over Rs ___" plus
  manual flag; outbound call by the call centre; only DIFM clients ever speak to Harish); call-centre routing and the
  adviser continuity flag; included calls per SKU and period as config; a la carte purchase record and receipt;
  outbound nudge calls and their task fields; WhatsApp template approval; compliance review workflow for copy changes;
  DPDP consent and deletion records; refund workflow (brief H5); record formats (brief H6); nudge copy slots and who
  edits them; the Spinach-built admin front end question (brief G2 note); recording consent and retention for calls.

## 7. Phase 7 - the site, the renderer, the compliance layer, the changelog, the checks

Commit: "v0.2 phase 7: site rebuilt". Never hand-edit docs/.

Renderer (extend the v0.1 renderer; grey low-fi stays; Spinach owns visual design):
- Filters: tier (DIY, DIWM, DIFM; kept), path (aa, manual, both), state (pick a state, see its landing and hero
  variant), compliance (flagged screens only, by reason category), template (one layout at a time, for Spinach).
- "Changed in v0.2" marker on every touched screen with the cause; "New in v0.2" on new screens; the dropped list on
  the Changelog tab.
- Spec panel: fields with gate, source and precision; ladder per number screen; events; compliance flag and reason;
  template tag; path set.
- Compliance layer: every screen carries a flag {review: true or false, reasons: [...]} (appendix G) and a compliance
  checklist card in the spec panel listing what the reviewers are asked to check for those reasons. A banner on the
  v0.2 tabs: "All copy is placeholder pending compliance review; comment on language on any screen." The comment
  controls offer "Compliance" as a reviewer identity and write to the "v02_comments" sheet tab with the reason
  category; the compliance filter walks the flagged screens in flow order.
- Comment controls (kept) for everyone: verdict and comment per screen, writing to "v02_comments"; export still
  produces a markdown build brief.
- Tabs after the rebuild: Meeting (frozen, read-only, decisions shown), Gaps (frozen), Inputs (frozen), Wireframes
  v0.1, Admin and CRM v0.1, Wireframes v0.2, Admin and CRM v0.2 (with the CRM backlog section), Changelog. Changelog
  tab sections: changed, added, dropped, rerouted branches, superseded brief items (section 0), to be verified
  (appendix E, by item), counts for Spinach (templates and instances by section; appendix F).
- noindex on every page (kept). No personal data beyond first names (kept). Nothing named "Priya" anywhere.

Acceptance checks before publishing (all must pass; print the results in the report):
1. Every branch target exists in screens_v02.json; no branch points at a dropped screen; no screen is orphaned.
2. No self-link stands in for a missing screen; every in-place self-link has a logic line.
3. The manual path reaches every gate field in appendix B; the AA path reaches every D screen; neither path skips
   D01; both reach D10 and G01.
4. Every state S1 to S25 has a landing screen, a primary action, a ladder, an exit, and a mock N05 to N30.
5. Every screen has a template tag, a path set, at least one event, and a compliance flag with reasons.
6. Every touched screen shows its cause; no page contains a person's name on a callout, the words "founders" or
   "recommendation", the name Priya, a drawn call count, a drawn call length, or "Yeslyf" with a capital.
7. P01 shows two cards and a period toggle; no one-time card; no 60-day credit line anywhere; no S26.
8. The tier, path, state, compliance and template filters each walk end to end without a dead end.
9. Export works with the sheet endpoint blank. Pages loads over HTTPS. noindex present.
10. docs/v01/ files are byte-identical to inputs/v01/.

## 8. Phase 8 - report and handover

Commit: "v0.2 from meeting decisions 2026-09-09 plus post-meeting overrides, data spine and states, <date>". Report,
in this order: the URL; the 4.2 branch with the fp_react_inputs.json summary; screen counts (total, by section,
templates vs instances); changelog counts (changed, added, dropped, rerouted, superseded); the to-be-verified list
by item; anything in this file that CLAUDE.md would not allow and was therefore not done, with the rule cited. Do not
ask spiff anything this file answers. If blocked, batch at most three questions.

## Appendix A - screen register (ID | title | template | path | status | cause)

Section A (auth, AA and CAS; A05 to A10 sit in section D of the data as in v0.1):
- A01 Welcome | T-card | both | kept (row 3 declined) | -
- A02 Phone number | T-tap | both | kept | -
- A03 OTP | T-tap | both | kept | -
- A04 Name and consent | T-tap | both | kept; DPDP notice slot | gap G03; compliance: consent
- A05 How should I get your numbers | T-source | both | rebuilt | Vatsal, 10 Sep 2026
- A05a Your bank is slow right now | T-source | both | new | Vatsal, 10 Sep 2026
- A06 Consent framing | T-webview | aa | changed (period copy) | Vatsal, 10 Sep 2026; compliance: consent
- A07 Fetching | T-progress | aa | kept | -
- A08 Here is what I found | T-review | aa | changed (-> D01) | 4.1 bug fix
- A09 AA partial or failed | T-card | aa | changed (-> A10) | 4.1 bug fix
- A10 Your CAS: request it | T-card | both | new | Vatsal, 10 Sep 2026
- A10a Your CAS: waiting for the email | T-card | both | new (S17) | Vatsal, 10 Sep 2026
- A10b Your CAS: upload and password | T-upload | both | new | Vatsal, 10 Sep 2026
- A10c Your CAS: what I read | T-review | both | new | Vatsal, 10 Sep 2026

Section R (reveal): R01 to R09 kept as dispositioned (rows 7 to 15; R02 gains nothing beyond the accepted row 9);
R10 Video (one video; rebuilt; brief B1); R11 dropped (into R10; brief B1); R12 Sample plan preview (kept; rows 16 to
18). Compliance: advertising code on R09, R10, R12. Templates: T-tap for R01 to R08, T-chart for R09, T-video for
R10, T-card-stack for R12.

Section X: X00 Decisions baked into v0.2 (rebuilt; lists sections 0 and 4.3); X01 Save and decide later (kept).

Section P: P01 Paywall (rebuilt; T-paywall; section 3.1; compliance: fees, advertising code); P02 KYC (kept; T-webview);
P03 Agreement and eSign (kept; T-webview; compliance: fees, disclosures); P04 Payment (changed; T-card; brief K1).

Section O: O01 Meet yeslyf (changed; T-card-stack; section 3.2); O02 Your next steps (rebuilt; T-hub); O03 When will you
finish (new; T-sheet).

Section D (the spine; path both unless stated):
- D00 Before you start | T-card-stack | new
- D01 Family circle | T-list | changed (entry both paths; Pets card)
- D01a Member detail | T-detail | new
- D08a to D08h Risk profile question 1 to 8 | T-tap | changed (moved early; one per screen) | brief H3
- D09 Your risk profile | T-card-stack | changed (declaration moved out)
- D05a Your monthly take-home | T-num | rebuilt
- D05b Partner's take-home | T-num | new (conditional)
- D05c Rental income | T-num | new (conditional)
- D05d Other income | T-num | new
- D06a Total monthly outgoings | T-num | rebuilt
- D06b The three buckets | T-split | new
- D06c How the month ends | T-tap | new (V5 Q1.4)
- D06d Already investing every month | T-num | new
- D02 Your investments, by type | T-list | rebuilt (both paths)
- D02a Bank balances and deposits | T-num | new
- D02b Mutual funds | T-num | new
- D02c Stocks and ETFs | T-num | new
- D02d NPS | T-num | new
- D02e EPF | T-num | new
- D02f PPF and post office | T-num | new
- D02g Gold and silver | T-num | new
- D02h Property | T-num | new
- D02i ULIP or endowment | T-num | new
- D02j Anything else | T-num | new
- D03 Loans and dues | T-list | changed
- D03a Loan detail | T-detail | new | row 59
- D04 Insurance | T-list | changed
- D04a Term cover | T-detail | new | row 60
- D04b Health cover | T-detail | new | row 60
- D04c Other policy | T-detail | new | row 60
- D07 Goals and key life events | T-list | kept
- D07a Goal detail | T-detail | new
- D07b Work-optional age | T-tap | new (split out)
- D10 Review, build, and what would sharpen it | T-review | rebuilt
- D11a Still there? (45 seconds) | T-sheet | new (V5)
- D11b Why this one matters (90 seconds) | T-sheet | new (V5)
- D11c Skip for now (120 seconds) | T-sheet | new (V5)
- D12a to D12h Section insight: family, risk profile, income, expenses, investments, loans, insurance, goals | T-card |
  new (V5)

Section G: G01 Building your plan (kept); G01a Building on what we have (new); G02 dropped (brief B2); G03 Plan
overview (changed; brief B2, B4); G04 Emergency fund (changed; sharpen link); G05 Protection (changed; verify actions);
G06 Cashflow (changed; sharpen link); G07 Debt (changed; -> G09); G08 dropped (brief B4); G09 Life events and
work-optional (changed; brief B3); G10 Summary (kept); G11 Allocation (changed; brief H1); G12 Existing holdings
(kept); G12a Locked holdings (new; section 0); G13 What to buy (changed; unverified state); G14 Action plan (kept).
Templates: T-card-stack; G11 T-chart; G12a T-locked. Compliance: advice language on every G screen; disclosures on G13.

Section H: H00 Navigation map (accepted; T-table); H01 Home base (changed; T-hub); H01a to H01k Home by state (new;
T-hub; 5.3); H02 Net worth (changed; freshness line; T-chart); H03 (kept); H04 Action queue (changed; verify actions);
H05 Plan updated (kept); H06 Vault (changed; "drop it here and it gets read"); H07 Help (changed; K01 entry); H08
Community (kept; menu); H09 Settings and account (changed; S25 line; DPDP slot); H10 Goals progress (accepted); H11
Portfolio (accepted).

Section E: E01 Execution hub (changed; brief H4); E02 One-time setup (kept); E03 Mutual fund order (kept); E04 ETF and
stock via smallcase Gateway (kept); E05 Guided protect action (kept; no aggregator links); E06 Self-report and detection
(kept); E07 BSE StAR MF onboarding (new; brief G1 default); E08 BSE StAR MF transactions (new); E09 BSE StAR MF
reporting (new); E10 SIP mandate registration (new; Kajal, 16 Sep 2026); E11 Set up monthly SIPs (new; Kajal, 16 Sep
2026). Compliance: execution disclosures on E03, E04, E07, E08, E10, E11.

Section K: K01 Talk to an adviser (rebuilt); K02 Call confirmed (changed); K03 After the call (changed); K04 Buy an
extra call (changed); K05 Pick a slot (new); K06 Your calls (new). Path both; tier all.

Section Q: Q01 Quarterly review, AA (changed); Q02 Change plan (changed; SKU and period); Q03 Subscription (kept as the
overview); Q03a Cancel (new); Q03b Payment failed (new); Q03c Lapsed (new); Q04 Annual confirmation (kept; S23 slot);
Q05 Update your numbers (new; manual review). Compliance: fees on Q02, Q03, Q03a; disclosures on Q04.

Section L (desktop): L00 Navigation (accepted); L01 to L08 kept with the changes in 3.3 and 3.4 (L02 assumptions; L03
grid; L04 link to L09; L05 validation; L08 records); L09 Portfolio constraints (new; brief H2).

Section M: M01 Admin and CRM overview (changed; brief G2 note; CRM backlog pointer).

Section N (desktop unless stated): N01 Master state table (rebuilt); N02 Onboarding ladder (new); N03 Post-plan ladder
(new); N04 Message templates (new); N05 to N30 State mocks S1 to S25 (new; T-msg; phone frame pairs).

Count: about 185 screens; the build prints the exact number by section and by template.

## Appendix B - gate and sharpen fields

Gate (the plan builds when each is value or explicit none). Branch B fallback in brackets.
- family: members, has_dependants [from R02 household type; partner earns assumed no]
- risk: rpq_answers, risk_band [no fallback; mandatory]
- income: take_home [R03 band midpoint, approx]
- expenses: total_outgoings [income times (1 minus R05 savings rate), approx]
- assets: bank_and_deposits, mutual_funds, stocks, epf [R04 corpus band split by the L02 default mix, assumed]
- loans: has_loans, total_emi [assumed none, verify action]
- protection: term_status, health_status [assumed none, verify action]
- goals: at least one goal or explicit none, work_optional_age [work_optional_age 60; goals none]

Sharpen (inside the plan section named): partner take-home, rental, other income (G06); three buckets, month-end
pattern, current SIP (G06); NPS, PPF, gold, property values, ULIP detail, other (G03, G09, G11); outstanding, years
left, rate, loan detail (G07); sum assured, sum insured, floater, policy detail (G05); goal cost and year (G09).

## Appendix C - capture ladder by item (order shown on the screen; only the sources that exist for the item)

- bank balances, deposits: AA; bank app balance typed exact; band
- mutual funds: AA; CAS upload (A10); total typed; band
- stocks and ETFs: AA; NSDL or CDSL CAS (A10); total typed; band
- NPS: AA where the CRA is live (to be verified: NPS on AA); CRA statement to the Vault; band
- EPF: guided lookup: UMANG passbook, or the EPFO balance SMS and missed-call services with the message prefilled on
  Android (to be verified: the current service numbers and that the deep link works on both platforms); passbook PDF
  to the Vault; band
- PPF and post office: passbook or net banking; band
- gold and silver: grams (priced from L07) or value; band
- property: what it would sell for, band; rent exact
- insurance amounts: policy schedule PDF from email to the Vault; premium from the bank debit; band
- loans: EMI exact; outstanding and years left bands; rate derived
- ULIP or endowment: surrender value from the insurer app or the statement to the Vault; premium exact
- crypto, international, business stake, informal loans: typed; band
- documents dropped in the Vault are read by the app (to be verified: V1 covers CAS only via A10; other document
  extraction is V1.5; until then the Vault stores the file and the field stays not sure)

## Appendix D - events (gap G07 applied as a convention)

- every screen: <id>_view
- number screens: <id>_set {source, precision}, <id>_skip, <id>_hesitation_45, _90, _120, <id>_ladder_<source>,
  <id>_band_tapped, <id>_exact_entered
- A05: source_choice {aa, cas, manual, later}; A10: cas_requested, cas_uploaded, cas_parsed; O03: return_time_picked
- D10: gate_met, plan_built {assumed_count, unknown_count}; G screens: sharpen_opened {field}, sharpen_saved
- K: call_booked {topic, tier}, call_purchased, call_no_show
- E10: mandate_started, mandate_active, mandate_rejected; E11: sips_registered, sip_setup_blocked (Kajal, 16 Sep 2026)
- N: state_enter_<S>, nudge_sent {slot, channel}, nudge_opened, crm_task_created {state}
- Beta rule on X00 (Vatsal, 10 Sep 2026): if fewer than 70 percent of paid users in the January beta reach the gate
  within 7 days, the gate list is cut again before Spinach starts screens.

## Appendix E - to be verified (by item; printed on the Changelog tab)

- CAS parsing effort in V1 (A10)
- TSP FIP health API readable before consent (A05a)
- maximum AA consent validity and fetch frequency under the wealth-management purpose (A05, A06)
- NPS CRA live on AA (D02d)
- EPFO SMS and missed-call numbers and the SMS deep link on both platforms (D02e)
- recurring UPI mandate type and limits for monthly and quarterly (P04)
- proration and refund on a period switch (Q02)
- the GST split rule (P04)
- direct plans and the RIA code on the BSE StAR rail (E07 to E09)
- amount limits and maximum tenure for UPI autopay and e-NACH on BSE StAR MF; e-NACH approval time; whether a limit
  change amends the mandate or registers a new one (E10)
- the earliest SIP start date after mandate approval (E11)
- call lengths in the recipe; recording consent and retention (K05, K06)
- WhatsApp template approval lead time (N04)
- what happens to advice if the annual confirmation is not given (Q04, S23)
- the RPQ scoring map (D08); the default asset mix for unknown splits (D02, L02)
- DPDP notice, deletion and retention text (A04, H09)
- record formats (L08); refund policy (Q03)
- the declaration wording (D10)

## Appendix F - templates (for Spinach's count)

T-tap (choice with auto-advance), T-num (number with readback, bands, ladder, skip), T-split (three-way slider),
T-list (cards with add and edit), T-detail (form behind a list card), T-card (one card and one action), T-card-stack
(cards and one CTA), T-hub (progress and steps), T-review (ledger rows with tags), T-chart (number and chart),
T-source (the four-way choice), T-upload (file and password), T-progress (fetching), T-webview (vendor frame),
T-sheet (bottom sheet over a screen), T-video, T-paywall (cards with a period toggle), T-locked (locked card with
unlock actions), T-picker (slot calendar), T-msg (message and landing pair), T-table (desktop table).

## Appendix G - compliance flag: reason categories and what the reviewers are asked to check

- advertising code: R09, R10, R12, P01, H01 hero cards, every nudge template. Check: projections and the two paths,
  sample plan, testimonials, any "returns" language, comparisons.
- advice language: every G screen, H04, E01, D09, D10, G12a, G13. Check: how a recommendation is worded, suitability
  and risk band references, "consider" versus "must", verify actions versus diagnoses.
- disclosures: P01, P03, G13, Q04, K01. Check: RIA registration line, fee schedule, complaints and grievance path,
  what the app is and is not, what a call is and is not.
- fees and refunds: P01, P04, Q02, Q03, Q03a, K04. Check: inclusive of GST, period, cancellation, refund, breakage.
- consent: A04, A05, A06, A10, D10 declaration, H06, H09. Check: AA consent wording and period, DPDP notice, CAS
  password handling, the declaration, deletion.
- execution: E03, E04, E07, E08, E09, E10, E11. Check: order and mandate language, direct plan, rail disclosures.
Every screen carries a flag; screens with no user-facing copy (L, M, N desktop tables) carry review false with reason
"internal".

## 9. Phase 9 - 11 Sep 2026 (Vatsal): the reversal, the seven improvements, the relabel, the audience files

Briefed in chat, not in this file; recorded here so the rules above read right. Cause on every change: "Vatsal,
11 Sep 2026". Commits: 9a "no client-data assumptions", 9b "data-capture improvements", 9c "split status",
9d "audience files". PLAN.md section 14 carries the status.

Supersedes in 4.2 and 4.3:
- 4.2 branch B resolution: a not-sure field is never filled from L02. The build gate is every field the React reads;
  a not-sure field blocks the build and is asked for as a fixed band on D13 Quick ranges (fp_react_inputs.json:
  "fallback": "band required" on every field). G01a "built on what we have" means built on bands.
- Rule 3: fixed bands per field from the M2 tables 9.1 to 9.5 where a table exists, else "Rs ___" chips; dynamic
  bands by income tier are shelved until the data flywheel exists; the L02 rows for tier boundaries, band tables
  and the default asset mix are removed (gap G16 not needed; gap G17: which fields have an M2 table).
- Rule 7: the plan builds when every field the React reads is a value (exact or band) or explicit none.
- Rule 9: source is aa, cas or manual; "default accepted" only for the work-optional age 60 taken on D07b. The word
  "assumed" appears on D07b alone. D07a "I am not sure yet" keeps the goal on the Yes list, out of the SIP maths,
  with the verify action "price this goal to fund it" in G09 (gap G15 not needed).
- Rule 10: D12a to D12h are relief cards (section done, N of eight, next section with minutes; Keep going or
  Remind me later); the adviser-voice line is a copy slot on the card.
- Rule 12: exit from any D screen is a silent autosave with a Saved toast; O03 is the reminder picker, opened only
  from Remind me later on a relief card or on O02.
- New rules 14 to 16 (on X00): the section strip on every spine screen; confirm or correct on every prefilled
  screen (That's about right / Change it; derivation "from what you told me earlier"); multi-select lists on D02
  and D04 (only ticked types open; unticked types are explicit none; AA-fed and CAS-verified types pre-ticked).

Also: Q06 Something changed and Q06a What I will ask again (gap G14 done; on the S11 exit path; slot N-Q06 on
N04); AA fetch in the background (A05 -> A06 -> D01; A07, A08 as a sheet, A09 as states; recovery on the D02
rows); "Why this one matters" link on every T-num and T-detail screen (slot W-<id>; D11b reuses it); status
"split" for D05, D06, D08 with their instances (dropped is R11, G02, G08); docs/audiences/ (team, Spinach,
compliance) from scripts/build_audiences.py. Acceptance: checks 1 to 10 above plus 11 to 17, all in
scripts/check_phase9.py. CLAUDE.md gained the line on client-data fallback assumptions.

## 10. 16 Sep 2026 (Kajal): mandate registration and SIP setup on the execution screens

Cause on every touched screen: "Kajal, 16 Sep 2026". Data: data/v02/sip_mandate_edits.json; order in data/v02/flow.json.
- Gap: the SIP mandate was one row on E02 with no flow and no states, and E03 claimed to cover SIPs while drawing a
  lumpsum. Two screens added, no new template.
- E10 SIP mandate registration (T-card): bank account from setup, monthly limit above the planned SIPs on the rail,
  UPI autopay or e-NACH, Approve the mandate as an in-place action; states not started, pending bank approval, active,
  rejected or expired; status from the rail webhook, never from a tap. Separate from the subscription mandate on P04.
- E11 Set up monthly SIPs (T-list): the plan's SIPs (G13) registered against the mandate in one confirmation; the date
  and the yearly step-up are editable here, funds and amounts are not; disabled until the mandate is active; the gold
  ETF SIP stays on the broker rail (E04). Confirm lands on E06; the calendar is on E08.
- Wiring: E02 gains the mandate link (E10); E01 gains the SIPs link (E11); E03 is lumpsum and redemption only. Flow
  order E01, E02, E07, E10, E03, E11, E08, E09, E04, E05, E06.
- To be verified: the E10 and E11 items in appendix E. Counts after the rebuild: 193 live screens, 21 templates.

## 11. 17 Sep 2026 (Vatsal): mandatory and optional inputs

The developers asked which inputs are mandatory and which are optional, that is, which ones stop the user from
moving forward. Cause on every touched screen: "Vatsal, 17 Sep 2026".

The test. An input is required only when the next screen cannot honestly exist without it: the app cannot identify
the user, cannot proceed lawfully, cannot compute what the next screen shows, or cannot save the item being added.
Everything else is optional and is picked up later by the ladder, D13 or a Sharpen this link.

Four tags, one per captured field (printed after the field name in the spec panel):
- required: the primary action stays disabled until the field is set.
- optional: never blocks; skipped means not sure or empty, never zero (rule 6 of 4.3).
- default: prefilled; counts as set; the user may change it.
- system: written by the app or a vendor; never typed.

Where it lands, section by section:
- Identity, consent and money are required: A02 mobile, A03 OTP; P01 the SKU (period defaults to monthly); P02 name
  as per PAN, PAN, date of birth and email (address only when the KRA fetch fails); P03 the signature; P04 the
  payment method (coupon optional); E02 bank account, FATCA and the nominee choice (mandate may stay pending; to be
  verified: the SEBI nomination rule for new folios and the UCC field set on BSE StAR MF); E04 the broker; E10 the
  mandate type (limit defaults to the planned SIPs plus headroom); E11 needs an active mandate, not a field.
- The free reveal, R01 to R07: one tap per screen is required (R01 first name and age; R03 to R05 a band, or the
  exact amount which satisfies it), except R06, which only sets tone and can be skipped.
- The AA and CAS ways: A05 needs the bank chip for the AA button only; A06 needs the consent approval for the AA path
  only; A08 and A10c start with every value included and never block; A10b needs the PDF and its password.
- The data spine, D01 to D07b and D13: no number blocks. Continue is always enabled; a field is a value, explicit
  none or not sure; a gate field left not sure is listed on D10 and, for amounts, asked as a range on D13 before the
  build (rule 7). The spine blocks in two places only: the eight risk questions (one answer each, no skip; SEBI
  suitability, no fallback) and D10 (declaration confirmed and every gate field value or explicit none). D07b needs
  one tap, and the "use 60" chip counts. A list item saves with its identity alone: D01a the relation, D03a the loan
  type, D04c the policy type, D07a the goal name; D04a and D04b save with nothing, since the tick on D04 already set
  the status. Every amount on a detail screen is optional and becomes a Sharpen this link in the plan.
- After the plan: K01 topic and note optional, K05 the slot required; Q01, Q05 rows start confirmed and never block;
  Q02 needs a change; Q03a a reason is never a condition of leaving; Q06 needs at least one change to reopen the
  spine; O03 exits with No reminder by default; H01j the Sunday choice is optional.
- Admin: L04 an ISIN adds a row (cells, weight and core-or-satellite are required before publish, checked on L05);
  L05 a user ID or persona to preview; L06 a reason to publish (publish_at defaults to now); L09 the two limits have
  defaults, overrides are optional.

How it is carried: every screen that draws an input carries spec.forward (the "Moving forward" block: what the
primary button needs, then Required, Optional, Default and System lines) and a forward tag on every field in
spec.fields. Non-generated screens get both from data/v02/required_optional_edits.json (op "forward", which refuses
an untagged field); the T-num and risk screens get theirs from scripts/gen_spine.py; validate_v02.py fails the
build when a screen with an in, radio or chips-with-fields row lacks the block or a field lacks its tag. Appendix A
is not repeated here; the Changelog tab carries the cause per screen.
