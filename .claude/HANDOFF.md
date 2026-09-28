# Handoff - 28 Sep 2026 (checkpoint mid-G4; G0, G3 and G5 closed)

State: phase G ("Zoho as if live", PLAN_zoho_live_v01.md) is half done. G0 (baseline, seed/zoho/live.py, commit
2a7d191), G3 (the 11 CRM saved views, 00fb249) and G5 (the Desk SLA and 4 ticket views, 91cc847) are in Zoho and
verified by API. G4 (dashboards) was opened and closed again unsaved: spiff asked for beautiful dashboards, not a
KPI per view, and the context was cleared before the first component. G1 (users) and G6 (Campaigns) need a person
(below); G2, G7, G8 wait on them and on spiff's answers.

When spiff says "go": start G4 at once as designed under "Next in this repo" (Chrome tools loaded in one
ToolSearch, tabs_context_mcp, a new tab at crm.zoho.in, Analytics, Create Dashboard). The three answers and the
person-only steps below are not blockers for G4; restate them once in the first reply and carry on.

## Read first
1. reports/phaseG_pass0.md (the baseline table, the grant's gaps, the 74th ticket), reports/phaseG_pass3.md (how
   the CRM view forms behave), reports/phaseG_pass5.md (Desk).
2. PLAN_zoho_live_v01.md sections 4 to 6; data/zoho_live.json (baseline, counts, items done in Zoho).
3. Memory zoho-trial (org, credentials, re-run recipe) and admin-crm-direction (the Admin + CRM tab answers owed).

## Verify before coding
- `git status --short`: clean apart from the untracked inputs kept out on purpose (two inputs/meeting/ files,
  inputs/spinach/2026-09-25/).
- `python3 seed/zoho/live.py` (read only, about 1 minute): users 1 of 11, profiles 2 of 3, views Deals 4 of 4,
  Contacts 3 of 3, Tasks 2 of 2, App Events 1 of 1, A la carte 1 of 1, desk views 4 of 4, calls 61 of 84, campaigns
  0, bookings staff 0 of 6, appointments 0 of 8.
- `python3 scripts/check_phase9.py` 19 PASS, `python3 scripts/check_site.py` 3 PASS.

## Waiting on spiff (asked in the G0 report reply; recommended answer first)
- (a) Homes for what Directus held: the admin panel Spinach builds over the app's database; Metabase's 13 rows to
  Zoho Analytics. Lands as its own commit on the Admin + CRM tab, never mixed into phase G.
- (b) Plan section 4 provisional calls: consent by silence (Missed for the 23 refused calls; past booked slots at the
  same weekday and time in the first future week; marketing and finance built under the admin user).
- (c) A wider grant with Desk.agents.READ before G2 (else the Support 01 agent id is read off Desk, Setup, Agents in
  Chrome). The v8 API list call also needs a scope the docs do not name.

## Steps only a person can do (the browser rules hand account creation and org setup back to a person)
- G1: Zoho One admin panel, User Management, Users, Add User, 9 users (the trial has 9 licenses left; order from plan
  section 4: Harish, Adviser 01, Adviser 02, Support 01, Compliance 01, Ops 01, Adviser 03, Adviser 04, Adviser 05;
  Adviser 06 is "to be decided: Adviser 06 user (trial cap)"). First name and last name from the seed's display
  name ("Adviser" / "01"; Harish with no last name if the form allows), email = the admin mailbox's local part + "+"
  + staff_id + "@" + its domain (read at run time with GET /users?type=CurrentUser; never written down), Employee Id
  = staff_id, "Send Notification Mail" unticked (nothing is mailed; an invitation can be resent later). Then apps:
  CRM for all (roles Principal officer, Adviser, Ops, Support, Compliance; profile Standard, provisional), Desk for
  Support 01 and Compliance 01, Bookings for the advisers. Then CRM Setup, Security Control, Profiles: clone Standard
  as "Finance read only", untick create, edit and delete.
- G6: campaigns.zoho.in shows a first-time onboarding form (industry, phone number, Get Started) before any list can
  exist; only Kajal or spiff should fill it. After that the four imports follow plan G6 (double opt-in and welcome
  mail confirmed off first).

## Next in this repo (in order)
1. G4 dashboards in Chrome (Analytics tab, Create Dashboard). spiff's brief, 28 Sep 2026: beautiful, not a KPI per
   view. Design worked out before the clear, one dashboard per seat, built on the seat's own Zoho questions and the
   seed's fields:
   - Principal officer: chart Paid deals by week stacked by SKU (Deals, Start, previous and current week); KPI DIFM
     prospects to call (Contacts, DIFM Prospect Flag manual or rule); donut DIFM prospects by Tier; KPI Refunds
     pending (Deals, Refund Requested true, Refund Status pending). Grievances past SLA lives in Desk (description).
   - Call centre: KPI Call centre today (Tasks, Status isn't Completed, State ID S2b/S19/S20, Due today or earlier);
     donut Call centre outcomes by Outcome (Outcome isn't pending); column Outcomes by State ID; bar Same adviser
     offer by Last Adviser (Contacts, Last Adviser not empty).
   - Marketing: KPI Opted in (WhatsApp Opt-in true, DND false); column Opted in by Journey Stage; donut Contacts by
     WhatsApp Opt-in; KPI DND. Stage lists live in Campaigns (description).
   - Compliance: KPI RPQ refresh due (App Events, Event rpq_due); column rpq_due by At (month); column App events by
     Event, last 30 days (the seat's audit trail question). Grievance register lives in Desk (description).
   - Finance: donut Deals by Status (Payment reconciliation); donut GST split by GST Type; KPI Refunds and bar by
     Refund Status; KPI A la carte receipts and column by Date (month); donut Mandates by Mandate Status.
   Editor mechanics learned: Create Dashboard, name field selected at (560,78), description below; component list on
   the left (Chart, KPI, Comparator, Anomaly Detector, Target Meter, Funnel, Cohort, Quadrant, Zone, Stage); KPI
   opens "Choose KPI Style" (Standard, Growth Index, Basic, Scorecard, Rankings) then a dialog: Component Name, KPI
   metric (module, measure), "+ Criteria filter", Duration (date field and range), Done; dialogs slide in from the
   top, so screenshot again after 3 seconds before clicking. Share each dashboard with all users if the save offers
   it. Verify by screenshot (the dashboards API scope is unknown) and write reports/phaseG_pass4.md, then commit
   "zoho live G4: ...".
2. When the users exist: G2 (seed/zoho/own.py, ownership by API), G7 (Bookings notifications off first, then staff
   and appointments), then G8 (provision.py rule for the 23 calls) once (b) is consented, then G9 (live.py as the
   verifier, build_operator.py marks from data/zoho_live.json, PLAN.md section 25, handoff, memory, push).

## Gotchas found this session
- CRM view form: type into a dropdown's search, screenshot, then click the match; clicking in the same batch picks
  the first unfiltered item. Any JavaScript run against the page closes an open dropdown.
- CRM column picker: the row's plus icon appears on hover and takes the click only some of the time; the working
  recipe is the page's own add control fired by JavaScript (mouseover, pointerdown, mousedown, pointerup, mouseup,
  click on the row's lyte-lb-add element), then read the view back by API before saving. Tasks views have no column
  picker on the form; set columns on the saved view's list (header icon, Manage Columns).
- Desk: typing while no input has focus fires keyboard shortcuts ("S" opens Setup); Desk's dropdowns render faint for
  a few seconds, take a second screenshot before clicking. Setup pages sit in an iframe that the wheel does not
  scroll; scrollIntoView by JavaScript or the wizard's own Next button.
- The auto-mode classifier refused the Add User form and one batch that mixed a Cancel click with a navigation; keep
  account and org-setup screens for a person.
- The Chrome tab left open on the unsaved dashboard editor is harmless; the window was resized to 1600x1200 but the
  screen caps screenshots at 1564x784.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends. No message reaches a seeded
  contact. Staff invitations, if ever sent, go only to plus-addresses on the admin mailbox.
- No regex or phrase rules; stdlib only; ASCII; Rs; first names; a cause on every change; "to be verified: <item>"
  and "to be decided: <item>" with no name attached. Secrets never in the repo; the admin address never in a file.
- One commit per phase, "zoho live G<N>: <what>", no AI attribution trailer. Board work (phase 14 pass 5) stays in
  separate commits and runs only on Vatsal's word. The Admin + CRM tab rewrite waits for (a) and is its own commit.
