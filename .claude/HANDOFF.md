# Handoff - 28 Sep 2026 (phase closed: 14, the Spinach Questions tab and the SQ1 exports)

State: phase 14 is closed and pushed (bfe5a3a to the closure commit on main). SQ1 is answered on the board:
data/questions.json, 231 rows (221 frozen, 7 open, 3 owed); docs/spinach_questions.html is HoA's working view, off the
review link; docs/exports/SQ1_*.xlsx are Spinach's copy, stamped 28 Sep 2026, carrying Vatsal's comments of 28 Sep 2026.
Phase F (Zoho provisioning) is a separate, uncommitted effort in this checkout; its handoff section is carried below.

## Read first
1. reports/phase14_pass4.md (the export, the cover-note counts) and reports/phase14_pass3.md (the tab and its controls).
2. PLAN.md section 22 (what closed, the limits, what is open).
3. Memory project_state.md (the rules: overrides file, pull before build).

## Verify before coding
- `git status --short`: only phase F's files (M .gitignore, M scripts/build_operator.py, M docs/admin_operator.html,
  ?? seed/zoho/, ?? data/zoho_provision.json) and the untracked inputs kept out on purpose (two inputs/meeting/ files,
  inputs/spinach/2026-09-25/ with Spinach's ops report pdf, marked confidential).
- `python3 scripts/pull_board.py`, then `python3 scripts/build_site.py`: docs/ changes only where the board moved;
  `python3 scripts/check_phase9.py` 19 PASS, `python3 scripts/check_site.py` 3 PASS, `python3 scripts/validate_v02.py` 7 PASS.
- `python3 scripts/import_sq.py` (dry run): 231 rows, 0 problems, 0 pending, one override applied (BE-04).

## Next (on Vatsal's word, not before)
- Pass 5 of yeslyf_phase14_brief.md: the approvals script (not written yet) reads the board table for page
  spinach_questions, field approve, and on instruction freezes the approved rows through data/sq_overrides.json
  (status frozen, cause "approved by <first name>, <date>", the changed date), closing the linked W row where the
  approval closes it; the next build re-exports with the "Changed since" marks (batch 2, about 1 Oct 2026). Vatsal
  approved the 9 open and owed rows on 28 Sep 2026 with comments; several say "will revert in 2 weeks", so approval
  does not mean the item is settled.
- BE-04 is open (owner Product, no date) and waits for its one-line item ("to be decided: ...") in data/sq_overrides.json.
- The CAS clash on W11: Raafiya (26 Sep 2026) says depository CAS confirmed; JD-AA-W5's answer says registrar CAS
  first. Vatsal's call; then the W11 row and, if the answer changes, an override on JD-AA-W5.
- Phase 13 after the admin session (30 Sep 2026): PLAN.md section 17, unchanged.

## Constraints carried forward
- Spinach never sees the tab: not in REVIEW_TABS, no review copy, no link from the Spinach audience file, no Spinach
  identity on it. Only the three export files go out; Vatsal sends them.
- Never hand-edit data/questions.json: scripts/import_sq.py regenerates it from the answer set plus
  data/sq_overrides.json (status changes by commit, logged on the row) and carries the export stamps across rewrites.
- Never change an answer's text. Spinach's cells stay verbatim (non-ASCII as entities on the page; the banned-word
  check skips their cells). No regex; stdlib only.
- Comments reach the export only after a board pull: pull_board.py, then build_site.py. The export restamps only when
  a row or a comment is newer than the last stamp.
- Never stage phase F's files with board work; phase F lands as its own single commit.

---

# Phase F (Zoho provisioning), carried unchanged from the 24 Sep 2026 handoff

Note added 28 Sep 2026: data/zoho_provision.json now exists in the tree (untracked), so step 2 of the run order below
has run at least once since; the git facts in "Verify before coding" below are as of 24 Sep 2026 (phase 14 has since
been pushed in full). The phase F session's own notes rule.

State: seed/zoho/ is built and reviewed (zoho.py, provision.py, verify.py) and scripts/build_operator.py reads
data/zoho_provision.json for "done by script" marks. Setup is done and the read-only check passed; nothing has been
written to Zoho and nothing is committed: the phase lands as ONE commit, "zoho provisioning F", after the live run
(Vatsal, 24 Sep 2026). spiff paused at 24 Sep 2026 evening ("i need to step away").

## Done this session (24 Sep 2026, evening)
- The org: Zoho One trial "Plan2prosper", India datacentre, owned by Kajal's Zoho login; spiff confirmed it is the
  yeslyf trial, not a live business org, and added CRM to it from crm.zoho.in (the console had refused CRM scopes
  until CRM existed). The Self Client was created under that login, 24 Sep 2026.
- seed/zoho/.env written (ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET; git ignores it) and the grant code exchanged:
  seed/zoho/.local/token.json exists. On the Generate Code tab the console asked for a portal per service (Desk,
  Campaigns, CRM), each set to Plan2prosper.
- `python3 seed/zoho/zoho.py check`: CRM org Plan2prosper, type production, edition free, trial zohooneenterprise;
  Desk portal id 60089105539; Bookings workspaces: none.
- Decisions 1 and 2 taken as recommended (Vatsal, 24 Sep 2026: "go with your recommendations"): the MANDATORY_FILL
  and CALL_STATUS_FIELDS rules stand, and provision.py got VALUE_MAP (zoho/tasks.csv Status: done -> Completed,
  open -> Not Started), applied in read_csv and Data.values so the picklist check, the bulk file and the records
  API see the same values; `--plan` prints "translated: ..." on that column. Verified: 94 Completed, 20 Not
  Started; calls.csv Status untouched.

## When spiff is back
1. Decision 3 is still open and required before the run: in the trial's Desk, Setup > Customization > Notifications
   (per department, the Desk KB path), every rule for customers and agents off? Ask for a yes or no; offer to look
   in Chrome if he is signed in to Desk.
2. Bookings has no workspace, so the "bookings/service" item would be left. Ask him to open Bookings once in the
   trial (Zoho One app list, or bookings.zoho.in) to create the workspace; then re-run `zoho.py check` and expect
   one workspace. Not a blocker for the rest of the run.
3. Then the run order below, from step 2 (`provision.py`); step 1 has run.

Scope line used (the console accepted it as is, including Desk.fields.CREATE):
ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.bulk.ALL,ZohoFiles.files.ALL,ZohoCRM.org.READ,ZohoCRM.users.READ,ZohoCRM.coql.READ,Desk.basic.READ,Desk.layouts.READ,Desk.layouts.UPDATE,Desk.fields.CREATE,Desk.tickets.ALL,Desk.contacts.READ,Desk.contacts.CREATE,Desk.search.READ,ZohoCampaigns.contact.READ,zohobookings.data.CREATE

## Read first
1. seed/zoho/provision.py: the docstring and the constants (MANDATORY_FILL, CALL_STATUS_FIELDS, DESK_STATUS,
   CAMPAIGN_LISTS, READ_ONLY_SEATS) hold every design call.
2. seed/zoho/.local/docs/docs_*.md: the Zoho doc research with verbatim quotes (local, gitignored). Read the
   relevant one before changing any request shape; the docs rule applies (Context7 first).

## Verify before coding
- `git status --short`: M .gitignore, M .claude/HANDOFF.md, M scripts/build_operator.py, ?? seed/zoho/, and the two
  untracked inputs/meeting/ files (untracked on purpose). inputs/spinach/ and yeslyf_phase14_brief.md were committed
  by the parallel Phase 14 session (below) and are not phase F.
- A second session ran Phase 14 in this same checkout on 24 Sep 2026 and committed bfe5a3a and bbabf36 at 19:16
  (changelog data, scripts/build_site.py, scripts/import_sq.py, reports/phase14_*.md; none of the phase F files).
  main is ahead of origin by those two commits; the phase F commit goes on top and the push carries all three. If that
  session wrote its own .claude/HANDOFF.md since, merge this phase F section into it rather than replacing it.
- `python3 seed/zoho/provision.py --plan`: no network; the last line names the service 'Talk to an adviser', 45 minutes.
- `python3 scripts/build_site.py`, then `python3 scripts/check_phase9.py` (19 PASS) and `python3 scripts/check_site.py`
  (3 PASS); docs/ stays unchanged while data/zoho_provision.json does not exist.

## Run order, after the answers
1. `python3 seed/zoho/zoho.py check`: read only; prints the CRM org, the Desk portal id and the Bookings workspaces.
2. `python3 seed/zoho/provision.py`: writes data/zoho_provision.json; run log in seed/zoho/.local/run-*.log. Re-runs are
   idempotent (check before create; bulk write upserts on each file's external ID). Read the log, fix, re-run, until
   what is left is only what the API refuses or no API covers.
3. `python3 seed/zoho/verify.py`: counts per object (whole sets of external IDs), ten people end to end, writes
   seed/zoho/leftovers.md.
4. `python3 scripts/build_site.py`: the operator page gets "done by script, <timestamp>" on finished items; Kajal's
   other steps unchanged. Both check scripts pass.
5. One commit "zoho provisioning F" (no AI attribution trailer), then push: .gitignore, .claude/HANDOFF.md,
   scripts/build_operator.py, docs/admin_operator.html, data/zoho_provision.json, seed/zoho/zoho.py, provision.py,
   verify.py, leftovers.md. Never stage seed/zoho/.env or seed/zoho/.local/.

## What the Zoho docs changed in the brief (already told to spiff)
- Left, no API: all 15 saved views (CRM v8 has only Get Custom View Metadata and Change Sort Order; Desk lists
  views only), the Desk SLA, Finance read only (a profile in Zoho, not a role).
- Left, the API may send: Campaigns lists S0, S0w, S1, S2 (listsubscribe mails a confirmation; the two bulk calls
  document their list key "to send a subscription mail"; email only) and Bookings staff and appointments.
- Calls are not a bulk write module: the records API upsert, each call linked to its contact (Who_Id).
- Created_Time is tested on the run's first record insert and logged in data/zoho_provision.json; docs suggest it
  is read-only.

## Watch on the first live run (docs silent or ambiguous)
- The check reports the CRM edition as "free" under the zohooneenterprise trial. If a create call (custom module,
  field, role, bulk write) is refused on edition grounds, stop and say so: the trial may need CRM Enterprise
  switched on in the Zoho One admin panel.
- Leads Company may be layout-mandatory: MANDATORY_NOT_FOUND-Company in the bulk result.
- Deals Pipeline is filled only if Zoho marks it mandatory and the org has one pipeline.
- Bulk write: header row = field API names (auto-map); date-times as 'YYYY-MM-DD HH:MM:SS' in the CRM user's zone.
- Call_Duration is sent as HH:mm ("00:45"); check the record reads 2700 seconds.
- Desk: custom field type "DateTime"; Category values are PATCHed only after the current list was read.
- Bookings createservice: a form-data field "data" holding JSON; Bookings reports refusals inside a 200.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends.
- No regex or phrase rules; stdlib only; ASCII; tokens and secrets never printed or committed.
- Kajal's remaining operator steps stay unchanged; only items the script finished get the "done by script" line.
