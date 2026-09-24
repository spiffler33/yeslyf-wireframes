# Spinach questionnaire SQ1 (received 22 Sep 2026): HoA answers

Written 24 Sep 2026 by Vatsal for the board. This file is the source of every row on the Spinach Questions tab
(data/questions.json is generated from it and from the three xlsx files; see yeslyf_phase14_brief.md). It lives at
inputs/spinach/2026-09-22/SQ1_answers.md next to the three files it answers:

- 2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx (11 sheets)
- Yesly_Backend_Clarifications_Questionaire.xlsx (1 sheet, 15 questions)
- 2026_Sep_22nd_Yesly_Journey_Description.xlsx (6 sheets: summary plus 5 journeys)

## How to read this file

Status uses the board's three words and nothing else:
- frozen: the answer stands. It changes only through the unfreeze log with a cause.
- open: HoA still has to decide this row's own answer. The row carries "to be decided: <item>", an owner
  (a function, not a name) and a date.
- owed: a fact somebody has to verify before the row can be frozen. The row carries "to be verified: <item>",
  an owner and a date. The owner can be Spinach.

A row is frozen when its own answer stands even though a linked item elsewhere is still open; the linked item has
its own row (a W row on the Tracker, an I row on Integrations, a screen on Wireframes v0.2) and the answer names it.

Cause, per row:
- an answer that begins "Accepted as proposed" carries the cause "Spinach proposal SQ1, accepted, Vatsal, 24 Sep 2026"
- every other frozen row carries the cause "Vatsal, 24 Sep 2026"
- an open or owed row carries no cause until it is frozen; the freezing commit writes "approved by <first name>,
  <date>" (or "delivered by <first name>, <date>" for an owed item)

Owner labels on the tab (functions): Product, Tech, Admin, Compliance, Financial planning, Investment advisory,
Copy, Team session (30 Sep 2026), Spinach. The Tracker rows behind them carry first names as the Tracker does.

Due dates below are proposals; Vatsal edits them on the Tracker.

Refs are board IDs: a screen (A08), a state (S2c), an integrations row (I08), a tracker row (W35), a tab (N01, X00,
Events). Part D (behaviour by template) and Part E (route-access map) are referenced by several rows and are
rendered on the tab as two short tables.

Column key for every table: id, status, Yesly comment (the export text, verbatim), refs, owner and due (open and
owed rows only).

---

## Part A. Frontend Technical Questionnaire

### A1. Sheet "Frontend Technical" (FE-01 to FE-80)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-01 | owed | to be verified: the exact Expo SDK and React Native versions, pinned by Spinach before development starts and stated in the project plan. The two supplementary sheets give two different floors (0.76+ on Foundation row 2, 0.87+ on row 3); one pair of numbers, please. HoA confirms on receipt. | W36 | Spinach, 28 Sep 2026 |
| FE-02 | frozen | Accepted as proposed. Expo with Development Builds from day one; Razorpay, Finvu and biometrics need native configuration; Expo Go is not a constraint. | I01, I09 | |
| FE-03 | frozen | Accepted as proposed. | | |
| FE-04 | frozen | Accepted as proposed. Expo Router only, one route per screen ID (A02, D02a, K05), so a screen ID, a route and an event name read the same. | | |
| FE-05 | frozen | Three route groups, drawn by the board's paywall line. Public: A01, A02, A03. Registered and unpaid: A04, R01 to R12, X01, P01 to P05. Paid: O01 onward (A05 to A10c, D, G, K, E, H, Q). The tier (DIY, DIWM, DIFM) is read from the subscription state, never from a route. The full map is Part E. | N01, P05 | |
| FE-06 | frozen | The map in Part E. Access is decided by the server-side state router (N01, states S1 to S25), never by a check inside a screen; a screen reached out of state redirects to that state's landing screen. | N01 | |
| FE-07 | frozen | After 30 minutes of inactivity the session locks. Re-authentication is biometric if enrolled, otherwise OTP (A02 with the number prefilled, then A03). After re-auth the person lands on the exact screen they left (minutes 16 Sep 2026, item 4). Nothing is lost: every saved step is on the server. There is no password and no PIN in this app. | A02, A03 | |
| FE-08 | frozen | Yes. Every returning-user state S1 to S25 carries a deep_link on the states tab (N01): that is the screen a push, a WhatsApp message or an email opens. One route per screen ID. No personal data in any URL: a signed token resolves to the person on the server. to be verified: the universal-link domain (W35). | N01, W35 | |
| FE-09 | frozen | Every external flow has a return state on the board. Payment: S2c lands on P04; a failed renewal lands on Q03b (S12). eSign: S2b lands on P03. AA consent: the return from the vendor lands on D01 with the fetch running in the background; a decline or a timeout lands on A09. CAS: S17 lands on A10a, then A10b. A la carte payment (K04): K05. On every return the app re-checks the vendor's authoritative status before it shows success. | N01, P03, P04, A06, A09, A10a, K04 | |
| FE-10 | frozen | By template, Part D. In short: on the reveal and the spine, back is the previous question with the value kept; in a vendor webview (A06, P03, P04) back cancels the vendor step and lands on the state's landing screen; on a progress screen (R08, A07, G01, G01a) back is disabled; on a sheet back closes it; on a hub (O02, H01) back minimises the app; on P01 back is X01. | Part D | |
| FE-11 | frozen | Accepted as proposed. Redux Toolkit with one feature slice per board section: reveal (R), checkout (P), source (A05 to A10c), spine (D), plan (G), calls (K), execution (E), home (H), subscription (Q). | | |
| FE-12 | frozen | Shared: session, subscription and tier, the current state (S number), spine completion flags and progress, aa_status, the offline write queue. Local: a screen's own inputs until autosaved, sheet open or closed, scroll. Server data lives in TanStack Query and is never copied into Redux. | O02 | |
| FE-13 | frozen | Accepted as proposed. | | |
| FE-14 | frozen | Persist: the last route, the session tokens (secure storage), the biometric flag, the encrypted queue of spine values not yet synced (purged on sync). Nothing else. The server holds every saved step (minutes item 4). No persisted query cache. | | |
| FE-15 | frozen | Accepted as proposed; folder names follow the board's section letters (FE-11). | | |
| FE-16 | frozen | The 21 templates on the board are the shared component list: T-tap, T-num, T-sheet, T-progress, T-chart, T-hub, T-card, T-card-stack, T-list, T-detail, T-review, T-webview, T-paywall, T-source, T-upload, T-picker, T-locked, T-split, T-video, T-table, T-msg. A screen is an instance of its template with its fields. Build one component per template; buttons, inputs, headers and loaders sit underneath. | X00 | |
| FE-17 | owed | to be verified: there is no Figma yet. Spinach owns visual design and produces it after the frozen wireframes. Until an approved visual design exists, Wireframes v0.2 on the board is the source of truth for structure, fields, tags, states and events. The Figma file and its version are recorded on X00 when they exist. | X00, W22 | Spinach, no date |
| FE-18 | frozen | A change to a frozen screen's template, fields and tags, branches, states or events goes through the unfreeze log (date, screen, cause, what changed). A visual-only change (colour, type, spacing, motion) does not, and the approved design is the visual QA source. Copy, prices, counts, bands and grid values are config and never a code change (I15). | X00, I15 | |
| FE-19 | frozen | Accepted as proposed. | | |
| FE-20 | frozen | Phones only. No tablets, no foldables. iOS 16+ and Android 10 (API 29)+ as proposed on the Foundation sheet. Layouts reflow; no fixed dimensions. | | |
| FE-21 | frozen | Portrait only, the T-chart screens included. | | |
| FE-22 | frozen | None intended. The one platform difference is SMS auto-read of the OTP on Android (A03). No Google or Apple sign-in in V1 (I22, later). | A03, I22 | |
| FE-23 | frozen | Already on the board since 17 Sep 2026: every input screen carries a "Moving forward" block and every field a tag (required, optional, default, system, read); 79 screens, 158 fields. Conditional fields are written on their screen: the P02 address only when the KRA record is not found; the K05 same-adviser chip only when the continuity flag is on; a D screen opens only for a type ticked on D02, D03 or D04. React Hook Form accepted. | Wireframes v0.2 | |
| FE-24 | frozen | One-question screens (T-tap, T-num): validate on Continue, with the format mask live (digits, Rs grouping). Multi-field forms (P02, D01a, D03a, D04a to D04c, D07a): on blur per field and again on Continue. Never on every keystroke. | Part D | |
| FE-25 | frozen | Accepted as proposed. | | |
| FE-26 | frozen | The copy is the content track (owner: Copy) and lands by screen ID and copy slot without a release (I15); build with placeholder text. Rule for the placeholders: short, says what to fix, no technical words. to be verified: the validation and error copy (W39). | I15, W39 | |
| FE-27 | frozen | Amounts: whole rupees, no decimals, Indian grouping (12,50,000), "L" and "Cr" shorthand accepted on entry and expanded, 12 digits maximum. Mobile: +91 only at launch, 10 digits, first digit 6 to 9. OTP: 6 digits. PAN: 5 letters, 4 digits, 1 letter, the fourth letter P. Name: as per PAN; letters, spaces and dots; 100 characters. Date of birth: 18 or older. Percentages: whole numbers. The per-field bands and validation ranges come as one table and do not block the components: to be verified: the bands and ranges table (W40). | A02, A03, P02, W40 | |
| FE-28 | frozen | Numeric keypad on every T-num screen with the keyboard's Done acting as Continue. Keyboard-aware scrolling on the multi-field forms (P02, D01a, D03a, D04a to D04c, D07a). Auto-advance across the six OTP boxes on A03 only. No auto-advance anywhere else: one question per screen. | Part D | |
| FE-29 | frozen | By template, Part D. Long operations have their own progress screen on the board: R08 (sketching your paths), A07 (fetching), G01 and G01a (building your plan). Every API-driven screen shows a skeleton, never a spinner over content. Navigation on the spine is optimistic: the autosave is queued and retried; a write that still fails shows a non-blocking "not saved yet" line and the next Continue waits for the queue to drain. | R08, A07, G01 | |
| FE-30 | frozen | Accepted as proposed. The empty states are already named per screen on the board (K06 no calls yet, H06 empty vault, G12 no holdings, D01 no members yet, H04 nothing queued); their copy is the content track. | | |
| FE-31 | frozen | Validation: inline, next to the field. Network: the offline banner plus the queued write (Connectivity row 3). Expired session: FE-07. Failed third party: a drawn state per vendor: A09 (AA partial or failed), A05a (bank slow), A10c (parse failed), P03 (eSign retry, S2b), P04 (payment failed) and Q03b (renewal failed, S12), the E screens per vendor status. Each says what to do next. | A09, A05a, A10c, P03, P04, Q03b | |
| FE-32 | frozen | Accepted as proposed. Retry freely: reads and autosave writes. Never blind-retry a payment (P04, K04), a consent (A06), an eSign (P03), an order or a mandate (E03, E04, E10, E11): re-query the vendor by reference first. | | |
| FE-33 | frozen | Every reveal screen (R01 to R07) and every spine screen (section D) autosaves per field (rule 12). The reveal resumes at the first unanswered screen (S1); the spine resumes from O02 at the first incomplete screen (S4); checkout and vendor flows resume by state (S2b, S2c, S17). K01's topic and note are the only other draft. Nothing else. | N01, O02 | |
| FE-34 | frozen | No unsaved-changes dialog anywhere. Leaving a screen is a silent autosave with a Saved toast (rule 12; Vatsal, 11 Sep 2026); the "when will you finish" prompt was considered and rejected. One exception, and it is a line on the screen, not a modal: a vendor webview (A06, P03, P04) says that leaving restarts the vendor step. This overrides the proposal. | D spine, A06, P03, P04 | |
| FE-35 | frozen | Multi-step flows: the reveal R01 to R07 (back and forward, values kept); the spine D01 to D10 in eight sections, with the section map and the endowed progress ring on O02 (rule 11) and a relief card between sections (D12a to D12h); the RPQ D08a to D08h (tap only, back allowed, a changed answer re-scores D09); checkout P01 to P05 (forward only past P03: a signed agreement is not signed again while its version is current); the one-time investing setup E02. | O02, D12a, D09, P03, E02 | |
| FE-36 | frozen | Accepted as proposed. On return to the foreground re-check payment (P04), eSign (P03) and consent (A06, A07) with the vendor before showing any result. | | |
| FE-37 | frozen | Read the device's last route and the server's state; when they disagree the server wins and the state router lands the person (N01). Every saved step is on the server (minutes item 4), so a restart never loses data. | N01 | |
| FE-38 | frozen | The flow is drawn: A05 chooses; A06 is Finvu's consent flow in a webview; the return lands on D01 and the fetch runs server-side in the background while the person answers (a "fetching your accounts" pill opens A07); A08 opens as a sheet when the fetch completes; A09 on a decline, a timeout or a failure. Provider-specific code stays behind one module, as proposed. to be verified: whether Finvu's current integration is a redirect URL, a hosted webview or a React Native SDK, read from the Finvu documentation Spinach already holds (W37). | A05, A06, A07, A08, A09, I01, W37 | |
| FE-39 | frozen | Each state is drawn. Pending: the pill on the section strip (A07 on tap). Connected: A08, the sheet, with include and exclude per account. Cancelled, declined or timed out: A09 with the CAS and manual ways. Partial: A09 rows per FIP with retry; "continue with what we have" lands on D01. A later retry that succeeds merges into A08 with a notification. Bank slow: A05a. | A05a, A07, A08, A09 | |
| FE-40 | frozen | Initiated and processing: P04 in progress. Success: P05. Failed: P04 "payment failed, retry with another method, nothing is lost". Abandoned after the eSign: S2c (lands on P04; the agreement is not signed again). Mandate pending bank approval: P04 allows entry with billing marked pending. Recovery: re-query Razorpay by order ID before any retry. Renewal failed: Q03b and H01f (S12). Lapsed: Q03c and H01g (S13). Refund requested: Q03a (S24). | P04, P05, Q03a, Q03b, Q03c, N01 | |
| FE-41 | frozen | State S2c. On return the app asks the backend, which asks Razorpay by order and payment ID; the webhook is authoritative; closing the app is never read as a failure. | P04, I09 | |
| FE-42 | frozen | P02 is in the app: name as per PAN, PAN, date of birth, email; the KRA lookup is server-side; the address fields appear only when the record is not found. P03 is the vendor eSign inside a webview; the return lands on P04. Full KYC for execution (bank, nominee, FATCA) is deferred to E02. The KYC vendor (I06) and the eSign vendor (I07) are open on the Integrations tab (W34, owner Admin with Compliance); the screens do not wait for them. | P02, P03, E02, I06, I07, W34 | |
| FE-43 | frozen | eSign cancelled or timed out: S2b lands on P03 with retry; the existing eSign status is checked before a new request, as proposed. KRA record not found: the address fields on P02; the agreement proceeds. KRA name or date mismatch: inline error, correct and retry. KRA service unavailable: the same path as not found (ask the address), the record is flagged for a later re-check, the agreement proceeds. | P02, P03, N01 | |
| FE-44 | frozen | V1 uploads are the CAS PDF only (A10b): one PDF, password-protected (a depository CAS with the PAN, a registrar CAS with the password chosen at request; A10b asks for it), 10 MB maximum. The vault (H06) is open and takes no uploads in V1. | A10b, H06 | |
| FE-45 | frozen | Accepted as proposed. | | |
| FE-46 | frozen | No journey needs the camera, the gallery or contacts in V1; the document picker only (A10b). None of those permissions is requested. | A10b | |
| FE-47 | frozen | The ladders on the board: N02 (paid, before the plan) and N03 (post-plan) list every push with its state and timing; N04 holds the templates; each state's deep_link on N01 is the screen a tap opens; FCM (I12). | N01, N02, N03, N04, I12 | |
| FE-48 | frozen | Logged out: the tap opens A02 with the number prefilled, then A03, then the state router lands on the deep_link. App open: navigate directly. In both cases the router validates the state first; a stale link lands on the state's current screen, as proposed. | N01 | |
| FE-49 | frozen | Accepted as proposed. Test VoiceOver and TalkBack on the reveal, the spine and checkout. | | |
| FE-50 | frozen | Supported. A number never truncates or wraps into ambiguity; layouts reflow; test at the largest system size. | | |
| FE-51 | frozen | Accepted as proposed. | | |
| FE-52 | frozen | None beyond the progress screens (R08, A07, G01, G01a), the reveal chart drawing itself on R09 and the progress ring on O02. Nothing animates in the way of an action. | R08, R09, O02 | |
| FE-53 | frozen | Sheets (T-sheet): A08, O03, D11a, D11b, D11c. Explainers open in place (A02 "why mobile and not email"). The relief cards D12a to D12h are full screens. Back and swipe close a sheet; standardised as proposed. | Part D | |
| FE-54 | frozen | The T-chart screens: R09 (the two paths: two lines over age), G11 (allocation), H02 (net worth growth, line), H03 (wheel of wealth, radial), H10 (goals progress, bars), H11 (portfolio: allocation plus holdings). Data comes from HoA Core Platform APIs (I04). A chart must render with band (approx) inputs and say so. The library is Spinach's choice. | R09, G11, H02, H03, H10, H11, I04 | |
| FE-55 | frozen | No list is large in V1 (D01, D07, G14, H04, H06, K06, E08 are tens of rows at most). FlatList is enough; FlashList is not needed. | | |
| FE-56 | frozen | None in V1. No search, sort or filter on any list. | | |
| FE-57 | frozen | Accepted as proposed (Performance sheet row 1). The spine must feel instant: one question per screen, optimistic navigation, the next two screens prefetched. | | |
| FE-58 | frozen | Screenshots blocked (FLAG_SECURE and the iOS equivalent) on A03, A06, A10b, P02, P03, P04, K04, E02, E03, E04, E07 to E11. Allowed everywhere else: people share their plan with a spouse. The app-switcher preview is blurred on every screen that shows a number. | | |
| FE-59 | frozen | See FE-14: the last route, the tokens, the biometric flag, the encrypted unsynced queue. No plan data, no PII, no persisted query cache. | | |
| FE-60 | frozen | The Events tab is the list: 461 events across 194 screens, <screenID>_view on every screen plus the named events (source_choice, gate_met, plan_built, call_booked, return_time_picked, the D-spine set of band, skip and hesitation events); the naming rule is appendix D of plan_v2.md. Tool: Mixpanel (I13, final, Vatsal, 24 Sep 2026); journeys and nudges stay in Zoho Campaigns and Flow, FCM and WATI. | Events, I13 | |
| FE-61 | frozen | A payload may carry: screen ID, state ID, event name, band index (never the rupee value), timers, source type (aa, cas, manual, later), tier, a pseudonymous user ID. Never: amounts, PAN, date of birth, name, mobile, email, account numbers, documents. | | |
| FE-62 | frozen | Sentry, as proposed on the Analytics sheet, with release, environment and app version attached; no PII in breadcrumbs or tags. | | |
| FE-63 | frozen | Accepted as proposed. | | |
| FE-64 | frozen | The critical journeys, each with an automated test: A02 to A03 to the state router; R01 to R09; P01 to P02 to P03 to P04 to P05 with the S2b and S2c returns; A05 to A06 to A08 and to A09; spine autosave and resume (S4); D10 to G01 to G03; K01 to K05 to K02; Q03a and Q03b; E01 to E05 to E06 (V1 without in-app execution, W25). | | |
| FE-65 | frozen | Accepted as proposed: the 21 template components, the reusable inputs and the validators. | | |
| FE-66 | frozen | The FE-64 list, with Maestro as proposed on the CI/CD sheet. | | |
| FE-67 | frozen | The approved visual design once it exists (FE-17); until then Wireframes v0.2 for structure, fields, states and events. | | |
| FE-68 | frozen | At least: one Redmi Note class Android on Android 10 and one on the latest Android, one Samsung mid-range, one small-screen iPhone (SE class), one recent iPhone. Spinach proposes the exact matrix. | | |
| FE-69 | frozen | Light only in V1. | | |
| FE-70 | frozen | Notifications: asked after P05, at the first reminder or ladder moment (O03 or the first nudge), never at first launch. Biometrics: offered on A03 to a returning user. SMS auto-read on Android through the retriever API (no permission). Files: the document picker on A10b (no permission on current OS versions). No camera, contacts, location or calendar. | P05, O03, A03, A10b | |
| FE-71 | frozen | Accepted as proposed. | | |
| FE-72 | frozen | Accepted as proposed. | | |
| FE-73 | frozen | HoA owns the Expo and EAS project, the GitHub organisation, the store accounts and the AWS account; Spinach receives developer and release access, as proposed. The accounts are opened in HoA's legal name now that the registration is in (W35, owner Tech). | W35 | |
| FE-74 | open | to be decided: the iOS bundle ID and the Android package name, the reverse of HoA's domain once the domain is confirmed (W35). | W35 | Tech, 30 Sep 2026 |
| FE-75 | open | to be decided: the Apple Developer and Google Play Console accounts in HoA's legal name; the registration is in, so they can be opened now (W35). The financial-app declarations and the listing text follow (W06, Compliance). | W35, W06 | Tech and Compliance, 30 Sep 2026 |
| FE-76 | frozen | Accepted as proposed, with one condition: an OTA update never changes copy on a compliance-flagged screen without the compliance sign-off recorded on the Tracker. | | |
| FE-77 | frozen | Product (Vatsal) approves the build; Tech (Gaurav) approves the release infrastructure; Compliance approves the flagged screens' copy. The three sign-offs are recorded on the Tracker before a submission. | | |
| FE-78 | open | to be decided: the store listing copy (owner: Copy) and the financial-app declarations (owner: Compliance, W06). Spinach handles the technical submission, as proposed. | W06 | Copy and Compliance, no date |
| FE-79 | frozen | The board is the requirement: the spec panel on every screen (template, path, fields with tags, logic, continue, states, dev notes, events, compliance flag), the states tab, the Events tab, the Integrations tab. Anything missing is a comment on the screen under the identity Spinach; it lands on the Tracker's question list. | X00 | |
| FE-80 | frozen | Yes. Every frozen row on the Spinach Questions tab is signed off; every open or owed row has an owner and a date; development starts on the frozen screens and the frozen answers now. | | |

### A2. Sheet "React Native Foundation & Archi" (FE-F1 to FE-F6)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-F1 | frozen | Accepted as proposed (see FE-02). | | |
| FE-F2 | frozen | Accepted in principle: the New Architecture on. The exact version is FE-01 (W36). | W36 | |
| FE-F3 | frozen | Accepted as proposed. The version claims in the cell ("default in RN 0.87+", "Node 22.13+", "Kotlin 2.0+") are Spinach's to verify against the pinned versions (W36); HoA does not check them. | W36 | |
| FE-F4 | frozen | Accepted. Folder and route names follow the board's section letters (FE-11, FE-15), so a screen ID, a route, a folder and an event name all read the same. | | |
| FE-F5 | frozen | Accepted with FE-76's condition. | | |
| FE-F6 | frozen | Accepted (FE-20). | | |

### A3. Sheet "Navigation & Routing" (FE-N1 to FE-N6)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-N1 | frozen | Accepted as proposed (FE-04). | | |
| FE-N2 | frozen | Accepted. Route groups by section letter; one route per screen ID including the letter suffixes (D02a, H01c); the layout files carry the section strip and the progress ring. | O02 | |
| FE-N3 | frozen | Accepted. The top progress indicator is the section strip already drawn on the spine; the relief cards sit between the sections (D12a to D12h). | D12a | |
| FE-N4 | frozen | Accepted. Custom scheme yeslyf:// as the fallback, as proposed. to be verified: the domain (W35). | W35 | |
| FE-N5 | frozen | Accepted with one rule: when the device's last route and the server's state disagree, the server wins (FE-37). | N01 | |
| FE-N6 | frozen | Accepted. The sheet list is FE-53. | | |

### A4. Sheet "Conectivity" (FE-C3, FE-C4; the sheet's numbering starts at 3)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-C3 | frozen | Accepted with one rule: only spine and reveal field values queue offline, in encrypted storage, purged on sync. Nothing external (a payment, a consent, an eSign, an order, a booking) ever queues. The offline banner is the one place this is said to the person. | | |
| FE-C4 | frozen | Accept the debounce and the prefetch of the next two spine screens. No "data saver" toggle: there is no autoplay to save (A04 and R10 play on tap) and the app is forms and small charts. | A04, R10 | |

### A5. Sheet "Performance & Optimization" (FE-P1 to FE-P6)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-P1 | frozen | Accepted as proposed. | | |
| FE-P2 | frozen | Accepted as proposed. | | |
| FE-P3 | frozen | FlatList suffices (FE-55). FlashList only if a list grows past a few hundred rows, which none does in V1. | | |
| FE-P4 | frozen | Accepted for assets. Vault images are not V1 (H06 open). The plan PDF goes by email (I10); it is not rendered in the app. | H06, I10 | |
| FE-P5 | frozen | Only the stable release of the React Compiler; not a release candidate on a fixed-date financial app. to be verified: the compiler version Spinach means (W36). | W36 | |
| FE-P6 | frozen | Accepted as proposed. | | |

### A6. Sheet "Security & Authentication" (FE-S1 to FE-S6)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-S1 | frozen | The OTP provider is Gupshup (I08, final), WhatsApp OTP as the fallback channel; not Amazon SNS, not MSG91. The verification logic is internal, as I08 says. The token model (a 15-minute JWT, a 7-day rotated refresh token in Keychain or Keystore, never AsyncStorage) is accepted. Rate limits on the board: 5 OTPs per hour (A02), 3 wrong codes (A03); the cooldown and lockout ladder on the Login sheet is accepted on top (JD-LOGIN-W2). | I08, A02, A03 | |
| FE-S2 | frozen | Accepted as proposed (A03 already offers enrolment to a returning user). | A03 | |
| FE-S3 | frozen | Accepted as proposed. PAN masked in the UI; date of birth never stored on the device; nothing in plain storage. | | |
| FE-S4 | frozen | Accepted as proposed. | | |
| FE-S5 | frozen | Warn on a rooted or jailbroken device; block payments (P04, K04) and execution (E02 to E04, E07 to E11); reading the plan stays allowed. | P04, K04 | |
| FE-S6 | frozen | 30 minutes of inactivity, then biometric if enrolled, otherwise OTP (FE-07). There is no password and no PIN; strike them from the proposal. | | |

### A7. Sheet "Native Device Features" (FE-D1 to FE-D5)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-D1 | frozen | Accepted as proposed (FCM, I12, final). The token is registered on OTP success and deleted on logout and on account deletion (S25). | I12, S25 | |
| FE-D2 | frozen | Accepted: the picker, a presigned upload to S3 (I17), parsing server-side, progress and retry. The parser is I23 (open; W11 closes the CAS source and shares a sample file; owner Product). A10a (waiting for the email) stays as drawn: it waits and reminds; nothing reads an inbox. | I17, I23, W11, A10a | |
| FE-D3 | frozen | Not in V1 (FE-46). | | |
| FE-D4 | frozen | Not in V1. There is no referral feature and no contacts access; nothing about partners or referrals goes in the app. | | |
| FE-D5 | frozen | No background fetch on the device. The server fetches against the consent (fetch now plus quarterly for the review; A05, A06); a refresh shows the diff first (A08, Q01). Sync on foreground is a read of state, not a fetch. | A05, A06, A08, Q01 | |

### A8. Sheet "CI_CD & Release Management" (FE-R1 to FE-R5)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-R1 | frozen | Accepted as proposed. | | |
| FE-R2 | frozen | Accepted as proposed; the credentials live in HoA's EAS account (FE-73). | W35 | |
| FE-R3 | frozen | Accepted as proposed, with FE-76's condition. | | |
| FE-R4 | frozen | Accepted as proposed. | | |
| FE-R5 | frozen | Accepted as proposed. | | |

### A9. Sheet "Analytics & Monitoring" (FE-M1 to FE-M4)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-M1 | frozen | Mixpanel over the board's event list (FE-60, FE-61); no Segment and no Kinesis pipeline in V1. Batching and the offline queue are accepted. | I13, Events | |
| FE-M2 | frozen | Accepted as proposed (Sentry). | | |
| FE-M3 | frozen | Accepted as proposed; custom traces for the plan build (G01) and the AA fetch (A07). | G01, A07 | |
| FE-M4 | frozen | No Instabug. H07 Help creates a Zoho Desk ticket (I14); Sentry's feedback dialog may ride on a crash report. Nothing routes to Slack or Linear. | H07, I14 | |

### A10. Sheet "Integrations (App-Specific)" (FE-X1 to FE-X5; the sheet numbers two rows 5)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-X1 | frozen | Finvu (I01, final), not Saafe, not Setu. The mode (redirect, webview or SDK) is FE-38 (W37). | I01, W37 | |
| FE-X2 | frozen | Accepted as proposed. The parser is I23 (FE-D2). The original file is filed in the vault (H06) when the vault ships, not in V1. | I23, H06 | |
| FE-X3 | frozen | Accepted as proposed, with the board's rules: UPI and netbanking only, no cards (brief K1); a recurring UPI mandate for monthly or quarterly (P04; to be verified: mandate type and limits); a single charge for an a la carte call (K04); the webhook is authoritative; the GST split rule is to be verified (P04). | I09, P04, K04 | |
| FE-X4 | frozen | Accord (I05, final), not TrueData. The app calls HoA's backend, never the vendor; the cache TTL is the backend's; the fallback is typing the holding (D02b, D02c). | I05, D02b, D02c | |
| FE-X5 | frozen | Accepted as proposed. Templates server-side; the plan PDF and the signed agreement go by email (I10). | I10 | |

### A11. Sheet "Open Decisions from Wireframes" (FE-O1 to FE-O4)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| FE-O1 | frozen | Accepted as proposed. This row is the data lifecycle map Spinach owes (W21): post it on X00 as agreed and W21 closes. | W21, X00 | |
| FE-O2 | frozen | Accepted as proposed: fixed bands from the M2 tables in V1; band-choice distributions collected without identity. "After 10k plans" is a suggestion; HoA sets the threshold later. | | |
| FE-O3 | frozen | Accepted as proposed (K05; the flag is config, off). | K05 | |
| FE-O4 | frozen | Accepted as proposed (A03). | A03 | |

---

## Part B. Backend Clarifications Questionnaire (BE-01 to BE-15)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| BE-01 | frozen | One active session per user. A new OTP login on a second device revokes the first device's refresh token; the first device shows "you signed in on another device" and returns to A02. No two concurrent sessions. | A02, FE-07 | |
| BE-02 | frozen | Deletion is S25 from H09: confirm, a cooling period during which the request can be withdrawn (config; 7 days as the placeholder), then personal data is erased. Regulated records are retained under restricted access for the period Compliance names: the KYC record, the signed agreement, consent records, plan snapshots (plan_input_version, the advice record), invoices and payment references, call records. The DPDP notice on H09 says so. to be decided: the retention period and the exact retained-record list (W05, owner Compliance). | H09, S25, W05 | |
| BE-03 | frozen | Already decided on the board. The consent asks fetch-now plus quarterly for the review (A05, A06: 12 months, read-only). A refresh shows the diff first and asks "we updated N numbers, good to go?" (A08, Q01). A manual override locks the field, so a refresh never overwrites it unless the person unlocks it (A08). Every value carries its source (AA-fed, CAS-verified, manual) and its as-of date. Sell and switch advice only on AA-fed or CAS-verified holdings; manual entries get buy advice only (A05). Q05 lets the person update any number at any time; Q06 reopens only the screens a life event touches. | A05, A06, A08, Q01, Q05, Q06 | |
| BE-04 | frozen | Data in: the Account Aggregator (Finvu, I01) and the CAS upload (A10b) only; the app never connects to a broker or a platform directly. Execution out: BSE StAR MF for mutual funds (I02) and smallcase Gateway for stocks, ETFs and REITs through the person's own broker (I03; the supported broker list is Gateway's: to be verified from its documentation). Per connection the app shows: institution, masked account, as-of date, consent valid till, status (connected, failed, stale, expired), include or exclude (A08 fields; consent_status, consent_valid_till, fetch_frequency and last_fetch_at per FIP). | I01, I02, I03, A08 | |
| BE-05 | frozen | HoA's eight-question RPQ (D08a to D08h), tap only; the band comes from the score (D09); the annual re-confirmation is Q04. The scoring map is a table HoA owes (gap G06, W30, owner Investment advisory); it is config, not code. | D08a, D09, Q04, W30 | |
| BE-06 | frozen | Harish, through the logic panel: L04 holds the instrument universe (ISINs), L03 the buckets and cohorts, L09 the constraints, L05 the staging area with impact preview, L06 publish. Nothing reaches a person unpublished; a publish triggers plan updates (S11, H05). There is no per-user approval and no human review gate on plan generation: advisers change inputs and the engine re-runs. (L00 to L09 are open on the board only for their table shapes, W04.) | L03, L04, L05, L06, L09, S11, H05 | |
| BE-07 | frozen | No in-app audio or video is built. K02 carries a join link from the CRM's meeting tool, or a phone number when there is no link. The meeting tool (I24, W32, owner Admin) and the recording consent and retention rule (W33, owner Compliance) are open; K02 and K06 stay open until then. | K02, K06, I24, W32, W33 | |
| BE-08 | frozen | Not in scope. A credit is a whole call: calls_included_per_period against calls_used (K01). Call length is config (to be verified: the recipe, W31). No metering by minutes, no automatic ending, no top-up during a call. | K01, W31 | |
| BE-09 | frozen | Prepaid, always. Included calls come with the subscription; an a la carte call is a single charge through P04 before the slot picker opens (K04, then K05). There is nothing to collect after a call; deleting the app changes nothing. | K04, K05, P04 | |
| BE-10 | frozen | HoA's own call centre; no external adviser network. The capacity number and the slot design are HoA's (gap G04, W31). | K05, W31 | |
| BE-11 | frozen | No list and no name. Any available adviser from the call centre takes any call (K05). The adviser-continuity flag is config, off by default; when on, a chip asks for the same adviser as last time. | K05 | |
| BE-12 | frozen | Slots come from Zoho Bookings (I14): one adviser, one call at a time. No slot within 7 days shows a waitlist and creates a call-centre task (K05). A no-show follows S20: rebook, nudges at 1 hour and 24 hours, a task after the second no-show. The number of advisers and their hours is W31. | K05, S20, I14, W31 | |
| BE-13 | frozen | Yes. The booking creates the event in Zoho Bookings and the adviser's calendar and returns the join link; the app shows the slot and the link on K02; the confirmation goes by push, WhatsApp and email per the ladder; the call centre sees the plan (G03) and the inputs (D10) before the call (M01). | K02, I14, M01 | |
| BE-14 | open | to be decided: the cancellation and refund rule (brief H5), owner Compliance with Harish (W05). What the board already fixes: cancel is always allowed from Q03a with no reason required; the plan stays readable and refresh stops; pause is offered; a refund request creates a CRM task with the payment reference and lands in S24; the rule itself is a parameter. Note for Compliance: SEBI's investment-adviser fee rules already shape the answer (a refund of the unexpired period on termination, a capped breakage amount); the exact wording is theirs. | Q03a, S24, W05 | Compliance, 30 Sep 2026 |
| BE-15 | frozen | The adviser writes the summary in the CRM as structured notes: the inputs that change (which re-run the plan) and a short note. The app shows them on K03, and H05 shows the plan diff. No automated transcription or AI summary in V1; that waits for the recording rule (W33). | K03, H05, W33 | |

---

## Part C. Journey Description

### C0. Sheet "Journey Summary" (JD-SUM-1 to JD-SUM-5: the "Key open area" cell of each row)

| id | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|
| JD-SUM-1 | frozen | Post-OTP routing is the states tab: N01, S1 to S25, each with a landing screen and a deep link. Resend and lockout: the ladder on the Login sheet is accepted (a 30-second cooldown doubling to 5 minutes; 3 wrong codes invalidate the OTP; a 15 to 30 minute lockout after repeated cycles; counters server-side) on top of the board's 5 OTPs per hour. Number change: from H09, with an OTP on the new number and a confirmation on the old. A recycled number whose PAN does not match the account on P02 is a support case (H07, Zoho Desk). | N01, A02, A03, H09, H07 | |
| JD-SUM-2 | frozen | A returning person lands by state: S1 on the first unanswered reveal screen; S2 on X01 (reveal saved, not paid) with the paywall one tap away; never a dashboard, because there is no dashboard before payment. The reveal is R01 to R09, then R10 and R12; the sheet's mapping (A04, A05) is corrected on the Reveal rows. | N01, X01, R01 | |
| JD-SUM-3 | frozen | The order is P01, P02, P03, P04, P05 (corrected on the Paywall rows). The refund rule is BE-14. Payment reconciliation and duplicate handling are FE-40 and FE-41 and the Paywall edge rows. eSign retry is FE-43. | P01, P02, P03, P04, P05 | |
| JD-SUM-4 | frozen | The mapping is corrected on the Onboarding rows (O01 meet yeslyf, O02 the hub, O03 the reminder). Consents: two, the DPDP notice (A04 or H09, text owed, gap G03) and the AA consent (A06). Withdrawal: Q03a and H09. Re-consent: S15 (AA expired) and Q04 (annual). Retention: W05. | O01, O02, O03, A06, Q03a, Q04, S15, W05 | |
| JD-SUM-5 | frozen | FIP coverage is Finvu's list; the eight bank chips are config from the FIP health check (A05). Consent expiry: 12 months, quarterly fetch, S15 when expired; to be verified: the maximum validity under the wealth-management purpose (A05, A06). Stale data: the as-of date is shown and Q05 updates it. Precedence: a manual override locks the field (A08). Partial fetch: A09. | A05, A06, A08, A09, Q05, S15 | |

### C1. Sheet "Login" (JD-LOGIN)

Workflow rows (W), edge cases (E), merge suggestion (M).

| id | row | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|---|
| JD-LOGIN-W1 | A01 Enter mobile number | frozen | Correction: A01 is the first-open card; the mobile number is A02. The behaviour as written is right for A02: +91 only at launch, 10 digits, 5 OTPs per hour, an inline error keeps the number editable. | A01, A02 | |
| JD-LOGIN-W2 | A02-A03 Enter OTP | frozen | The OTP screen is A03. Six digits; 3 wrong codes invalidate the OTP; resend after a cooldown. The ladder in the best-practice cell is accepted as the policy: a 30-second cooldown doubling to 5 minutes, a 15 to 30 minute lockout after repeated cycles, counters and cooldowns server-side. | A03, I08 | |
| JD-LOGIN-W3 | Post OTP | frozen | The state router (N01). New: A04 (its placement, right after the OTP or after the first reveal questions, is to be decided on the board, W27). Returning: the state's landing screen. "Any pending mandatory step first, otherwise home" is exactly what N01 does. | N01, A04, W27 | |
| JD-LOGIN-E1 | Invalid number / provider failure | frozen | Accepted as proposed. A02 inline error; log the Gupshup reference. | A02 | |
| JD-LOGIN-E2 | Wrong/expired OTP | frozen | Accepted as proposed. A03 tells wrong from expired. | A03 | |
| JD-LOGIN-E3 | State lookup unavailable | frozen | Accepted as proposed. Never guess the state; retry, then a "we are checking" line; the verified session stays. | N01 | |
| JD-LOGIN-E4 | User exits or loses connectivity | frozen | Accepted as proposed (FE-33, FE-37). | | |
| JD-LOGIN-E5 | Invalid/unsupported mobile number | frozen | Accepted as proposed. +91 only at launch. | A02 | |
| JD-LOGIN-E6 | OTP not received | frozen | Accepted as proposed. The alternate channel is WhatsApp OTP (I08), in scope. | I08 | |
| JD-LOGIN-E7 | Incorrect OTP | frozen | Accepted as proposed; show the remaining attempts. | A03 | |
| JD-LOGIN-E8 | Expired OTP | frozen | Accepted as proposed. | A03 | |
| JD-LOGIN-E9 | Existing user detected | frozen | Accepted as proposed; the routing is N01. | N01 | |
| JD-LOGIN-E10 | New user detected | frozen | Accepted as proposed. The minimum record is the mobile number and the verified flag. A person is a lead with a wrong OTP and a verified lead with the right one (minutes 16 Sep 2026, item 1; W26). | W26 | |
| JD-LOGIN-E11 | OTP verified on another device/session | frozen | Accepted as proposed, and see BE-01: one active session. | | |
| JD-LOGIN-E12 | Unverified number retained/contacted | open | to be decided: owner Compliance (W29). Until then: not contacted, retained only as the OTP transaction log. | W29, A02 | Compliance, 30 Sep 2026 |
| JD-LOGIN-M1 | A02 and A03 combined (3 to 2) | frozen | No merge now: A02 and A03 are frozen. Propose it as a comment on A03 and it goes to v0.3 with the visual design. Not a build change. | A02, A03 | |

### C2. Sheet "Reveal" (JD-REVEAL)

| id | row | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|---|
| JD-REVEAL-W1 | A04-A05 Start/continue reveal | frozen | Correction: the reveal is R01 to R09 (then R10 the video and R12 the sample plan; X01 is reveal saved, not paid). A04 is the welcome video (placement open, W27). A05 is the post-paywall source chooser and is not part of the reveal. Autosave per screen and resume at the first unanswered screen (S1) are on the board. | R01, R09, X01, A04, A05, S1 | |
| JD-REVEAL-W2 | CRM S4 Resume abandoned reveal | frozen | Correction: the abandoned reveal is state S1 (signed up, no reveal); S2 is reveal seen, not paid; S4 is "data partial", after payment. The resume rule is N01 (a landing screen per state). The CRM only sends the nudge; the app decides the screen. | S1, S2, S4, N01 | |
| JD-REVEAL-W3 | R10 / summary Review reveal | frozen | Correction: the outcome is R09 (the reveal chart, two paths); R10 is the video; R12 the sample plan preview; then P01. Calculation unavailable: R08 shows retry and never a made-up result (accepted; it matches the board's no-assumptions rule). | R08, R09, R10, R12 | |
| JD-REVEAL-E1 | Corrupt/incompatible saved state | frozen | Accepted as proposed (state version). | | |
| JD-REVEAL-E2 | Old deep link points to completed screen | frozen | Accepted as proposed; N01 wins. | N01 | |
| JD-REVEAL-E3 | Calculation unavailable | frozen | Accepted as proposed (R08 retry). | R08 | |
| JD-REVEAL-E4 | User exits or loses connectivity | frozen | Accepted as proposed. | | |
| JD-REVEAL-E5 | User exits midway | frozen | Accepted as proposed. Resume versus restart: always resume. After 90 days away (config) the reveal is shown again from R01 with the values prefilled for confirm-or-correct, then R08 and R09 re-run. | R01, S1 | |
| JD-REVEAL-E6 | User goes back and changes prior answer | frozen | Accepted as proposed; R08 and R09 re-run. | R08 | |
| JD-REVEAL-E7 | Required reveal input missing | frozen | Accepted as proposed (Continue disabled). | | |
| JD-REVEAL-E8 | Answers conflict | frozen | The reveal has no cross-field rule beyond the ranges (income, saved and savings rate are bands). No clarification question; the ranges are the validation. | R03, R04, R05 | |
| JD-REVEAL-E9 | User enters R screen directly | frozen | Accepted as proposed (the router). | N01 | |
| JD-REVEAL-E10 | Unconverted reveal user returns much later | frozen | The 90-day rule in E5. | | |
| JD-REVEAL-E11 | Analytics event fails | frozen | Accepted as proposed. | | |
| JD-REVEAL-M1 | A04/A05 merge; keep R10 | frozen | Does not apply: A04 and A05 are not two intro states (see W1). R01 to R12 froze as drawn on 17 Sep 2026; no merges now. | A04, A05 | |

### C3. Sheet "Paywall" (JD-PAY)

| id | row | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|---|
| JD-PAY-W1 | P01 Choose plan | frozen | Accepted as proposed. The SKU cards are config (I15): DIY and DIWM, monthly or quarterly, prices "Rs ___" until set; no DIFM card. Revalidate price and availability at checkout, as proposed. | P01, I15 | |
| JD-PAY-W2 | P03-P05 Pay/subscribe | frozen | Correction of order: P04 is the payment; P03 is the agreement and eSign and comes before the payment; P05 is "you're in". Razorpay rules: FE-40, FE-41, FE-X3. | P03, P04, P05 | |
| JD-PAY-W3 | Agreement/eSign | frozen | P03. The eSign vendor is I07 (open, W34). The agreement version is stored with the eSign reference; the signed artefact is an audit record (I19). Accepted otherwise. | P03, I07, I19, W34 | |
| JD-PAY-W4 | P02 KYC | frozen | Correction: P02 is on every paid path (name as per PAN, PAN, date of birth, email). It is a KRA fetch to prefill the agreement, not a KYC gate; the address only when the record is not found; full KYC for execution is E02. The order is P01, P02, P03, P04, P05. | P02, E02, I06 | |
| JD-PAY-E1 | Plan changed/retired | frozen | Accepted as proposed. Note: the Best Practice column of this block is shifted (it reads like the Reveal column pasted down); every answer here is against the edge case, not the cell. | | |
| JD-PAY-E2 | Debit but callback missing | frozen | Accepted; re-query by order ID (FE-41). | P04 | |
| JD-PAY-E3 | Cancel/timeout/reject (eSign) | frozen | S2b, P03 retry; check the existing status first (FE-43). | S2b, P03 | |
| JD-PAY-E4 | Mismatch/not found/API unavailable (KYC) | frozen | FE-43. | P02 | |
| JD-PAY-E5 | User exits or loses connectivity | frozen | FE-09. | | |
| JD-PAY-E6 | User leaves at paywall | frozen | S2 lands on X01; the offer stays; no entitlement. | S2, X01 | |
| JD-PAY-E7 | KYC not found | frozen | The address fields on P02. | P02 | |
| JD-PAY-E8 | PAN/DOB mismatch | frozen | Inline error, correct and retry; support through H07 (Zoho Desk) if it persists. | P02, H07 | |
| JD-PAY-E9 | User cancels eSign | frozen | S2b. | S2b | |
| JD-PAY-E10 | Provider timeout / callback missing (eSign) | frozen | Reconcile before any new request; a "we are checking your signing status" line on P03. | P03 | |
| JD-PAY-E11 | Payment failed | frozen | P04 retry with another method; nothing is lost. | P04 | |
| JD-PAY-E12 | Payment debited but callback missing | frozen | Re-query first; P04 "we are confirming your payment"; never ask the person to pay again before the query. | P04 | |
| JD-PAY-E13 | Duplicate click/retry | frozen | One idempotency key per order; P04 "already being processed". | P04 | |
| JD-PAY-E14 | User requests refund/cancellation | open | Q03a, state S24; the rule is BE-14 (to be decided, Compliance, W05). | Q03a, S24, W05 | Compliance, 30 Sep 2026 |
| JD-PAY-E15 | Confirmation email bounces | frozen | Accepted as proposed. The in-app confirmation on P05 stands; the SES bounce is recorded; a CRM task asks for a corrected email (H09). | P05, I10, H09 | |
| JD-PAY-M1 | Combine adjacent checkout steps | frozen | No merges. P01 to P05 are frozen except P04 (open for the mandate items). P02, P03 and P04 each need an independent authoritative status, as the sheet itself says. | P01, P02, P03, P04, P05 | |

### C4. Sheet "Onboarding" (JD-ONB)

| id | row | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|---|
| JD-ONB-H1 | Header block | owed | to be verified: the sheet is rebuilt by Spinach against O01 to O03 as built (W38). The header cells are scrambled (Entry criteria reads "O01 - O03", Primary APIs reads "High") and the right-hand "State / decision" column holds AA-sheet decisions. | W38 | Spinach, 28 Sep 2026 |
| JD-ONB-W1 | O01 Select service mode | frozen | Correction: O01 is "Meet yeslyf": what the app is, and what a call is and is not (compliance-flagged copy). There is no mode choice. The SKU was chosen at P01 (DIY or DIWM); DIFM is never self-serve (provisioned from admin, lands on H01h); a plan change is Q02, allowed any time. Please redo this row against O01 as built. | O01, P01, Q02, H01h | |
| JD-ONB-W2 | O02 Complete intermediate step | frozen | Correction: O02 is the hub: the section map of the eight spine sections with done ticks, the progress ring, three cards (continue, review and build, book a call) and "remind me later". It is the landing screen for S3, S4, S5, S16, S17 and S19. Please redo this row against O02 as built. | O02, S3, S4, S5, S16, S17, S19 | |
| JD-ONB-W3 | O03 Choose return time | frozen | Accepted as written. return_time_picked is stored as an absolute instant with the IANA zone; the chosen time schedules the first push and replaces the first ladder step; "no reminder" keeps the standard ladder; O03 opens only from a relief card or O02, never on exit. | O03, N02 | |
| JD-ONB-E1 | Selects DIY then switches to DIWM/DIFM | frozen | Not an onboarding case. A plan change is Q02, allowed any time; nothing on O02 is invalidated by a tier change: the app is identical across tiers, only the paywall cards, the adviser screens, the call steps and the help channel differ. | Q02 | |
| JD-ONB-E2 | Plan/tier changes in another session | frozen | Accepted as proposed: revalidate on commit, at Q02 and P04. | Q02, P04 | |
| JD-ONB-E3 | Returning user already has a mode | frozen | Not applicable: there is no mode. O02 preloads the section map. | O02 | |
| JD-ONB-E4 | O02 not applicable to a mode | frozen | Not applicable: O02 is for every tier. | O02 | |
| JD-ONB-E5 | Partially completes O02 and exits | frozen | O02 holds no inputs; the spine screens autosave (FE-33). | O02 | |
| JD-ONB-E6 | O01 change invalidates some O02 fields | frozen | Not applicable. | | |
| JD-ONB-E7 | DST/timezone offset changes | frozen | Accepted as proposed (O03). | O03 | |
| JD-ONB-E8 | Chooses later but no reminder channel | frozen | Accepted as proposed. The push permission is asked here if not yet granted (FE-70); if declined, the reminder goes by WhatsApp or email when opted in; otherwise the state ladder runs without the chosen time and O03 says so. | O03, N02 | |
| JD-ONB-E9 | Same return selection submitted twice | frozen | Accepted as proposed (idempotency). | O03 | |
| JD-ONB-E10 | Continue now after a reminder exists | frozen | Accepted as proposed (cancel the task). | O03 | |

### C5. Sheet "Account Aggreviator" (JD-AA)

| id | row | status | Yesly comment | refs | owner, due |
|---|---|---|---|---|---|
| JD-AA-W1 | A05 Choose AA | frozen | Accepted as proposed, plus: the four ways are AA, CAS, type it in, not now; AA is the default card; A05a is the bank-slow state; every way lands on D01 (rule 1). | A05, A05a, D01 | |
| JD-AA-W2 | A06-A07 Select accounts/consent | frozen | Correction: A06 is the consent (Finvu's flow); A07 is the fetching progress screen, opened from the pill. The return from A06 lands on D01 and the fetch runs in the background (Vatsal, 11 Sep 2026). Consent scope, purpose and expiry are shown in plain words above the webview (12 months, quarterly, read-only; to be verified: the maximum validity). Excluded accounts are recorded. | A06, A07, D01 | |
| JD-AA-W3 | A08 Fetch/import data | frozen | Correction: the fetch is server-side (A07 shows the progress). A08 is the review sheet "here is what came through": include and exclude per account, an override with a source lock, the as-of date and the source per record. Holdings are stored at ISIN level with units, value and SIP mandates (needed for I02). | A07, A08, I02 | |
| JD-AA-W4 | A09 Review imported data | frozen | Correction: A09 is the partial-or-failed screen: rows per FIP with retry, the CAS and manual ways, "continue with what we have" lands on D01. The imported-versus-manual precedence is A08's lock rule (BE-03). | A09, A08, D01 | |
| JD-AA-W5 | A10 Request / upload CAS | frozen | Accepted as proposed. A10 is the how-to (where to request the file). The CAS source closes with W11 (registrar CAS first, depository CAS next). | A10, W11, I23 | |
| JD-AA-W6 | A10a-A10b Submit CAS | frozen | Correction: A10a is the wait for the email (state S17; it waits and reminds, nothing reads an inbox); A10b is the upload with the password. Parsing is server-side (I23, open). Parse failure, PAN mismatch and several investors are accepted as separate outcomes. | A10a, A10b, S17, I23 | |
| JD-AA-W7 | A10c Confirm parsed CAS | frozen | Accepted as proposed. The parsed holdings are confirmed on A10c, tagged CAS-verified, with source and as-of stored; the original parse is kept apart from the confirmed values. | A10c | |
| JD-AA-E1 | Provider unavailable | frozen | Accepted as proposed (A05a, A09). | A05a, A09 | |
| JD-AA-E2 | Consent rejected/abandoned | frozen | Accepted as proposed; abandoned lands on D01 as a manual user with aa_status not_connected; the re-asks are at G12a and Q01. | A06, D01, G12a, Q01 | |
| JD-AA-E3 | Partial/stale/error response | frozen | Accepted as proposed. What came through is tagged AA-fed; the rest is typed on the spine, where the D02 rows show "not fetched". | A09, D02 | |
| JD-AA-E4 | Imported vs manual conflict | frozen | Accepted as proposed; the rule exists (A08 lock, the diff on refresh, BE-03). | A08 | |
| JD-AA-E5 | User exits or loses connectivity | frozen | Accepted as proposed. | | |
| JD-AA-API1 | API-03 Journey State / Autosave | frozen | Accepted as proposed (the autosave and state service; version check as proposed). | N01 | |
| JD-AA-API2 | API-07 Consent Ledger | frozen | Accepted as proposed: the DPDP notice, the AA consent, the contact consent from A02, the agreement version. | A02, A06, P03 | |
| JD-AA-API3 | API-08 Account Aggregator | frozen | Accepted as proposed (Finvu, I01; server-side). | I01 | |
| JD-AA-API4 | API-09 Financial Profile | frozen | The financial profile lands in HoA Core Platform through its data-in APIs (I04, W03), with bands or midpoints as the input shape and source and precision per field. Spinach aligns API-09 with that contract rather than defining a second one. | I04, W03 | |
| JD-AA-M1 | A06/A07 and A08/A09 merges | frozen | A06 and A07 are not sequential screens (A07 opens from the pill); A08 is a sheet over the spine and A09 the failure screen. No merges. | A06, A07, A08, A09 | |

---

## Part D. Behaviour by template (referenced by FE-10, FE-24, FE-28, FE-29, FE-53)

| template | screens | Android back | loading | keyboard | validation |
|---|---|---|---|---|---|
| T-tap | A02, A03, R01 to R07, D08a to D08h, D06c, D07b | previous screen, value kept | none (local) | none; OTP boxes auto-advance on A03 | on Continue |
| T-num | D05a to D05d, D06a, D06d, D02a to D02j | previous screen, value kept | none (local) | numeric keypad, Done acts as Continue | on Continue; format mask live |
| T-list | D01, D02, D03, D04, D07, D13, G14, H04, H06, H09, K06, E02, E07, E08, E09, E11, Q06, Q06a | the hub or previous | skeleton rows | none | on Continue |
| T-detail | D01a, D03a, D04a to D04c, D07a | the list; fields autosaved | none | keyboard-aware scroll | on blur and on Continue |
| T-split | D06b | previous | none | numeric | the three buckets must sum to D06a, inline |
| T-sheet | A08, O03, D11a, D11b, D11c | closes the sheet | none | none | none |
| T-webview | A06, P02, P03 | cancels the vendor step; lands on the state's landing screen | vendor page with a timeout to the failure state | vendor's | vendor's; P02 fields on blur and Continue |
| T-progress | R08, A07, G01, G01a | disabled | the screen is the loading state; a timeout shows retry | none | none |
| T-chart | R09, G11, H02, H03, H10, H11 | previous or Home | skeleton until I04 responds | none | none |
| T-card, T-card-stack | O01, X01, P05, D00, D09, D12a to D12h, G03 to G10, G12, G13, K01 to K04, H05, H07, H08, Q03, Q03a to Q03c, Q04, E03, E04, E05, E10, A09, A10, A10a | previous or Home | skeleton | none | none |
| T-paywall | P01, Q02 | X01 (P01), Q03 (Q02) | SKU cards from config | none | a plan must be chosen |
| T-hub | O02, H01 and H01a to H01k, E01 | minimises the app | skeleton cards | none | none |
| T-review | D10, A10c, E06, Q01, Q05 | O02 (D10), A10b (A10c), E01 (E06), Home (Q01, Q05) | skeleton | none | the declaration on D10 |
| T-upload | A10b | A10 | upload progress, cancel, retry | password field | file type, size, password before upload |
| T-picker | K05 | K01 | slots from Zoho Bookings | none | a slot must be chosen |
| T-locked | G12a | G12 | none | none | none |
| T-source | A05, A05a | O02 | bank chips from config | none | none |
| T-video | A04, R10 | skip to the next screen | the player | none | never blocks |
| T-table, T-msg | N, L, M tabs on the board | not app screens | | | |

## Part E. Route-access map (FE-05, FE-06)

| group | screens | who | rule |
|---|---|---|---|
| public | A01, A02, A03 | anyone | the only screens before a verified OTP |
| registered, unpaid | A04, R01 to R12, X01, P01, P02, P03, P04, P05, H07 | states S1, S2, S2b, S2c | reached only through the state router; P05 flips the person to paid |
| paid | O01, O02, O03, A05 to A10c, every D, G, K, E, H and Q screen | states S3 to S25 | the tier (DIY, DIWM) changes the paywall cards, the adviser screens, the call steps and the help channel, nothing else |
| DIFM | H01h and the read screens | state S14 | provisioned from admin; no self-serve path |

## Part F. Open rows and the tracker rows behind them

New Tracker rows (W30 onward; first names on the Tracker, functions on the tab). Dates are proposals.

| W | item | owner (tracker) | function (tab) | due | source |
|---|---|---|---|---|---|
| W30 | RPQ scoring map: the table behind D09 (gap G06) | Harish, Somil | Investment advisory | 30 Sep 2026 | SQ1 BE-05 |
| W31 | The calls recipe: calls included per period, call length, adviser capacity and hours, slot design (gap G04; K01 and K05 owed items) | Bhuvanaa, Harish | Team session (30 Sep 2026) | 30 Sep 2026 | SQ1 BE-08, BE-10, BE-12 |
| W32 | Meeting tool for calls (I24): the join link on K02, the list on K06 | Kajal | Admin | 30 Sep 2026 | SQ1 BE-07, BE-13 |
| W33 | Recording consent and retention rule for calls (K06) | Compliance | Compliance | 30 Sep 2026 | SQ1 BE-07, BE-15 |
| W34 | Close the KYC vendor (I06) and the eSign vendor (I07) | Kajal, Harish | Admin | 30 Sep 2026 | SQ1 FE-42, JD-PAY-W3 |
| W35 | Accounts in HoA's legal name (Apple Developer, Google Play Console, Expo/EAS, GitHub organisation, AWS); the iOS bundle ID and Android package name; the domain for universal links | Gaurav, Kajal | Tech | 30 Sep 2026 | SQ1 FE-73, FE-74, FE-75, FE-08, FE-N4 |
| W36 | The exact Expo SDK and React Native versions, pinned; the React Compiler release status | Spinach | Spinach | 28 Sep 2026 | SQ1 FE-01, FE-F2, FE-F3, FE-P5 |
| W37 | Finvu's integration mode (redirect, hosted webview or SDK), from the documentation Spinach holds | Spinach | Spinach | 28 Sep 2026 | SQ1 FE-38, FE-X1 |
| W38 | The Onboarding sheet rebuilt against O01 to O03 as built | Spinach | Spinach | 28 Sep 2026 | SQ1 JD-ONB-H1 |
| W39 | Validation and error copy for the reusable inputs, by screen ID and copy slot | Bhuvanaa | Copy | no date; not a blocker | SQ1 FE-26 |
| W40 | The bands and validation ranges table, per field | Bhuvanaa, Vatsal | Financial planning | 30 Sep 2026 | SQ1 FE-27 |

Existing rows touched:

| W | change |
|---|---|
| W05 | notes gain: the refund and cancellation rule (BE-14, JD-PAY-E14), the deletion retention period and the retained-record list (BE-02), the DPDP notice text (JD-SUM-4) |
| W06 | linked from FE-75 and FE-78 |
| W07 | delivered: Mixpanel (Vatsal, 24 Sep 2026) |
| W11 | linked from FE-D2, FE-X2, JD-AA-W5; still open, owner Vatsal |
| W19 | delivered: the corporate RIA registration is in (Vatsal, 24 Sep 2026) |
| W21 | in progress: FE-O1 is the map; closes when Spinach posts it on X00 |
| W22 | in progress: the journey description is the first output |
| W24 | delivered: SQ1 received 22 Sep 2026 |
| W27 | linked from JD-LOGIN-W3 and JD-REVEAL-W1 |
| W29 | linked from JD-LOGIN-E12 |
