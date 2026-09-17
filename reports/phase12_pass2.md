# Phase 12, pass 2: frozen and final markers (17 Sep 2026)

Source: yeslyf_phase12_brief.md, pass 2 (2.1 to 2.8). Cause on everything: minutes 16 Sep 2026, item 19; Vatsal,
17 Sep 2026.

## What changed

- 2.1 Screen marker. data/v02/freeze.json is the register: since 17 Sep 2026, the open list with a cause per screen,
  the blocking "to be verified" items (per item and screen), the "to be decided" lines that only owe (X00's
  session rule, W21) and an empty unfreeze log. scripts/apply_decisions.py writes screen.freeze on every live screen
  (status, since, cause, reason, owed) and fails the build when an open screen has no reason, a frozen screen
  carries a blocking item, or a listed screen is not live. The reason is picked up from the screen: its "to be
  decided" lines and its blocking "to be verified" items, plus an explicit line where the screen has none (the E
  screens, K02, the L group). Only a commit changes a status; the page has no control.
- Shown as text: "open" next to the title in the left list (frozen screens carry no mark, so the list stays calm);
  the word after the template in the screen header; in the spec panel's marker box, "Frozen since 17 Sep 2026" or
  "Open since 17 Sep 2026, because:" with the reasons (one inline, several as a list) and "Owed:" items; and a
  filter "Frozen" (frozen and open, frozen only, open only) next to Template. The audience files carry the same.
- Changelog: "To be decided" (6 items), "Freeze register" (counts, the 34 open screens with reasons and owed items,
  the owed items on frozen screens), "Unfreeze log" (empty); the stats strip and the counts for Spinach carry
  frozen and open per section and per template, and the templates' status. The Spinach file's Counts page too.
- 2.3 Templates: all 21 frozen since 17 Sep 2026 (element types and their order); the template filter says so on
  its first option; the template table carries the status.
- 2.4 Open on day one: 34 (A03, A04; A10, A10c, D02c, G12a; H06; P04; E02, E03, E04, E07 to E11; Q02; Q04, N28;
  D02d, A05a; K02, K06; M01; L00 to L09). Frozen: 160 of 194. The L group freezes with W04; if the drawn shapes
  are the delivery, drop the ten L entries from freeze.json open and rebuild (24 open, 170 frozen).
- 2.5 Blocking items (the screen is open): CAS parsing effort (A10); NPS on AA (D02d); FIP health before consent
  (A05a); direct plans and the RIA code (E07 to E09); e-NACH approval time (E10); mandate type and limits and
  netbanking mandate (P04); proration (Q02); recording consent (K06); nomination rule and UCC field set (E02); the
  annual confirmation (Q04, N28; owed on N01); the BSE JSON services (E02, E07); parsing effort (the four CAS
  screens). Every other item is owed and listed on its screen as owed.
- 2.6 Integrations rows: field "choice" (final or open), seeded final on I01, I02, I03, I04 (minutes item 12), I08
  (item 3), I14 (Vatsal, 16 Sep 2026), I17 (Gaurav, 16 Sep 2026), I10 (Vatsal, 17 Sep 2026); 17 rows open. Each
  seed carries final_since (the date, for the daily update). The word sits next to the vendor in the list, a
  "Final or open" select opens the row's panel, a "Final or open" filter and counts (8 final, 17 open) sit on top.
  "Every row final by" is one date for the page (board row integrations / final_by, with history); empty today.
  The export carries the choice and the date. Costs: the field stays with the hint "kept off the board".
- 2.7 Every screen's spec panel carries "Integrations": the rows whose screens list names the screen, as "I06 CAMS
  KRA, open; if it slips: <fallback>", or "none". The site pages read the current choice from the board table
  (scripts/board_store.js read); until it arrives, and in the audience files, the build's value shows with its
  date ("as of 17 Sep 2026", the date of the last board pull). Rows serving every screen (I17, screens all) are
  not repeated on each screen.
- 2.2 and 2.8 X00: the old card "Frozen" is retitled "Frozen files and tabs"; the new cards "What frozen means"
  (the text of 2.2, three lines) and "How Spinach works from this board" (five lines) follow it.
- Check 18 (scripts/check_phase9.py): every field entry tagged, no vendor names on screens, the freeze register
  adds up, the wireframes, integrations and changelog pages carry the marks. 18 PASS.

## Counts

- Screens 194: 160 frozen, 34 open. Templates 21, frozen. States 27. Field entries 290 of 290.
- Integrations rows 25: 8 final, 17 open. To be verified 30; to be decided 6.

## Contradictions and judgment calls

- The brief's freeze key "status" collides with v02.status; the marker is screen.freeze.
- Reasons are not repeated: where a screen carries its own "to be decided" line (A03, A04, H06, the four CAS
  screens, M01) the register lists that line and no second explicit reason.
- The item cutter in scripts/apply_decisions.py now respects brackets, so "DPDP notice text (gap G03)" reads whole
  on the Changelog (it was cut at the first bracket before); the 27 items are the same items.
- Rows with screens ["all"] (I17 AWS) are left off the per-screen Integrations line to keep the spec panel calm;
  the Integrations tab says it serves every screen.
- I24 and I23 are "not decided" vendors and read "I24 not decided, open" on K02 and K06; that is the marker
  Spinach needs (no vendor, open).
