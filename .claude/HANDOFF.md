# Handoff - 28 Sep 2026 (phase closed: F, Zoho provisioning; phase G planned, not started)

State: the run-3000 seed is in the Zoho One trial "Plan2prosper" (commit e93d9b8; 32 operator items done by script,
24 leftovers in seed/zoho/leftovers.md). Phase G, "Zoho as if live" (PLAN_zoho_live_v01.md), is written and committed
and starts only when spiff says "go": phases G0 to G9 in order, one browser, one commit each, no message ever
reaching a seeded contact. Phase 14 is closed (b761fdb); its pass 5 runs only on Vatsal's word.

## Read first
1. PLAN_zoho_live_v01.md: purpose, the three decisions taken, the provisional calls, phases G0 to G9 with done criteria.
2. PLAN.md sections 23 (what phase F built and the design calls it forced) and 24 (phase G and the open points).
3. Memory zoho-trial (the org, where the credentials live, the re-run recipe) and admin-crm-direction (Vatsal's
   28 Sep 2026 direction for the Admin + CRM tab: no Directus, app to Zoho one way, revenue in Zoho).

## Verify before coding
- `git status --short`: clean apart from the untracked inputs kept out on purpose (two inputs/meeting/ files,
  inputs/spinach/2026-09-25/ with Spinach's ops report pdf, marked confidential).
- `python3 seed/zoho/zoho.py check` (read only): CRM org Plan2prosper, type production, edition free, trial
  zohooneenterprise; Desk portal id 60089105539; Bookings workspaces: Plan2prosper. seed/zoho/.env and
  seed/zoho/.local/token.json exist (check with `ls`, never print them).
- `python3 seed/zoho/provision.py --plan` (no network; last line names the service 'Talk to an adviser', 45 minutes);
  `python3 scripts/build_site.py`, `python3 scripts/check_phase9.py` 19 PASS, `python3 scripts/check_site.py` 3 PASS.

## When spiff says "go": build phase G
1. Ask at most three things, in plain text, recommended answer first, then start: (a) the homes for what Directus
   used to hold (admin over app tables, app content and config: the admin panel Spinach builds over the app's
   database, recommended) and whether Metabase's 13 rows also move to Zoho Analytics; (b) veto or consent on the
   provisional calls in plan section 4 (the 23 refused calls logged as Missed; past booked slots booked at the same
   weekday and time in the first future week; marketing and finance built under Kajal); (c) nothing else unless G0
   finds something. The answers to (a) are a separate small commit on the Admin + CRM tab (13 placement rows,
   decisions D1 and D5, the INBOUND rows, a legend line for Console, Fold and Change), never mixed into phase G.
2. G0 first (API, read only): the baseline table and seed/zoho/live.py. Context7 before every new call shape.
3. Chrome: load the claude-in-chrome tools in one ToolSearch, `tabs_context_mcp`, then a new tab; Kajal's session was
   signed in at crm.zoho.in and desk.zoho.in on 28 Sep 2026 (if it has expired, spiff signs in; never type a password).
   Screenshot before and after every save; every UI step goes into reports/phaseG_pass<N>.md with its screen path.
   Any screen that could send (invitations beyond Kajal's mailbox, Campaigns import options, Bookings notifications,
   Desk SLA escalation actions) is checked and screenshotted before the step; if a switch cannot be turned off, stop
   and report.
4. One commit per phase, "zoho live G<N>: <what>", no AI attribution trailer; G9 closes with the live verifier,
   data/zoho_live.json, the operator page marks, PLAN.md section 25, handoff, memory, push.

## Constraints carried forward
- Never call anything that connects a channel, verifies a sender or domain, or sends. Staff invitations go only to
  plus-addresses on Kajal's mailbox (her address is read from Zoho at run time and never written down).
- No regex or phrase rules; stdlib only; ASCII; Rs; first names; a cause on every change; "to be verified: <item>"
  and "to be decided: <item>" with no name attached. Secrets never in the repo.
- Kajal's remaining operator steps stay as they are until the script or the Chrome work finishes them; only then do
  they get a "done by script" or "done in Zoho" line.
- The placeholders "Individual" (Leads Company, the Deals account) stay unless Vatsal says otherwise.
- Board work (phase 14 pass 5: the approvals script, BE-04's item line, the CAS clash on W11) and Zoho work stay in
  separate commits; pass 5 only on Vatsal's word.
