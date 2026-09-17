# yeslyf - minutes of the wireframe walkthrough with Spinach, 16 Sep 2026

Source: the Zoom transcript "House of Alpha HOA's Zoom Meeting 2026-09-16 11_10(GMT+5_30).txt" in this folder.
The recording starts at 11:13 and ends at 12:39 IST; the first three minutes of the call (the nine-frame overview
was already under way) are not in the transcript. Written 17 Sep 2026 by Vatsal against the board as built at
commit 628b6d3 (mandatory and optional inputs). Where a point touches the board, the screen ID or row ID is given
and the current state of the board is stated.

Present: Vatsal, Harish, Kajal, Somil, Gaurav (joined late; first spoke at 11:46) for HoA. Eshani, Saquib, Ankur,
Guneet for Spinach. Raafiya was on the call and did not speak. Bhuvanaa was not on the call.

Purpose: walk Spinach through the v0.2 wireframes and the board (wireframes, admin and CRM, integrations, events),
answer the questions Saquib sent by email, and agree what Spinach can start on now.

## 1. What was shown

- The nine frames: first open, the free reveal, the paywall (DIY and DIWM built now; DIFM clients are onboarded from
  the admin side and land on H01h), the four ways to get the numbers (AA, manual, CAS upload), the picture on D10,
  the plan overview (G03), the action plan, the execution hub (smallcase Gateway and BSE StAR MF), and the home base
  (H01). HoA's maths (allocation, splits, the five alphas) is HoA's IP and comes through HoA Core Platform APIs.
- The spec panel on every screen: template, path (DIY, DIWM, both), fields, logic, continue, state, dev notes,
  events, compliance flag. Saquib asked that the team keep reading that panel as questions come up.
- The states tab (N): every stop point, happy and unhappy, with its exit and nudge ladder; N09 as the example.
- The logic panel (L): rules, layouts, assumptions; the maths itself is delivered by HoA on a date to be set.
- The integrations tab: every external API, the screens it serves, owner, status and dates; live on every device.
- The comment box on each screen: an entry typed with an identity is saved for everyone. Somil wrote a test comment on
  O01 at 11:53 (it is in the table; treat it as a test row like the setup row and the A02 Keep by Kajal).
- The events tab, filterable by section: the variables the nudges and the CRM run on.
- Admin and CRM: Zoho One (CRM, Creator, Campaigns, Bookings, Flow, connected to Slack) named as the platform; events
  flow in, nudges go out.

## 2. Decisions and answers

Each item: what was said, who said it, and what it means for the board.

1. Registration is the mobile number plus OTP (A02, A03). A person is registered the moment the OTP is right; there
   is no separate registration step and email is never the login. Gaurav: a mobile number with a wrong OTP is a lead;
   with the right OTP a verified lead; the reveal bands are saved so marketing can reach people by band later; from
   OTP onwards a person has a profile fulfilment percentage that grows with every screen. Eshani offered email OTP as
   the lower-friction alternative; Gaurav: Bhuvanaa's decision was mobile plus OTP because it saves a step later and
   the number can be prefilled from the device; the drop-off of people who will not give a number is accepted, and an
   explanation or exit path for them comes later.
   Board: A02 and A03 are tagged required; R09 says the reveal snapshot is stored. Not on the board: the lead stages
   (lead, verified lead, fulfilment percentage) as contact fields in the admin spec. Gap, to be decided (N tab, admin).
2. Email is taken later, to send things, not at entry (Vatsal). Board: P02 collects it (required) with the name as per
   PAN, PAN and date of birth; H09 holds it afterwards.
3. OTP vendor: Gupshup, final (Vatsal). Board: I08 already says so.
4. Saving and resuming (Gaurav, Vatsal). Every step is saved on the server as it is written (Gaurav: the PostgreSQL
   database); it is a partial save, so the person can go back and forward and change anything; killing the app,
   restarting the phone or a session timeout brings the person back to the exact screen they left (Gaurav's example:
   halfway through D01a, back to D01a). Whether the client keeps the data or only the position is Spinach's call.
   O02 opens on the section list (done, not done) and the state opens the exact page from there (Vatsal).
   Board: the D spine's rule 12 (autosave on exit) and the states tab already carry this; nothing to change. Spinach
   will draw the data lifecycle (what is saved when, session rules) and share it; Vatsal asked that it lands on the
   board so everyone reads the same copy.
5. Vault (H06). Gaurav: files in S3 behind an encrypted link, the link stored in the database; the vault needs
   upload, tags, expiry dates and possibly versions; Eshani may improve on it. Board: H06's logic covers filing and
   extraction only; the storage mechanics are not written. I17 (cloud and document storage) still says Azure, while
   Gaurav said AWS and a board row set W02 to delivered with the note "AWS and SES" at 10:56 on 16 Sep 2026 (no
   identity chosen). I17 is to be corrected with the cause "Gaurav, 16 Sep 2026".
6. CAS. A10 is the how-to (where to request the file), A10a is the wait for the email, A10b is the upload with the
   password, A10c is what was read. Gaurav: reading the CAS from the email (A10a) will probably not be built; A10b is
   the path. NSDL CAS or CAMS CAS is not decided; the need is holdings and their values, not transactions; both are
   fixed-format PDFs protected with the PAN. Vatsal will close the choice and share a sample file with Spinach. Ankur's
   question (does the user create the PDF) is answered: no, the depository or registrar issues it.
   Board: A10a is live with state S17. If it is dropped it keeps its ID with status dropped and A10 and S17 are
   rerouted. Gap, to be decided (A10a). Appendix E already lists the CAS parsing effort.
7. Ranges for missing numbers (D13). Harish: the app never suggests a range from the rest of the data; the person
   gives what they know, exact or a band. Board: D13 asks, never assumes; matches the standing rule.
8. Content is a separate track and is not ready (Vatsal). Eshani: not a blocker, since there is no UI/UX yet. The
   why-this-matters copy (D11b) and the relief cards (D11a) come from the CMS. Board: I15 (Directus, choice open).
9. Paywall numbers (P01): monthly or quarterly, the prices and the calls included in DIWM are not decided; a la carte
   calls exist for every tier (K04). Not a blocker (Vatsal). Board: "Rs ___" and "N" stay as placeholders.
10. Welcome video (A04): whether it sits right after the OTP or after the first questions is open (Vatsal). Gap, to
    be decided (A04).
11. Execution hub is built last (Vatsal): it needs vendor documentation and sandboxes. The wireframe carries two
    tracks, execution in the app (E02 to E04, E07 to E11) and execution outside the app with self-report (E05, E06).
    Eshani noted the outside-app track had not been discussed before; Vatsal: nothing changes for development, only
    the build order. Vendors are not signed; Harish: the platforms will not change; what is open is the SKU.
12. Integrations page. Final (Vatsal): Finvu (I01), BSE StAR MF (I02), smallcase Gateway (I03), HoA Core Platform
    (I04). Market data (I05, Accord) was not confirmed on the call. Kajal: most rows are final, a few may change.
    Saquib asked for two things: a marker per row, final or open, and a date by which every row is final, so Spinach
    can read the endpoints of the final ones now. Vatsal and Kajal agreed to both. Board: the status list is not
    started, in talks, agreement signed, sandbox, production, dropped; there is no final or open marker and no date
    yet. Action for Vatsal.
13. API format (Saquib asked for JSON). Gaurav: assume JSON; BSE StAR MF is not JSON today but HoA will use BSE
    version 2, which is; Finvu is a consent journey (a reference ID, then a fetch against a consent ID), so two or
    three round trips; a sandbox returns dummy data but every endpoint can be hit. Read the public documentation of
    the final vendors now; sandbox access follows the contracts, which follow the corporate RIA registration.
14. Documentation and sandboxes. Kajal: documentation exists and will be shared. Harish: a vendor may ask HoA to sign
    up first, and may ask for the SEBI registration document, which is a few days away; public documents will be
    shared meanwhile. Eshani: ask every vendor for a sandbox before the paperwork (a client would want to see it before
    signing) and put Spinach on the vendor email threads, routed through Kajal or Raafiya. Vatsal and Kajal agreed.
15. Mandatory and optional inputs (Saquib's question). Vatsal took it. Done on 17 Sep 2026 (commit 628b6d3): every
    input screen carries a "Moving forward" block and every field a tag (required, optional, default, system); 79
    screens, 158 fields. The unhappy paths Saquib asked about are the states (N tab) plus Help (H07); the tags close
    the skip cases.
16. After the journey (Saquib): the home base H01 by state, settings on H09, exits on every state (Vatsal). Spinach to
    flag any gap they find.
17. The maths. Goal progress, portfolio and the net worth growth chart are HoA logic delivered through HoA Core
    Platform APIs (I04). Gaurav: APIs to push the captured data in will be given too, and the inputs on this journey are
    bands or midpoints, not the detail of the usual onboarding (a note for Raafiya). Vatsal asked Harish and Somil to
    set the date for handing over the maths. Board: W03 (repo access and fp_react_inputs.json) is due 19 Sep 2026; the
    output contract date is still to be given.
18. Community (H08) opens the Slack community outside the app; nothing comes back into the app.
19. Working on the board. Saquib: Spinach will work from it on one condition, a frozen marker on each screen and each
    API so they know what will not change, since the screens will keep changing over the coming months. Vatsal agreed
    to mark screens frozen. Board: screens carry a verdict (keep, change, drop) and the changelog, not a frozen flag.
    Action for Vatsal.
20. Admin panel, CRM, website (Eshani). Spinach sent two rounds of admin panel sketches, Kajal gave feedback, and the
    thread went quiet; Spinach asks for a brief: which parts of the admin panel Spinach builds, which are bought, and
    the 360 view of what the app must expose to it; the same for the website, which has not been discussed; the CRM is
    new to them. Vatsal: the decision stands to go external as far as possible (Zoho One and about ten providers) with
    a possible consolidation layer; the events tab already lists what the admin side needs; the brief will say "A to W
    is ours, X, Y and Z is yours".
    Board: I14 says Zoho One decided (Vatsal, 16 Sep 2026) while the admin spec text still reads "platform to be
    decided (one platform)" in places; the CRM backlog already holds the Spinach-built admin front end question
    (brief G2 note). The admin spec text is to follow I14.
21. Cadence and project management (Eshani, Vatsal). Spinach wants daily movement, not weekly, and a project manager
    on HoA's side who posts on WhatsApp which parts are done on any given date, since one-to-one calls lose the
    larger team. Spinach can meet on Monday 21 Sep 2026 with their questions ready; HoA is available for questions
    daily. A full session like this one in about two weeks (about 30 Sep 2026), where HoA brings the admin panel, the
    CRM and the website closed to the same level as the wireframes. Spinach will send its next steps as a project
    plan, not a waterfall.

## 3. Action points

Owner, action, due date, and where it stands on the board.

Vatsal
- Frozen marker per screen and a final or open marker per integrations row, plus the date by which every row is final
  (items 12, 19). Due: not set on the call. Not built yet.
- Mandatory and optional tags on every input (item 15). Done 17 Sep 2026.
- Close NSDL versus CAMS with Gaurav, share a sample CAS file with Spinach, decide A10a (item 6). Due: not set.
- The admin panel brief for Spinach, the CRM plan and the website (items 20, 21). Due: about 30 Sep 2026.
- Name the project manager who posts status on WhatsApp (item 21). Due: not set; Eshani asked for it soon.
- Board upkeep from this meeting: correct I17 to AWS (cause "Gaurav, 16 Sep 2026"); make the admin spec platform text
  follow I14; append the gaps in section 5; record Ankur's Excel and Saquib's later questions as board rows against
  their screens when they arrive.

Kajal, with Raafiya
- Ask every final vendor for its public documentation now and for a sandbox before the contract; put Spinach on the
  vendor email threads (item 14). Due: not set; Spinach called it their most important item.
- Set each integrations row to final or open and fill the dates (W01) (item 12).

Harish and Somil
- The date for handing the maths and logic to Spinach through I04 (item 17). W03 and W04 are due 19 Sep 2026.

Gaurav and Raafiya
- The HoA Core Platform API details, including the data-in APIs, with bands or midpoints as the input shape (item 17).
  W02 (cloud and email) shows delivered on the board as AWS and SES; W08 (event schema) is due 19 Sep 2026.

Harish
- The corporate RIA registration with SEBI (about a week), then the vendor contracts (items 11, 14). W06 (app store
  declarations) follows the registration.

Spinach (Eshani, Saquib, Ankur)
- A project plan of what Spinach does next, and the data lifecycle timeline (what is saved when, session and storage
  rules), shared onto the board (items 4, 21).
- Technical writing and user stories from the wireframes as they stand (item 21).
- Consolidate the two rounds of admin panel sketches with Kajal's feedback for the admin session (item 20).
- Questions ready for Monday 21 Sep 2026; Ankur's field-level questions as an Excel; Saquib's further questions after
  a deep read; comments on the board under the identity Spinach (items 19, 21).

## 4. Takeaways

- Spinach's critical path is integrations, not wireframes: documentation and sandboxes, which today sit behind the
  SEBI registration and the contracts. Asking vendors for a sandbox before signing is the one move that shortens it.
- The board is accepted as the working surface, on the condition of frozen markers. Until they exist, Spinach cannot
  tell what is safe to build against.
- Mobile plus OTP is the identity and the registration; everything after the OTP is saved on the server and a person
  always resumes at the exact screen. The states tab is the contract for that.
- HoA owes Spinach three closures in two weeks: the admin panel brief (what Spinach builds versus what is bought), the
  CRM, and the website. The events tab is the base for all three.
- Found while writing these minutes: I17 says Azure where the call and the W02 row say AWS; the admin spec still says
  the platform is to be decided where I14 says Zoho One; A10a may be dropped; the lead stages Gaurav described are not
  on the board.

## 5. Gaps to append (gap, to be decided; screen in brackets)

- Lead stages as contact fields: lead, verified lead, profile fulfilment percentage (N tab, admin spec).
- Keep or drop A10a, reading the CAS from the email; NSDL or CAMS as the CAS source (A10, A10a).
- Vault storage mechanics: upload, tags, expiry, versions, S3 link in the database (H06).
- Welcome video placement, after the OTP or after the first questions (A04).
- Client-side storage and session timeout rule, to be answered by Spinach's data lifecycle map (D01a, O02).

## 6. Not in the transcript

- The AI-generated minutes in this folder mention UI/UX quotes from Eshani. No such line is in the recorded part of
  the call; it is not recorded here.
- Nothing was said about the review round on the wireframes (verdicts per screen); the board was shown, not reviewed.
