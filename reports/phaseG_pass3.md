# Phase G, pass 3: the CRM saved views (28 Sep 2026)

Source: PLAN_zoho_live_v01.md, G3 (11 CRM views; the count corrected in G0). Done in Chrome on Kajal's signed-in
session at crm.zoho.in, one browser tab; verified by API after every save (GET /settings/custom_views/{id}). Nothing
was sent. G1 and G2 did not run first: adding users in the Zoho One admin panel is an account creation, which the
browser rules hand back to a person (see the G0 report reply); the views need no users.

Screen path for every view: CRM, the module's tab, the view picker, New Custom View (the page
/tab/<module>/custom-views/create), name, criteria rows, the column picker (search the column, hover it, click its
plus icon), Save. The saved view opens with its record count. Zoho saved every view as public (access_type public in
the API answer); the create page shows no sharing control, so "shared with all users" needed no step.

## The 11 views, as built and as read back by API

| module | view | criteria (API answer) | columns | records |
|---|---|---|---|---|
| Deals | Paid by SKU, this week and last | Start is Previous Week or Start is Current Week | Deal Name, Amount, Stage, Closing Date, Start, SKU | 12 |
| Deals | Payment reconciliation | none (all deals) | Deal Name, Amount, Stage, Closing Date, Razorpay Customer Id, Razorpay Subscription or Txn Id, Start, Status, Next Billing | 206 |
| Deals | GST split | none (all deals) | Deal Name, Amount, Stage, Closing Date, GST Type, SKU, Period, Start | 206 |
| Deals | Refunds | Refund Requested is selected | Deal Name, Amount, Stage, Closing Date, Refund Status, Cancel Reason, SKU, Start | 6 |
| Contacts | DIFM prospects to call | DIFM Prospect Flag is manual or rule | First Name, Last Name, Phone, Email, Tier, Adviser Owner, Last Call | 20 |
| Contacts | Same adviser offer | Last Adviser is not empty | First Name, Last Name, Phone, Email, Last Adviser, Adviser Continuity, Adviser Owner | 50 |
| Contacts | Opt-in and DND | WhatsApp Opt-in is selected and DND is not selected | First Name, Last Name, Phone, Email, Journey Stage, WhatsApp Opt-in, DND | 1203 |
| Tasks | Call centre today | (Status isn't Completed and State ID is S2b, S19, S20) and (Due is Till Yesterday or Due is Today) | Subject, State ID, Missing Fields, Tier | 8 |
| Tasks | Call centre outcomes | Outcome isn't pending and State ID is S2b, S19, S20 | Subject, State ID, Outcome | 94 |
| App Events | RPQ refresh due | Event is rpq_due | App Event Name, Contact External ID, At, Props | 6 |
| A la carte | A la carte receipts | none (all purchases) | A la carte Name, Date, Amount, Receipt, Call Id | 9 |

Record counts from `python3 seed/zoho/live.py` (the records API paged by cvid), 28 Sep 2026, 15:37 IST. The first
four default columns of Deals and Contacts (Deal Name, Amount, Stage, Closing Date; First Name, Last Name, Phone,
Email) stay; the leftover's "show" list was added after them.

## Where the build differs from the leftover text, and why

- Paid by SKU, this week and last: the leftover says "Start in the last 14 days"; Zoho's date conditions offer
  Previous Week and Current Week and no rolling 14-day window (Age in Days is a single value), and the seat question
  reads "this week against last week", so the view takes the two calendar weeks (Zoho, 28 Sep 2026). The grouping by
  SKU and by week is a dashboard notion and moves to the Principal officer dashboard (G4).
- Call centre today: "Status is open" is written as Status isn't Completed (the seed writes Not Started and
  Completed; isn't Completed keeps any open status Zoho adds later). "Due is today or earlier" is Due is Today or
  Due is Till Yesterday, two rows joined by OR in the criteria pattern. The field is the seed's own Due (a datetime
  custom field that carries the export's dates); Zoho's standard Due Date is empty on every task.
- Call centre outcomes: the grouping by Outcome moves to the Call centre dashboard (G4); the view shows State ID and
  Outcome so the list reads without the grouping.
- GST split: the grouping by GST Type moves to the Finance dashboard (G4); the view shows GST Type, SKU, Period, Start.
- Opt-in and DND shows WhatsApp Opt-in and DND beside Journey Stage, so the list shows why a row is in it.
- Tasks views have no column picker on the create page (Zoho, 28 Sep 2026): the columns were set afterwards on the
  saved view's list, the column icon at the right of the header, Manage Columns, tick, Save. The API reads them back
  on the view.
- The column picker's plus icon appears on hover and took the mouse click only some of the time; the columns were
  added by firing the page's own add control for the column (a pointer event sequence on the row's add element), and
  every column was read back by API before the save. Kajal repeats the step by hand: search the column, hover the
  row, click the plus.

## Verification

- API, every view: access public, criteria and columns as in the table (the fields list of the two Tasks views was
  read after the Manage Columns step). Two views saved short of a column on the first pass (Payment reconciliation
  without Next Billing, GST split without Start); both were opened again (/custom-views/{id}/edit), the column added,
  saved, and read back.
- live.py rows: views Deals 4 of 4, Contacts 3 of 3, Tasks 2 of 2, App Events 1 of 1, A la carte 1 of 1.
- data/zoho_live.json items: views/call-centre, views/marketing and views/finance are "done in Zoho"; views/
  principal-officer and views/compliance are "partly done" until their Desk views exist (G5); views/support is all
  Desk (G5).

## What is left

- G5 builds the four Desk views and the SLA; G4 builds the dashboards on these views.
- G1 (users), G2 (ownership), G7 (Bookings staff) and G8 wait as the G0 report reply says.
