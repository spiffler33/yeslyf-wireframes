# Handoff - 16 Sep 2026 (phase closed: 10b-2, owed-to-Spinach table and event schema)

State: docs/integrations.html (and its review copy) carries "Owed to Spinach", W01 to W09 from data/dependencies.json,
under the 22 integration rows; docs/events.html and docs/review/events.html list the event schema, 540 rows = 193
screen_view + 339 named events + 8 core actions (data/events_extra.json); the Events tab is on every page and on the
review link. Commit a3d902e pushed, closure commit after it. No build work is pending; the next unit is the second
review round.

## Read first
1. PLAN.md section 14, the "16 Sep 2026, phase 10b-2" bullet (what shipped, the known limitations), then the phase 10b
   bullet above it (the owner rule).
2. scripts/build_events.py's docstring (the row rules and the count check) and the "note" keys of
   data/events_extra.json and data/dependencies.json (every field explained).
3. Memory project_state (constraints the repo does not state: the owner rule, Google and Apple sign-in at P02, page
   density, the Opus floor, no Apps Script change).

## Verify before coding
- `git status --short` is empty; HEAD is the closure commit after a3d902e.
- `python3 scripts/build_site.py` ends with "wrote docs/review/events.html (... 540 rows: 193 screen views, 339 named
  events, 8 core actions)" and leaves docs/ and data/ unchanged (`git status --short` still empty afterwards).
- `python3 scripts/check_phase9.py` prints 17 PASS lines and no FAIL.

## What to do next
- Second review round on the review link (https://spiffler33.github.io/yeslyf-wireframes/review/): reviewers press
  Export comments and the markdown goes to spiff. Owners set status and dates on the Integrations tab and on the Owed
  to Spinach rows (W07 journey tool, W08 event schema and W03, W04 in part are due 19 Sep 2026; W09 was due 16 Sep
  2026); those edits stay in their browser unless the endpoint is set, so Export brief is the record.
- When the exported comments arrive: parse them into data (never docs/), dispositions with causes ("<first name>,
  <date>" or "row N"), a new edit group under data/v02, then rerun apply_decisions, build_site (it builds the
  integrations and events pages too) and check_phase9; commit per phase and push.
- Then the CRM planning session: the Admin and CRM v0.2 tab, CRM backlog section.

## Constraints carried forward
- inputs/ is read-only; docs/ is generated (never hand-edit; build_site.py calls build_integrations.py, then
  build_events.py, at the end); docs/v01/ stays byte-identical to inputs/v01/.
- Owed rows: IDs W01.. in message order, never renumbered; owners as given in the message; statuses are set in the
  page, not in data; the sheet row's type column is trailing so an existing v02_integrations tab keeps its six
  columns aligned; no Apps Script redeploy.
- Events page: rows come only from the v0.2 screens data plus data/events_extra.json (spiff, 16 Sep 2026); one row
  per event per screen; no comment control (comments on events go on the screens in Wireframes v0.2).
- Integrations owners: Kajal, Vatsal or Spinach; Gaurav on DevOps monitoring; Gaurav and Raafiya on the HoA Core
  Platform; Compliance and Harish on the store declarations. One vendor per row; alternatives only where the choice
  is open (I13 journey tool, decision by 19 Sep 2026; I15 Directus).
- Google and Apple sign-in: later in the journey (P02, where the email is asked), gates launch; entry is always
  mobile OTP. The P02 sign-in step is not drawn in v0.2 and has no gap entry yet.
- Vendor facts stay "to be verified: <item>"; every new number stays a placeholder ("Rs ___", "about N minutes", "N").
- v0.2 rules: causes only ("brief X", "row N", "<first name>, <date>"); no adviser named; "yeslyf" lowercase; "Rs";
  no "recommendation" or "founders"; ASCII only; no em dashes.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026). Secrets stay out of the repo.
- Page density (spiff, 16 Sep 2026): a board page reads as a calm list first, editing behind a click.
