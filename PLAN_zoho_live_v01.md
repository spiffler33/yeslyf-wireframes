# PLAN: Zoho as if live (phase G), v0.1

Status, 28 Sep 2026: written after phase F closed (commit e93d9b8). G0 done on 28 Sep 2026 on Vatsal's "go"
(reports/phaseG_pass0.md: the baseline, seed/zoho/live.py, data/zoho_live.json). G1 to G9 run phase by phase, in
order, with a commit at each phase boundary.

Date: 28 Sep 2026. For Claude Code in the yeslyf-wireframes repo. CLAUDE.md rules apply throughout (ASCII, Rs, first
names, a cause on every change, "to be verified: <item>" and "to be decided: <item>" with no name attached, no regex,
stdlib only, secrets never in the repo).

Cause labels used in this file:
- "Vatsal, 28 Sep 2026": his call. He agreed the three shaping decisions in section 3 on 28 Sep 2026.
- "plan G, 28 Sep 2026": a provisional call made in this plan; Vatsal vetoes by reply. Silence after the phase report
  is consent.
- "Zoho, <date>": a fact the trial org or the Zoho docs forced.

## 0. Purpose and non-goals

Purpose: make the Zoho One trial (org Plan2prosper, India datacentre) look and work as if the run-3000 seed were the
live book of business: staff users in their seats, records owned by those staff, the seats' saved views and
dashboards, the Desk SLA and views, the Campaigns lists filled, the Bookings staff and appointments in place, and the
23 calls Zoho refused logged one way or another. Phase F (seed/zoho/, PLAN.md section 23) loaded the data and
everything the API allows; this phase does the rest, mostly through the Zoho UI in Chrome with Kajal's signed-in
session, and by API where one exists.

Hard rule (Vatsal, 28 Sep 2026): no message of any kind reaches a seeded contact. No campaign is sent, no test mail,
no WhatsApp or SMS channel is connected, no Desk email channel, no booking confirmation to a customer. Every step that
could send is checked for its notification setting before it runs, and stopped if the setting cannot be turned off.

Non-goals: no Zoho Flow, no workflow rules, no webhooks, no Razorpay, no channel connections, no Zoho Analytics
workspace, no Mixpanel or Metabase work. No visual redesign of anything. No change to the seed data itself except the
ownership and call-logging rules below.

Tooling: Python 3 standard library for the API steps (seed/zoho/zoho.py, provision.py, verify.py); Claude in Chrome
for the UI steps, one browser, one tab group, screenshots before and after every save; every UI step is written to
the phase report with its screen path so Kajal can repeat or reverse it.

## 1. Inputs to read first

| input | what it gives | where |
|---|---|---|
| seed/zoho/leftovers.md | the 24 manual steps with their criteria (the 16 views verbatim), the 23 refused calls | repo |
| data/seed/run-3000/staff.json | the 10 staff: Harish (principal officer, DIFM owner), Adviser 01 to 06 (adviser and call centre), Ops 01, Support 01, Compliance 01 | repo |
| data/seats.json | the 8 seats and their Zoho questions (the views hang off them) | repo |
| data/seed/run-3000/exports/campaigns/S0.csv, S0w.csv, S1.csv, S2.csv | the four Campaigns lists (email column; 205, 230, 131 and 284 rows with an email) | repo |
| data/seed/run-3000/exports/zoho/calls.csv | the 84 calls; the 23 refused rows are Status no_show (14), cancelled (1), booked (8) | repo |
| .claude/HANDOFF.md, phase F section | the org facts, the credentials' location, the design calls the live run forced | repo |
| memory zoho-trial | the same, across sessions | memory |
| seed/zoho/.local/docs/docs_*.md | the Zoho doc research (local, gitignored); Context7 first for anything new | local |

## 2. Deliverables

| id | deliverable | where | phase |
|---|---|---|---|
| G-D1 | 10 staff users in Zoho One with CRM access, roles per seat; Support 01 and Compliance 01 as Desk agents; the Finance read-only profile | the trial org | G1 |
| G-D2 | record ownership: Tasks to their Assignee, Contacts and Leads to their adviser field, Calls to their Adviser, Deals to the contact's owner, tickets to Support 01 | the trial org | G2 |
| G-D3 | the 11 CRM saved views (G0, 28 Sep 2026: counted from leftovers.md; the plan said 12), shared with all users | the trial org | G3 |
| G-D4 | one dashboard per seat that has Zoho questions: principal officer, call centre, marketing, compliance, finance | the trial org | G4 |
| G-D5 | Desk: SLA of one business day; the 4 ticket views; agents in place | the trial org | G5 |
| G-D6 | Campaigns: lists S0, S0w, S1, S2 filled by UI import with no confirmation mail | the trial org | G6 |
| G-D7 | Bookings: notifications off, 6 advisers as staff on Talk to an adviser, the booked calls as appointments | the trial org | G7 |
| G-D8 | the 23 refused calls logged (rule in provision.py), Calls 84 of 84 | the trial org, seed/zoho/provision.py | G8 |
| G-D9 | seed/zoho/verify.py extended with the live checks; data/zoho_live.json (what was done by hand, when); the operator page marks those items "done in Zoho, <date>"; reports/phaseG_pass0.md to pass9.md; PLAN.md section 24 | repo | G9 |

## 3. Decisions already taken (Vatsal, 28 Sep 2026, on the three questions of the phase F report)

1. Staff identities: the 10 users get plus-addresses on Kajal's own mailbox (her address is read from Zoho at run time
   with GET /users?type=CurrentUser and never written into the repo, the plan or a report), so every invitation lands
   with Kajal and no real person is mailed. Display names are the seed's: Harish, Adviser 01 to 06, Ops 01,
   Support 01, Compliance 01. Passwords are set by the admin flow and never recorded anywhere.
2. Campaigns: the four lists are imported through the UI only after the list's double opt-in and welcome mail are
   confirmed off on the list's settings screen and the import screen offers no confirmation mail. The addresses are
   all example.com in any case.
3. Bookings: customer and staff notifications are turned off in the workspace settings first; then the six advisers
   are added as staff and the booked calls are booked as appointments.

## 4. Provisional calls (plan G, 28 Sep 2026; Vatsal vetoes by reply)

- The 23 refused calls: no-shows and booked slots already past are logged with Call_Type "Missed" (Zoho's own kind
  for a call that did not happen; the docs list Inbound, Outbound and Missed), start = Slot, no duration; the one
  cancelled call is logged the same way with the Subject prefixed "cancelled: ". If Zoho refuses Missed without a
  duration, the fallback is a Task per refused call ("no-show", "cancelled", "slot passed") on the contact, and the
  Calls count stays at 61 with the reason written.
- Appointments: a booked slot already in the past is booked at the same weekday and time in the first week that is
  in the future, with the note "seed: original slot <date>". Bookings refuses past slots; the alternative is no
  appointments at all.
- Marketing and finance have no staff person in the seed; their views and dashboards are built under Kajal and
  shared with all users. The Finance read-only profile is created now so a finance user can be added later.
- Dashboards hold one component per view: a KPI (count) where the view is a list, a chart where the view groups
  (Paid by SKU by week, Call centre outcomes by Outcome, GST split by GST Type). Nothing beyond the seats' questions.
- Leads are owned by their Adviser field when it is set, else they stay with Kajal. Deals follow their contact's
  owner. Tickets go to Support 01.
- If the Zoho One trial caps the number of users, the seats are created in this order until the cap: Harish,
  Adviser 01, Adviser 02, Support 01, Compliance 01, Ops 01, Adviser 03 to 06; the rest are written as
  "to be decided: <seat> user (trial cap)" in the report.

## 5. Phases, in order, one commit each

Every phase: read its inputs, do the work, verify by API where an API exists and by a screenshot in the report where
none does, write reports/phaseG_pass<N>.md (what was done, screen paths, what Zoho refused, what is left), update
data/zoho_live.json (item id, status, "at" timestamp, "how": api or chrome), commit "zoho live G<N>: <what>". A phase
that hits a send it cannot switch off stops and reports; it does not improvise. The phases share one browser and one
org, so they never run in parallel.

### G0. Preflight (API, read only)
- `python3 seed/zoho/zoho.py check` (org, Desk portal, Bookings workspace). Read and print counts only: users
  (GET /users?type=AllUsers), profiles (GET /settings/profiles), roles (GET /settings/roles), custom views per module
  (GET /settings/custom_views?module=<api>), Desk views (the Desk list views call), Desk SLAs (the Desk list SLAs
  call), Campaigns lists (getmailinglists), Bookings staff (GET /staffs) and appointments (fetchappointment). Context7
  for every call shape before it is written (the docs rule).
- Done when: reports/phaseG_pass0.md holds the baseline table (object, count now, target after G9) and
  seed/zoho/live.py exists with those reads (it grows into the verifier of G9).

### G1. Users, roles, profiles (Chrome: Zoho One admin; API for verification)
- Zoho One admin panel, Users, Add User, for each of the 10 staff: first name and display name from staff.json,
  email = Kajal's local part + "+" + the staff_id + "@" + her domain (read at run time), apps CRM (all), Desk
  (Support 01, Compliance 01), Bookings (Adviser 01 to 06). CRM role per seat: Harish principal-officer, advisers
  adviser, Ops 01 ops, Support 01 support, Compliance 01 compliance (the roles exist from phase F). Screenshot before
  each save; the invitation mail goes to Kajal's mailbox only (decision 1).
- CRM Setup, Security Control, Profiles: clone Standard as "Finance read only", untick create, edit and delete on every
  module (the roles/finance leftover).
- Done when: GET /users?type=AllUsers lists Kajal plus the 10 (or the trial cap, written); GET /settings/profiles lists
  "Finance read only"; each user's role in the API answer matches the seat table. Report: pass1.

### G2. Ownership (API: records update, 100 per call)
- Map display name to user id from GET /users. Tasks: Owner = the user named in Assignee. Contacts: Owner = Adviser
  Owner when set (else Kajal). Leads: Owner = the Adviser field when set (else Kajal). Calls: Owner = Adviser. Deals:
  Owner = the contact's owner. Desk tickets: assignee Support 01 (Desk PATCH ticket, assigneeId; no notification
  rule for assignment is on, checked in phase F). Written as seed/zoho/own.py (stdlib), idempotent, with "trigger": []
  on every CRM call.
- Direction: the ownership written here mirrors the app side's adviser assignment. Data flows app to Zoho only;
  nothing in this phase makes Zoho write into the app, and no webhook or Flow is created (Vatsal, 28 Sep 2026).
- Done when: a COQL count per Owner per module matches the export's counts per Assignee / Adviser Owner / Adviser
  (own.py prints both tables; they agree); tickets show assignee Support 01 on GET. Report: pass2.

### G3. CRM saved views (Chrome), 11 views
- For each of the 11 CRM rows in leftovers.md (Deals 4, Contacts 3, Tasks 2, App Events 1, A la carte 1; G0, 28 Sep
  2026: counted from leftovers.md, the plan said 12): module, list view, Create
  Custom View, name exactly as the leftover says, criteria as written, columns as written, shared with all users.
  Where the UI lacks a criterion (for example "group by week of Start" is a report or dashboard notion, not a view
  filter), the view carries the filter part and the grouping moves to the seat's dashboard component; the report says
  so per view.
- Done when: GET /settings/custom_views?module=<api> lists each name; the report holds one screenshot per view with
  its record count. Report: pass3.

### G4. CRM dashboards (Chrome: Analytics, Create Dashboard), 5 dashboards
- One dashboard per seat with Zoho questions: "Principal officer" (Paid by SKU by week chart; DIFM prospects to call
  KPI; Grievances past SLA lives in Desk, so a note component points there), "Call centre" (Call centre today KPI;
  Call centre outcomes by Outcome chart; Same adviser offer KPI), "Marketing" (Opt-in and DND KPI; Stage lists is a
  Campaigns notion, a note component points to the lists), "Compliance" (RPQ refresh due KPI; Grievance register
  points to Desk), "Finance" (Payment reconciliation KPI; GST split by GST Type chart; Refunds KPI; A la carte
  receipts KPI). Each component reads its saved view from G3. Shared with all users.
- No revenue component: Deals Amount is blank in the seed (prices are "Rs ___", never invented). When prices exist,
  Amount by SKU by month becomes a Finance dashboard chart, with Zoho Books as the ledger fed from Razorpay and
  Razorpay as the source of money movement (plan G, 28 Sep 2026; pending Vatsal's answer on revenue in Zoho).
- Done when: the Analytics dropdown lists the 5 names; one screenshot per dashboard in the report with the KPI
  numbers; the numbers agree with the view counts of G3. If the CRM dashboards API (v8 Analytics) can list them, the
  check is by API too (Context7 first). Report: pass4.

### G5. Desk (Chrome; Desk API for verification)
- Setup, SLAs: one SLA "One business day" for the department: resolution due in 1 business day for every ticket;
  no escalation action that mails anyone (escalation actions are left empty; that is checked on the screen).
- Tickets, views: the 4 rows in leftovers.md (Grievances past SLA, Grievance register, Open tickets with context,
  Past SLA), criteria and columns as written, shared with all agents.
- Agents: Support 01 and Compliance 01 appear under Setup, Agents (from G1); Support 01 owns the tickets (from G2).
- Done when: the Desk list SLAs call shows the SLA; the Desk list views call shows the 4 names; screenshot per view
  with its count. Report: pass5.

### G6. Campaigns (Chrome)
- For each of S0, S0w, S1, S2: Contacts, Lists, create the list with that name; open its settings and confirm double
  opt-in is off and no welcome or confirmation mail is set (screenshot); Import, upload the export CSV (email
  column), map Email and the name columns, and confirm the import screen sends nothing (screenshot of that option
  before Import). If any of those switches cannot be turned off, stop, do not import, and report.
- Done when: `python3 seed/zoho/verify.py` (campaign_counts) shows the four lists with counts equal to the rows with
  an email (205, 230, 131, 284; Campaigns may drop malformed addresses: the difference is listed). Report: pass6.

### G7. Bookings (Chrome; Bookings API for verification)
- Workspace settings: customer notifications off, staff notifications off (email and SMS), screenshot.
- Staff: add Adviser 01 to 06 (plus-addresses from G1, or the Zoho One users if Bookings offers them), assign all six
  to Talk to an adviser; working hours default.
- Appointments: for each of the 8 booked calls (Status booked), book the contact (name and example.com email from the
  export) with the adviser of the row, at the shifted future slot (section 4), note "seed: original slot <date>".
- Done when: GET /staffs lists 6 and each is on the service; fetchappointment lists 8 with the notes; no mail was
  sent (the notification switches were off before the first booking; screenshot). Report: pass7.

### G8. The 23 refused calls (API: provision.py)
- Apply the section 4 rule to CALL_STATUS_FIELDS (no_show and booked in the past: Call_Type Missed, no duration;
  cancelled: Missed with the Subject prefix), re-run `python3 seed/zoho/provision.py` (idempotent, about 6 minutes),
  then `python3 seed/zoho/verify.py`.
- Done when: verify.py counts Calls 84 of 84 (or the fallback Tasks exist and the count line explains the 61).
  Report: pass8.

### G9. Close
- seed/zoho/live.py (from G0) becomes the live verifier: users, profiles, ownership tables, views per module, Desk
  views and SLA, Campaigns counts, Bookings staff and appointments; it writes a "Live build" section into
  seed/zoho/leftovers.md. scripts/build_operator.py reads data/zoho_live.json and marks items "done in Zoho, <date>"
  (same style as "done by script"); operator items neither done by script nor in Zoho stay as they are.
- `python3 scripts/build_site.py`, `check_phase9.py` 19 PASS, `check_site.py` 3 PASS. PLAN.md section 24 (status,
  what closed, what is open). Handoff, memory, one commit "zoho live G9: close", push.

## 6. Verification summary (what "done" means for the phase)

| check | how | target |
|---|---|---|
| users | GET /users?type=AllUsers | Kajal + 10 (or the cap, written) |
| Finance read only | GET /settings/profiles | present |
| ownership | own.py tables (COQL per Owner vs export per Assignee / Adviser Owner / Adviser) | equal |
| CRM views | GET /settings/custom_views per module | 11 names present |
| dashboards | Analytics dropdown screenshot; API if one exists | 5 names |
| Desk SLA and views | Desk list SLAs, list views | 1 SLA, 4 views |
| Campaigns | verify.py campaign_counts | 205, 230, 131, 284 (differences listed) |
| Bookings | GET /staffs, fetchappointment | 6 staff, 8 appointments |
| Calls | verify.py | 84 of 84, or 61 plus the fallback Tasks |
| sends | every notification screen screenshotted before the step that could send | none sent |

## 7. Placeholders and to be verified

- to be verified: whether the Zoho One trial caps users below 11 (section 4 gives the order if it does).
- to be verified: whether Zoho One accepts plus-addresses as distinct user emails; if not, the fallback is users on
  the org domain if Zoho One shows the domain as verified (no external mail then), and the report says which.
- to be verified: whether Call_Type Missed is accepted without a Call_Duration (section 4 fallback).
- to be verified: whether Zoho Campaigns' UI import offers a "send confirmation" switch or sends nothing by design;
  the phase stops if it cannot be confirmed off.
- to be decided: how a no-show, a cancelled call and a booked slot already past are logged (section 4 proposes Missed).
- to be decided: a wider grant with Desk.agents.READ before G2 (the agents list gives Support 01's agent id for the
  ticket assignee and the G5 agents check), or the agent id read off the Desk agents page in Chrome (G0, 28 Sep 2026).
- to be verified: the scope the v8 API list call (GET /crm/v8/__apis) needs; the grant's 17 scopes were refused
  (G0, 28 Sep 2026). Desk holds Zoho's sample ticket beside the 73 seed tickets; it stays as it is.
- The Account "Individual" placeholder on Deals and the Company "Individual" on Leads stay unless Vatsal says
  otherwise; making Account Name optional on the Deals layout is a Kajal step outside this phase.
