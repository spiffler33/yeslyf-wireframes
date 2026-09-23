# Seed and admin discovery: progress

Plan: PLAN_admin_seed_v01.md (the spec; CLAUDE.md wins on a conflict). Resume from this file plus the plan.

## State (23 Sep 2026)

- Phase A done: config, generator, run-500 and run-3000, report.md per run. Committed as "seed A: generator and
  two runs". Stopped for Vatsal's go before phase B (his instruction, 23 Sep 2026).
- Phases B to E: not started. After the go they run in sequence without stopping, one commit per phase (plan
  section 18 messages), the one-line tracker update at the end of each phase.

## Files

- seed/config.json: every count, ratio, floor, band placeholder, archetype and rule; each block carries a cause
  ("Vatsal, 22 Sep 2026", "assumption", "seed plan, 22 Sep 2026"); blocks with "added": "phase A" are decisions
  taken where the plan was silent (report.md section 8 lists them).
- seed/names.json: synthetic name lists by region (team names, retired personas and the wireframe example name left out).
- scripts/seed_gen.py: generator, state resolver, validation and report. `python3 scripts/seed_gen.py` builds both
  runs with the anchor = the run date; `--run run-500`; `--anchor YYYY-MM-DD`. About 1 s for both runs.
  Output is fixed by seed and anchor (checked: identical hashes on a rerun).
- data/seed/<run>/: one JSON per table keyed by person_id (people, households, reveal, financial_records, loans,
  covers, goals, rpq, holdings, aa_consents, cas_uploads, plan_versions, actions, subscriptions, payments,
  a_la_carte, calls, tickets, ops_queue, integration_events, tasks, nudges_sent), state_flags.json (what the
  resolver reads), staff.json, config.json (the app config table), events.jsonl, report.md.
- Inspect with scripts and counts; never load a full seed JSON or events.jsonl into context.

## How the generator works (for phases B to E)

- Each paid person gets a target state; overlay states (S7, S11, S12, S13, S15, S17, S20, S22, S23, S24, S25)
  sit on an underlying state (config overlay_bases). The timeline is drawn from the time model until the target
  holds at the anchor; the resolver then derives the state and the state_enter history from state_flags only.
- report.md checks: targets vs resolved (none differ), coherence (0 violations), gate (0 unknown gate or React
  fields on built plans), event order (0 before signed_up, 0 plan_read before plan_built), names (all on the board).
- Money: every amount on a deal, payment or a la carte purchase is "Rs ___" with a price key (CLAUDE.md: prices are
  never invented). Included calls "N". Minutes "about N minutes".
- Vendors: integration_events carry the vendor key of plan section 11 and the I-number; screens must cite the
  I-number only (CLAUDE.md).

## Phase A results (run-3000; run-500 in its report)

- 3,040 people: 1,400 leads, 400 S1, 990 S2, 25 S2b, 15 S2c, 210 paid; topups 0 (run-500: 507, topups 7).
- Every ugly case at its count. 86 people with more than one predicate (the N01 gap list). 3 engine-failure people
  match no state (kept at S5). 72,371 events (the plan estimated about 150,000).

## Open questions (in the phase A summary, 23 Sep 2026)

1. The O02 progress ring: the seed plan says endowed 20 at OTP; plan_v2 4.3 rule 11 says 20 after the reveal. The
   seed follows the seed plan (S1 people show 20).
2. DIFM share: the plan gives DIFM 10 percent and S14 8 people; every DIFM person resolves to S14, so the seed has
   DIFM = 8 (3.8 percent). Veto: raise S14 to 21.
3. S16: the plan says about 30 percent (manual or CAS path); the seed flags manual plus AA-failed (37 percent).

## Next (after the go)

- Phase B: exports (Zoho CSVs, Desk, Campaigns, landing sheet, fixtures, minimisation scan) and docs/admin_operator.html
  (checkboxes writing to board_entries). One subagent per export file, each given plan section 12, seed/config.json
  and data/seed/<run>/.
