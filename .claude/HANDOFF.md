# Handoff - 7 Oct 2026 (unit closed: W12 delivered; Kajal's M03 answers on the board; phase G stays open on G1 and G6)

State: the admin brief (docs/admin_brief.html) went to Spinach on 7 Oct 2026 with Kajal's six answers on the staff view
M03 applied (commit 1f76412), and tracker W12 reads delivered (f54a82b). M03 now carries: the subscription actions
(refund, cancel, extend, comp) for the support seat through I09; suspend for ops with "to be decided: when an account
is suspended" (gap G20, the one open reason on M03 besides "until the brief is accepted"); a devices and sessions tab
of web sessions only; no reassign (the adviser owner is the Contact owner in Zoho, read by the app; M02's pointer says
so); sign-in with the Zoho account, MFA in Zoho One, the allowlist maps each Zoho user to a seat. Gaps G19, G21, G24
closed on 7 Oct 2026 (G22 on 5 Oct); G18, G20, G23 open. Phase G ("Zoho as if live", PLAN_zoho_live_v01.md) is
unchanged since 29 Sep 2026: G0, G3, G4, G5 in Zoho; G1 (users) and G6 (Campaigns) need a person; G2, G7, G8, G9 follow.

Owed by people: Kajal's check with her team on anything they do daily that M03 misses (question 6, "will check");
Spinach's reply and estimate on the brief; the 1 Oct meeting notes were never provided. One reading to confirm with
spiff if it ever matters: Kajal's "Web or mobile / then only web" on the devices tab was read as "a tab of web
sessions only".

Untracked on purpose in the tree: inputs/spinach/admin panel/, inputs/spinach/kajal-admin panel/, the two
inputs/meeting/ files, inputs/spinach/2026-09-25/, and the two seed CSV zips at the repo root (never commit them).

## Read first
1. PLAN.md section 26 (W12, 2 to 7 Oct 2026; the last bullet is this unit) and docs/admin_split.html sections 1, 2, 4.
2. Memory spinach-admin-split (decisions and what is open) and admin-crm-direction (the 28 Sep rules).
3. For Zoho work: reports/phaseG_pass0.md to pass5.md, PLAN_zoho_live_v01.md sections 4 to 6, memory zoho-trial.

## Verify before coding
- `git status --short`: clean apart from the untracked items above.
- `python3 scripts/build_site.py` (about 2 minutes), then `python3 scripts/check_phase9.py` 19 PASS and
  `python3 scripts/check_site.py` 3 PASS; the build prints "T3 3" for the brief and "12 sheet rows, 7 builds, 9 own
  rows, 13 sketches" for the split page.
- `python3 seed/zoho/live.py` (read only, about 1 minute): users 1 of 11, views Deals 4 of 4, Contacts 3 of 3,
  Tasks 2 of 2, App Events 1 of 1, desk views 4 of 4, campaigns 0.

## When spiff says "go"
- If Spinach replies with questions or an estimate: record the estimate on tracker W12's notes (hand-formatted file,
  edit as text) and answer questions on the board with the cause "Spinach, <date>" where a fact changes.
- If Kajal's team adds a daily task M03 misses: add it to M03 (data/admin_screens.json, cause "W12, <date>"; the
  file bans team names and vendor strings, use {I14}, {I09} tokens), the Split page row (data/admin_split.json) and
  the change log on the tab (data/admin_crm.json changes_v02, cause "Kajal, <date>"); rebuild; one board commit; push.
- If the suspension rule is decided: close G20 in data/gaps.json (status "done", "closed: <who>, <date>",
  closed_note), drop the reason from M03's freeze list and the "decide" entries on the Split page.
- If a Zoho "to be verified" item was tested: record the outcome on the Admin and CRM tab (data/admin_crm.json STACK
  notes) and in docs/admin_split.html's outcome.verify list; a failed one returns the row to Spinach with a cause.
- Phase G: only when G1 and G6 are done by a person; then G2 (seed/zoho/own.py, to be written), G7, G8, G9.

## Steps only a person can do
- G1: Zoho One admin panel, User Management, Add User, 9 users in plan section 4 order (Harish, Adviser 01, Adviser 02,
  Support 01, Compliance 01, Ops 01, Adviser 03, 04, 05; Adviser 06 is "to be decided: Adviser 06 user (trial
  cap)"); email = the admin mailbox local part + "+" + staff_id + "@" + its domain (read at run time, never written
  down); Employee Id = staff_id; "Send Notification Mail" unticked; then CRM roles, Desk for Support 01 and
  Compliance 01, Bookings for the advisers; CRM profile "Finance read only" cloned from Standard without create,
  edit, delete.
- G6: campaigns.zoho.in's first-time onboarding form is for Kajal or spiff only; then the four imports per plan G6.

## Gotchas
- Data formats: data/admin_crm.json, data/admin_split.json and data/gaps.json round-trip with json.dumps(indent=1)
  plus a newline; data/admin_screens.json, data/seats.json and data/integrations.json with indent=2;
  data/admin_pack.json, data/operator.json and data/tracker.json are hand-formatted: edit them as text (a json dump
  of admin_pack.json rewrites 116 lines).
- data/admin_screens.json: role values are only "act", "read" or "read, own people"; every write event is listed in
  events; freeze status "open" with a reason; a dropped screen needs a pointer; team names and vendor strings banned.
- Pages ban the words in build_site.FORBIDDEN (the brand with a capital, "recommendation", among others).
- Zoho in Chrome: CRM dropdowns take a typed search then a click; any JavaScript closes an open dropdown; Desk
  typing with no focus fires shortcuts; the auto-mode classifier refuses the Add User form.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends. No message reaches a seeded
  contact. Staff invitations, if ever sent, go only to plus-addresses on the admin mailbox.
- No regex or phrase rules; stdlib only; ASCII; Rs; first names; a cause on every change; "to be verified: <item>"
  and "to be decided: <item>" with no name attached. Secrets never in the repo; the seed CSV zips never in a commit.
- One commit per unit; "board: ..." and "zoho live G<N>: ..." stay separate; no AI attribution trailer. No Directus,
  Appsmith, Retool or Metabase anywhere new; the Split page's picks change only with a cause. inputs/ is read-only.
