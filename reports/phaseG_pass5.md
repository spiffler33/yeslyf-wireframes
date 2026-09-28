# Phase G, pass 5: Desk, the SLA and the four ticket views (28 Sep 2026)

Source: PLAN_zoho_live_v01.md, G5. Done in Chrome on Kajal's signed-in session at desk.zoho.in (portal Plan2prosper,
department Plan2prosper, id 277666000000010772); the views verified by API (GET /views?module=tickets, then
GET /tickets?viewId= for the counts). Nothing was sent: the SLA has no escalation action, and Desk's notification
rules were not touched (they were read off in phase F, all off but the four "Mentioning in ..." rules). The agents
part of G5 (Support 01 and Compliance 01 under Setup, Agents) waits for the users of G1.

## The four ticket views

Screen path: Tickets, the view switcher at the top of the list, Add Custom View (the page /tickets/view/new), Name,
Filter Criteria rows, Permissions, Visible To: All Agents, Create. Desk views carry criteria and visibility only;
the list's columns and sort order are the list's own settings, not the view's (Zoho, 28 Sep 2026), so the
leftovers' "show ..." and "sort by ..." parts have no place on a Desk view.

| view | criteria as built | visible to | tickets (API, 15:58 IST) |
|---|---|---|---|
| Grievances past SLA | Category is grievance and Status is OPEN (Escalated, Open) and Is Overdue is true | All Agents | 0 |
| Grievance register | Category is grievance | All Agents | 5 |
| Open tickets with context | Status is OPEN (Escalated, Open) | All Agents | 13 |
| Past SLA | Status is OPEN (Escalated, Open) and Is Overdue is true | All Agents | 1 (Zoho's sample ticket) |

- "Status is open" is Desk's own condition "is OPEN", which covers the Open and Escalated statuses.
- "SLA Due is before now" is Desk's own field "Is Overdue" (true when the ticket's due date has passed). Grievances
  past SLA shows 0 because no seed ticket carries a due date yet (finding 2 of the G0 report); Past SLA shows Zoho's
  sample ticket, which is overdue since 25 Sep 2026.

## The SLA

Screen path: Setup (the gear), Automation, Service Level Agreement(SLA), New SLA. Name "One business day",
description "Resolution due in one business day for every ticket. No escalation action.". When: Ticket Create only
(Ticket Update, Customer Reply, Agent Response, Private Thread and Comment unticked; "Execute only when associated
with an Account" off). Next. Targets, Add Target: no condition (every ticket), Respond Within empty, Resolve Within
1 Days, Operational Hours Calendar Hours, Response Escalation off, Resolution Escalation off, Save. The SLA appears
in the ACTIVE list as the fifth entry, after Zoho's four defaults (Priority based, Gold, Silver, Bronze).

- Operational Hours offered Calendar Hours only: the org has no business hours (Setup, Business Hours is empty), so
  "one business day" is one calendar day until business hours exist. "to be decided: the org's business hours (which
  days, which hours) so the SLA counts business days".
- The four default SLAs stay active above the new one. Desk evaluates SLAs in list order; a ticket that matches
  none of the defaults' conditions falls through to One business day. "to be decided: deactivate the four default
  SLAs so every ticket takes One business day".
- The SLA fires on ticket create; the 12 open seed tickets keep their empty due date (live.py row "tickets with a due
  date" stays at 1, the sample ticket). This settles the G0 question: Desk does not apply a new SLA to tickets that
  already exist. Grievances past SLA and Past SLA fill from the next ticket created.
- No API lists the SLA for this org (the only documented list call is per account, and the seed has no Desk
  accounts); the screenshot of the ACTIVE list is the evidence.

## Verification

- GET /views?module=tickets&departmentId=277666000000010772: 24 views, 4 custom, the four names present.
- GET /tickets?viewId=<id>&limit=100 per view: 0, 5, 13, 1.
- live.py: desk views 4 of 4.
- data/zoho_live.json items: views/principal-officer, views/compliance and views/support now "done in Zoho" (their
  Desk views exist); desk/sla "done in Zoho" with the calendar-hours note.

## What is left

- Agents: Support 01 and Compliance 01 appear under Setup, Agents once the users exist (G1); Support 01 owns the
  tickets after G2.
- The two "to be decided" items above (business hours; the default SLAs).
