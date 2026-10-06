# Handoff - 6 Oct 2026 (unit closed: W12 the admin split, the pack for Spinach and the cleanup; phase G stays open on G1 and G6)

State: the admin split is decided and on the board. Three admin screens are built by Spinach (M03 the staff view of a
client, M07 the health page, M10 the config screen) plus the logic panel L00 to L09; the other ten M screens are
dropped with a pointer each (M08 to L08, M12 and M14 into M03); Metabase is out and Zoho Analytics holds the database
KPIs; I15 (Zoho Creator or a CRM custom module) is content and copy only, configuration sits in M10. docs/admin_split.html
is the one-page split (confirmed by Vatsal on 5 Oct 2026 after Kajal's review), docs/admin_brief.html the brief for
Spinach, generated from the board (sections 1 to 5, the annex tables T1 to T7 folded; data/admin_pack.json holds the
narrative). The Admin and CRM v0.2 tab shows the current truth first and folds its history; the admin wireframes nav
groups the moved screens; the seats page folds the N01 precedence pairs. Everything is pushed (last commit on main
before this closure: affe675). Phase G ("Zoho as if live", PLAN_zoho_live_v01.md) is unchanged since 29 Sep 2026: G0,
G3, G4, G5 in Zoho; G1 (users) and G6 (Campaigns) need a person; G2, G7, G8, G9 follow them.

Owed by people: Kajal's answers to the six M03 questions (the walkthrough notes went to her on WhatsApp on 5 Oct
2026: subscription extend or comp, suspension, a devices tab, the adviser owner's home, staff sign-in and MFA, anything
missing); the brief sent to Spinach (then tracker W12 reads delivered); the 1 Oct meeting notes and any Spinach
estimate were never provided.

Untracked on purpose in the tree: inputs/spinach/admin panel/ and inputs/spinach/kajal-admin panel/ (the latter is
byte-identical to inputs/hoa/Admin Panel - Yeslyf.docx), the two inputs/meeting/ files, inputs/spinach/2026-09-25/,
and two seed CSV zips at the repo root (yeslyf_csvs_run-500.zip and run-3000; .gitignore does not cover them; never
commit them).

## Read first
1. PLAN.md section 26 (the whole W12 story, 2 to 6 Oct 2026) and docs/admin_split.html sections 1, 2 and 4.
2. Memory spinach-admin-split (what was decided and why; what is still open) and admin-crm-direction (the 28 Sep
   rules the split rests on: one way app to Zoho, writes stay in the app, bands only in Zoho).
3. For Zoho work: reports/phaseG_pass0.md to pass5.md, PLAN_zoho_live_v01.md sections 4 to 6, memory zoho-trial.

## Verify before coding
- `git status --short`: clean apart from the untracked items listed above.
- `python3 scripts/build_site.py` (about 2 minutes) then `python3 scripts/check_phase9.py` 19 PASS and
  `python3 scripts/check_site.py` 3 PASS; the build prints "T3 3" for the brief (three built screens) and
  "12 sheet rows, 7 builds, 9 own rows, 13 sketches" for the split page.
- `python3 seed/zoho/live.py` (read only, about 1 minute; nothing in Zoho has moved since 29 Sep 2026): users 1 of
  11, views Deals 4 of 4, Contacts 3 of 3, Tasks 2 of 2, App Events 1 of 1, desk views 4 of 4, campaigns 0.

## When spiff says "go"
- If Kajal's answers are in: apply them to M03 (data/admin_screens.json freeze reasons and dev lines; the file bans
  team names and vendor strings, so causes read "W12, <date>" there and "Kajal, <date>" on the tab), close the
  matching gaps G19 to G21 and G24 in data/gaps.json, rebuild, one board commit, push.
- If the brief went to Spinach: data/tracker.json W12 status "delivered" (hand-formatted file; edit as text), notes
  with the date; rebuild; commit; push.
- If a Zoho "to be verified" item was tested (the database feed to Analytics, Creator forms and approval, Campaigns
  setup G6, Books from Razorpay): record the outcome on the Admin and CRM tab (data/admin_crm.json STACK notes, cause
  "Vatsal, <date>") and in docs/admin_split.html's outcome.verify list; if one fails, the row returns to Spinach on
  the Split page and the brief, with a cause.
- Phase G: only when G1 and G6 are done by a person (below); then G2 (seed/zoho/own.py, to be written: ownership
  by API), G7, G8 (once the plan section 4 provisional calls are consented), G9 (live.py as the verifier,
  reports/phaseG_pass9.md, PLAN.md section 25 completed, one commit "zoho live G9: close", push).

## Steps only a person can do (the browser rules hand account creation and org setup back to a person)
- G1: Zoho One admin panel, User Management, Users, Add User, 9 users (the trial has 9 licenses left; order from plan
  section 4: Harish, Adviser 01, Adviser 02, Support 01, Compliance 01, Ops 01, Adviser 03, Adviser 04, Adviser 05;
  Adviser 06 is "to be decided: Adviser 06 user (trial cap)"). First name and last name from the seed's display
  name ("Adviser" / "01"; Harish with no last name if the form allows), email = the admin mailbox's local part + "+"
  + staff_id + "@" + its domain (read at run time with GET /users?type=CurrentUser; never written down), Employee Id
  = staff_id, "Send Notification Mail" unticked. Then apps: CRM for all (roles Principal officer, Adviser, Ops,
  Support, Compliance; profile Standard, provisional), Desk for Support 01 and Compliance 01, Bookings for the
  advisers. Then CRM Setup, Security Control, Profiles: clone Standard as "Finance read only", untick create, edit
  and delete.
- G6: campaigns.zoho.in shows a first-time onboarding form (industry, phone number, Get Started) before any list can
  exist; only Kajal or spiff should fill it. After that the four imports follow plan G6 (double opt-in and welcome
  mail confirmed off first).

## Gotchas found so far
- Data formats: data/admin_crm.json, data/admin_split.json, data/admin_pack.json and data/gaps.json round-trip with
  json.dumps(indent=1) plus a newline; data/admin_screens.json, data/seats.json and data/integrations.json with
  indent=2; data/operator.json and data/tracker.json are hand-formatted, edit them as text. build_site.py strips
  every key ending in _v01 from the rendered DECISIONS.
- data/admin_screens.json: validate_admin_screens bans team names and every vendor string from integrations.json
  (write {I14}, {I15} tokens), needs ids M02 to M14 exactly, freeze status "open" with a reason, a pointer on a
  dropped screen, and every write event listed in events. A dropped admin screen renders as "moved" with its pointer
  (admin_core.js, renderer_v02.js); the M14 matrix skips dropped screens.
- The brief (scripts/build_brief.py) imports build_admin_split for the sheet, sketches and holds tables; the seats
  surface "Logic panel" links to wireframes_v02.html#L0x and is validated against section L of screens_v02.json.
- Pages ban the words in build_site.FORBIDDEN (among them the brand spelled with a capital and "recommendation"):
  never write a file name that carries the brand into page text.
- Zoho in Chrome (phase G): CRM dropdowns take a typed search then a click on the match; any JavaScript closes an
  open dropdown; the column picker's add control is fired by JavaScript on the row's lyte-lb-add element; Desk
  typing with no focus fires shortcuts and its setup pages sit in an iframe; the dashboard editor's dialogs take 15
  to 30 seconds and a batch over about 40 seconds times out; the auto-mode classifier refuses the Add User form.
  The Chrome window is 1600x1079 CSS pixels; the screenshot frame 1329x896; clicks map correctly.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends. No message reaches a seeded
  contact. Staff invitations, if ever sent, go only to plus-addresses on the admin mailbox.
- No regex or phrase rules; stdlib only; ASCII; Rs; first names; a cause on every change; "to be verified: <item>"
  and "to be decided: <item>" with no name attached. Secrets never in the repo; the admin address never in a file;
  the seed CSV zips never in a commit.
- One commit per unit; board work "board: ..." and Zoho work "zoho live G<N>: ..." stay separate; no AI attribution
  trailer. No Directus, Appsmith, Retool or Metabase anywhere new; a v0.1 key on the Admin and CRM tab changes only
  with a cause listed under changes_v02; the Split page's picks change only with a cause. inputs/ is read-only.
