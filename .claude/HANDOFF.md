# Handoff - 29 Sep 2026 (checkpoint mid-phase G: G4 closed; G0, G3, G4 and G5 done; G1 and G6 need a person)

State: phase G ("Zoho as if live", PLAN_zoho_live_v01.md) has G0 (baseline, seed/zoho/live.py, commit 2a7d191), G3
(the 11 CRM saved views, 00fb249), G5 (the Desk SLA and 4 ticket views, 91cc847) and G4 (the 5 CRM dashboards,
56963f7, reports/phaseG_pass4.md) in Zoho. G4 was built in Chrome on 28 and 29 Sep 2026 to spiff's brief (beautiful,
not a KPI per view): one dashboard per seat, 24 components, every rendered number equal to its G3 view count; the
ids and the component lists are in data/zoho_live.json (items dashboards/*). G1 (users) and G6 (Campaigns) need a
person (below); G2, G7, G8 wait on them and on spiff's answers; G9 closes the phase.

When spiff says "go": nothing in Zoho can move until a person does G1 (users) and the G6 onboarding form, so the
session does the unattended work that was queued for "after G4" (Vatsal's answer (a), G0 report reply): the Admin +
CRM tab rewrite in data/admin_crm.json, its own commit, never mixed with phase G. Sort the 13 Directus rows by the
test in memory admin-crm-direction (app-bound: Spinach admin panel; the rest: Zoho Creator or a CRM custom module),
rewrite decisions D1 and D5, write the three one-way conditions on the INBOUND rows, add the Console/Fold/Change
legend, leave Metabase's 13 rows as "to be confirmed: Metabase rows to Zoho Analytics" (not moved), cause on every
changed row "Vatsal, 28 Sep 2026 (supersedes D1)". Then build_site.py, the checks, one commit "board: Admin + CRM
tab ..." and push. The first reply restates, once and briefly, the person-only steps and the answers owed below, then
carries on without waiting. After that commit, if there is still session left: G9 prep that needs no users
(build_operator.py marks from data/zoho_live.json items, a PLAN.md section 25 draft), as a "wip:" commit.

## Read first
1. reports/phaseG_pass0.md (the baseline table, the grant's gaps, the 74th ticket), reports/phaseG_pass3.md (how
   the CRM view forms behave), reports/phaseG_pass4.md (the dashboards, the editor's behaviour, the sharing gap),
   reports/phaseG_pass5.md (Desk).
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
- (a) Answered (Vatsal, 28 Sep 2026): only the Directus parts that must sit on the app's own database (admin over
  app tables, client data edits) are built by Spinach as the admin panel; every other Directus item goes to Zoho
  (Creator or a CRM custom module for non-sensitive content and config). Still to confirm: Metabase's 13 rows to
  Zoho Analytics. The Admin + CRM tab rewrite (13 Directus rows sorted by that test, D1 and D5, INBOUND rows, the
  Console/Fold/Change legend) is its own commit, never mixed into phase G; do it after G4 or when spiff asks.
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
1. G4 is done (56963f7). If a dashboard needs a change: Analytics, the picker, the dashboard, hover the tile,
   the three dots, Edit; or Manage Dashboards for Rename, Clone, Delete. Sharing is "to be verified after G1": no
   sharing control exists in this org's Analytics (details in reports/phaseG_pass4.md).
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
- Dashboard editor (G4): dialogs take 15 to 30 seconds to open and sometimes open scrolled to their bottom (wheel
  up over the dialog); a click made before a dialog opens lands on the canvas behind it; a batch longer than about
  40 seconds times out in the browser tool, so wait in two or three 10-second steps and screenshot at 0.4 scale
  between steps; picklist value boxes filter when typed into, the field and module search boxes filter too, but a
  module name that contains the search word (App Events for "Event") lists every field, so scroll the list; the
  criteria pattern is edited by Edit Pattern then the tick; the editor draws charts clipped until the save, the saved
  dashboard renders whole; Save keeps the create page open ("Added Successfully"), a second Save complains about the
  name. The Chrome window is 1600x1079 CSS pixels and the screenshot frame is 1329x896; clicks map correctly.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends. No message reaches a seeded
  contact. Staff invitations, if ever sent, go only to plus-addresses on the admin mailbox.
- No regex or phrase rules; stdlib only; ASCII; Rs; first names; a cause on every change; "to be verified: <item>"
  and "to be decided: <item>" with no name attached. Secrets never in the repo; the admin address never in a file.
- One commit per phase, "zoho live G<N>: <what>", no AI attribution trailer. Board work (phase 14 pass 5) stays in
  separate commits and runs only on Vatsal's word. The Admin + CRM tab rewrite waits for (a) and is its own commit.
