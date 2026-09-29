# Phase G, pass 4: the CRM dashboards (28 and 29 Sep 2026)

Source: PLAN_zoho_live_v01.md, G4, and the brief of 28 Sep 2026 (Vatsal: beautiful dashboards, not a KPI per view).
Done in Chrome on Kajal's signed-in session at crm.zoho.in, Analytics, one browser tab; every dashboard was saved,
opened again and read off the screen. Nothing was sent. The numbers below are the rendered tiles; where a G3 view
answers the same question its count is given beside them, and they agree.

Screen path for every dashboard: Analytics, Create Dashboard, name and description, then a component from the left
rail. KPI opens Choose KPI Style (Basic for a plain count, Standard for a count against the previous period), then a
dialog: Component Name, module, measure (Count of), + Criteria filter, Duration, Done. Chart opens Add Chart, Quick
chart, then a dialog: Component Name, module, measure, grouping (a date grouping offers By Day, By Calendar Week, By
Month), a second grouping for a stacked chart, + Criteria filter, the chart type at the top right (Column, Bar,
Donut, Pie, Treemap and more), More options (Sort by, Maximum grouping), Done. Save at the top right. The saved
dashboard opens from the Analytics picker or from Manage Dashboards.

## The 5 dashboards, as built and as rendered

Principal officer (id 1438206000000650349). Description: paid deals this week against last, by SKU, and the DIFM
prospects to call; Grievances past SLA is a Desk view.

| component | type | definition | rendered |
|---|---|---|---|
| DIFM prospects to call | Basic KPI | Contacts, DIFM Prospect Flag is manual or rule | 20 (view 20) |
| Paid deals this week | Standard KPI | Deals, Duration Start is This Week, compared to the previous period | 0, last week 12 |
| Paid deals by week and SKU | column, normal stack | Deals, Start by calendar week, stacked by SKU, Start is Previous Week or Current Week | week 20 to 26 Sep 2026: diwm 9, diy 3 (12; view 12) |
| DIFM prospects by Tier | bar | Contacts, Tier, DIFM Prospect Flag is manual or rule | diy 8, difm 12 (20) |

Call centre (id 1438206000000650361). Description: calls due today or earlier, outcomes of the calls made, and the
same adviser offer; the call list itself is the Tasks view Call centre today.

| component | type | definition | rendered |
|---|---|---|---|
| Call centre today | Basic KPI | Tasks, ((Status isn't Completed and State ID is S2b, S19, S20) and (Due is Till Yesterday or Due is Today)) | 8 (view 8) |
| Same adviser offer | Basic KPI | Contacts, Last Adviser is not empty | 50 (view 50) |
| Call centre outcomes | bar, value descending | Tasks, Outcome, State ID is S2b, S19, S20 | done 94, pending 8 (view 94, which excludes pending) |
| Outcomes by State ID | column, normal stack | Tasks, State ID stacked by Outcome, State ID is S2b, S19, S20 | S2b 26 (23 done, 3 pending), S19 70 (done), S20 6 (1 done, 5 pending) |
| Same adviser offer by Last Adviser | bar, value descending | Contacts, Last Adviser, Last Adviser is not empty | Adviser 04 11, Adviser 05 11, Adviser 01 9, Adviser 03 8, Adviser 06 7, Adviser 02 4 (50) |

Marketing (id 1438206000000650377). Description: who can be messaged on WhatsApp (opted in and not DND), by journey
stage and by source; the stage lists S0, S0w, S1 and S2 are Campaigns lists.

| component | type | definition | rendered |
|---|---|---|---|
| Opted in | Basic KPI | Contacts, WhatsApp Opt-in is selected and DND is not selected | 1203 (view 1203) |
| DND | Basic KPI | Contacts, DND is selected | 139 |
| Opted in by Journey Stage | column, value descending | Contacts, Journey Stage, same criteria as Opted in | S2 745, S0 288, then 27, 19, 16, 11, 9, 9, 7, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 2, 2 |
| Opt-in by Source | column, normal stack | Contacts, Source stacked by WhatsApp Opt-in | community 739, corporate_session 334, web_reveal 255, organic 221, referral 91 (1640), each split true or false |

Compliance (id 1438206000000650386). Description: RPQ refreshes due and the app event trail; the grievance
register is a Desk view.

| component | type | definition | rendered |
|---|---|---|---|
| RPQ refresh due | Basic KPI | App Events, Event is rpq_due | 6 (view 6) |
| RPQ refresh due by month | column | App Events, At by month, Event is rpq_due | August 2026 4, September 2026 2 |
| App events, top 10 types | bar, value descending, maximum grouping 10 | App Events, Event | signed_up 1640, state_enter_S1 1632, data_progress 1375, reveal_seen 1232, state_enter_S2 1232, paywall_viewed 793, plan_updated 376, and three more below the fold |
| App events by month | column | App Events, At by month | July 2025 4, August 58, September 103, October 33, November 13, December 30, January 2026 15, February 13, March 66, April 977, May 1633, June 1721, July 2304, August 2563, September 2931 |

Finance (id 1438206000000650394). Description: payment reconciliation, GST, refunds, a la carte receipts and
mandates; Amount is blank in the seed (prices are Rs ___), so there is no revenue chart until prices exist.

| component | type | definition | rendered |
|---|---|---|---|
| Refunds | Basic KPI | Deals, Refund Requested is selected | 6 (view 6) |
| A la carte receipts | Basic KPI | A la carte, count | 9 (view 9) |
| Payment reconciliation by Status | bar, value descending | Deals, Status | active 177, lapsed 12, failed 6, cancelled 6, pending_mandate 5 (206; view 206) |
| GST split by GST Type | bar, value descending | Deals, GST Type | igst 160, cgst_sgst 43, none 3 (206; view 206) |
| Refunds by Refund Status | bar | Deals, Refund Status, Refund Requested is selected | pending 6 |
| A la carte receipts by month | column | A la carte, Date by month | August 2025 1, May 2026 1, June 2026 2, July 2026 1, August 2026 2, September 2026 2 (9) |
| Mandates by Mandate Status | bar, value descending | Deals, Mandate Status | active 150, none (charged per period) 51, the rest of the 206 below the fold |

Manage Dashboards lists the five names, created by Kajal's login on 28 Sep 2026 (Principal officer) and 29 Sep 2026
(the other four). The site's Zoho page can link them by id: /crm/org60089264369/tab/Dashboards/<id>.

## Where the build differs from the plan and the design in the handoff, and why

- Sharing. No sharing control exists in this org's Analytics: the create page has none, the Dashboard Details
  dialog (pencil) has name and description only, the Manage Dashboards row menu has Rename, Clone and Delete, and the
  three-dot button on a dashboard opens the component gallery. The Manage filter offers Shared with me and Public,
  so a sharing state exists somewhere Zoho did not expose. Every dashboard was created under the admin user.
  To be verified: whether users on the Standard profile see the five dashboards once G1 creates them; the org has
  one user today, so the question cannot be answered yet.
- Principal officer. Paid deals this week is a Standard KPI against the previous week, which is the seat's question;
  it read 0 against last week 12 on Monday 28 Sep because the seed dates no deal after 27 Sep. The week chart carries
  the same 12 as the view (Previous Week or Current Week; Zoho weeks run Sunday to Saturday). The Refunds pending KPI
  in the handoff design went to Finance instead, where the refund question lives.
- Call centre. The two outcome charts include pending, which the view excludes: the seed's only non-pending outcome
  is done, so the chart of the view alone was a single bar. With pending, the same charts show the calls left (8,
  the Call centre today number) against the calls done (94, the view's number). Cause: the brief of 28 Sep 2026.
- Marketing. The Journey Stage chart is sorted by count so the two large stages (S2, S0) lead; the plan's "stage
  lists" are Campaigns lists (G6) and the description says so. Opt-in by Source stacks WhatsApp Opt-in true and
  false per source, a chart the plan did not name; it answers where the opted-in contacts come from.
- Compliance. The plan named the RPQ refresh due KPI; the pass adds RPQ refresh due by month and two audit-trail
  charts (event types, events by month), which are the seat's audit question in the seed. The grievance register
  stays a Desk view (G5) and the description says so.
- Finance. No revenue component (Amount is blank; prices are Rs ___). No donuts: the seed's classes are few and
  unequal, and a bar sorted by value reads them without a legend (the dataviz form rule for a magnitude comparison).
- Editor behaviour learned: the dialogs take 15 to 30 seconds to open, and a click made before they open lands on
  the canvas behind (once on Add Dashboard Filters, which was cancelled); the dialogs sometimes open scrolled to
  their bottom, a wheel scroll up over the dialog fixes it; the editor draws a chart clipped or with one bar until
  the dashboard is saved, and the saved dashboard renders it whole; a picklist value box filters when typed into,
  a text-field value box does not; the criteria pattern is edited by Edit Pattern, typed as "( ( 1 and 2 ) and ( 3
  or 4 ) )", then the tick. Save on the create page keeps the page open and shows Added Successfully; a second Save
  answers "A dashboard with the same name exists".
- API. GET /__apis still answers OAUTH_SCOPE_MISMATCH for this grant (G0), and the v8 docs on Context7 (29 Sep
  2026) list no dashboards endpoint, so the check is by screen only. To be decided: a dashboards row in live.py if
  an Analytics API appears.

## Verification

- Manage Dashboards: five names, Principal officer, Call centre, Marketing, Compliance, Finance.
- Each dashboard was opened after its save and every tile rendered with the numbers in the tables above; the ten
  numbers that a G3 view also answers agree with the view counts of 28 Sep 2026 (20, 12, 8, 50, 94, 1203, 6, 206,
  206, 6, 9).
- data/zoho_live.json items: dashboards/principal-officer, dashboards/call-centre, dashboards/marketing,
  dashboards/compliance, dashboards/finance are "done in Zoho" (phase G4). live.py's rows are unchanged; the
  dashboards are outside its checks.

## What is left

- G1 (users), G2 (ownership), G6 (Campaigns), G7 (Bookings) and G8 wait as the G0 report reply says; G9 closes the
  phase.
- Sharing of the five dashboards: to be verified after G1, from a Standard profile login.
