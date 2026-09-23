# PLAN: seed people and admin discovery, v0.1

Date: 22 Sep 2026. For Claude Code in the yeslyf-wireframes repo. CLAUDE.md rules apply throughout (ASCII, Rs, first names, a cause on every row, "to be verified: <item>" with no name attached, freeze markers, per-screen comment controls through the Supabase write-back).

Cause labels used in this file:
- "Vatsal, 22 Sep 2026": his call.
- "seed plan, 22 Sep 2026": a provisional call made in the plan; Vatsal vetoes by reply. Silence after the Phase A report is consent.
- "assumption": a number with no data behind it; it shapes the seed and nothing else. No seed ratio ever leaks into product logic (no client-data assumptions until a flywheel exists; Vatsal, 11 Sep 2026).

## 0. Purpose and non-goals

Purpose: make the staff side of yeslyf visible with realistic synthetic people so the team can sit in each operator seat, ask its real questions, and find what the built admin tool, the bought CRM, the database and the app's event feed must contain. The gaps become the developer brief: tracker W12 (admin panel brief), W13 (CRM plan), W26 (lead stages and profile fulfilment), integrations I13 (journey and analytics tool) and I15 (runtime config store).

Non-goals in round one (Vatsal, 22 Sep 2026): no API calls to any vendor, no Zoho Flow, no webhooks, no Razorpay test mode, no Postgres, no Metabase, no messaging channel. Everything is static files plus static board pages. Wiring is Spinach's job once the brief exists.

Tooling: Python 3, standard library only, no network, deterministic random with seed 20260922. No external data services.

## 1. Inputs to read first

| input | what it gives | where |
|---|---|---|
| SCREENS data behind wireframes_v02.html (194 screens) | spec.fields per screen with gate, source, precision, forward tag; events per screen; branches; states | data/screens_v02.json or the embedded var, per CLAUDE.md |
| STATES data (27 states) | ladder, escalation by tier, exit rules, crm_task fields, copy slots | data/v02/states.json |
| admin_crm.json | stack, placement rows, contact and deal fields (v0.1 and v0.2), events app to CRM, inbound, compliance records, decisions D1 to D13, CRM backlog | data/admin_crm.json |
| integrations rows I00 to I24 | vendors, screens per vendor, final or open | the Integrations page data |
| tracker rows W07, W12, W13, W23, W26 | owed items this work lands at | the Tracker page data |
| plan_v2.md section 6, appendix B (gate list), C (capture ladders), D (events) | rules the generator must respect | inputs/ |
| the FP React | the exact fields it reads (mirrors the G03 to G14 read rows) | inputs/ |

Do not read the M-series backend docx files from the project; v0.2 supersedes them where they conflict (the FP React supersedes M4).

## 2. Deliverables

| id | deliverable | where | phase |
|---|---|---|---|
| D1 | generator config: counts, floors, ratios, archetypes, band placeholders, anchor date, seed | seed/config.json | A |
| D2 | canonical seed, two runs: run-500 and run-3000 | data/seed/run-500/, data/seed/run-3000/ | A |
| D3 | coverage and validation report per run | data/seed/<run>/report.md | A |
| D4 | exports: Zoho CSVs, Desk CSV, Campaigns lists, landing-sheet CSV, fixtures bundle for Spinach, Mixpanel JSONL | data/seed/<run>/exports/ | B |
| D5 | operator checklist page for the Zoho afternoon, with checkboxes writing to board_entries | docs/admin_operator.html | B |
| D6 | Admin wireframes tab, screens M02 to M14 over the seed | docs/admin_wireframes.html | C |
| D7 | seats page: eight seats, questions, surface, answered or gap | docs/admin_seats.html | D |
| D8 | brief skeleton: tables T1 to T6 pre-filled from data, gap rows appended from D7 | docs/admin_brief.html | D |
| D9 | nav on every page, changelog rows, tracker W12 and W13 lands_at links | all pages | E |

## 3. Composition of the people

Two runs from one config (Vatsal, 22 Sep 2026: N is a config value, both runs always produced).

| layer | run-3000 | run-500 | Zoho object | cause |
|---|---|---|---|---|
| Leads never OTP'd (S0 community, corporate session, web reveal S0w, organic, referral) | 1,400 | 230 | Leads | assumption |
| S1 signed up, no reveal | 400 | 70 | Contacts | assumption |
| S2 reveal seen, not paid, spread across the ladder days 1, 3, 7, 21, 82 and beyond | 990 | 140 | Contacts | assumption |
| S2b checkout started, eSign incomplete | 25 | 5 | Contacts | assumption |
| S2c eSign done, not paid | 15 | 5 | Contacts | assumption |
| Paid, all post-paid states | 210 | 50 | Contacts + Deals | assumption; floors below |
| total | 3,040 | 500 | | |

Lead source split (assumption): community 45%, corporate session 20%, web reveal 15%, organic 15%, referral 5%.

Paid states, run-3000, dwell-weighted with a floor of 6 (assumption): S3 12, S4 22, S5 8, S6 8, S7 8, S8 16, S9 32, S10 10, S11 8, S12 6, S13 8, S14 8, S15 6, S17 6, S18 6, S19 8, S20 6, S21 8, S22 6, S23 6, S24 6, S25 6. S16 is carried as a flag on about 30% of paid people (manual or CAS path, AA not connected). run-500 uses the same weights with a floor of 2.

Floor rule: when the funnel ratios leave a state below its floor, top it up and set is_topup true on those people. Every chart on the KPI page shows the topup count in its footer so no ratio is read as real.

Tier mix among paid (assumption): DIWM 55%, DIY 35%, DIFM 10%. DIFM people are provisioned from the admin side (M12), never self-serve: no S1 or S2 history, source corporate session or referral, tier difm from creation, state S14. Harish is the relationship owner for DIFM; call-centre advisers own everyone else by round robin.

Source path among paid (assumption): AA connected 50%, CAS upload 20%, manual 30%. Inside the AA half: 25 people AA partial (some FIPs failed, A09), 15 people AA failed entirely and fell back to manual.

Subscription period (assumption): monthly 60%, quarterly 40%. Payment method: UPI 75%, netbanking 25%. GST type by state of residence: cgst_sgst for the org's own state, igst otherwise, none for a coupon that zeroes the invoice on 2% of deals; to be verified: the GST split rule (brief K1).

## 4. Time model

Anchor date is a config parameter and defaults to the run date; every date in the seed is relative to it, so a regeneration on demo morning makes the org look live.

| moment | rule | cause |
|---|---|---|
| lead created | uniformly across the 180 days before the anchor, weighted by a ramp rising from 0.5x to 1.5x of the weekly mean | assumption |
| OTP verified | 0 to 14 days after the lead, median 2 | assumption |
| reveal seen | 0 to 3 days after OTP, median same day | assumption |
| paid | 0 to 60 days after the reveal with mass on the ladder days (1, 3, 7, 21) | assumption |
| data steps | 1 to 21 days after paid; D screens saved in the spine order with gaps | assumption |
| plan built | same day as D10, minutes later | plan_v2 (G01 builds instantly) |
| plan read | 0 to 10 days after built | assumption |
| first action done | 2 to 30 days after read; later actions 1 to 6 weeks apart | assumption |
| call booked | 3 to 20 days after built; second call for DIWM only | assumption |
| quarterly review | 90 days after built; Q01 generated, opened or ignored (S22) | N01 |
| renewal | per period; 5% of renewals fail (S12), of which half recover and half lapse (S13) | assumption |
| refund requested | within 14 days of paying (S24) | assumption |
| consent expiry | AA consents expire 90 days after connect; S15 when past due | assumption; to be verified: consent duration in the Finvu template |
| deletion requested | any time after paid (S25) | assumption |

Every timestamp must be consistent with the N01 exit rules: no event before signed_up, no plan_read before plan_built, state_enter rows in the order the exits allow.

## 5. Archetypes

Eight archetypes inside the confirmed ICP (28 to 40, salaried, Tier 1 primary, Tier 2 secondary), plus a 5% tail aged 24 to 45. Each person is one archetype with noise on every parameter. The Rajesh and Deepika personas are retired (seed plan, 22 Sep 2026).

| id | who | city | household income Rs | signature |
|---|---|---|---|---|
| A1 | single, 28 | Bengaluru | 12 L | renting, first SIPs, no cover |
| A2 | single, 31 | Pune | 18 L | education loan closing, stocks dabbler |
| A3 | couple no kids, 30 and 29 | Mumbai | 30 L | dual income, home loan hunting |
| A4 | couple, one child aged 2, 34 and 33 | Gurugram | 40 L | home loan EMI, term cover missing |
| A5 | couple, two children 7 and 4, 38 and 36 | Hyderabad | 50 L | two loans, ULIPs, employer-only health |
| A6 | single parent, 36 | Chennai | 22 L | supports parents, health cover employer only |
| A7 | joint family, 33 | Ahmedabad (Tier 2) | 20 L | gold heavy, informal loans, PPF |
| A8 | senior IC, 40 | Delhi | 75 L | stocks and ESOP heavy, over the DIFM threshold |

Names: synthetic, region-diverse by city, drawn from lists committed in the repo. Aspiration (R07) weighted by archetype. Journey feel (R06) random.

## 6. Bands, precision and coherence

Bands: placeholder ladders per field in config, labelled placeholder (income, corpus, savings rate, take_home, total_outgoings, each asset class, EMI, covers). The real M2 tables 9.1 to 9.5 drop in when they arrive (tracker: band values and validation ranges still to come). A band tap stores the midpoint tagged approx; a typed number is exact.

Tri-state per field (rule 6): value, explicit none, or not sure. Not sure is never stored as zero. A D02 or D04 type left unticked is explicit none.

Source and precision by path:
- AA path: bank_and_deposits, mutual_funds, stocks, nps, current_sip AA-fed and exact; epf, ppf, gold, property, ulip, other_assets manual.
- CAS path: mutual_funds and stocks exact from CAS at ISIN level; the rest manual.
- Manual path: a mix of exact, approx and unknown; the sharpen loop (G03 to G14) later converts some approx to exact for 40 people.
- Every paid person with plan_built has no unknown gate field: D13 rows exist for the fields they resolved as a range before the build. S4 and S5 people may still carry unknowns.

Coherence rules (assumption, every rule a config line):
- corpus between 0.3x and 3x annual income, scaled by years since 22.
- total_emi at most 45% of take_home; total_outgoings between 40% and 85% of take_home; current_sip at most the surplus.
- term cover missing for 40% of people with dependants; health employer-only for 50%; home loan on 35% of couples; ULIP on 20%; gold heavier in Tier 2.
- DIFM prospect flag when total investable assets from D02 exceed the threshold; placeholder Rs 1 Cr (assumption; the board reads Rs ___), plus a manual flag set after a call on 5 people.
- Goals: at least one per person or explicit none; a goal with unknown cost goes to the yes_list and out of the SIP maths.
- RPQ: eight answers, score, risk_band from the score; no fallback.

## 7. State derivation

State is computed from stored flags on every open, never stored as a label (N01). The generator writes the flags; a resolver derives the single state and the state_enter history from them. Predicates come from the states.json entry and exit rules.

Precedence when more than one predicate holds (assumption; to be confirmed against N01): S25, S24, S12, S13, S14, S11, S23, S22, S15, S20, S7, S19, S18, S17, S5, S4, S3, S21, S10, S9, S8, S6, S2c, S2b, S2, S1. S16 rides as a flag beside the core state and surfaces at the review quarter.

Report every person for whom more than one predicate holds, listed by state pair with counts. That list is the N01 precedence gap list; it goes into report.md and onto the seats page as gaps for the principal officer seat.

## 8. Event log

For every person, an events.jsonl consistent with the path and the dates:
- <screen>_view for every screen visited, in spine order, with hesitation_45 / 90 / 120 on 15% of number screens; set, skip, band_tapped, exact_entered and the ladder events per D screen as listed in the screen's events.
- The CRM events from admin_crm.json: signed_up, reveal_seen, paywall_viewed, esign_done, paid, aa_connected / aa_declined / aa_failed, data_progress, data_complete, plan_built, plan_read, pdf_downloaded, call_booked / call_completed / no_show, action_done, plan_updated, update_accepted, review_due / review_done, payment_failed / payment_recovered, cancelled / lapsed / resubscribed, rpq_due / agreement_due, ticket_created, with the payload fields the spec lists.
- state_enter per state change.
- nudge_sent per ladder step that fell due before the anchor, respecting the O03 chosen time rule and the one-per-week cap from day 14 after payment (N01 rules), with channel and copy slot ID.

Expected volume for run-3000: about 150,000 rows. Fine as JSONL.

## 9. Ugly cases, deliberately present (run-3000; run-500 scales by a third, minimum 1)

| case | count | surfaces on |
|---|---|---|
| engine failure: data complete, plan not built | 3 | M06, M13 |
| AA partial | 25 | M09, A09 |
| AA failed to manual | 15 | M09 |
| unknown ISINs in holdings | 12 holdings | M06, L04 |
| plausibility flags (D02 total against R04 band) | 20 | M07 |
| second no-show | 6 | tasks S20 |
| refund requested | 6 | tasks S24, M06 |
| deletion requested | 6 | tasks S25, M06, M11 |
| grievance tickets with SCORES ref | 5 | Desk |
| payment failed in grace | 6 | Deals |
| lapsed | 8 | Deals |
| DIFM prospects over threshold, across tiers | 15 | M02 filter, Zoho view |
| sharpen loop used | 40 | M03 |
| life event Q06 reopening screens | 8 | M03 timeline |
| consent expired | 6 | M09 |

## 10. PII and safety

- Names synthetic. Phones synthetic 10-digit numbers per config; India has no reserved fictional mobile range (assumption), so safety is the never-connect list on the operator page, not the numbers.
- Emails first.last.NNN@example.com; the domain is reserved and cannot deliver.
- PAN synthetic in format only; present in the canonical seed and the fixtures bundle, never in any Zoho export.
- Zoho exports carry bands and dates only: no exact rupee values, no PAN, no holdings.
- No real community member, no real client, no staff record beyond Harish as the DIFM owner. Advisers are Adviser 01 to 06, Ops 01, Support 01, Compliance 01.
- The minimisation scan (section 12) fails the build on any breach.

## 11. Canonical seed tables (D2)

One JSON file per table under data/seed/<run>/, keyed by person_id. This is also the proposal of what the app must store and expose (T1); the physical schema is Gaurav's and Spinach's.

| table | key fields |
|---|---|
| people | person_id, kind (lead, user), first_name, last_name, phone, email, city, city_tier, age, age_band, source, whatsapp_optin, dnd, created_at, otp_verified_at, lead_stage (lead, verified_lead), archetype, is_topup, tier, sku, period, subscription_status, adviser_id, state_id, state_entered_at, progress_pct (endowed 20 at OTP), profile_fulfilment_pct, aa_status, consent_valid_till, source_completeness, sharpen_count, last_manual_update, difm_prospect_flag, adviser_continuity, last_adviser, key dates (signed_up, reveal_seen, paid, data_complete, plan_built, plan_read, last_call, next_review, renewal_due, last_activity), mirrors (onboarding_pct, kyc_status, aa_status, fp_status, ip_status, actions_done, actions_total) |
| households, members | household_id, household_type (R02), members (relation, name, age, earns, lives_with_you), has_dependants, partner_earns, pets |
| reveal | income_band, income_exact, corpus_band, corpus_exact, savings_rate_band, journey_feel, aspiration, path_now_band, path_yes_band, reveal_seen_at |
| financial_records | field (the spine names from the SCREENS field list), value, value_kind (exact, band, none, not_sure), band_id, source (aa, cas, manual, default_accepted, derived), precision (exact, approx, unknown), locked, captured_at, screen_id |
| loans | type, emi, outstanding, years_left, rate |
| covers | term_status, term_sum_assured, term_premium, term_cover_until_age, health_type, health_sum_insured, health_floater, health_premium, other_policies |
| goals | name, year, cost_today, cost_kind, priority, yes_list |
| rpq | answers (8), score, risk_band, taken_at, questionnaire_version |
| holdings | isin, name, units, value, source (aa, cas), unknown_isin flag |
| aa_consents | consent_handle, status (active, declined, expired, failed, not_connected), institutions_ok, institutions_failed, consent_expiry, fetched_at |
| cas_uploads | requested_at, cas_source, reminder_count, uploaded_at, parsed_at |
| plan_versions | plan_version, assumptions_version, instrument_set_version, built_at, built_on (full, partial), band_count, read_at, pdf_downloaded_at, reason (initial, sharpen, update, publish, review, life_event), accepted_at, summary stub (emergency_months, monthly_surplus, sip_total, cover_gap) labelled stub, not the engine |
| actions | action_id, type, amount, due, channel (in_app_mf, smallcase, outside), status (open, done, verified), done_at |
| subscriptions | deal_id, sku, period, amount, gst_type, payment_method, coupon, razorpay_customer_id, razorpay_subscription_id or txn_id, mandate_status, start, next_billing, status (active, pending_mandate, failed, cancelled, lapsed), grace_until, retry_count, calls_included_per_period, calls_used, cancel_reason, refund_requested, refund_status |
| payments | payment_id, deal_id, amount, gst breakup, status, paid_at, invoice_no |
| a_la_carte | purchase_id, date, amount, receipt, call_id |
| calls | call_id, adviser_id, booked_at, slot, topic, note, status (booked, completed, no_show, cancelled), notes, input_changes, recording_ref (null; to be verified: recording consent and retention), same_adviser_requested |
| tickets | ticket_id, category (support, adviser_message, grievance), subject, description, created_at, sla_due, status, resolved_at, scores_ref |
| ops_queue | item_id, type (unknown_isin, data_quality, aa_failure, refund_request, reassignment, difm_provisioning, deletion_request, engine_failure), created_at, owner, status |
| integration_events | vendor (finvu, cams_kra, protean, razorpay, bse_star, smallcase, gupshup, wati, fcm, ses, accord, engine), call, outcome (ok, failed, timeout), latency_ms, at |
| tasks | task_id, state_id, fields per states.json crm_task (tier, days_unsigned, missing_fields, last_screen, minutes_left, call_topic, no_show_count, payment_reference, cancel_reason, period_unexpired, records_retained, requested_at), assignee, due, status |
| nudges_sent | slot, channel, sent_at, delivered, opened, clicked, cap_check |
| events | person_id, event, screen_id, at, props (JSONL) |
| staff | adviser and ops records, roles |
| config | sku_cards (P01), copy_slots (every N-* and W-* slot from SCREENS and STATES with placeholder text), feature_flags, calls_included matrix, bands (placeholder), difm_threshold |

## 12. Exports (D4) and the minimisation scan

Every Zoho file: UTF-8 CSV, header row with the field labels the operator page tells Kajal to create, one external ID column per object so re-imports update instead of duplicate.

| file | columns |
|---|---|
| zoho/leads.csv | Lead External ID, First Name, Last Name, Phone, Email, City, Lead Source, Lead Stage (lead, verified lead: W26), WhatsApp Opt-in, DND, Age Band, Top Concern, Keyword (PLAN, ALPHA), Community Joined, Created Date, Is Seed Topup |
| zoho/contacts.csv | Contact External ID, First Name, Last Name, Phone (key), Email, City, Age Band, Source, WhatsApp Opt-in, DND, Journey Stage (picklist S0, S0w, S1 to S25 with S2b and S2c), Tier, SKU, Subscription Status, Adviser Owner, Income Band, Corpus Band, Savings Band, Aspiration, the ten key dates, the seven mirrors, AA Status, Consent Valid Till, Source Completeness, Sharpen Count, Last Manual Update, DIFM Prospect Flag, Adviser Continuity, Last Adviser, Profile Fulfilment %, Admin Link (deep link to M03 for this person), Is Seed Topup |
| zoho/deals.csv | Deal External ID, Contact External ID, Deal Name, SKU, Period, Amount, GST Type, Payment Method, Coupon, Razorpay Customer Id, Razorpay Subscription or Txn Id, Mandate Status, Start, Next Billing, Status, Grace Until, Retry Count, Calls Included Per Period, Calls Used, Cancel Reason, Refund Requested, Refund Status |
| zoho/a_la_carte.csv | Purchase External ID, Contact External ID, Date, Amount, Receipt, Call Id |
| zoho/calls.csv | Call External ID, Contact External ID, Adviser, Booked At, Slot, Topic, Status, Notes, Input Changes |
| zoho/tasks.csv | Task External ID, Contact External ID, Subject (state ID plus primary action), State ID, Tier, Missing Fields, Last Screen, Minutes Left, Call Topic, No-show Count, Payment Reference, Cancel Reason, Period Unexpired, Records Retained, Requested At, Assignee, Due, Status |
| zoho/app_events.csv (custom module App Events) | Event External ID, Contact External ID, Event, Screen, At, Props; CRM events and state_enter only, not screen views, so the module stays readable (about 20,000 rows for run-3000) |
| desk/tickets.csv | Ticket External ID, Contact Email, Contact Phone, Category, Subject, Description (carries stage, tier, last screen, that person's last integration failure), Created At, SLA Due, Status, Resolved At, SCORES Ref |
| campaigns/<stage>.csv | Email, Phone, First Name, Stage, Tier, WhatsApp Opt-in; one file per journey stage |
| landing/landing_sheet.csv | Timestamp, Email, Top Money Concern, Keyword, Source, Community Joined, Resource Sent; shaped like the yeslifers.com Google Sheet; to be verified: the sheet's current column names |
| fixtures/ | the canonical JSON bundle plus README.md listing tables, keys and joins, for Spinach's dev and staging databases |
| mixpanel/events.jsonl, profiles.jsonl | event, distinct_id, time (unix seconds), properties (screen_id, section, tier, state, source_path, is_topup); round two, produced now, imported later |

Minimisation scan: the build fails if any file under zoho/, desk/, campaigns/ or landing/ contains a PAN pattern, a rupee value that is not a band label, a holding, or an email outside example.com.

## 13. Operator page (D5): the Zoho afternoon

A page like the tracker, checkboxes writing to board_entries, in this order.

1. Org: a Zoho One trial under hey@yeslifers.com, India datacentre (zoho.in). to be verified: whether the trial needs a card; whether trial orgs cap record counts below 3,040 plus deals and events; whether Created Time can be mapped on CSV import (if not, the custom key-date fields carry the timeline and the audit stamp reads import day). If HoA has already bought Zoho One, a second org is the sandbox; the live org is never used.
2. Never-connect list: no WhatsApp (WATI, I11), no SMS, no email sending domain, no Desk mail channel, no Campaigns sender verification, no Bookings calendar sync. Campaigns lists are imported and never sent.
3. Custom fields per object, generated from the CSV headers with types and picklist values.
4. Picklists: Journey Stage, Tier, SKU, Subscription Status, Source, Lead Stage, AA Status, Task State ID.
5. Custom module App Events.
6. Roles: Principal officer, Adviser, Call centre, Ops, Marketing, Compliance, Support, Finance (read only). One principle: advisers see their own people, ops sees records, the principal officer sees everything.
7. Desk: one department, categories support / adviser message / grievance, SLA one business day, SCORES ref field.
8. Campaigns: one list per stage. Marketing Automation: one journey drawn from the S4 ladder, never activated.
9. Bookings: one service, 45-minute slots, staff Adviser 01 to 06, a handful of appointments by hand.
10. Import order: Leads, Contacts, Deals, A la carte, Calls, Tasks, App Events, Desk tickets, Campaign lists.
11. Saved views per seat (the filter list from the seats page).
12. Screenshots to capture for the brief: one per seat view.

## 14. Admin wireframes tab (D6)

Same renderer and layout as wireframes_v02.html: left the screen list, middle the screen, right the spec (purpose, seat, reads, write actions, role, bought or built marker, a "Zoho instead?" line, dev notes, comment box, freeze marker open). Data loads from data/seed/<run>/ with a run switch (500 or 3,000). Section M, built; M01 (admin stack) stays as is.

| id | screen | seat | reads | write actions (mock) | Zoho instead? |
|---|---|---|---|---|---|
| M02 | People: search and list | ops, adviser | people, state, filters by state, tier, path, adviser, flags, DIFM prospect, topup | open, assign adviser, export list | Contact list view; no financial record |
| M03 | Person record | all seats | everything for one person: identity strip, timeline from events, financial record with source and precision badges and lock, plan versions, AA consents, CAS, holdings, calls, tickets, tasks, actions, subscriptions, audit | edit inputs on behalf (opens the D screen, re-runs the engine), force re-run, refund flag, reassign, provision DIFM, handle deletion request | Contact with mirrors only; the record itself cannot live in Zoho |
| M04 | Pre-call view | adviser, call centre | G03 snapshot, missing fields, last call, K01 topic and note, script by state, calls left | capture K03 notes and input changes, mark no-show | Contact plus a Directus-style deep link; the walkthrough decides |
| M05 | States board | principal officer, ops | counts per state by tier, S2 ladder-day histogram, click-through to M02 | none | Zoho report on Journey Stage; no ladder days |
| M06 | Ops queue | ops | item type, owner, age, SLA, linked person | assign, resolve, escalate | Zoho Tasks could hold it; data-work items argue for built |
| M07 | Data quality and integrations | ops, devs | plausibility flags, unknown ISINs, integration_events by vendor: last success, failures, latency | acknowledge, retry (mock) | none |
| M08 | Plan versions and publish impact | Harish, principal officer | who is on which version, unaccepted updates (S11), links to L05, L06, L08 | none | none |
| M09 | AA and CAS | ops | consent statuses, expiry calendar, FIP failures, CAS awaiting, uploaded, parsed | resend CAS reminder (mock) | Contact field mirror only |
| M10 | Config | ops, Bhuvanaa, Harish | SKU cards, copy slots N-* and W-* with current text, feature flags, calls_included matrix, bands (placeholder), DIFM threshold | edit (mock) | three columns: built, Zoho Creator, Directus; this is I15 made visible |
| M11 | Audit log | compliance | who changed what and when on regulated records | export | Zoho audit covers Zoho only |
| M12 | Assisted onboarding and DIFM provisioning | ops | a DIFM household created from admin, claimed later by OTP | create, invite | none |
| M13 | KPI page | principal officer | the Placement rows computed in the browser from the seed: total users, new users, in onboarding per state, paid by SKU, plans built and read, pending actions, AUA by tier, SIP book (StAR vs AA-detected), AA availed, KYC and AA failure rates, revenue mirror, topup footers | none | Zoho Analytics for CRM-side rows; the DB-side rows need the built tool or Metabase |
| M14 | Roles and permissions | principal officer | matrix seat by screen by action | none | Zoho profiles cover Zoho only |

## 15. Seats page (D7)

A table: seat, question, surface (Zoho, Admin tab, vendor console), screen, answered (yes or no), gap note with a comment box writing to board_entries. Pre-filled:

| seat | questions |
|---|---|
| Principal officer (Harish) | paid by SKU this week vs last; AUA and SIP book; DIFM prospects to call; regulatory overdue (annual RPQ, agreement renewals, grievances past SLA); engine failures; refunds pending; who is on an old plan version |
| Adviser, call at 11 | who is this person; plan at a glance; actions done; what they asked on K01; what is missing; last call's input changes; the script for their state; calls left this period |
| Call centre | today's tasks (S2b, S19, S20) with state, missing fields, tier, deep link; outcome capture; the a la carte offer for DIY; who to offer the same adviser to |
| Ops (Kajal's seat) | the queue by type and age; AA failures needing follow-up; unknown ISINs; plausibility flags; reassignments; DIFM assisted onboarding; refund requests; deletion requests with the retention override |
| Marketing (Bhuvanaa) | lists by stage; who received which slot; template approval status; the weekly cap; opt-in and DND; which S2 day-3 message converts; the S8 first-action message performance |
| Compliance | grievance register export; advice register per person (plan version, assumptions version, instrument set); agreement versions signed; RPQ refresh due list; audit trail; deletion vs retention |
| Support | a ticket with context (stage, tier, last screen, that person's integration failures); SLA one business day; the reply landing in-app |
| Finance | Razorpay vs Deals reconciliation; GST split by type; invoices; refunds; a la carte receipts |

A question marked gap appends a row to T1 to T6 on the brief page with the seat as its cause.

## 16. Brief skeleton (D8)

Six tables, pre-filled from data, each row with a cause, gap rows appended from the seats page.

| table | contents | pre-filled from |
|---|---|---|
| T1 Data model | table, field, type, source tag, precision tag, PII class, where mirrored (Zoho field or none) | section 11 plus the SCREENS field list |
| T2 Event contract | event, trigger screen, payload, consumers (CRM, analytics, nudge ladder) | admin_crm.json events plus SCREENS events |
| T3 Built screens | screen, seat, reads, write actions, role | section 14 |
| T4 Zoho configuration | object, fields, picklists, layouts, saved views per role, tasks created on state_enter, Desk categories and SLA, Campaigns lists, Bookings, roles | section 12 and 13 |
| T5 Nudge rules | the v0.2 matrix by reference; where the weekly cap is enforced; opt-in and DND handling; the WhatsApp template approval list (WATI, I11) | STATES |
| T6 Analytics | screen_view plus named events, user properties, the three funnels (R01 to R09, R12 to P05, O02 to D10), retention by paid cohort, dashboards, tool (I13 open) | SCREENS events and the Placement rows |

## 17. Validation and report (D3)

- Counts per layer and the state by tier grid against the floors; funnel ratios realised vs config; topup counts.
- Coherence rule violations: zero.
- One state per person; the multi-predicate list by state pair (the N01 gap list).
- Every paid person with plan_built has no unknown gate field; D13 rows exist where a range was taken.
- Event order consistent with dates and exits; no event before signed_up.
- Minimisation scan on exports: pass.
- report.md per run, plus one changelog row on the board and the daily-update line for the tracker.

## 18. Phases and commits

| phase | work | commit |
|---|---|---|
| A | config, generator, run-500 and run-3000, report.md | seed A: generator and two runs |
| B | exports, minimisation scan, operator page | seed B: exports and operator page |
| C | admin wireframes tab M02 to M14 | admin wireframes v0.1 |
| D | seats page, brief skeleton | admin brief skeleton |
| E | nav on every page, changelog rows, tracker W12 and W13 lands_at links, Mixpanel JSONL | seed E: board links |

Each phase ends with the one-line daily update for the tracker. Existing pages are not otherwise touched.

## 19. Placeholders and to be verified

- Bands: placeholder ladders until the M2 tables arrive (tracker).
- DIFM threshold: Rs 1 Cr placeholder; the board reads Rs ___.
- Refund policy: S24 path only, no rule (brief H5, to be decided).
- to be verified: Zoho One trial card requirement; trial record caps; Created Time mapping on import; Finvu consent duration; recording consent and retention (K06); the yeslifers.com sheet column names.
- Assumptions register (config.json carries every one): funnel ratios, dwell distributions, tier and path mixes, period and payment mixes, archetype ranges, coherence bounds, precedence order.
