# yeslyf board - Phase 12 brief: corrections, frozen and final markers, tracker

Written 17 Sep 2026 for Claude Code. Sources: the minutes of 16 Sep 2026
(yeslyf_minutes_2026-09-16_spinach_walkthrough.md), the board as built at commit 628b6d3, the live board table
(12 rows, newest 16 Sep 2026 11:53 IST), and Vatsal's decisions of 17 Sep 2026. If the mandatory and optional
inputs run already took the number 12, renumber this phase; the content does not change.

Three passes, one commit each, in this order: Pass 1 corrections, Pass 2 markers, Pass 3 tracker. Pass 0 is a
short append to the minutes file and rides with Pass 1.

## 0. Read me first

### Why this phase exists
Spinach works from the board on one condition (minutes item 19): a frozen marker on each screen and each API, so
they know what will not change. They also asked for a final or open marker per integrations row and a date by
which every row is final (item 12), and for an HoA-side project manager who posts what is done each day (item 21).
Until the markers exist Spinach cannot tell what is safe to build against.

### Standing rules (unchanged, restated)
- Every change carries a cause and nothing else. The causes used in this phase:
  - "minutes 16 Sep 2026, item N"
  - "Gaurav, 16 Sep 2026"
  - "Vatsal, 17 Sep 2026"
- Unconfirmed vendor or regulatory facts are written "to be verified: <item>", no name attached.
- New in this phase: an open product decision is written "to be decided: <item>" on the screen it touches, same
  grammar as "to be verified". The Changelog aggregates them the same way (a "To be decided" section next to
  "To be verified").
- First names only. ASCII only. The brand is yeslyf, lowercase.
- Screen IDs, state IDs and event names are never reused or renamed. Existing event names do not change in this
  phase: Spinach is already reading the Events tab.
- Do not touch: the v0.1 pages, the Meeting, Gaps and Inputs tabs (frozen on 9 Sep 2026; their gap IDs G01 to G13
  stay as they are), the board table's existing rows (append only).
- Causes on a screen are a list: append, never delete history.
- After each pass: rebuild the site, the /review/ copy and the three audience files; run the validation scripts.
- If the repo contradicts this brief (a file, a field name, a count, a phase number), stop and report. Do not guess.

### Decisions this brief carries (Vatsal, 17 Sep 2026)
1. Cloud is AWS and email is Amazon SES. Final.
2. I22 (Google and Apple sign-in at P02) is not a login and not V1: gate "later". P02 is unchanged.
3. The reveal block R01 to R12 freezes as drawn.
4. The frozen marker lives in the repo data, not in the board table. The final or open marker on integrations
   rows is edited on the page.
5. A10a stays as drawn. It waits and reminds; nothing on the board reads an inbox.
6. CAS source, position only, not yet applied to screens: registrar CAS (CAMS and KFintech; funds only; one
   format) first; depository CAS (NSDL or CDSL, whichever the investor's broker uses; funds and shares; two
   formats) next. It closes with Gaurav (W11). The screens it touches stay open until then.
7. Project manager: Vatsal; the deputy on the daily update is to be confirmed with Kajal.

## Pass 0. Append to the minutes file

Append a section "7. Corrections after writing (17 Sep 2026)" to the minutes md. Do not edit sections 1 to 6.

- Item 6: A10a on the board is the wait screen (the S17 landing) with reminders at one hour and 24 hours. Nothing
  reads the CAS from the email. What was declined on the call was never on the board; A10a stays.
- Item 6: "protected with the PAN" holds for the depository CAS only. The registrar CAS (CAMS and KFintech mail
  back) opens with a password the investor chooses when requesting it. A10b already says both.
- Item 6: the fork is not NSDL versus CAMS. The depository CAS comes from NSDL or CDSL depending on where the
  investor's first demat account was opened; HoA cannot choose between them. The choice is depository CAS (two
  formats, funds and shares) versus registrar CAS (one format, funds only).
- Item 4: "nothing to change" is not right in one place. Coming back to the exact screen (item 4) and the state
  landings (S1 always on R01; S3, S4 and S19 on O02) are two different rules and the board only carried the second.
  Fixed in this phase (1.10, 1.12).
- Item 14 against the board: the I01 note and the A06 dev note said the FIU registration was in hand; the call
  said the SEBI registration document is a few days away. Fixed in this phase (1.4).
- Section 3, board upkeep: I17 was listed; I10 (SendGrid) was missed. Email is Amazon SES (Vatsal, 17 Sep 2026).
- Section 3: W08 is shown as due 19 Sep 2026 under Gaurav and Raafiya. On the board W08 was set to delivered on
  16 Sep 2026 with the owner Vatsal and a link to the Events tab.
- Item 1: a number that failed the OTP has proven neither ownership nor consent. Whether it may be stored or
  contacted is a compliance question (W29), not a settled rule.
- Section 5: the A10a gap is not appended (see the first correction). The other four gaps are recorded as
  "to be decided" lines on their screens and as tracker rows.

## Pass 1. Corrections

Each line: where, from, to, cause. "See Ixx" means the screen names the integrations row, never the vendor.
Rule for all screens from now on: dev notes cite I-numbers; the vendor name and its marker are rendered from the
integrations row (2.7), so a vendor change is made in one place.

### 1.1 Cloud
- I17 vendor: "Azure" -> "AWS". Notes: "Indian region." -> "AWS, Indian region. PostgreSQL holds the app data,
  every step saved as it is written. Vault files sit in S3 behind an encrypted link; the link is held in the
  database." Cause: Gaurav, 16 Sep 2026 (minutes item 5).

### 1.2 Email
- I10 vendor: "SendGrid" -> "Amazon SES". Cause: Vatsal, 17 Sep 2026. W02 stays delivered.

### 1.3 Entry and sign-in
- I08 notes: "Entry is always mobile OTP; Google and Apple sign-in come later in the journey, at P02 (I22)." ->
  "Entry is always mobile plus OTP. A person is registered the moment the OTP is right; email is never the login."
  Cause: minutes 16 Sep 2026, items 1 and 2.
- I22 gates: "launch" -> "later". Notes -> "Not a login and not V1. An optional way to fill the email at P02; P02
  is unchanged and the email is typed." Cause: Vatsal, 17 Sep 2026.

### 1.4 Registration status
- New row I00 (sorts first). Category "Regulatory". Vendor "SEBI". Role: "The corporate RIA registration that
  vendor contracts, sandbox requests and the store listings are made under." Screens: none. Gates: launch.
  Fallback: none. Notes: "About a week away as of 16 Sep 2026. Public documentation does not wait for it;
  contracts and most sandboxes do. to be verified: which rows need the registration document before a sandbox."
  Cause: minutes 16 Sep 2026, items 11 and 14.
- I01 notes: "FIU registration in hand (Vatsal, 16 Sep 2026)." -> "FIU onboarding follows the corporate RIA
  registration (I00)." The rest of the note stays. Cause: minutes 16 Sep 2026, item 14.
- A06 dev note 1: "TSP options: Setu, Finvu, OneMoney. Corporate RIA FIU registration is in hand per spiff." ->
  "AA vendor: see I01. FIU onboarding follows the corporate RIA registration (I00)." Same cause.

### 1.5 Vendor names on screens
- P02 dev note 1: "Vendor: Digio for KRA/CKYC fetch and eSign, unless HoA already has one." -> "KYC fetch: see
  I06. eSign on P03: see I07." Cause: Vatsal, 17 Sep 2026.
- H07 dev: "Chat routed to the CRM desk (platform to be decided; section 6)." -> "Chat routed to Zoho Desk (see
  I14)." The rest of the note stays. Cause: minutes 16 Sep 2026, item 20.
- E02 dev note 1 and E07 dev note 1: the "or an API layer ..." wording -> "Direct BSE StAR MF APIs (see I02), the
  newer JSON interface. to be verified: which BSE StAR MF services exist in the JSON interface (client
  registration, mandate, order, SIP, payment, reports)." Cause: Gaurav, 16 Sep 2026 (minutes item 13).
- L04 dev: "ISIN facts via an external API (spiff, Q19): AMFI or MF data API for funds; exchange master for
  listed instruments. Refresh NAVs nightly." -> "Instrument master, prices and NAVs: see I05. Refresh NAVs
  nightly." Cause: Vatsal, 17 Sep 2026.
- A10b dev note 1: "Parsing via the open-source casparser library or a vendor (spec v0.1 A09)." -> "CAS parsing:
  see I23." Add a dev note: "The registrar CAS opens with the password the investor chose when requesting it; the
  depository CAS opens with the PAN in capitals. The field accepts either." Cause: Vatsal, 17 Sep 2026.
- M01: the Tool column is rendered from the integrations rows by I-number, so it cannot drift again. Row by row:
  payments I09; CRM, nudges, support I14; push I12; KYC I06 and eSign I07; Account Aggregator I01; calendar I14
  (Zoho Bookings) and video I24; analytics I13. The two rows that today say "Appsmith ... or Retool" read
  "to be decided: the tool over the app database (admin brief, W12)". Logic line 3 ("CRM platform: to be decided
  ...") -> "CRM platform: Zoho One (I14)." Add a logic line: "External as far as possible, with a possible
  consolidation layer; what Spinach builds and what is bought is the admin brief (W12)." The closing note loses
  "Platform to be decided (one platform);". Causes: Vatsal, 16 Sep 2026 (Zoho One decided); minutes 16 Sep 2026,
  item 20.
- Admin and CRM v0.2 page: every "platform to be decided (one platform)" string, including the note_v02 values on
  the 5 stack entries and 9 placement rows, the intro line and the placement note -> "Zoho One (I14)". Nothing
  else on that page changes in this phase; the full rebuild is Phase 13, after the admin session. The v0.1 keys
  and the v0.1 page are untouched. Cause: minutes 16 Sep 2026, item 20.

### 1.6 Integrations rows: screens lists
The four "to be verified: screens: the vendor is also named on ..." flags are resolved and deleted:
- I02: add E10 and E11 (mandate and SIP registration run on this rail). E04 and H06 only mention it: not added.
- I03: E11, G13 and L04 only mention it: not added.
- I09: add Q03a, Q03c (subscription cancel, pause and webhooks) and K04 (the a la carte charge runs through P04).
  M01 only mentions it.
- I01: M01 only mentions it.
- I14: add K01, K05, K02, K06. Role gains: "Bookings for adviser slots; Creator; Campaigns; Flow; connected to
  Slack." Cause: minutes 16 Sep 2026, section 1.
Cause for the rest: Vatsal, 17 Sep 2026.

### 1.7 Integrations rows: two missing vendors
- New row I23. Category "CAS parsing". Vendor "not decided". Alternatives: "the open-source casparser library run
  on the server; a parsing vendor; smallcase Gateway's fund holdings import on MF Central rails in place of
  parsing". Role: "Reads the uploaded CAS PDF into holdings and their values; no transactions." Screens: A10b,
  A10c. Gates: launch. Fallback: "D02b and D02c: the holdings are typed". Cause: minutes 16 Sep 2026, item 6.
- New row I24. Category "Calls: video and recording". Vendor "not decided". Alternatives: "a meeting tool inside
  Zoho One (to be verified); Google Meet; Zoom". Role: "The join link on K02 and the recordings listed on K06."
  Screens: K02, K06. Gates: launch. Fallback: "K02 gives a phone call in place of a join link; K06 lists calls
  without recordings". Notes: "to be verified: recording consent and retention (K06)." Cause: Vatsal, 17 Sep 2026.

### 1.8 Documentation links (minutes item 13: read the public documentation of the final vendors now)
Seed docs_url on three rows; every other row stays empty for the documentation push (W16).
- I01: https://finvu.github.io/sandbox/ (the sandbox entry on Sahamati's public list)
- I03: https://developers.gateway.smallcase.com/
- I02: https://www.bsestarmf.in/APIFileStructure.pdf (the web services structure document, version 3.5, August
  2023). Note on the row: "to be verified: that this document covers the newer JSON interface HoA will use. It
  says a member gets the API documents and test market credentials by mailing BSE."
Cause: Vatsal, 17 Sep 2026.

### 1.9 The checkout states (a state nobody can reach, and one that is missing)
P03 says payment cannot start without a completed eSign, and P03 leads to P04. So "S2b Paid, eSign incomplete"
cannot happen to a new user; yet P03 parks its failures in S2b, whose message says the payment went through and
whose day 14 step opens a refund. Cause for everything in 1.9: Vatsal, 17 Sep 2026.
- S2b "who": "Paid, eSign incomplete" -> "Checkout started, eSign incomplete (not paid)". Lands on P03 (stays).
  Ladder: keep the day 1 push and the day 3 WhatsApp; both copy slots are rewritten as slots with no payment
  claim; remove the day 14 email, the refund escalation on both tiers, and payment_reference from the CRM task.
  Exit -> "eSign done (P03) -> S2c. No progress after day 3: the S2 ladder carries on from its current
  day; day 82 -> stop".
- New state S2c "eSign done, payment not completed", between S2b and S3. Lands on P04. Rule: the signed agreement
  is not asked again while its version is current. Ladder: day 1 push (slot N-S2c-d1), day 3 WhatsApp (slot
  N-S2c-d3); copy slots only. Exit -> "paid (P05) -> S3. No progress after day 3: the S2 ladder carries on from its current day; day 82 ->
  stop". Escalation:
  ladder only. CRM task: none.
- New mock screen N31 "State S2c: eSign done, payment not completed", template T-msg, built like N07.
- N07 is rebuilt for the new S2b: title, the three cards, no refund card.
- S1 exit: "reveal seen (R09) -> S2; paid -> S2b or S3" -> "reveal seen (R09) -> S2".
- S2 exit: "paid -> S2b or S3; day 82 -> stop" -> "P02 started -> S2b; eSign done -> S2c; paid -> S3; day 82 ->
  stop".
- P04 states gain: "Payment abandoned after the eSign: state S2c; the return lands here and the agreement is not
  signed again while its version is current".
- N01 (the state table), the Admin and CRM v0.2 nudge matrix, the journey stage picklist and the Events tab
  (state_enter for S2c) follow from states.json. States: 26 -> 27. Screens: 193 -> 194.

### 1.10 Coming back: two rules, one order (minutes item 4)
X00 gains a card "Saving and coming back":
1. "Every step is saved on the server as it is written. A half-typed number is a draft: it is never read by the
   engine and never shown as an answer. A value counts once the person moves forward, taps That's about right, or
   taps a chip."
2. "Reopening the app after a kill, a restart or a session timeout returns to the exact screen that was left,
   with its draft."
3. "A state landing (section N) applies when the state has changed since the last visit or when the person
   arrives from a nudge link. Otherwise rule 2 wins."
4. "to be decided: client-side storage and the session timeout rule, by Spinach's data lifecycle map (W21)."
Cause: minutes 16 Sep 2026, item 4; Vatsal, 17 Sep 2026.

### 1.11 X00, other lines
- "... write to the v02_comments sheet tab when the endpoint is set." -> "... are written to the shared board
  table as rows; the pill in the top bar reads live or offline." Cause: Vatsal, 17 Sep 2026.
- The field tag sentence gains "read" (see 1.14).
- "Decisions baked into v0.2" gains: "Entry is mobile plus OTP; a person is registered the moment the OTP is
  right; email is never the login" and "Cloud AWS; email Amazon SES". Causes as in 1.1 to 1.3.
- New cards "What frozen means" (2.2) and "How Spinach works from this board" (2.8).

### 1.12 S1 landing
- S1 lands on the first unanswered reveal screen, R01 to R07; R01 stays drawn as the example on N05. The two copy
  slots that say "stopped at your name and age" take the screen title as a variable. Cause: minutes 16 Sep 2026,
  item 4.

### 1.13 To be decided lines (the gaps from minutes section 5, written on their screens)
- A04: "to be decided: placement, right after the OTP or after the first reveal questions." Item 10.
- A03: "to be decided: the new-user branch follows A04's placement." Item 10.
- H06: "to be decided: storage mechanics: upload, tags, expiry dates, versions, and which files a person may
  delete; files in S3 behind an encrypted link, the link in the database." Item 5.
- A10, A10c, D02c, G12a: "to be decided: CAS source for V1. Position: registrar CAS first, depository CAS next
  (Vatsal, 17 Sep 2026); to be verified: parsing effort." A10c adds: "With holdings and values only (minutes item
  6), SIPs are not read from the CAS; D06d asks."
- A10a logic gains: "This screen waits and reminds. Nothing reads the email or the inbox." Vatsal, 17 Sep 2026.
- A02 and A03, compliance reason "consent": "to be verified: whether a number that failed the OTP may be stored
  or contacted; ownership and consent are not proven." Vatsal, 17 Sep 2026.
- O02 dev gains: "progress_pct is the display ring only (endowed, rule 11). The CRM's profile fulfilment
  percentage (minutes item 1) is a separate, unendowed number defined in the admin spec (W26). Never one stored
  number for both." Vatsal, 17 Sep 2026.

### 1.14 Every field entry carries a tag
290 field entries; 158 carry required, optional, default or system. The other 132 sit on 29 screens that show or
hold values captured elsewhere (O02, A05a, A09, A10, A10a, D09, G01a, G03 to G07, G09 to G14, G12a, K02, K03,
K04, K06, E08, E09, H05, Q03, Q03c, Q06a).
- New tag "read": the screen shows a value captured on another screen. Tag "system" where the app or a vendor
  writes it (source system, ids, links, timestamps, queues, records).
- The 18 entries stored as plain strings take the same shape as the rest ({f, forward, note}).
- The spec panel heading reads "Fields captured" when any entry is required, optional or default; otherwise
  "Fields read". No Moving forward block is added to these 29 screens.
- Result to report: 290 of 290 tagged. Cause: Vatsal, 17 Sep 2026.

### 1.15 Causes on the execution screens
- E02, E03, E06, E07, E08, E09, H06: append "minutes 16 Sep 2026, item 12 (rails final)" after "brief G1
  (default, not confirmed in the meeting)".

### 1.16 Test rows
- Exports and counts ignore three groups of rows in the board table (they cannot be deleted): setup / TEST /
  probe; wireframes_v02 / A02 verdict and comment of 16 Sep 2026 10:25 IST; wireframes_v02 / O01 "somil:example".
  Keep the ignore list in the repo, keyed by page, item and time. Cause: minutes 16 Sep 2026, section 1.

## Pass 2. Frozen and final markers

### 2.1 Screen marker
- Per screen, in the repo data: status frozen or open; since (date); cause; for open screens the reason (the
  "to be decided" or blocking "to be verified" lines, picked up automatically); for frozen screens an "owed" list.
- Shown as text, never colour alone: in the left list, in the screen header, in the spec panel ("Open because:
  ..." or "Frozen since ..., owed: ..."), and as a filter next to tier, path, state, compliance, template.
- Changelog gains "Freeze register" (counts, then the open screens with their reasons), "Unfreeze log" (empty
  today) and "To be decided". Counts for Spinach gain frozen and open per section and per template.
- Only a commit changes a freeze status. No control on the page.

### 2.2 What frozen means (the X00 card, verbatim)
"Frozen: this screen's template, its fields and their tags, its branches, its states and its events will not
change without an entry in the Unfreeze log on the Changelog tab, giving the date, the cause and what changed.
Not covered by frozen: copy, prices, counts, bands, scoring maps and grid values; those are config and arrive
later without changing the build. Open: something named on the screen can still change its build; the reason is
written on it."

### 2.3 Templates
All 21 templates are frozen today (element types and their order). Shown in the template filter and in the
template table on the Changelog. Cause: minutes 16 Sep 2026, item 19; Vatsal, 17 Sep 2026.

### 2.4 Open on day one: 34 screens. Everything else is frozen: 160 of 194.
- A03, A04: video placement (1.13).
- A10, A10c, D02c, G12a: CAS source (1.13).
- H06: storage mechanics (1.13).
- P04: mandate type for monthly and quarterly recurring UPI; whether netbanking can carry a mandate.
- E02, E03, E04, E07, E08, E09, E10, E11: built last; open until the vendor documentation is read (minutes item
  11). E01, E05 and E06 are frozen.
- Q02: proration and refund on a period switch.
- Q04, N28: what happens to advice if the annual confirmation is not given.
- D02d: NPS on AA. A05a: whether FIP health is readable before consent.
- K02, K06: no video and recording vendor (I24); recording consent.
- M01: the admin brief (W12).
- L00 to L09: the table shapes are owed under W04 (in progress, due 19 Sep 2026). They freeze with that delivery.
  If the drawn shapes are already the delivery, report it and Vatsal flips them; that makes 24 open, 170 frozen.

### 2.5 The 27 "to be verified" items: which block a freeze, which are only owed
Blocks (the screen is open): CAS parsing effort (A10); NPS on AA (D02d); FIP health before consent (A05a);
direct plans and the RIA code on this rail (E07 to E09); e-NACH approval time and amend or new mandate (E10);
mandate type and limits for recurring UPI (P04); proration on a period switch (Q02); recording consent and
retention (K06); the nomination rule and UCC field set (E02); what happens without the annual confirmation (Q04,
N28); whether netbanking can carry a mandate (P04).
Owed (the screen is frozen, the item is listed as owed): DPDP notice text (H09, N01, N30; A04 is open anyway);
V1 covers CAS only via A10 (D04a to D04c); WhatsApp template lead time (N04); call lengths (K01, K05); maximum
AA consent validity and fetch frequency (A05, A06); record formats (L08, with the L group); the GST split rule
(P04, open anyway); the Q7 and Q8 wording (D08g, D08h); the RPQ scoring map (D08a to D08h, D09); UPI autopay and
e-NACH limits (E10, open anyway); the EPF service numbers and deep link (D02e); the declaration wording (D10);
the earliest SIP start date (E11, open anyway); the grid values (L03, with the L group); the annual confirmation
item on N01 (the table itself is frozen).

### 2.6 Integrations rows: final or open
- New field per row: choice, final or open. New field at the top of the page: "Every row final by" (a date; empty
  today).
- Both are edited on the page like owner and status, saved as rows in the board table, with history.
- Seeds at build, overridden by any later row in the table:
  final: I01, I02, I03, I04 (minutes item 12); I08 (item 3); I14 (Vatsal, 16 Sep 2026); I17 (Gaurav, 16 Sep
  2026); I10 (Vatsal, 17 Sep 2026). Every other row: open, until it is set on the page (W01). I05 was not
  confirmed on the call.
- The marker sits next to the vendor name, with a filter. The status list (not started to production) is
  unchanged: it answers a different question.
- No costs on this page: the board is public and needs no login. Replace the Cost field's hint with "kept off
  the board". Existing values: none.

### 2.7 Integration line on every screen
In the spec panel: "Integrations: I06 CAMS KRA, open; if it slips: P02 asks the address" or "Integrations: none".
Rendered from the rows' screens lists; the live page reads the current choice from the board table; the audience
files carry the choice as of the build date, with that date shown.

### 2.8 The X00 card "How Spinach works from this board"
Five lines: what frozen and open mean; what final and open mean on the Integrations tab; questions go in the
comment box of the screen under the identity Spinach; answers appear under the question and in the Tracker's
question list; the daily update is posted from the Tracker.

## Pass 3. Tracker (project management on the page)

### 3.1 The tab
- New tab "Tracker", after "Wireframes v0.2". The "Owed to Spinach" table (W01 to W09) moves there with its saved
  rows; the Integrations tab keeps a link. IDs continue the W series (T and S are taken by the 9 Sep brief items
  and the states).
- Fields: id, item, direction (HoA to Spinach, Spinach to HoA, HoA internal), owner, due, status (not started, in
  progress, delivered, blocked), blocked by (a row ID), source (the cause), lands at, notes. Edited on the page:
  owner, due, status, blocked by, notes. History under each row.
- A milestone strip on top: 19 Sep 2026 (W03, W04 due); 21 Sep 2026 (Spinach's questions session); about 23 Sep
  2026 (I00); about 30 Sep 2026 (admin panel, CRM and website session); every integrations row final (the date
  from 2.6).
- Overdue rows say so in words.

### 3.2 Seed rows (source: minutes 16 Sep 2026 unless stated)
- W10 Frozen marker per screen; final or open per integrations row; the date every row is final. HoA to Spinach.
  Vatsal. In progress. Items 12, 19. Lands at Wireframes v0.2 and Integrations.
- W11 Close the CAS source with Gaurav; share a sample CAS file with Spinach. HoA to Spinach. Vatsal. Item 6.
  Lands at A10, I23.
- W12 Admin panel brief: what Spinach builds, what is bought, what the app must expose; includes the tool over
  the app database. HoA to Spinach. Vatsal and Kajal. Due about 30 Sep 2026. Item 20.
- W13 CRM plan. HoA to Spinach. Vatsal and Kajal. Due about 30 Sep 2026. Items 20, 21.
- W14 Website brief. HoA to Spinach. Vatsal. Due about 30 Sep 2026. Items 20, 21.
- W15 Name the project manager who posts the daily update. HoA internal. Delivered: Vatsal; the deputy on the
  daily update is to be confirmed with Kajal. Item 21; Vatsal, 17 Sep 2026.
- W16 Public documentation from every final vendor now; a sandbox ask before the contract; Spinach on the vendor
  threads. HoA to Spinach. Kajal with Raafiya. Item 14. Notes: "Spinach called this their most important item."
  Lands at the docs field on Integrations.
- W01 (exists): owner Kajal with Raafiya; notes gain "final or open and the dates per row (item 12)".
- W17 The date for handing the maths and logic to Spinach through I04. HoA to Spinach. Harish and Somil. Item 17.
- W18 HoA Core Platform API details, including the data-in APIs, with bands or midpoints as the input shape. HoA
  to Spinach. Gaurav and Raafiya. Item 17. Lands at I04.
- W19 The corporate RIA registration, then the vendor contracts. HoA internal. Harish. Due about 23 Sep 2026.
  Items 11, 14. Lands at I00. W06 is blocked by W19.
- W20 Project plan of Spinach's next steps. Spinach to HoA. Eshani. Item 21.
- W21 Data lifecycle map: what is saved when, session and storage rules, shared onto the board. Spinach to HoA.
  Item 4. Lands at X00 (a link).
- W22 Technical writing and user stories from the wireframes as they stand. Spinach to HoA. Item 21.
- W23 The two rounds of admin panel sketches consolidated with Kajal's feedback, for the admin session. Spinach
  to HoA. Item 20.
- W24 Questions for 21 Sep 2026; Ankur's field-level Excel; Saquib's further questions. Spinach to HoA. Due
  21 Sep 2026. Items 19, 21. Lands at the screens' comment boxes.
- W25 V1 without in-app execution is E05 and E06; closes gap G10 of 9 Sep 2026. HoA internal. Vatsal. Delivered.
  Item 11.
- W26 Lead stages (lead, verified lead) and the profile fulfilment percentage as contact fields. HoA internal.
  Vatsal and Kajal. Item 1. Lands at the admin spec (Phase 13).
- W27 Welcome video placement (A04). HoA internal. Owner empty. Item 10.
- W28 Vault storage mechanics (H06). HoA internal. Owner empty. Item 5.
- W29 Whether a number that failed the OTP may be stored or contacted. HoA internal. Compliance. Vatsal, 17 Sep
  2026. Lands at A02.

### 3.3 The daily update
A button "Copy today's update" on the Tracker. It composes plain text for WhatsApp from the last 24 hours of the
board table plus the build data, and copies it. Anyone can press it. No messaging API. At most about 15 lines,
ASCII, first names, no costs. Sections, each dropped when empty: Delivered; Now final (integrations rows);
Frozen and unfrozen (from the freeze dates and the Unfreeze log); Spinach questions, new and answered, with
screen IDs; Overdue, with owner and days; Next milestone; the board link. Expected shape:

    yeslyf board, 18 Sep 2026
    Delivered: W10 markers
    Now final: I10 Amazon SES; I17 AWS
    Frozen: 160 screens, 21 templates. Open: 34, reasons on the Changelog
    Spinach questions: 3 new (A10b, D05a, P04); 1 answered (A02)
    Overdue: none
    Next: 19 Sep, W03 and W04 due
    <board link>

### 3.4 Spinach's questions
- A list on the Tracker of every comment written under the identity Spinach, on any page: screen or row ID, age,
  open or answered.
- An answer is a new row on the same item (field "answer", with who). A question is answered once an answer row
  follows it. The answer shows under the question on the screen.
- An import script for Ankur's Excel (screen ID, field, question): dry run first, then one board row per line
  under the identity "Spinach (Ankur)".

### 3.5 Identity
- No write on any page without an identity chosen; the page says so in plain words. Nine of the 12 saved rows
  have no name. Old rows stay and show "(no identity)".

## 4. Report back (one md file per pass)
- Counts: screens 194; frozen and open with the open list and reasons; templates 21 frozen; field entries 290 of
  290 tagged; states 27; integrations rows 25 (I00 to I24) with 8 seeded final; tracker rows W01 to W29; to be
  verified and to be decided totals; audience file sizes.
- Validation added: no vendor names in screen dev notes (Digio, Setu, OneMoney, Cybrilla, SendGrid, Azure,
  HubSpot, OneSignal, Calendly, Appsmith, Retool); every open screen has a reason; no frozen screen carries a
  blocking item; every screens entry on an integrations row is a live screen ID.
- Anything in the repo that contradicted this brief, and what was done about it.

## 5. Not in this phase
- Phase 13, after the admin session with Kajal: the Admin and CRM page rebuilt against Zoho One, the tool over
  the app database, lead stages and the fulfilment percentage defined, the website brief.
- The CAS decision applied to A10, A10c, D02c and G12a, once W11 closes.
- Filling docs links and sandbox dates beyond the three seeds (W16).
