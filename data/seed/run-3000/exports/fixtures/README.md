# Fixtures bundle: run-3000

For Spinach's dev and staging databases. The canonical bundle for this run ships as a
private zip in this folder: yeslyf_seed_2026-09-23_run-3000.zip.
It is not committed to the repo (see .gitignore) and never published on the board;
Spinach receives it by hand (Vatsal, 23 Sep 2026). It holds data/seed/run-3000/*.json,
events.jsonl and report.md, plus this README, all under a folder named like the zip
(the zip name without .zip).

## Tables

| file | key | holds | rows (run-3000) | joins |
|---|---|---|---|---|
| people.json | person_id | one record per person: identity, contact, lifecycle dates, mirrors, state | 3040 | person_id |
| households.json | person_id | the person's household composition (members, dependants, pets) | 1565 | person_id |
| reveal.json | person_id | the R01 to R09 reveal answers: income, corpus and savings bands and exact values, aspiration, path bands | 1565 | person_id |
| financial_records.json | person_id | every D-screen spine field captured for a person, with source, precision and lock state | 7138 | person_id |
| loans.json | person_id | one entry per loan: type, EMI, outstanding, years left, rate | 125 | person_id |
| covers.json | person_id | the person's term and health cover position | 162 | person_id |
| goals.json | person_id | one entry per goal: name, year, cost, priority | 290 | person_id |
| rpq.json | person_id | the risk profiling questionnaire answers and resulting band | 188 | person_id |
| holdings.json | person_id | AA- or CAS-sourced holdings: ISIN, name, units, value | 585 | person_id |
| aa_consents.json | person_id | account aggregator consent history: status, institutions, expiry | 133 | person_id |
| cas_uploads.json | person_id | CAS statement upload and parse timeline | 41 | person_id |
| plan_versions.json | person_id | every plan version built for a person, with the summary stub | 514 | person_id |
| actions.json | person_id | post-plan actions (SIP starts, stock baskets) and their verification state | 639 | person_id |
| subscriptions.json | person_id | one entry per deal: SKU, period, mandate and billing state | 206 | person_id; deal_id joins payments.json |
| payments.json | person_id | one entry per payment attempt against a deal | 511 | person_id; deal_id joins subscriptions.json |
| a_la_carte.json | person_id | single-call purchases outside the plan | 9 | person_id; call_id joins calls.json |
| calls.json | person_id | one entry per booked call: adviser, topic, status, notes | 84 | person_id; call_id joins a_la_carte.json |
| tickets.json | person_id | one entry per support, adviser-message or grievance ticket | 73 | person_id |
| ops_queue.json | person_id | internal ops work items: AA failures, data quality, refunds, DIFM provisioning | 100 | person_id |
| integration_events.json | person_id | one entry per vendor call: integration I-number, outcome, latency | 12115 | person_id |
| tasks.json | person_id | one entry per CRM escalation task (the five crm_task states) | 114 | person_id |
| nudges_sent.json | person_id | one entry per nudge send: slot, channel, delivery and click state | 8767 | person_id |
| state_flags.json | person_id | the resolver's internal per-person timeline; state_id and the state_enter history in events.jsonl are derived from this | 1640 | person_id |
| staff.json | staff_id | the ten staff records: advisers, ops, support, compliance, Harish | 10 | n/a |
| config.json | n/a | the app's own config table for this run: SKU cards, copy slots, feature flags, calls-included matrix, bands, DIFM threshold | n/a (a single config object, not person-keyed) | n/a |
| events.jsonl | event_id | the full event log: every screen view and product event, not just the CRM subset in zoho/app_events.csv | 72398 | person_id |

## Joins not carried by a column name above

- staff_id: people.json (adviser_id, last_adviser), calls.json (adviser_id), tasks.json
  (assignee) and ops_queue.json (owner) all reference a key in staff.json.

## Personal data

- people.json carries first_name, last_name, phone, email, legal_name, pan and dob.
- households.json carries each member's name and age.
- reveal.json carries first_name.
- PAN is synthetic in format only. It appears in the canonical seed and in this
  fixtures bundle; it never appears in any Zoho export (the minimisation scan enforces
  this).

