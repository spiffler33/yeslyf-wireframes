# Handoff - 2 Oct 2026 (unit closed: the Admin + CRM tab rewrite and the G9 prep; phase G stays open, G1 and G6 need a person)

State: phase G ("Zoho as if live", PLAN_zoho_live_v01.md) has G0 (baseline, 2a7d191), G3 (the 11 CRM saved views,
00fb249), G5 (the Desk SLA and 4 ticket views, 91cc847) and G4 (the 5 CRM dashboards, 56963f7) in Zoho; nothing in
Zoho has changed since 29 Sep 2026. Two units closed on this machine on 29 Sep 2026: (1) the Admin + CRM tab
rewrite, its own commit 21018b4 (Directus out; 13 placement rows sorted, 6 to the Spinach admin panel and 7 to Zoho
Creator or a CRM custom module; D1 and D5 rewritten; INBOUND one way, app to Zoho, under the three conditions; the
bucket legend; revenue in Zoho Books; I15 in data/integrations.json to match); (2) G9 prep, commit 544657f
(docs/admin_operator.html marks the 12 data/zoho_live.json items "done in Zoho, <date>" with what was built, the
five dashboards are operator step 13, PLAN.md section 25 is a draft that G9 completes). G1 (users) and G6
(Campaigns) still need a person; G2, G7, G8 wait on them and on spiff's answers; G9 closes the phase.

New in the tree on 2 Oct 2026, untracked, not yet looked at: inputs/spinach/admin panel/ (two Spinach files, an admin
panel sketches pdf dated 19 Aug 2026 and an admin panel details xlsx dated 9 Jul 2026; inputs/ is read-only; what to
do with them is spiff's call) and two seed CSV zips at the repo root (yeslyf_csvs_run-500.zip and run-3000;
.gitignore does not cover them; never commit them).

When spiff says "go": if G1 is still not done, nothing unattended is queued; say so in one line and ask for G1 and
G6 (below), an answer to the open items, or what to do with the admin panel inputs. If the users exist: G2
(seed/zoho/own.py, to be written: ownership by API), then G7, G8 (once (b) is consented), then G9 (live.py as the
verifier, reports/phaseG_pass9.md, PLAN.md section 25 completed, handoff, memory, one commit "zoho live G9: close",
push). Board work (phase 14 pass 5) runs only on Vatsal's word.

## Read first
1. reports/phaseG_pass0.md (the baseline table, the grant's gaps, the 74th ticket), reports/phaseG_pass3.md (how
   the CRM view forms behave), reports/phaseG_pass4.md (the dashboards, the editor's behaviour, the sharing gap),
   reports/phaseG_pass5.md (Desk).
2. PLAN_zoho_live_v01.md sections 4 to 6; data/zoho_live.json (baseline, counts, the 12 items done in Zoho); PLAN.md
   section 25 (the draft status).
3. Memory zoho-trial (org, credentials, re-run recipe) and admin-crm-direction (what landed on the tab, what is open).

## Verify before coding
- `git status --short`: clean apart from the untracked items kept out on purpose (two inputs/meeting/ files,
  inputs/spinach/2026-09-25/, inputs/spinach/admin panel/, the two zips at the root).
- `python3 seed/zoho/live.py` (read only, about 1 minute; last run 29 Sep 2026, nothing in Zoho moved since): users 1
  of 11, profiles 2 of 3, views Deals 4 of 4, Contacts 3 of 3, Tasks 2 of 2, App Events 1 of 1, A la carte 1 of 1,
  desk views 4 of 4, calls 61 of 84, campaigns 0, bookings staff 0 of 6, appointments 0 of 8.
- `python3 scripts/check_phase9.py` 19 PASS, `python3 scripts/check_site.py` 3 PASS; docs/admin_operator.html carries
  12 "done in Zoho" lines and 32 "done by script" lines.

## Waiting on spiff (recommended answer first)
- (a) Answered and landed (21018b4). Two items stay open on the tab, written as "to be decided": Metabase's 13
  placement rows to Zoho Analytics (the rows stay as written; when answered, move them with cause "Vatsal, <date>"
  and a changes_v02 entry), and Creator or a CRM custom module as the content and config home.
- (b) Plan section 4 provisional calls: consent by silence (Missed for the 23 refused calls; past booked slots at the
  same weekday and time in the first future week; marketing and finance built under the admin user).
- (c) A wider grant with Desk.agents.READ before G2 (else the Support 01 agent id is read off Desk, Setup, Agents in
  Chrome). The v8 API list call also needs a scope the docs do not name.
- (d) What to do with inputs/spinach/admin panel/ (read into the board, and on which tab).

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
1. If a dashboard needs a change: Analytics, the picker, the dashboard, hover the tile, the three dots, Edit; or
   Manage Dashboards for Rename, Clone, Delete. Sharing is "to be verified after G1" (no sharing control exists in
   this org's Analytics; reports/phaseG_pass4.md).
2. When the users exist: G2 (seed/zoho/own.py, to be written: ownership by API), G7 (Bookings notifications off
   first, then staff and appointments), then G8 (provision.py rule for the 23 calls) once (b) is consented, then G9.
   For G9 the operator marks and PLAN.md section 25 already exist: live.py grows into the verifier and writes the
   "Live build" section of seed/zoho/leftovers.md; section 25 gets what closed and what is open.

## Gotchas found so far
- data/operator.json is hand-formatted (one item per line, a step's id, n and title on one line): edit it as text,
  never by json.dump; build_operator.validate() requires every item id to start with its step's id plus "/", so a
  live key like dashboards/<seat> needs its own step (step 13 now). data/admin_crm.json round-trips with
  json.dumps(indent=1) plus a newline, data/integrations.json with indent=2. build_site.py runs build_operator at
  the end; it strips every key ending in _v01 from the rendered DECISIONS (owner_v01, position_v01, stated_by_v01).
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
  and "to be decided: <item>" with no name attached. Secrets never in the repo; the admin address never in a file;
  the seed CSV zips never in a commit.
- One commit per phase, "zoho live G<N>: <what>", no AI attribution trailer. Board work stays in separate commits and
  runs only on Vatsal's word. No Directus, Appsmith or Retool anywhere new; a v0.1 key on the Admin + CRM tab changes
  only with a cause listed under changes_v02. inputs/ is read-only.
