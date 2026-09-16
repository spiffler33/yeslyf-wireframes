# Handoff - 16 Sep 2026 (phase closed: 10b, the integrations page)

State: docs/integrations.html and docs/review/integrations.html are live: 22 rows I01 to I22 from
data/integrations.json, one compact line per row with a panel behind a click, owners per Vatsal (16 Sep 2026), three
rows marked "to be verified: screens" by the build cross-check (I01, I02, I09). No build work is pending; the next
unit is the second review round.

## Read first
1. PLAN.md section 14, the "16 Sep 2026, phase 10b" bullet (what shipped, the owner rule, the known limitations).
2. data/integrations.json: its "note" key explains every field. scripts/build_integrations.py's docstring explains
   the cross-check, the page behaviour and the sheet row format.
3. Memory project_state (constraints the repo does not state: the owner rule, Google and Apple sign-in later in the
   journey at P02, page density, the Opus floor, no Apps Script change).

## Verify before coding
- `git status --short` is empty; HEAD is the closure commit after 99de140.
- `python3 scripts/build_site.py` ends with "cross-check: 22 rows, 3 marked 'to be verified: screens', 19 clean"
  and leaves docs/ and data/ unchanged (`git status --short` still empty afterwards).
- `python3 scripts/check_phase9.py` prints 17 PASS lines and no FAIL.

## What to do next
- Second review round on the review link (https://spiffler33.github.io/yeslyf-wireframes/review/): reviewers press
  Export comments and the markdown goes to spiff. Owners set status and dates on the Integrations tab; those edits
  stay in their browser unless the endpoint is set, so Export brief is the record.
- When the exported comments arrive: parse them into data (never docs/), dispositions with causes ("<first name>,
  <date>" or "row N"), a new edit group under data/v02, then rerun apply_decisions, build_site (it builds the
  integrations pages too) and check_phase9; commit per phase and push.
- Then the CRM planning session: the Admin and CRM v0.2 tab, CRM backlog section.

## Constraints carried forward
- inputs/ is read-only; docs/ is generated (never hand-edit; build_site.py calls build_integrations.py at the end);
  docs/v01/ stays byte-identical to inputs/v01/.
- Integrations owners: Kajal, Vatsal or Spinach; Gaurav on DevOps monitoring; Gaurav and Raafiya on the HoA Core
  Platform; Compliance and Harish on the store declarations. Vatsal is the PM for yeslyf, not a vendor owner. One
  vendor per row; alternatives only where the choice is open (I13 journey tool, decision by 19 Sep 2026; I15 Directus).
- Google and Apple sign-in: later in the journey (P02, where the email is asked), gates launch; entry is always
  mobile OTP. The P02 sign-in step is not drawn in v0.2 and has no gap entry yet.
- Vendor facts stay "to be verified: <item>"; statuses start at "not started" and are set in the page, not in data.
- v0.2 rules: causes only ("brief X", "row N", "<first name>, <date>"); no adviser named; "yeslyf" lowercase; "Rs";
  no "recommendation" or "founders"; ASCII only; no em dashes.
- Subagents: Opus is the floor, never Sonnet (spiff, 10 Sep 2026). No Apps Script redeploy (the deployed script
  creates the v02_integrations tab from the posted cols). Secrets stay out of the repo.
- Page density (spiff, 16 Sep 2026): a board page reads as a calm list first, editing behind a click; no form-heavy
  tables.
