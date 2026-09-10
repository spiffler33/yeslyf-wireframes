# Handoff - 10 Sep 2026 (phase closed: the meeting board, PLAN.md Phases 0 to 2)

State: the yeslyf product board is built, live and finished its job. The team meeting ran on it on
9 Sep 2026, the decisions are exported, and the next unit of work is wireframes v0.2 from plan_v2.md.

## Read first
1. `plan_v2.md` - the plan to run. Section 0 holds two defaults that become Vatsal's decisions if the
   plan is run unedited; check with spiff whether he has edited them before starting.
2. `inputs/meeting/yeslyf_meeting_brief_2026-09-09.md` - what the room decided, all 18 items.
3. `PLAN.md` section 12 (status) plus sections 1 to 6, which still hold. Sections 7 to 11 are superseded.

## Verify before coding
- `git status --short` is empty; HEAD is the 10 Sep phase-boundary commit.
- `python3 scripts/build_site.py` prints seven "wrote docs/..." lines and rebuilds `docs/` byte-identical
  to what is committed. `git status --short` must still be empty afterwards.
- `python3 scripts/assign_inputs.py` exits 0 and prints `{'open': 26, 'quick-accept': 14, 'accepted': 21,
  'answered': 12}` (73 rows). It is the data-layer validator; run it after any change to data/.
- `cmp inputs/v01/yeslyf_wireframes_v0.1.html docs/v01/yeslyf_wireframes_v0.1.html` is silent, same for
  the admin/CRM file.

## What to do next
Run plan_v2.md, Phase 3 onward. Do not run Phase 3 from PLAN.md; it describes a different plan.

Constraints carried forward.
- The two v0.1 HTML files are frozen. spiff, 9 Sep 2026: "do not change wireframes as well as crm/admin
  htmls at all - everyone is used to them now". They are served byte-identical from `docs/v01/`.
- `inputs/` is read-only. `docs/` is generated; never hand-edit it. `data/*.json` is the single source.
- The repo's own CLAUDE.md governs voice and attribution: first names only, never "founders", never
  "recommendation" on an open item, "Vatsal recommendation" only on gaps and dependency blocks, ASCII
  only, "Rs" never the rupee symbol.
- Screen IDs are permanent; new screens take the next free number in their section.
- Two brief anomalies to resolve before applying them: T1 has all four SKU options ticked, including the
  one-time card whose dependency block removes the 60-day credit rule; T2 records no choice, only the
  note "DIY no calls at all only a la carte, DIWM - 4 qtrly review calls".
- Secrets stay out of the repo. The sheet id and Apps Script endpoint live in `.local/sheet.json`,
  gitignored. The two HoA PDFs are gitignored: they carry a client's name, PAN, address and phone.
- The Pages site is private-repo but publicly reachable by URL; noindex stays on every generated page.
