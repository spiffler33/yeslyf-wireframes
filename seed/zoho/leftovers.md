# Zoho provisioning leftovers (phase F)

Written by seed/zoho/verify.py on 28 Sep 2026, 13:40 IST from data/zoho_provision.json (provision run of 28 Sep 2026, 13:39 IST) and the verify counts, run-3000 exports. Each row is a step the API refused or that no API covers, with the manual fallback. Operator page items that are neither marked done by script nor listed here were never part of this phase; they stay as they were.

Created_Time on the first record insert (Leads P00010, sent 2026-03-27T00:00:00+05:30): ignored, Zoho stamped 2026-09-28T13:09:35+05:30.

## Left for a manual step (24)

| Operator item | What | Why | Manual fallback |
|---|---|---|---|
| roles/finance | make the Finance seat read only | read only is a profile in Zoho, not a role; the role exists | When a Finance user is added, give them a profile with view permissions only (clone Standard, untick create, edit and delete). |
| views/principal-officer | saved view Paid by SKU, this week and last (Deals) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Deals: Start in the last 14 days; group by SKU and by week of Start. |
| views/principal-officer | saved view DIFM prospects to call (Contacts) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Contacts: DIFM Prospect Flag is rule or manual; show Phone, Tier, Adviser Owner, Last Call. |
| views/principal-officer | saved view Grievances past SLA (Tickets) | no create endpoint: the Desk API lists views but has no create call | Create it by hand on Tickets: Category is grievance; Status is open; SLA Due is before now. |
| views/call-centre | saved view Call centre today (Tasks) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Tasks: Status is open; State ID is S2b, S19 or S20; Due is today or earlier; show State ID, Missing Fields, Tier. |
| views/call-centre | saved view Call centre outcomes (Tasks) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Tasks: Outcome is not pending; State ID is S2b, S19 or S20; group by Outcome. |
| views/call-centre | saved view Same adviser offer (Contacts) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Contacts: Last Adviser is not empty; show Last Adviser, Adviser Continuity, Adviser Owner. |
| views/marketing | saved view Opt-in and DND (Contacts) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Contacts: WhatsApp Opt-in is true; DND is false; show Journey Stage. |
| views/compliance | saved view Grievance register (Tickets) | no create endpoint: the Desk API lists views but has no create call | Create it by hand on Tickets: Category is grievance; show Created At, Subject, Status, Resolved At, SCORES Ref; export. |
| views/compliance | saved view RPQ refresh due (App Events) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on App Events: Event is rpq_due; show Contact External ID, At, Props (due_date). |
| views/support | saved view Open tickets with context (Tickets) | no create endpoint: the Desk API lists views but has no create call | Create it by hand on Tickets: Status is open; show Category, Subject, Description, SLA Due. |
| views/support | saved view Past SLA (Tickets) | no create endpoint: the Desk API lists views but has no create call | Create it by hand on Tickets: Status is open; SLA Due is before now; sort by SLA Due. |
| views/finance | saved view Payment reconciliation (Deals) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Deals: all deals; show Razorpay Customer Id, Razorpay Subscription or Txn Id, Status, Start, Next Billing. |
| views/finance | saved view GST split (Deals) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Deals: group by GST Type; show SKU, Period, Start. |
| views/finance | saved view Refunds (Deals) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on Deals: Refund Requested is true; show Refund Status, Cancel Reason, SKU, Start. |
| views/finance | saved view A la carte receipts (A la carte) | no create endpoint: CRM API v8 has Get Custom View Metadata and Change Sort Order only | Create it by hand on A la carte: all purchases; show Date, Amount, Receipt, Call Id. |
| import/calls | 23 of 84 Calls rows not written | DEPENDENT_FIELD_MISSING-Call_Duration (cancelled): 1 rows; DEPENDENT_FIELD_MISSING-Call_Duration (no_show): 14 rows; INVALID_DATA-Call_Start_Time (booked): 8 rows | to be decided: how a no-show, a cancelled call and a booked slot already past are logged in Zoho Calls; then re-run (upsert). |
| desk/sla | SLA of one business day | no create endpoint: the Desk API lists SLAs but cannot create or edit one | Set it by hand: Setup, SLAs, one business day. |
| import/campaigns-s0 | the S0 list, 205 of 1170 rows with an email | not called: every Campaigns call that adds contacts can send (listsubscribe mails a confirmation to lists with a signup form; addlistandcontacts and addlistsubscribersinbulk document their list key as 'to send a subscription mail'), and they take email addresses only | Import campaigns/S0.csv by hand into a list named S0 (Contacts, Import, from file); map Phone, First Name, Stage, Tier and WhatsApp Opt-in; rows without an email are skipped by Campaigns. |
| import/campaigns-s0w | the S0w list, 230 of 230 rows with an email | not called: every Campaigns call that adds contacts can send (listsubscribe mails a confirmation to lists with a signup form; addlistandcontacts and addlistsubscribersinbulk document their list key as 'to send a subscription mail'), and they take email addresses only | Import campaigns/S0w.csv by hand into a list named S0w (Contacts, Import, from file); map Phone, First Name, Stage, Tier and WhatsApp Opt-in; rows without an email are skipped by Campaigns. |
| import/campaigns-s1 | the S1 list, 131 of 400 rows with an email | not called: every Campaigns call that adds contacts can send (listsubscribe mails a confirmation to lists with a signup form; addlistandcontacts and addlistsubscribersinbulk document their list key as 'to send a subscription mail'), and they take email addresses only | Import campaigns/S1.csv by hand into a list named S1 (Contacts, Import, from file); map Phone, First Name, Stage, Tier and WhatsApp Opt-in; rows without an email are skipped by Campaigns. |
| import/campaigns-s2 | the S2 list, 284 of 990 rows with an email | not called: every Campaigns call that adds contacts can send (listsubscribe mails a confirmation to lists with a signup form; addlistandcontacts and addlistsubscribersinbulk document their list key as 'to send a subscription mail'), and they take email addresses only | Import campaigns/S2.csv by hand into a list named S2 (Contacts, Import, from file); map Phone, First Name, Stage, Tier and WhatsApp Opt-in; rows without an email are skipped by Campaigns. |
| bookings/service | the staff Adviser 01, Adviser 02, Adviser 03, Adviser 04, Adviser 05, Adviser 06 | not called: the add staff API requires an email and does not say whether it sends an invitation; the seed has no staff emails | Add them by hand in Bookings with invitations off, then assign them to Talk to an adviser. |
| bookings/service | a handful of appointments | not called: booking notifications to customer and staff are a workspace setting the book appointment API cannot switch off | Turn off customer and staff notifications in the workspace, then book them by hand. |

## Imported without a column (1)

| Operator item | What | Why | Later |
|---|---|---|---|
| import/deals | column Amount not imported | the Deals field with that label cannot hold this column (the column carries only placeholder values) | Map it once the field can hold the values (for Amount: when prices are set). |

## Missing after the run (1)

| Operator item | What | Manual fallback |
|---|---|---|
| import/calls | 23 Calls rows missing (P00385-C1, P00458-C1, P00458-C2, P00612-C1, P00749-C1) | Re-run provision.py (upsert) once the cause in the rows above is fixed, or import those rows by hand. |

## Counts

| Object | Export | In Zoho | Missing |
|---|---|---|---|
| Leads | 1400 | 1400 | - |
| Contacts | 1640 | 1640 | - |
| Deals | 206 | 206 | - |
| A la carte | 9 | 9 | - |
| Calls | 84 | 61 | P00385-C1, P00458-C1, P00458-C2, P00612-C1, P00749-C1 and 18 more |
| Tasks | 114 | 114 | - |
| App Events | 12464 | 12464 | - |
| Tickets | 73 | 73 | - |
| Campaigns S0 | 205 | 0 | list not imported yet (manual step) |
| Campaigns S0w | 230 | 0 | list not imported yet (manual step) |
| Campaigns S1 | 131 | 0 | list not imported yet (manual step) |
| Campaigns S2 | 284 | 0 | list not imported yet (manual step) |
| Bookings service | 1 | 1 | - |

## Ten people end to end

| Person | Object | Linked rows found | Result |
|---|---|---|---|
| P00194 | Contacts | record ok, tickets 1/1, App Events 54/54, Calls 2/2, Deals 1/1, Tasks 1/1 | ok |
| P02751 | Contacts | record ok, tickets 1/1, A la carte 1/1, App Events 18/18, Calls 1/1, Deals 1/1 | ok |
| P00462 | Contacts | record ok, tickets 1/1, App Events 52/52, Calls 1/1, Deals 1/1, Tasks 1/1 | ok |
| P00306 | Contacts | record ok, tickets 1/1, App Events 51/51, Calls 1/1, Deals 1/1, Tasks 1/1 | ok |
| P00749 | Contacts | record ok, tickets 1/1, App Events 46/46, Calls 0/2, Deals 2/2, Tasks 1/1 | Calls missing: P00749-C1, P00749-C2 |
| P01482 | Contacts | record ok, tickets 1/1, App Events 39/39, Calls 0/1, Deals 1/1, Tasks 1/1 | Calls missing: P01482-C1 |
| P01621 | Contacts | record ok, tickets 1/1, App Events 36/36, Calls 1/1, Deals 1/1, Tasks 1/1 | ok |
| P01374 | Contacts | record ok, tickets 1/1, App Events 35/35, Calls 1/1, Deals 1/1, Tasks 1/1 | ok |
| P00010 | Leads | record ok | ok |
| P00011 | Leads | record ok | ok |
