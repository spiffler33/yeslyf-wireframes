# Phase G, pass 0: preflight (28 Sep 2026)

Source: PLAN_zoho_live_v01.md, G0. Started on Vatsal's "go", 28 Sep 2026. Read only: nothing was written to Zoho,
nothing was sent. Cause labels as in the plan ("plan G, 28 Sep 2026" for a provisional call, "Zoho, 28 Sep 2026"
for a fact the org forced).

## What was done

- Preflight. `git status --short` clean apart from the untracked inputs kept out on purpose. `python3 seed/zoho/zoho.py
  check`: CRM org Plan2prosper, type production, edition free, trial zohooneenterprise; Desk portal id 60089105539;
  Bookings workspace Plan2prosper. `python3 seed/zoho/provision.py --plan` ends on the service Talk to an adviser,
  45 minutes. `python3 scripts/build_site.py`, `check_phase9.py` 19 PASS, `check_site.py` 3 PASS.
- seed/zoho/live.py (stdlib, read only): one row per read (object, count now, target after G9, detail); a read the
  grant refuses is a row, never a crash. It writes data/zoho_live.json: "baseline" on the first run only, "counts" on
  every run, "items" (what later phases finish by hand or by API: status, at, how, phase) left untouched. It grows
  into the G9 verifier.
- Docs before each call shape (the docs rule). Local notes from phase F (seed/zoho/.local/docs): users, roles,
  profiles and custom views (docs_crm_setup.md), Desk views (docs_desk.md), getmailinglists, staffs and
  fetchappointment (docs_campaigns_bookings.md). Context7 (Zoho Desk API, Zoho CRM API v8): the Desk SLA list, views,
  tickets list and accounts list; the CRM records list and the v8 API list. Context7 has no Zoho Bookings entry, so
  fetchappointment's encoding came from the official page (form-data, one field "data" holding JSON; from_time and
  to_time as dd-MMM-yyyy HH:mm:ss; per_page up to 100; next_page_available in the answer).

## Baseline (live.py, 28 Sep 2026, 14:47 IST)

| object | now | target after G9 | detail |
|---|---|---|---|
| users | 1 | 11 | the admin user: role CEO, profile Administrator, active |
| roles | 10 | 10 | CEO, Manager, Adviser, Finance, Principal officer, Marketing, Ops, Support, Call centre, Compliance |
| profiles | 2 | 3 | Administrator, Standard; Finance read only not yet |
| views Deals | 0 | 4 | 11 views on the module; missing: Paid by SKU, this week and last; Payment reconciliation; GST split; Refunds |
| views Contacts | 0 | 3 | 10 views on the module; missing: DIFM prospects to call, Same adviser offer, Opt-in and DND |
| views Tasks | 0 | 2 | 17 views on the module; missing: Call centre today, Call centre outcomes |
| views App Events | 0 | 1 | 6 views on the module; missing: RPQ refresh due |
| views A la carte | 0 | 1 | 6 views on the module; missing: A la carte receipts |
| v8 api paths listed | - | - | not read: OAUTH_SCOPE_MISMATCH (see finding 1) |
| calls | 61 | 84 | export rows by status: booked 8, cancelled 1, completed 61, no_show 14 |
| desk views | 0 | 4 | 20 views, 0 custom; missing: Grievances past SLA, Grievance register, Open tickets with context, Past SLA |
| tickets assigned | 1 | 74 | 74 tickets (see finding 2); G2 assigns the 73 seed tickets to Support 01 |
| tickets with a due date | 1 | 13 | 13 open tickets; an SLA sets the due date |
| campaigns S0 | 0 | 205 | no list yet |
| campaigns S0w | 0 | 230 | no list yet |
| campaigns S1 | 0 | 131 | no list yet |
| campaigns S2 | 0 | 284 | no list yet |
| bookings staff on the service | 0 | 6 | 1 staff in the workspace (the admin user); service Talk to an adviser found |
| bookings appointments | 0 | 8 | window 01-Jan-2026 to 31-Dec-2027; the target is the export's booked rows |

## What G0 found

1. The grant (Zoho, 28 Sep 2026). The stored refresh token carries 17 scopes: ZohoCRM.modules.ALL, settings.ALL,
   bulk.ALL, org.READ, users.READ, coql.READ, ZohoFiles.files.ALL, Desk.basic.READ, layouts.READ, layouts.UPDATE,
   fields.CREATE, tickets.ALL, contacts.READ, contacts.CREATE, search.READ, ZohoCampaigns.contact.READ,
   zohobookings.data.CREATE. Every G0 read but one ran on them. What they do not cover:
   - Desk.agents.READ: the agents list (GET /agents). G2 needs Support 01's agent id for the ticket assignee and G5
     checks the agents; without the scope the id is read off the Desk agents page in Chrome instead. "to be decided:
     a wider grant with Desk.agents.READ before G2, or the agent id read in Chrome".
   - Desk.accounts.READ: the only documented SLA list call is per account (GET /accounts/{id}/sla); the seed has no
     Desk accounts, so the call is of no use either way. G5 verifies the SLA by the tickets' due dates and a
     screenshot.
   - The v8 API list (GET /crm/v8/__apis) answered OAUTH_SCOPE_MISMATCH; its docs page names no scope. "to be verified:
     the scope the v8 API list call needs". live.py keeps the read; it becomes a row once a grant covers it. The
     custom view create call stays "not found" on the phase F research (four documented URL guesses, all 404).
2. Tickets (Zoho, 28 Sep 2026). Desk holds 74 tickets: the 73 seed tickets and Zoho's own sample ticket "Here's your
   first ticket." (created 23 Sep 2026 with the portal, channel Email, assigned to the admin user, due date two days
   after creation). The sample ticket stays as it is; the targets count it. The 12 open seed tickets carry no due
   date: the portal's default SLA did not touch tickets created by API. "to be verified: whether Desk applies a new
   SLA to tickets that already exist" (G5 reads the due dates after the SLA is saved).
3. The plan's view count (G0, 28 Sep 2026, counted from seed/zoho/leftovers.md). The leftovers hold 15 saved views:
   11 on CRM modules (Deals 4, Contacts 3, Tasks 2, App Events 1, A la carte 1) and 4 on Desk tickets. The plan said
   12 CRM views (Deals 5, Contacts 4); PLAN_zoho_live_v01.md now says 11 in G-D3, G3 and section 6.
4. Roles and profiles as phase F left them: the 8 seat roles plus Zoho's CEO and Manager; the profiles Administrator
   and Standard. Bookings: one staff in the workspace (the admin user), none on the service, no appointments in the
   window. Campaigns: no lists. Calls 61 of 84, the 23 refused rows as in leftovers.md.

## To be decided before G1 (asked in the phase report reply, recommended answer first)

- to be decided: the homes for what Directus held (admin over app tables, app content and config) and whether
  Metabase's 13 rows move to Zoho Analytics; a separate commit on the Admin + CRM tab, never mixed into phase G.
- to be decided: the provisional calls of plan section 4 (the 23 refused calls logged as Missed; past booked slots
  booked at the same weekday and time in the first future week; marketing and finance built under the admin user).
- to be decided: a wider grant with Desk.agents.READ before G2 (finding 1).

## What is left

G1 to G9 as planned. Nothing in the org changed in this pass.
