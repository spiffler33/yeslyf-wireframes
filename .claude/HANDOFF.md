# Handoff - 28 Sep 2026 (phase closed: 14, the Spinach Questions tab and the SQ1 exports)

State: phase 14 is closed and pushed (bfe5a3a to the closure commit on main). SQ1 is answered on the board:
data/questions.json, 231 rows (221 frozen, 7 open, 3 owed); docs/spinach_questions.html is HoA's working view, off the
review link; docs/exports/SQ1_*.xlsx are Spinach's copy, stamped 28 Sep 2026, carrying Vatsal's comments of 28 Sep 2026.
Phase F (Zoho provisioning) closed on 28 Sep 2026 in its own commit ("zoho provisioning F"); its section is below.

## Read first
1. reports/phase14_pass4.md (the export, the cover-note counts) and reports/phase14_pass3.md (the tab and its controls).
2. PLAN.md section 22 (what closed, the limits, what is open).
3. Memory project_state.md (the rules: overrides file, pull before build).

## Verify before coding
- `git status --short`: clean apart from the untracked inputs kept out on purpose (two inputs/meeting/ files,
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
- Phase F landed as its own single commit on 28 Sep 2026; board work and Zoho work stay in separate commits.

---

# Phase F (Zoho provisioning): closed 28 Sep 2026, one commit "zoho provisioning F"

State: the seed is in the Zoho One trial "Plan2prosper" (India datacentre, Kajal's Zoho login; spiff confirmed on
24 Sep 2026 that it is the yeslyf trial, not a live business org). Four idempotent passes of seed/zoho/provision.py on
28 Sep 2026 (13:08 to 13:39 IST; each pass fixed what the one before it surfaced), then seed/zoho/verify.py: 32
operator items done by script, 24 leftovers, every one of them "no API" or "the API may send" or the 23 refused calls.
docs/admin_operator.html carries "done by script, <time>" on the finished items; Kajal's other steps are unchanged.
Setup: seed/zoho/.env (client id and secret) and seed/zoho/.local/token.json (refresh token), both gitignored; the Self
Client sits under Kajal's login at api-console.zoho.in.

## Counts (verify.py, 28 Sep 2026, 13:40 IST)
Leads 1400/1400, Contacts 1640/1640, Deals 206/206, A la carte 9/9, Tasks 114/114, App Events 12464/12464, Tickets
73/73, Calls 61/84. The 23 calls Zoho refused: 14 no-shows and 1 cancellation (a logged call needs a Call_Duration)
and 8 booked slots already past (a scheduled call needs a future Call_Start_Time); "to be decided" in leftovers.md.
Campaigns lists 0 (left for the manual import). Bookings service 'Talk to an adviser', 45 minutes, found. Ten people
end to end: 8 ok, 2 differ only by those refused calls.

## Design calls made during the run (each sits in provision.py with its cause)
- Leads Company is layout-mandatory: every lead carries the placeholder "Individual" (MANDATORY_FILL).
- Deals Account_Name is layout-mandatory: one placeholder Accounts record "Individual" holds all 206 deals, and Deals
  go through the records API upsert (import_records) because a bulk write lookup column needs a find_by mapping.
  Kajal can make Account Name optional on the Deals layout and clear the lookup later; the record is one row.
- Deals Stage: the org has no pipelines (GET settings/pipeline answers 204), so the won stage is read off the Stage
  field's own picklist (forecast_type Closed Won): "Closed Won".
- Labels Zoho refuses (LABEL_MAP; the file column keeps its name): Leads Keyword -> "Keyword Sent" (reserved word);
  Calls Status -> "Slot Status" and Tasks Contact External ID -> "Task Contact External ID" (Tasks, Calls and Events
  share one label namespace); Calls Notes -> the built-in Description field (any label holding "Notes" is refused
  on Calls). Leads City maps to the built-in field labelled "Address - City" (label_index also matches api_name).
- Multi-line fields need "textarea": {"type": "small"} on create. Tasks Status is translated done -> Completed,
  open -> Not Started (VALUE_MAP).
- Calls are not an upsert module ("the given module is not supported for this api"): insert, or update by id for
  rows an earlier run wrote; this org's status field is Outgoing_Call_Status (CALL_STATUS_APIS covers both names).
- Created_Time sent on the first record insert was ignored (Zoho stamped its own time); recorded in
  data/zoho_provision.json.
- Desk: the notification rules were read in Chrome before the run (28 Sep 2026): every contact, department and
  agent rule off except the four "Mentioning in ..." rules, which the script never triggers (no comments, no
  mentions). Category values support, adviser_message, grievance were added (the layout had none). Tickets are
  closed with disableClosureNotification.
- Bookings: the workspace came from adding the Bookings app to the Zoho One org (28 Sep 2026, from Chrome); the
  service was created; staff and appointments are left (those APIs may send).

## Leftovers (seed/zoho/leftovers.md, 24 rows)
15 saved views (no create endpoint), the Desk SLA (no endpoint), Finance read only (a profile, not a role), the 4
Campaigns lists (every adding call may send), Bookings staff and appointments (may send), and the 23 refused calls
(to be decided: how a no-show, a cancelled call and a past booked slot are logged in Zoho Calls).

## Verify (after this commit)
- `git status --short`: clean apart from the untracked inputs kept out on purpose.
- `python3 seed/zoho/zoho.py check`: CRM org Plan2prosper, Desk portal id 60089105539, Bookings workspaces: Plan2prosper.
- `python3 seed/zoho/provision.py --plan`: no network. A re-run of provision.py is idempotent (about 6 minutes) and
  rewrites data/zoho_provision.json; verify.py rewrites seed/zoho/leftovers.md; then build_site.py.
- `python3 scripts/build_site.py`, `python3 scripts/check_phase9.py` 19 PASS, `python3 scripts/check_site.py` 3 PASS.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends.
- No regex or phrase rules; stdlib only; ASCII; tokens and secrets never printed or committed (seed/zoho/.env and
  seed/zoho/.local/ are gitignored).
- Kajal's remaining operator steps stay unchanged; only items the script finished carry the "done by script" line.
- seed/zoho/.local/docs/docs_*.md holds the Zoho doc research (local, gitignored): read the relevant one before
  changing a request shape; the docs rule applies (Context7 first).

Scope line of the Self Client (the console accepted it as is):
ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.bulk.ALL,ZohoFiles.files.ALL,ZohoCRM.org.READ,ZohoCRM.users.READ,ZohoCRM.coql.READ,Desk.basic.READ,Desk.layouts.READ,Desk.layouts.UPDATE,Desk.fields.CREATE,Desk.tickets.ALL,Desk.contacts.READ,Desk.contacts.CREATE,Desk.search.READ,ZohoCampaigns.contact.READ,zohobookings.data.CREATE
