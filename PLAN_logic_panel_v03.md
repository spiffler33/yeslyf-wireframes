# PLAN: logic panel side wireframes and tech plan, v0.3 (lean)

Status, 8 Oct 2026: written, nothing built. This file replaces PLAN_logic_panel_v02.md and PLAN_logic_seed_v01.md of
the same day; neither reached the repo and neither is to be used. The phases of section 12 (A0 to C2, then Vatsal's
look in D) run in order on Vatsal's "go", one commit per phase, no push. Plan-ready pass, 8 Oct 2026: section 12
rebuilt into phases with done-criteria and the choices the first draft left to the executor resolved in 12.0.

Date: 8 Oct 2026. For Claude Code in the yeslyf-wireframes repo. CLAUDE.md rules apply throughout (ASCII, Rs, first
names, a cause on every row, "to be verified: <item>" and "to be decided: <item>" with no name attached, no regex,
stdlib only, freeze markers, per-screen comment controls through the Supabase write-back).

What this plan is for (Vatsal, 8 Oct 2026):
1. Better logic panel wireframes: the panel as its two operators will use it.
2. The tech plan around four things: who may do what (access), how a change reaches clients without shocking them,
   cohorts that can grow, and the stored versions of every plan a client was shown.
3. An ops page: what each kind of change sets in motion for ops, the call centre and support.

How it is built, and why it is small (Vatsal, 8 Oct 2026: cut to what is needed):
- The side screens are data in the board's own screen format, drawn by the renderer that already draws L00 to L09.
  No new renderer and no drawing code.
- A state that matters is its own screen with a letter suffix, the board's convention (H01a to H01k, G12a).
  Thirty-nine screens in all.
- Example values are typed, as on the board today ("1,240 of 1,900"). Nothing is computed: no scripted clients, no
  arithmetic, no generated files.
- No seat switch, no step-through, no mock buttons. Who may do what is a table.
- Four static pages (Tech, Access, Walkthroughs, Ops) come from one small builder.
Expected new code: one page builder of about 200 lines and, only if the wireframe builder cannot take a second data
file, a stripped copy of the admin wireframes builder. Everything else is JSON content. If a phase seems to need more
code than that, stop and report before writing it.

Cause labels used in this file:
- "Vatsal, 8 Oct 2026": his call. The brief for this work (section 0) and the design in section 4.
- "7 Oct 2026 call": said on the HoA and Spinach call of 7 Oct 2026. Vatsal gave the transcript on 8 Oct 2026; it is
  not in the repo and nothing here needs it (if he places it under inputs/meeting/ it stays untracked like the other
  meeting files). A first name is attached only where a person stated a fact about their own system or work.
- "logic plan, 8 Oct 2026": a provisional call made in this plan; Vatsal vetoes by reply.
- "rehearsal value": a logic value the screens need in order to show something (a return, a mix, a threshold, a fund
  on a list). It is never a position on what the real value should be, it is never copied into
  data/screens_v02.json, and every screen that shows one says so. The real values are owed under tracker W04 and W30.
- "example": a typed value on a screen (a count per 1,000 plan holders, an instalment, a date). Examples agree with
  each other because they all come from section 6. They are illustrative, not evidence; no ratio here ever leaks
  into product logic (no client-data assumptions until a flywheel exists; Vatsal, 11 Sep 2026).

On every page of this work the design reads "proposed, to be confirmed at the logic panel review" (the board's own
phrase for the admin session; to be decided: the review date). Nothing is decided for the team by being drawn here.

Ids in this file, chosen so none collides with a screen id on the board: releases REL01 to REL12; market input
releases MI00 (the launch values, inside REL01) and MI01 to MI15, which are also that lane's version ids; lane
versions as-N (assumptions), co-N (cohorts), fu-N (funds), rs-N (risk scoring); engine versions EN1, EN2; model
portfolios MP1 to MP9; walkthroughs Y01 to Y04; example clients C01, C04, C11, C12; open items LQ1 to LQ46;
deliverables DV1 to DV7. Side screens keep the board's form: L00 to L15 with letter suffixes for variants, and V01 to
V06 for the client views (section V is unused on the board; real ids are assigned at the merge).

## 0. Purpose and non-goals

Purpose: make the logic panel buildable and its working life visible before Spinach builds it.
- The two seats that will operate the panel (Principal officer, Logic analyst) can see every screen they will work
  on, in the states that matter, and walk four whole jobs through them.
- Ops can see what each kind of change sends to clients, the call centre and support, and what ops does before, on
  the day and after.
- Tech can see what must be stored, which jobs run, what the engine must accept and where access is enforced.
- Everyone can see who may do what, in one place, across the logic panel and the three built admin screens.
What it cannot answer becomes a "to be decided" or "to be verified" item. Accepted items later become the changes to
section L of wireframes v0.2 and a pack for Spinach (section 13; not in this plan).

Who reads what: the Logic tab and the Walkthroughs page are for the Principal officer and Logic analyst seats (Harish
and Somil sit there); the Tech page is for Raafiya and Gaurav; the Ops page is for the Ops seat (Kajal's seat); the
Access page is for all of them. No real person is an actor in an example: staff are "Principal officer 01", "Logic
analyst 01" and so on, because the examples include mistakes and no real person is drawn making one. A cause on a
page may carry a first name, as everywhere on the board.

Non-goals (Vatsal, 8 Oct 2026):
- No edit to data/screens_v02.json, to any L screen on the Wireframes v0.2 tab, to data/admin_screens.json, to the
  admin tab or to the freeze register. The wireframes update comes later, after acceptance.
- Nothing on the review link (docs/review/) or in the three audience files. Spinach sees this only after the merge;
  the one exception Vatsal may choose to make is the Access page (section 8).
- No engine maths and no stand-in for it. This shows the panel's operations. The working version of the maths spoken
  of on the 7 Oct 2026 call is owed under W04 and W17.
- No generator, no seeded or scripted clients, no simulation. data/seed/ is not touched; scripts/seed_gen.py is not
  run.
- No vendor call, no Zoho change, no message sent, no database, no object store. Static files and static pages.
- No real fund name: a fund in the examples goes on Hold and to Exit, so every fund is synthetic.

Tooling: Python 3, standard library only, no network.

## 1. What the 7 Oct 2026 call asked, and where this plan answers it

The Walkthroughs page opens with this table (9). "Spinach" in the second column means a question from their side.

| # | asked or said on the call | by | proposed answer | drawn on |
|---|---|---|---|---|
| 1 | Is there access control on the panel: which roles, what access, what permissions | Spinach | ten fixed seats; two draft and review, one of them publishes; compliance and ops each have narrow writes; permissions by action (4.8) and by screen (5.4) | Access page, L13 |
| 2 | The publish button must be guarded with two factors | Vatsal | a fresh second-factor check at publish and at the other guarded actions (rule 15) | L06; LQ29 |
| 3 | A few people, or opened up later | Spinach; Vatsal: a few, always | two operating seats, compliance and read only; seats are fixed, never user-defined | Access page |
| 4 | How many people at one time; who may change; across how many it is approved | Spinach | one open draft per lane with one author at a time; a second person reviews; only the Principal officer publishes; compliance acknowledges where rule 14 asks | L05, L10, L06 |
| 5 | Is there an approval workflow; should it be stepwise: enter, run, review, send for approval | Spinach | 4.6: open, validated, previewed, in review, approved, published | L05, L10, L06 |
| 6 | How often do the values change | Spinach; Somil: an equity return expectation moved from 11 to 10 after four years; Vatsal: instruments month on month or quarter on quarter | a cadence per lane on a calendar; M2's registry (section 2 of that file) already reads "annual review" against returns and inflation | L12; LQ16 |
| 7 | When a value changes, what happens to a client who already has a plan | Spinach | rule 2: new plans at once; an existing plan at its next rebuild; a push only where the route says so. On the call the answer given was "everyone, at publish"; Vatsal, 8 Oct 2026 replaces it | L06, L11 |
| 8 | The engine holds central defaults and copies them to each client; a client's numbers hold steady between that client's reviews | Gaurav, Raafiya | the same aim as rule 2; what is open is where the values live, whether a review reads the central value or the client's own copy, and who refreshes the copy | Tech page; LQ17, LQ18, LQ32 |
| 9 | A client sees 19.2 become 18 or 22 and is shocked | Spinach | 4.3: net worth today moves with prices, plan numbers move only at a rebuild; 4.5: four sizes; rule 8: instalments change as a set or not at all | client views, L05 |
| 10 | Conflicts: a change that breaches a client's portfolio against their risk profile | Spinach | guards a draft must pass (L09) and a conflicts panel in the preview (L05) | L05, L09; LQ39 |
| 11 | Automatic checks that stop a change ("five errors, cannot proceed"); a lakh of portfolios | Spinach | hard stops in validation; the preview is a batch job, sized on the Tech page for 1,000, 10,000 and 100,000 plans | L05, Tech page |
| 12 | The edge case directory | Spinach; Vatsal: HoA does the heavy lifting | the awkward cases of the operations are drawn as screen variants (5.2) and walked in section 9. The maths cases come with the working version owed under W04 and W17 | Walkthroughs page |
| 13 | Are versions stored; audit log; version control | Spinach; Vatsal: yes | releases and lane versions, append-only; an audit row for every write and every refused write | L08 |
| 14 | Cohorts could be 15 to 20, each with its history, why it changed and which portfolios were affected | Spinach | cohorts as data (rule 16); one version per lane; a history per cohort read from it | L03, L14 |
| 15 | An adviser sees, per client, each change and why | Spinach | L15, which becomes M03's plan versions tab at the merge | L15 |
| 16 | Versions, history and intelligence per cohort are overkill; a simple review and approve will do | Gaurav | 4.9: what must exist at launch because it cannot be added backwards, and what can follow | Tech page; LQ37 |
| 17 | Take a snapshot every time anything changes | Vatsal | rule 7 | L15, Tech page |
| 18 | Sample plans are affected; they are not a flat file | Spinach | rule 21: regenerated by a release from fixed sample inputs | L05, client views; LQ34 |
| 19 | Someone who sat with the app for six months without deciding | Spinach | proposed here (logic plan, 8 Oct 2026): a saved reveal stays as shown until sketched again (rule 21); drawn as V06. On the call the answer given was that the numbers will change and that this must be communicated | client views, L15; LQ35 |
| 20 | An in-app notice that "we changed this" costs trust; a client who joined a month before a change | Spinach; Vatsal: an email with an explanation, not a notification | rule 20: house-view changes arrive on a calendar, inside the client's own review, with the reason; the letter (V05) | client views, Ops page; LQ33, LQ21 |
| 21 | The hit spreads to sample plans, adviser views and other interfaces; the change life cycle must be mapped | Spinach | 4.7 and the surface map (5.6) | L00, L05 |
| 22 | Access control for the app as well | Spinach | the app has one kind of user; its tier gates are entitlement, already on each screen | Access page; LQ40 |

Two facts from the call that the rest of this plan leans on, both "to be verified" until tech confirms them:
- {I04} keeps central values as defaults, copies them to each client and lets a client's copy be changed on its own;
  a client's numbers are recalculated at that client's review (Gaurav and Raafiya). Whether that review reads the
  central value of the day or the client's own copy was said both ways.
- Execution at launch may leave the app through a link that opens {I02} with the portfolio loaded, with in-app
  execution following (Vatsal; gap G10 on the board). Section E of the board draws execution in the app. LQ36.
One more thing said there has no home on the board yet: the allocation maths itself "will change multiple times"
(Vatsal). A new engine version is not a lane and has no workflow here; LQ46 holds it.

## 2. Inputs to read first

| input | what it gives | where |
|---|---|---|
| section L of the SCREENS data (L00 to L09) | the logic panel as drawn today, and the screen schema to write in | data/screens_v02.json |
| H05, H01, H01e, H02, H10, N16, Q01, Q04, Q05, Q06, D09, G01, G03, G11 to G14, E03, E08, E11, R08, R09, R12, X01 | every client screen a release touches; link targets for the side screens | data/screens_v02.json |
| states S2, S11, S13, S22, S23, S25 | the ladders the ops page refers to | data/v02/states.json |
| data/admin_screens.json | the role and writes fields to reuse; M03, M07 and M10 for the access matrix (read only) | repo |
| integrations rows I02, I03, I04, I05, I11, I12, I13, I14, I15, I17, I19 | the names behind the {I..} tokens | data/integrations.json |
| tracker rows W03, W04, W17, W30; gaps G06, G08, G10 | the owed items this work lands at | data/tracker.json, data/gaps.json |
| the builder and renderer behind wireframes_v02.html; scripts/build_admin_wireframes.py; the screen validator; scripts/build_site.py (nav, FORBIDDEN); scripts/build_seats.py or another static page builder (the page shell and the comment box); build_audiences.py | what to reuse; what the review copy and the audience files render | repo |

Do not read the M-series backend docx files.

Field changes to L02 to L09 are in progress (Somil, 7 Oct 2026 call). They reach the board through their own change;
LQ38 holds the list. The board's L02 rows are composite text ("6.5 / 7 / 9 / 8 / 11 %", "6%, 8%"), so the side
screen types one row per value. The board's L04 and L09 example rows name real funds; the side screens use the
synthetic funds of 6.1 and none from the board.

## 3. Deliverables

| id | deliverable | where | phase |
|---|---|---|---|
| DV1 | the side screens as data: 39 screens in the board's screen schema | data/logic_screens.json | A0 to A4 |
| DV2 | Logic tab: the side wireframes on the existing renderer | docs/logic_wireframes.html, scripts/build_logic_wireframes.py | A0 |
| DV3 | Tech page | docs/logic_tech.html, data/logic_tech.json | B0, B1 |
| DV4 | Access page: the access write-up | docs/logic_access.html, data/logic_access.json | B0, B2 |
| DV5 | Walkthroughs page: the call table and four walkthroughs | docs/logic_walk.html, data/logic_walk.json | B0, B3 |
| DV6 | Ops page | docs/logic_ops.html, data/logic_ops.json | B0, B4 |
| DV7 | nav, changelog rows, open items handling | all main-board pages; data/changelog_logic.json; data/logic_gaps.json (A0); section 12 | C2 |
| DV8 | the checks of section 11 as a script | scripts/check_logic.py | C1 |

## 4. The design the wireframes draw

### 4.1 Words

| word | meaning |
|---|---|
| lane | one family of logic values with its own draft and its own version: assumptions, cohorts, funds, market inputs, risk scoring |
| draft | an unpublished set of changes in one lane; a lane has at most one open draft, with one author at a time |
| release | a published lane version, frozen: every value of the lane, who drafted, reviewed and published it, when, why, by which route, and the preview it was approved on |
| route | how a release reaches plans that already exist (4.4) |
| rebuild | the engine running one client's plan again: a review completed (Q01, Q05), a life event (Q06), a sharpen, the annual confirmation (Q04), a questionnaire retake, a staff edit (M03), a push, a stale-cap open |
| pinned | a plan stays on the lane versions it was built on until it next rebuilds |
| stale cap | the most days a plan's latest snapshot may sit behind a live assumptions, cohorts or funds release; past it, the plan rebuilds at the next app open on the inputs on file. Risk scoring and market inputs have no cap: their routes never reach an existing plan by rebuild alone |
| size | how much a rebuild changed for the client: note, outlook, review or urgent (4.5) |
| Hold | a fund status: keep the units, no new money |
| sleeve | the funds and weights that fill one asset class; each model portfolio names the sleeve that fills each of its classes |
| lead fund | the fund with the largest weight in a sleeve |
| model portfolio | a named mix over the six asset classes |
| cohort | one combination of dimension bands; the cohort map points each cohort at a model portfolio |
| guard | a limit a draft must pass before it can be submitted (L09) |
| conflict | a plan the change would leave breaking a rule, found by the preview |
| snapshot | the frozen record of one build of one client's plan |
| snapshot in force | the client's plan: the latest snapshot that is a first plan, an accepted update, a note or an outlook. A note or an outlook is in force as soon as it is written, because nothing in it needs the client's say; a review or urgent update when it is accepted |
| correction | a release that supersedes a paused one |
| letter | the email that explains a house-view release to the clients it will reach |

### 4.2 Rules (Vatsal, 8 Oct 2026)

1. A change is drafted in a lane, validated, previewed, reviewed by a second person and then published as a release.
   The review covers the items, the route and the client reason; a change to any of them after approval returns the
   draft to review.
2. Publish is not apply. A release reaches every plan built or rebuilt from its effective time. A plan that already
   exists stays pinned until it next rebuilds. On the board today L06 recomputes every affected user at publish and
   Q01 runs on a publish; the side wireframes draw the alternative beside it and edit nothing on the board. {I04} is
   described as holding a client's numbers steady between that client's reviews (7 Oct 2026 call; LQ17, LQ18), and
   M2's registry has a change in an assumption set a re-calculation flag on the affected plans.
3. Only the latest live release of each lane is ever run. Older releases are records. A rebuild reads the live
   version of every lane at its start and never mixes two versions of one lane. Risk scoring is the one exception:
   a rebuild reads it as of the client's last questionnaire (rule 10), and the snapshot is stamped with that version.
4. A release is pushed to existing plans only when its route says so (4.4). The test printed on L06: would a prudent
   adviser phone this client about it today.
5. Stale cap: 120 days (rehearsal value). A lapsed or cancelled account's plan freezes and rebuilds on return.
6. The effective time of a release is never earlier than its publish time. Between the publish and the effective
   time of a scheduled release its lane takes no other publish, except an urgent Hold.
7. Every rebuild writes a snapshot: the inputs, the lane versions, the engine version, the cohort per goal, the
   outputs, the actions, the diff shown with a cause on every line (house view, your numbers, your confirmation,
   time passing, staff edit), the size, and what the client did with it. Releases and snapshots are append-only; a
   correction is a new record. The record is the stored output, not a promise to recompute it (on the board today
   L08 reads "the register can reproduce any advice given"; the side wireframes draw the stored output as the
   record).
8. Size decides what the client sees (4.5). Targets always recompute. Instalments change as a set or not at all: when
   any sleeve's amount moves past the tolerance band, every sleeve is restated to its target; when none does,
   nothing changes; a fund on Hold or Exit restates its own sleeve. An update still waiting when the plan next
   rebuilds is superseded, and the new diff is drawn against the snapshot in force (H05 on the board: pending
   updates merge into one).
9. A fund leaving the approved list goes to Hold by default. Exit is a separate decision with its own reason. A Hold
   that would empty a sleeve is blocked until the same draft adds a fund to it. The app never stops a running SIP
   instalment on its own: a client's SIP into a fund on Hold keeps running until the client accepts the update, and
   the update says so in plain words.
10. Risk band thresholds apply only when a client next completes or reconfirms the questionnaire.
11. Market inputs reach new plans and new deployment actions only. Every threshold carries a buffer either side.
12. Undo is three actions, not a mirror rollback. Pause: the release stops being the latest of its lane and rebuilds
    use the one before it. Withdraw: every update built on it and not yet accepted is replaced by a rebuild on the
    release before it, keeping the client's own changes; the client sees "an update was withdrawn" in plan history.
    Correct: a new release; every plan whose snapshot in force was built on the paused one (first plans, accepted
    updates and quiet rebuilds alike) is rebuilt on it at once, and a client is shown an update only if something
    moves for them.
13. Two people on every release: the author cannot review; only the Principal officer publishes. One exception: an
    urgent Hold by the Principal officer alone. It may carry the sleeve weights the rescale needs to pass L09 and
    nothing else; compliance is notified at once; a second person ratifies it within two working days. Unratified,
    it stays in force and shows as overdue on L08, L10 and L11 (LQ30).
14. An assumptions release and a risk scoring release need a compliance acknowledgement before publish: the first
    changes the assumption lines and the reveal (R08, R09, G01's copy), the second the band a client is told (D09).
    Compliance is notified of every other release as it is published, and of an urgent Hold at once. Most plan
    screens carry a compliance flag on the board, so a wider rule would gate every release; LQ45 holds the line
    (logic plan, 8 Oct 2026).
15. One staff identity across the admin screens and the logic panel: the sign-in decided for M03 on 7 Oct 2026.
    Seats are fixed, not user-defined. The greyed control is never the control; the server checks every write. A
    second-factor check is asked again at the guarded actions: publish, schedule, pause, withdraw, an urgent Hold, a
    ratification, a seat change and an export (7 Oct 2026 call for publish; the rest is logic plan, 8 Oct 2026).
16. Cohorts are data: dimensions, a cohort map, model portfolios. Funds attach to sleeves, not to grid cells. A new
    band, or a new dimension on a field the app already holds, is data; a dimension that needs a new question is a
    release of the app.
17. A scheduled review that changes nothing is recorded: "reviewed, no change", signed by the Principal officer.
18. A draft is built on the live version of its lane. If that version moves while the draft is open (an urgent
    Hold), the draft is rebased and its validation and preview run again before it can be reviewed.
19. A client screen never recomputes a plan number when it opens: it shows the client's snapshot in force, and H05
    the update that is waiting. Between rebuilds only net worth today moves, with holdings and prices (4.3; Gaurav,
    7 Oct 2026 call).
20. A house-view change reaches a client on a calendar they were told about (assumptions yearly, effective 1 April;
    the approved list quarterly), inside their own review, with its reason. A change that fails the push test sends
    no notification; its explanation goes out as the letter, by email (7 Oct 2026 call).
21. Sample plans (R12) and the assumption lines (R08, G01) are surfaces of a release: regenerated at its effective
    time and stamped with its date. A saved reveal (X01) is a record of what was shown: it stays as it is, and the
    nudges keep quoting it, until the person sketches again.

### 4.3 What moves, and when (logic plan, 8 Oct 2026; the answer to "19.2 becomes 18 or 22")

| what the client sees | where | it depends on | when it moves | does a release move it |
|---|---|---|---|---|
| net worth today | H01, H02 | holdings and prices | at each refresh (Account Aggregator on open; typed values when the client updates them) | no |
| the plan: projections, what each goal needs, how far it is funded | G03 and the plan tabs, H10 | the client's inputs, the assumptions | at a rebuild only | at the client's next rebuild |
| the target mix per goal | G11 | the risk band, the horizon, the cohort map | at a rebuild only | at the next rebuild; never pushed, a correction apart |
| the funds and the amounts | G13, G14, E11 | the sleeves, the amounts | at a rebuild; a Hold or an Exit by push | by route (4.4) |
| what can be bought now | E03, E11 | fund status | at the publish moment | yes, at once, for a Hold or an Exit |
| the risk band | D09 | the client's answers, the score ranges | at a questionnaire | at the client's next questionnaire |
| lumpsum or staggered | G13 | market inputs | when a new action is made | new plans and new actions only |
| the assumption lines | R08, G01 | the assumptions | at the effective time | yes |
| a new reveal | R09 | five answers, the assumptions | when sketched | new sketches only |
| a saved reveal | X01 and the S2 nudges | what was shown | never, until sketched again | no |
| sample plans | R12 | fixed sample inputs, every lane | regenerated per release | yes, at the effective time |

### 4.4 Routes (Vatsal, 8 Oct 2026; the defaults are proposed)

Size is always decided per client by 4.5; the size column gives the sizes a route can produce. A push rebuilds every
plan it selects; a client is messaged only at review or urgent size.

| change | lane | default route for plans that already exist | sizes it can produce | push can be proposed |
|---|---|---|---|---|
| planning assumptions: returns, inflation, income growth, life expectancy | assumptions | quiet: at next rebuild; reviewed yearly, effective 1 April beside the April SIP step-up on G14; the letter | note, outlook, review | yes |
| rules and thresholds in L02: emergency months, EMI ceiling, floater rule, glide path, the tolerance bands, the stale cap | assumptions | quiet: at next rebuild | note, outlook, review | yes |
| cohort map, a dimension's bands, a portfolio's mix | cohorts | quiet: at next rebuild only; the letter where the author proposes one | note, outlook, review | no; a correction apart |
| risk band thresholds (the score ranges of the risk band dimension) | risk scoring | at the client's next questionnaire (Q04 or a retake); never by a rebuild alone | review, on the client's own confirmation | no |
| fund added, sleeve weights changed | funds | new plans at once; an existing plan takes the new split only when its instalments are restated for another reason (rule 8). Pushed, it restates the sleeve for every plan using it | note; review when pushed | yes |
| fund to Hold, routine | funds | no new order from the publish moment; pushed in waves to clients running a SIP into it; a client with an open action naming it is rebuilt in the same waves and shown the update at the next app open, with no message | review; note for other holders | always pushed |
| fund to Hold, urgent | funds | no new order from the publish moment; pushed at once to clients running a SIP into it; open actions as above | urgent for SIP runners; review for an open action; note for other holders | always pushed |
| fund to Exit | funds | pushed over five working days to holders with verified holdings; a holder without verified holdings sees the locked card (G12a) | urgent | always pushed |
| unknown ISIN classified | funds | quiet: at the next rebuild of the clients holding it | note, review | no |
| a correction (rule 12) | any | every plan whose snapshot in force was built on the paused release, at once; at next rebuild for the rest | note, outlook, review | always pushed |
| market inputs | market inputs | new plans and new deployment actions only; an existing action is never rewritten | none | no |
| guards and constraints (L09) | the lane they guard | none; they gate validation | none | no |
| configuration on M10 (prices, flags) | not a lane | its own effective dates; no rebuild | none | no |
| a new engine version (the maths) | not a lane | to be decided (LQ46); in the examples EN2 changes no output | - | - |

A Hold rescales the sleeve's remaining weights to 100 for new money (largest remainder, whole numbers) and runs L09 on
the result before it is placed; if the rescale breaches L09 the Hold screen says so and asks for weights.

Wave plans, one per pushed release (rehearsal values; LQ14): urgent Hold and correction, everyone at once;
routine Hold, 200 clients an hour from 10:00 to 18:00 IST; Exit, even daily batches over five working days.

### 4.5 Sizes and what the client is told (Vatsal, 8 Oct 2026; the thresholds are rehearsal values)

| size | when | the client started the rebuild (Q01, Q05, Q06, Q04, a sharpen) | the rebuild came from a push or the stale cap | acceptance | messages |
|---|---|---|---|---|---|
| note | nothing moved past the tolerance band | the update screen reads "nothing changes for you", with "assumptions as of <date>" | a plan history entry only | none | none |
| outlook | no instalment changes, but a goal's funded share moved past the band or a goal changed portfolio | the update screen reads "your outlook moved; nothing to do", a cause on every line | the same card on Home at the next open | none; marked seen | none beyond the letter |
| review | an instalment changes (a sleeve is restated), or the risk band changes | the update screen (H05) with a cause on every line; accept refreshes the action plan | Home for S11 (H01e), then H05 | needed | for a pushed update: a push notification when it is ready, then the S11 ladder as on the board; none when the client started the rebuild or the update waits for the next app open |
| urgent | a Hold marked urgent, or an Exit, on a fund the client runs a SIP into (Hold) or holds on verified holdings (Exit) | not applicable | the urgent form of H05; no new order for the fund from the publish moment (E03, E11) | needed | push and WhatsApp at once, email the next morning; a call task for a DIWM client who has not accepted after three days |

Tolerance band: per sleeve, the larger of Rs 1,000 or 10 percent of the running amount; funded share, 5 points.
Amounts are whole hundreds, and a sleeve's funds always add up to its amount (largest remainder). For a client not
executing through the app the comparison is the new target per sleeve against the last target shown.

Causes: every line of a diff carries the cause that moved it (rule 7). Two kinds of line carry a second cause: a fund
that enters or leaves the client's split also names the funds release that changed the sleeve; a risk band that
changes at a questionnaire is tagged your confirmation and also names the risk scoring release when the same score
read differently before.

Why four sizes: under the M4 reconciliation rule most plans deploy the whole surplus, so a change in returns or
inflation leaves the instalments where they are and moves how far they are projected to go. In the rough run behind
6.4 an assumptions change is a note for about 33 plans in 100, an outlook for about 54 and a review for about 13. An
outlook asks for nothing, so it is not chased.

The letter (7 Oct 2026 call): one email per house-view release that changes what clients see. It says what changed,
why, and that the client's plan takes it up at their next review, with the date. It is copy slots, not copy; the
slots live with the other message slots. LQ33 holds when it is sent.

### 4.6 Approval workflow: the life of a draft (logic plan, 8 Oct 2026; the stepwise flow asked for on the call)

| step | who | screen | what must be true to move on | what is recorded |
|---|---|---|---|---|
| 1 open a draft | Logic analyst or Principal officer | the lane's own screen | the lane has no other open draft | the draft, its author, the live version it is based on |
| 2 edit the items, each with a rationale | the author | the lane's own screen | every value passes its hard limit at the field | each item: row, from, to, rationale |
| 3 validate | the author | L05 | no hard failure; every flag carries a typed reason | the list of checks and results |
| 4 preview | the author | L05 | the preview is newer than the last edit; no hard conflict | the preview record |
| 5 propose the route, the client reason and the letter | the author | L05 | the route is one that 4.4 allows for this kind of change | on the draft |
| 6 submit | the author | L05 | steps 3 to 5 hold | state: in review |
| 7 review | the second person | L10 | the reviewer is not the author | approved, or sent back with a comment; the preview panels the reviewer opened (LQ22) |
| 8 acknowledge | Compliance | L10 | asked for an assumptions or a risk scoring release (rule 14) | who and when |
| 9 publish or schedule | Principal officer | L06 | approved; acknowledged where asked; the second-factor check passes | the release and its signed note |

Draft states: open -> validated -> previewed -> in review -> approved (or sent back -> open) -> published; or
discarded. The urgent path collapses steps 1 to 8 into one action by the Principal officer and adds a ratification
after (rule 13).

### 4.7 Change life cycle: the life of a release (logic plan, 8 Oct 2026; the mapping asked for on the call)

| stage | what happens | who or what acts | what the client sees | what is stored |
|---|---|---|---|---|
| 1 published | the release is frozen; it is live from its effective time, scheduled until then | Principal officer; the clock | nothing | the release; audit rows |
| 2 surfaces refresh | the assumption lines and the sample plans regenerate at the effective time (rule 21) | a job | a new visitor sees the new lines | the sample plan versions |
| 3 new plans | every plan built from the effective time uses it | the engine | their first plan | a snapshot |
| 4 existing plans, quiet route | each plan takes it at its next rebuild; the letter goes by email | the client; ops for the letter | by size (4.5) | a snapshot carrying the cause |
| 5 existing plans, pushed route | the rollout job rebuilds the selected plans in waves | a job; the Principal officer watches L11 | review or urgent | snapshots, messages, call tasks |
| 6 the client responds | accept refreshes the action plan; an outlook is marked seen; no answer follows the ladder | the client; the call centre | - | accepted or seen, with the time |
| 7 stragglers | the stale cap rebuilds a plan at the next app open | the app | as stage 4 | a snapshot |
| 8 closed | no active plan is behind it | - | - | the release reads closed |
| 9 if it was wrong | pause, withdraw, correct (rule 12) | Principal officer | "an update was withdrawn"; a corrected update where something moves | an incident; snapshots |

At every stage an adviser or support can open L15 and read which versions a client is on and why their last update
said what it said. Release states: scheduled -> live -> replaced (a later release of its lane is live; plans may
still be on it) -> closed (no active plan is on it); or paused, then corrected. Every transition is an audit row
with who, when and why.

### 4.8 Seats (Vatsal, 8 Oct 2026 for the two-person rule; the seat list is logic plan, 8 Oct 2026)

The eight seats of data/admin_screens.json plus two: Logic analyst and Read only (product and tech sit there).
Marketing and Finance have no access to the logic panel. On the board today L01's "Adviser" (edits the grid) and the
admin Adviser seat (takes calls) share a name; here the editor is the Logic analyst and the Adviser seat only reads.
The table is by action; the seat by screen table is in 5.4.

| action | Principal officer | Logic analyst | Compliance | Adviser, Call centre | Ops | Support | Read only |
|---|---|---|---|---|---|---|---|
| see live logic and its rationale | yes | yes | yes | yes | yes | yes | yes |
| see drafts and previews | yes | yes | yes | no | no | no | yes |
| see the release monitor | yes | yes | yes | no | yes | no | yes |
| open and edit a draft; run validation and preview; propose a route | yes | yes | no | no | no | no | no |
| see named client rows in a preview or the monitor | yes | masked; an unmask is logged | yes | no | masked | no | masked |
| review a draft as the second person | yes, not own draft | yes, not own draft | no | no | no | no | no |
| acknowledge an assumptions or a risk scoring release (rule 14) | no | no | yes | no | no | no | no |
| publish, schedule, pause, withdraw, start a correction | yes | no | no | no | no | no | no |
| urgent Hold on a fund | yes, alone, ratified after | request only | no | no | no | no | no |
| ratify an urgent Hold | not the one who placed it | yes | no | no | no | no | no |
| unknown-ISIN queue | decides by publishing | drafts the classification | no | no | adds facts | no | no |
| mark a calendar item reviewed, no change | yes | no | no | no | no | no | no |
| queue the letter for a release (done in {I14}; L06 shows whether it is queued) | no | no | no | no | yes | no | no |
| export the registers; read the audit rows; add an incident entry | yes | no | yes | no | no | no | read |
| staff and seats: add, change, suspend, revoke; run the access review | yes | no | read; acknowledges an operating seat (LQ42) | no | no | no | no |
| client plan history (L15) | yes | masked | yes | own people | yes | yes | masked |

### 4.9 Launch and later (logic plan, 8 Oct 2026; the answer to "overkill"; LQ37)

The line is drawn by one question: can it be added afterwards without losing anything. A version that was never
stamped on a plan cannot be recovered; a chart over stored rows can be drawn any day.

| piece | at launch | can follow | why |
|---|---|---|---|
| lane versions and frozen releases | yes | | a plan built without them can never be explained |
| the pin: lane versions on every snapshot; a rebuild reads the live versions | yes | | this is what stops the shock |
| a snapshot per rebuild; a PDF for every first plan and every update shown at review or urgent size | yes | | the record of advice |
| an audit row per write and per refused write | yes | | |
| seats, server checks, two people on a release, a second factor at publish | yes | | |
| validation hard stops: sums, coverage, limits, guards | yes | | a wrong value must not be publishable |
| preview panels a, b, d, e, f, g, h: reach, the size split, actions, conflicts, the reference personas, one client by id, surfaces | yes | | the operator must see the effect before signing |
| preview panels c, i, j: distributions and the migration matrix, the load under each route, recent joiners | | yes | more views over the same batch run |
| routes: quiet; Hold, routine and urgent; correction; a scheduled release | yes | | |
| route: Exit, with staged sells | | yes | Hold is the default; the first Exit can wait for it |
| release monitor: counts, failures, the biggest movers, pause, withdraw, correct | yes | | pause is the only brake |
| release monitor: curves | | yes | views |
| release register and audit rows; export | yes | | |
| versions in use as of a date; history of one cohort or one row | | yes | read from stored releases |
| add a band, a map row, a portfolio as data | yes | | |
| add a dimension as data | | yes | the tables carry it from day one; the editor can follow |
| review calendar | | yes | at launch the due items sit on Home |
| staff and seats | yes | | |
| the access review as a screen | | yes | a list and the audit rows serve at first |
| client plan history for staff (L15) | yes | | advisers and support need it from the first update |
| the stale cap | by day 120 | | nothing is 120 days behind before then |
| the letter | yes | | an email slot and a list, not a build |

### 4.10 Open items the pages carry

| id | item | lands on |
|---|---|---|
| LQ1 | to be decided: the default route per kind of change (4.4) | L06 |
| LQ2 | to be decided: the tolerance band values; whether an outlook needs the client's acceptance | L02 |
| LQ3 | to be decided: the stale cap in days | L08 |
| LQ4 | to be decided: Hold as the default when a fund leaves the list, and when an Exit is ever advised (G12 on the board reads: not on the approved list, exit) | L04 |
| LQ5 | to be decided: the dimensions beyond risk band and horizon, and a ceiling on the number of cohorts | L03 |
| LQ6 | to be decided: how many model portfolios, and whether a mix change ever moves existing units | L14 |
| LQ7 | to be decided: who publishes when the principal officer is unreachable | L13 |
| LQ8 | to be decided: whether planning rows in L02 are reviewed by the financial planning function before publish | L02, L10 |
| LQ9 | to be decided: the allowlist's home (M03 as decided on 7 Oct 2026, or the staff and seats screen), and one sign-in for both panels against L01's "same auth as the app" | L13 |
| LQ10 | to be decided: where the client reason slots live and who edits them ({I15} or the panel) | L06 |
| LQ11 | to be verified: what satisfies "digitally signed" for the rationale record of a release | L06 |
| LQ12 | to be verified: whether a change to the score-to-band thresholds needs the client's fresh confirmation before it applies | L03 |
| LQ13 | to be verified: the wording that tells clients how and when a plan is updated (the fixed-fee agreement, gap G06) | client views |
| LQ14 | to be decided: the wave plan per kind of push; a call task after every urgent update or only one not accepted after three days | L11 |
| LQ15 | to be decided: whether the Adviser, Call centre and Support seats read the live rationale in the panel or as content in {I15} | L04, L14 |
| LQ16 | to be decided: the review cadence per lane, and whether the monthly market inputs take the second person | L12, L07 |
| LQ17 | to be decided: where the logic values live at run time: passed by the app to {I04} on every run, or held in {I04} as central defaults with a copy per client (7 Oct 2026 call); which system holds the snapshot of record | Tech page |
| LQ18 | to be verified: whether {I04} can run a stored input snapshot at an as-of date, as a dry run, in a batch; whether a call recalculates or returns the stored result until a review is run; whether a review reads the central value of the day or the client's own copy | Tech page |
| LQ19 | to be verified: whether a running SIP can be redirected through {I02} in one step, and how a Hold reaches a basket on {I03} | L04, client views |
| LQ20 | to be decided: whether a one-fund sleeve is acceptable under the per-product cap | L09 |
| LQ21 | to be decided: whether a scheduled release can be edited before its effective time or must be withdrawn and redrafted; whether a first plan built in that window uses the scheduled values | L06 |
| LQ22 | to be decided: whether approval is blocked until the reviewer has opened every preview panel; a hard limit on a single-class move | L10, L05, L14 |
| LQ23 | to be decided: whether a correction carries its own client explanation and a watch on grievances | L11 |
| LQ24 | to be verified: the record list and the minimum retention against the nine records on the Admin and CRM tab (brief H6); whether a saved reveal is one of them | L08 |
| LQ25 | to be decided: how the principal officer is reached for an urgent request | L04 |
| LQ26 | to be decided: the rule for staging an exit across financial years (not modelled) | L04 |
| LQ27 | to be verified: {I04} run time per plan, and how many runs it takes in parallel | Tech page |
| LQ28 | to be verified: real snapshot and PDF sizes once the plan JSON contract exists (W03) | Tech page |
| LQ29 | to be verified: a second-factor prompt at the moment of publish through {I14} | L06 |
| LQ30 | to be decided: what follows when an urgent Hold is not ratified within two working days | L08, L11 |
| LQ31 | to be decided: whether a self-reported SIP outside the app counts as a running SIP for a Hold | L04 |
| LQ32 | to be decided: whether a staff seat may change an assumption for one client (the engine allows a client-wise change; 7 Oct 2026 call), and with what record | L15 |
| LQ33 | to be decided: when the letter for a house-view release is sent: on the effective date to every plan it will change, or to each client when their plan takes it up | L06 |
| LQ34 | to be decided: whether R12's sample plans are regenerated by a release from fixed sample inputs, or stay hand-maintained content (gap G08) | L05 |
| LQ35 | to be decided: what a saved reveal shows once the assumptions behind it have moved, and whether the nudges keep quoting its numbers | client views |
| LQ36 | to be verified: whether launch runs execution in the app as section E draws, or through a link that opens {I02} with the portfolio loaded (gap G10; 7 Oct 2026 call); what the app then knows about a running SIP | L04 |
| LQ37 | to be decided: the launch cut (4.9) | Tech page |
| LQ38 | to be verified: the field changes to L02 to L09 now in progress (7 Oct 2026 call), so the side screens draw the same rows | L02 |
| LQ39 | to be decided: the equity ceiling per risk band and any other guard a change must pass | L09 |
| LQ40 | to be decided: whether the access write-up for Spinach also lists the app's tier gates | Access page |
| LQ41 | to be decided: session rules for staff: the idle timeout, one session at a time, the age of the second-factor check | L13 |
| LQ42 | to be decided: whether giving someone an operating seat needs a second person (it is the one way around the two-person rule) | L13 |
| LQ43 | to be verified: whether a pushed update (a Hold, an Exit, a correction) reaches a client whose annual confirmation is overdue (Q04 on the board blocks plan re-runs) | L11 |
| LQ44 | to be decided: what the engine does with an amount below a fund's minimum SIP | L09 |
| LQ45 | to be decided: which releases need a compliance acknowledgement before publish, beyond assumptions and risk scoring | L10 |
| LQ46 | to be decided: how a new version of the engine (the maths) is approved, previewed against existing plans and named as a cause on a client's update | L08 |

## 5. The side wireframes (DV1, DV2): the main piece

### 5.1 How they are drawn

- data/logic_screens.json is a list of screens in exactly the schema of data/screens_v02.json: id, sec, title, tier,
  frame "desktop", template, path, purpose, ui, spec (fields, logic, branches, states, dev, forward), compliance,
  events, v02 (status and causes), freeze (open, with its reason). Two fields are added from
  data/admin_screens.json: role (each of the ten seats of 4.8 with one of act, read, "read, own people", read masked,
  none) and writes (action, event, the seats that may do it).
- The page docs/logic_wireframes.html is made by the renderer behind wireframes_v02.html (scripts/renderer_v02.js and
  renderer_v02.css, inlined): the screen list on the left, the screen in the middle, the spec on the right, the
  comment box and the freeze marker as on the board. Board page key "logic_wireframes". The board's own builder
  cannot take a second data file (12.0), so the page is built by scripts/build_logic_wireframes.py, a copy of
  scripts/build_admin_wireframes.py with the seed loading and the draw hooks removed (12.0 names what goes). No new
  renderer and no screen-specific JavaScript.
- Each screen carries a group field (start, logic, change, records, access, reference, client: the first column of
  the 5.2 table, "client views" written "client"). The data keeps sec L and V; the builder sets the page's sec to
  the group so the list on the left reads by what the operator is doing (12.0).
- The existing spec panel has no place for role and writes, so each screen repeats them as two plain lines at the
  top of spec.logic ("Seats: ..." and "Writes: ..."). The fields themselves are read by the Access page.
- A state that matters is its own screen with a letter suffix (L05a), the board's convention. The base screen's
  spec.states lists every state the screen can be in, drawn or not. A variant's first logic line says which state it
  is and what happened just before.
- The ui rows carry typed examples from section 6. Every screen that shows one carries a note: "Example values:
  rehearsal values and illustrative figures per 1,000 plan holders; nothing here is decided."
- A btn or a link points at another side screen, or at a board screen where the target is a client screen. Nothing
  executes. A control is drawn the same for every seat; who may use it is in the spec.
- The open items of 4.10 that land on a screen are lines in its spec.dev, in the exact "to be decided" or "to be
  verified" form.
- Checks are in section 11. No team names in the file; vendor names as {I..} tokens ("WhatsApp" and "email" are
  channels, as in data/v02/states.json).

### 5.2 The screens

Ids L00 to L09 keep their meaning; L10 to L15, the letter variants and V01 to V06 are new and become permanent only
at the merge (a proposed screen that is not accepted keeps its id unused, per the never-renumber rule). The list on
the left of the tab is grouped by what the operator is doing; on the board today L01 lists seven tabs.

| group | id | screen | drawn as | against the board today | launch cut (4.9) |
|---|---|---|---|---|---|
| start | L01 | Home: what needs me, the lanes, the layout | L01, L01a | changed: today a table of three roles and the tab strip | launch |
| logic | L02 | Assumptions | L02, L02a | changed: columns added, values typed and checked | launch |
| logic | L03 | Dimensions and cohort map | L03, L03a, L03b | changed: the grid becomes a registry, a map and a proof | launch; the dimension editor later |
| logic | L14 | Model portfolios | L14, L14a | new: the grid's mixes, named | launch |
| logic | L04 | Funds and sleeves | L04, L04a, L04b | changed: a fund belongs to a sleeve, not to cells | launch |
| logic | L09 | Guards and constraints | L09 | kept, with portfolio guards added | launch |
| logic | L07 | Market inputs | L07 | kept, with buffers and the monthly record | launch |
| change | L05 | Drafts, validation and preview | L05, L05a, L05b | changed: ten preview panels, conflicts among them | launch; three panels later |
| change | L10 | Review | L10, L10a | new | launch |
| change | L06 | Publish | L06, L06a, L06b | changed: route, second factor, the urgent path | launch |
| change | L11 | Release monitor | L11, L11a, L11b | new: with pause, withdraw, correct | launch; curves later |
| records | L08 | Release register and audit | L08, L08a | changed: versions in use, incidents, audit rows | launch; the as-of view later |
| records | L15 | Client plan history | L15, L15a, L15b | new; M03's plan versions tab at the merge | launch |
| records | L12 | Review calendar | L12 | new | later |
| access | L13 | Staff and seats | L13 | new | launch |
| reference | L00 | Engine map | L00 | kept, with the life cycle and the surface map | launch |
| client views | V01 to V06 | six phone screens (5.5) | V01 to V06 | proposals for H05, plan history, the letter and X01 | launch |

Thirty-three panel screens and six client views.

### 5.3 Screen by screen

For each screen: the blocks top to bottom, what each drawn screen shows (examples from section 6), the checks (they
go into spec.logic), the writes with their seats, what differs from the board, the open items.

L01 Home
- Blocks: (1) Needs you: the worklist of the seat signed in. Principal officer: drafts by others waiting for review,
  approved drafts waiting for publish, urgent requests, a Hold to ratify, calendar items due or overdue, releases
  with failures or paused, the access review when due. Logic analyst: own drafts and their state (sent back, with
  the comment), reviews waiting, a Hold to ratify, calendar items, the unknown-ISIN queue. Compliance:
  acknowledgements waiting, incidents open, unratified Holds. Ops: queue items that need facts, what goes out this
  week. (2) Lanes: one row per lane: the live version and since when, plans on it and behind it (illustrative), the
  open draft with its author and state, a scheduled release with its effective date, the next review due. (3) Going
  out: releases in rollout, with progress and a link to L11. (4) Layout and seats: the four groups, the board's three
  roles mapped to the seats, a link to L13.
- Drawn: L01, a working day (7 May 2027): a fund draft waiting for review, the quarterly fund review open on the
  calendar, a release going out. L01a, an urgent day (24 Sep 2027, 18:00): an urgent Hold in force, its rollout going
  out, its ratification overdue.
- Writes: none; every row links to the screen that acts on it.
- Against the board: L01 today is a documentation screen; its role table moves to L13 and the Access page.

L02 Assumptions
- Blocks: (1) the rows in four groups: returns; inflation and growth; planning rules and thresholds; change rules
  (the tolerance bands, the stale cap). Columns: assumption, live value, draft value, unit, effective from, domain
  (planning or investment), route (4.4), limits (hard range, soft step), cadence with last reviewed and next due,
  used in (screen ids), changed by (release). (2) one row: the value's history by release with the reason each time,
  and the screens that show it. (3) the draft bar: who holds the draft, its state, a link to L05.
- Values are typed, not picked, and checked at the field (7 Oct 2026 call): a number in the row's unit, inside the
  hard range.
- Drawn: L02, the live values (20 Apr 2027). L02a, a draft open (10 Mar 2028): equity return 11.0 to 10.0 and expense
  inflation 6.0 to 6.5, each with its typed reason; 65 typed for inflation refused at the field (hard range 0 to 15).
  In spec.states and not drawn: a scheduled release pending, the row reading "6.0 now, 6.5 from 1 Apr 2028"; read by
  another seat, live values and rationale only.
- Checks: the hard range per row; the soft step per row.
- Writes: open a draft; edit a row in the draft with a rationale; drop a row from the draft (Logic analyst,
  Principal officer).
- Against the board: the board's rows and its three columns are kept, one typed row per value (section 2); the tax
  slabs row is listed as "row to drop at the merge: its section was dropped (brief B4)". The thresholds and buffers
  of the market inputs are rows here, as L07 on the board says.
- Open: LQ2, LQ8, LQ38.

L03 Dimensions and cohort map
- Blocks: (1) Dimensions: dimension, source field and its screen, bands with bounds, lane, since. Risk band shows
  its score ranges, which belong to the risk scoring lane; horizon reads years to the goal. (2) The cohort map: the
  board's grid while there are two dimensions (each cell names its portfolio and shows the mix), a list of rows once
  there are more; each cohort shows the goals in it per 1,000 plan holders (illustrative) and a "thin" mark under
  30 (rehearsal value). (3) Coverage proof: every combination of bands resolves to exactly one row; the most specific
  row wins. (4) What is data and what is an app release (rule 16). (5) History of one cohort: by release, the
  portfolio it pointed at, the mix, the reason, the goals in it then.
- Drawn: L03, launch: nine cohorts on seven rows, the proof passing, the history of Moderate x Long as the example for
  block 5. L03a, a draft adding the band "Very long: over 7" (1 Nov 2027): the new column, Aggressive x Very long
  empty so coverage fails, Conservative x Very long pointed at MP8 so its guard fails. L03b, a draft adding a third
  dimension, goal priority (21 Feb 2028): twenty-four cohorts as a list, about five marked thin; the draft is
  discarded on 25 Feb. In spec.states and not drawn: a risk scoring draft, with the line "nobody changes band today".
- Checks: the bands of a dimension tile its range with no gap and no overlap (a band owns its upper bound);
  coverage; every row's portfolio exists; the equity ceiling of each risk band (L09).
- Writes: add a band; edit a bound; add a dimension from the fields the app already holds; add, edit or retire a map
  row (a cohorts draft). Edit the score ranges (a risk scoring draft). Logic analyst, Principal officer.
- Against the board: the three tables of today's L03 are the launch state; the grid's mixes move to L14 as named
  portfolios, so twenty cohorts do not mean twenty mixes to maintain.
- Open: LQ5, LQ12.

L14 Model portfolios
- Blocks: (1) the list: portfolio, mix over the six classes, the sleeve that fills each class, blended return under
  the live assumptions (example), cohorts pointing at it, goals in it per 1,000 plan holders (illustrative). (2)
  one portfolio: the mix editor with the sum shown as it is typed; "against live": each class from, to and the move
  in points; both rationales (internal, client); its history by release.
- Drawn: L14, launch: MP1 to MP7. L14a, MP6 open in a draft (29 Nov 2027): keyed 0/24/10/10/56/0, the sum 100, the
  9-point flag on two classes with its typed reason.
- Checks: the sum is 100 (hard); no class below 0 (hard); a class with no sleeve is 0 (hard); the equity ceiling of
  every risk band whose cohorts point at it (hard); a move of 5 points or more on one class asks for a typed reason
  (soft; LQ22).
- Writes: add or edit a portfolio in the draft; retire one that no map row points at (Logic analyst, Principal
  officer).
- Open: LQ6, LQ15.

L04 Funds and sleeves
- Blocks: (1) Sleeves: sleeve, asset class, the portfolios that use it, funds and weights, lead fund. (2) Funds:
  name, ISIN, category (fetched; an override is logged on L09), status (approved, hold, exit, retired) with since and
  the release, minimum SIP, exit-load window, both rationales; a fund's status history. (3) Add a fund by ISIN: the
  facts come from the instrument master ({I05}); an ISIN the master does not know, or a plan that is not direct, is
  refused at the field (7 Oct 2026 call; E02 on the board: direct plans only). (4) Exposure, per fund: per 1,000 plan
  holders, how many are advised into it, run a SIP into it, hold an open action naming it, hold units (verified, not
  verified). (5) Unknown-ISIN queue: ISIN, the name on the statement, holders,
  the facts ops added, the proposed class (known and not approved, legacy hold, unknown).
- Drawn: L04, launch: the sleeves and funds of 6.1. L04a, the flexi cap fund's exposure with an urgent Hold request
  waiting (22 Sep 2027, 10:05). L04b, the unknown-ISIN queue with two items and the facts ops added.
- Checks: a sleeve's weights sum to 100; the L09 limits; a Hold that would empty a sleeve is blocked (rule 9); the
  ISIN is in the master and the plan is direct.
- Writes: add a fund to a sleeve; change weights; change a status (Hold, Exit); class a queue item (a funds draft;
  Logic analyst, Principal officer). Request an urgent Hold (Logic analyst). Add facts to a queue item (Ops).
- Against the board: today's L04 assigns an instrument to grid cells with a weight; here a fund belongs to a sleeve
  and a portfolio names its sleeves, so one fund change is one edit however many cohorts exist. "Staged" and
  "Published" become the draft and the release.
- Open: LQ4, LQ15, LQ19, LQ25, LQ26, LQ31, LQ36.

L09 Guards and constraints
- Blocks: (1) fund constraints, in the funds lane: the most weight in one fund of a sleeve that has more than one
  (60; rehearsal value, the board reads ___ %); the most direct shares within equity (the board's row, drawn with no
  data: direct shares are not in the rehearsal's sleeves); the minimum SIP per fund. (2) portfolio guards, in the
  cohorts lane: the equity ceiling per risk band (Conservative 30, Moderate 80, Aggressive 100; rehearsal values);
  a class with no sleeve is 0. (3) the board's category table (fetched category, override, breach), filled with the
  script's funds.
- Drawn: L09, with one breach showing from an open funds draft: weights 65 / 15 / 10 / 10 against the limit of 60.
- Checks: a draft that loosens a guard and passes only because of that is flagged "passes on its own change" for the
  reviewer.
- Writes: edit a value in a draft of its lane; override a category, logged (Logic analyst, Principal officer).
- Against the board: the three constraints and the category table are kept. The guards answer the conflict question
  of the 7 Oct 2026 call: a mix that breaches a risk band cannot be submitted.
- Open: LQ20, LQ39, LQ44.

L07 Market inputs
- Blocks: (1) the month's four values with their thresholds, the buffer either side and the rule each gives. (2) by
  month: the fifteen months, the rule in force each month, the months where it changed. (3) the line "new plans and
  new deployment actions only; an existing action is never rewritten".
- Drawn: L07 at 1 Nov 2027: the PE at 26.4 has passed the buffer and the rule for new actions reads "stagger
  strongly"; the by-month table shows MI05 inside the buffer with no change, and one entry that ran late (MI09).
- Checks: each value inside its hard range; a monthly move beyond the soft step asks for a typed reason.
- Writes: enter the month's values in the draft (Logic analyst, Principal officer).
- Against the board: today's four rows and rules are kept; the buffers, the monthly record and the second person are
  added.
- Open: LQ16.

L05 Drafts, validation and preview
- Blocks: (1) Drafts: one row per lane: the draft, the live version it is based on, the author, the state, when it
  was last validated and previewed. (2) Items: row, from, to, rationale. (3) Validation: every check with pass, fail
  or flag; a fail blocks; a flag needs a typed reason. (4) Preview, ten panels:
  - a. reach: how many plans the release would change, under the route proposed (per 1,000, illustrative);
  - b. the size split: note, outlook, review, urgent;
  - c. what moves: funded share and instalments in buckets, by horizon; the migration matrix for a cohort change;
  - d. actions: sells and exit-load flags, SIP changes, the average change (the board's three rows);
  - e. conflicts: plans the change would leave breaking a rule: a goal with no cohort, a risk band over its ceiling,
    a fund under its minimum SIP, an engine error. A hard conflict blocks submit; amounts under a fund's minimum
    SIP are counted and listed (LQ44);
  - f. the six reference personas, before and after; they are also the sample plans of R12 (LQ34);
  - g. one client, by id (masked for some seats) or a persona: old against new mix and action plan (the board's
    input and chart);
  - h. surfaces touched: the screens and content that show a changed number (5.6), and whether the release needs a
    compliance acknowledgement (rule 14);
  - i. load and timing: the quiet route week by week against a push on day one: rebuilds, updates to accept,
    messages, call tasks, tickets;
  - j. recent joiners: plans built in the 30 days before the effective date.
  (5) The proposal: route, effective time, client reason slot, the letter.
- Drawn: L05, the assumptions draft of 10 Mar 2028, validated and previewed: the ten panels with the figures of 6.4,
  the quiet route beside a push on day one, the proposal filled in. L05a, validation failed (1 Nov 2027): coverage and
  a guard failing on the cohorts draft. L05b, a draft sent back by the reviewer with the comment (7 May 2027), read
  only until edited. In spec.states and not drawn: no draft; a preview running as a job; a draft rebased after an
  urgent Hold moved its lane; a draft discarded.
- Checks, by lane: sums; hard ranges; coverage; guards; the L09 limits; the ISIN known and direct; a Hold that
  empties a sleeve; a draft whose base is no longer live; a preview older than the last edit.
- Writes: run validation; run preview; set the proposal; submit; discard (the author: Logic analyst or Principal
  officer).
- Against the board: today's L05 has the staged list, four counts, one client or persona, and Publish. Here Publish
  sits two screens on, behind the second person, and conflicts is the panel asked for on the 7 Oct 2026 call.
- Open: LQ22, LQ34.

L10 Review
- Blocks: (1) Waiting for me: drafts by others; an urgent Hold to ratify, with its clock; for Compliance, the
  acknowledgements. (2) one draft: the items; validation with the author's reason for each flag; the preview, each
  panel marked opened or not; the proposal; the surfaces and the acknowledgement. (3) the decision.
- Drawn: L10, one draft waiting (17 Mar 2028, the assumptions draft): the diff, validation with the author's reasons,
  the ten panels each marked opened or not, the proposal, the acknowledgement of 14 Mar, approve and send back. L10a,
  two examples of what the second person cannot and must do, each with its date: a draft the viewer wrote, reading
  "you wrote this" with no approve (4 May 2027); the urgent Hold of 22 Sep 2027 waiting for ratification, overdue on
  24 Sep.
- Writes: approve; send back with a comment (Principal officer, Logic analyst; never the author). Ratify an urgent
  Hold (the second person). Acknowledge (Compliance).
- Open: LQ8, LQ22, LQ45.

L06 Publish
- Blocks: (1) Ready: approved drafts. (2) one release: what changes; the route as approved, with the push test
  printed beside it; the wave plan; the effective time (now or scheduled, never earlier than now); the client reason
  slot and how it reads at each size; the letter and whether ops has queued it; the acknowledgement; the release
  note to sign; the second-factor prompt. (3) Urgent Hold: the fund, its exposure, the reason, the weights if the
  rescale breaches L09, the client
  reason, who is told, the ratify clock. (4) Scheduled: releases waiting for their effective time.
- Drawn: L06, ready to publish (20 Mar 2028, the assumptions release): the route as approved with the push test beside
  it, the effective time 1 Apr 2028 00:00, the client reason slot at each size, the letter queued, the
  acknowledgement, the release note, the second-factor prompt. L06a, the urgent Hold path (22 Sep 2027, 10:40): the
  fund, its exposure, the rescale to 75 / 25 breaching L09, the weights asked for and set to 60 / 40. L06b, two
  examples of waiting, each with its date: a release approved and not yet acknowledged, publish disabled (20 Dec
  2027); a release scheduled and not editable (22 Mar 2028).
- Writes: publish; schedule; urgent Hold (Principal officer).
- Against the board: "Notify affected users: push and email" becomes the route and the size; "Roll back to v13"
  becomes pause, withdraw and correct on L11.
- Open: LQ1, LQ10, LQ11, LQ21, LQ29, LQ33.

L11 Release monitor
- Blocks: (1) header: release, lane, route, live since, status, an unratified mark. (2) Reach: plans on it and
  behind it; by day: rebuilt, shown, read, accepted or seen; by size (per 1,000, illustrative). (3) Failures: engine
  failures per client, with retries. (4) Biggest movers. (5) Tickets and call tasks tagged to it. (6) Controls:
  pause, withdraw, start a correction, each with a confirmation that says what it will do and to how many.
- Drawn: L11, the urgent Hold three days in (25 Sep 2027): per 1,000 plan holders 500 reached, 300 accepted by day 2,
  105 call tasks created, 40 tickets expected; one rebuild failed at 10:46 and succeeded on retry at 10:52; the
  ratification overdue. L11a, the wrong release (16 Dec 2027, 11:05): the biggest movers opened from a ticket, about
  14 plans per 1,000 built on it, pause pressed and the withdraw confirmation open, saying what it will do and to how
  many. L11b, a quiet release four weeks in (28 Apr 2028): about one existing plan in six rebuilt; nobody messaged
  beyond the letter.
- Writes: pause; withdraw; start a correction (Principal officer).
- Open: LQ14, LQ23, LQ30, LQ31, LQ43.

L08 Release register and audit
- Blocks: (1) Register: every release: id, lane, version, what changed, drafted, reviewed and published by,
  published at, effective from, route, reason, status; open one for its frozen record: the values, the diff, the
  preview it was approved on, the signed note, the acknowledgement, the monitor's summary. (2) Versions in use: per
  lane, plans on each version (illustrative), days behind, the stale-cap list, frozen accounts, plans blocked from
  rebuilding and why; as of a date. (3) Incidents. (4) Audit rows: who, seat, when, what, before, after, reason;
  refused attempts marked. (5) Records kept: the board's nine-record card. (6) Export for the advice register.
- Drawn: L08 at 30 Apr 2028: the twelve releases of 6.2 in the register; versions in use per lane with the share of
  plans on each; one plan past the stale cap, one frozen, one blocked by an overdue annual confirmation; the incident
  of 17 Dec 2027; audit rows with one refused attempt marked. L08a, the frozen record of REL08: its values, the diff,
  the preview it was approved on, who signed, the pause and the withdrawal, the release that corrected it, the
  incident entry.
- Writes: export (Principal officer, Compliance); add an incident entry (Compliance, Principal officer).
- Against the board: today's version table and the nine-record card are kept; "the register can reproduce any advice
  given" becomes "the register holds what was advised" (rule 7).
- Open: LQ3, LQ24, LQ30, LQ46.

L15 Client plan history (at the merge, M03's plan versions tab)
- Blocks: (1) find a client by id; the example clients listed. (2) the pin: the versions the client is on
  against the live ones, days behind, the next review due, anything blocking a rebuild; per sleeve, the funds
  version its split was last restated on, which can be older than the plan's (rule 8). (3) the timeline: a saved
  reveal if there was one, then every snapshot: when, the trigger, the lane versions, the engine version, the size,
  the causes, what the client did. (4) one snapshot: the inputs used, cohort and portfolio per goal, what each goal
  needs and gets, the instalments per fund, the actions, the diff as shown with a cause per line, the messages
  sent, the PDF stub. (5) compare two snapshots. (6) as of a date: which snapshot was the client's plan that day.
- Drawn: L15, C01's timeline and pin (6.3). L15a, C01's snapshot of 12 May 2027 open: the inputs, cohort and portfolio
  per goal, the instalments per fund, the diff with two causes. L15b, the wrong release as two clients lived it: C11
  accepted it and was corrected; C12's update was withdrawn in time.
- Writes: none.
- Open: LQ32.

L12 Review calendar
- Blocks: each lane and row with its cadence, last reviewed and next due; due and overdue marked; the "reviewed, no
  change" entries with their signature; the promise to clients that each cadence stands behind (G13 on the board
  reads "reviewed every quarter").
- Drawn: L12 at 1 Mar 2028: the annual assumptions review open a month ahead; the fund review of 7 Feb closed by
  REL11; the "reviewed, no change" entries of 1 Apr and 5 Nov 2027; one monthly entry that ran late.
- An item is overdue when it is not closed 14 days after its due date; a monthly item, from the next working day
  (rehearsal values).
- Writes: mark reviewed, no change (Principal officer); open a draft from a due item (Logic analyst, Principal
  officer).
- Open: LQ16.

L13 Staff and seats
- Blocks: (1) Staff: label, seats, status (active, suspended, revoked), added by and when, last sign-in, second
  factor on. (2) What each seat may do: 4.8 and 5.4 as one matrix for the logic panel and, read only from
  data/admin_screens.json, for M03, M07 and M10. (3) The two-person rule and who stands in (LQ7). (4) Access
  reviews, each with its rows and outcomes.
- Drawn: L13 at 15 Oct 2027: the staff list of 6.1, one seat suspended at the July access review, Logic analyst 02
  added on 4 Oct and acknowledged by compliance, the seat matrix, access review 2 in progress.
- Writes: add; change seats; suspend; revoke; run the access review (Principal officer). Acknowledge an operating
  seat (Compliance; LQ42).
- Against the board: L01's three roles become seats; M14 (roles and permissions) was folded into M03 on 5 Oct 2026,
  and LQ9 holds where the allowlist lives.
- Open: LQ7, LQ9, LQ41, LQ42.

L00 Engine map
- Blocks: (1) the board's table of steps, read at build time, with two columns added: the lane that feeds the step
  and how a change in it reaches an existing plan (4.4). (2) four rows added: release, pinned plan, snapshot,
  rollout. (3) what moves, and when (4.3). (4) the change life cycle (4.7). (5) the surface map (5.6).
- Drawn: L00, one screen. Writes: none.

### 5.4 Seat by screen

act, read, own = read own people, masked = read masked, - = none. For Adviser, Call centre, Ops and Support, "read"
on L02, L03, L14, L04, L09 and L07 means the live values and rationale only; draft rows are not sent.

| screen | Principal officer | Logic analyst | Compliance | Adviser | Call centre | Ops | Support | Read only | Marketing | Finance |
|---|---|---|---|---|---|---|---|---|---|---|
| L01 | read | read | read | read | read | read | read | read | - | - |
| L02 | act | act | read | read | read | read | read | read | - | - |
| L03 | act | act | read | read | read | read | read | read | - | - |
| L14 | act | act | read | read | read | read | read | read | - | - |
| L04 | act | act | read | read | read | act | read | read | - | - |
| L09 | act | act | read | read | read | read | read | read | - | - |
| L07 | act | act | read | read | read | read | read | read | - | - |
| L05 | act | act | read | - | - | - | - | masked | - | - |
| L10 | act | act | act | - | - | - | - | read | - | - |
| L06 | act | read | read | - | - | - | - | read | - | - |
| L11 | act | masked | read | - | - | masked | - | masked | - | - |
| L08 | act | read | act | - | - | - | - | read | - | - |
| L15 | read | masked | read | own | own | read | read | masked | - | - |
| L12 | act | act | read | - | - | read | - | read | - | - |
| L13 | act | read | act | - | - | - | - | - | - | - |
| L00 | read | read | read | read | read | read | read | read | - | - |
| V01 to V06 | read | masked | read | own | own | read | read | masked | - | - |

On L08 the Logic analyst sees the register and the versions in use, not the audit rows. On L13 the Logic analyst
sees the staff list and the seat matrix, not the access reviews. "own" is written "read, own people" in the data.

### 5.5 Client views

Six phone screens in the same file, section V, each a proposal for a screen the client sees; each links to the board
screen it would change and carries its own comment box. Copy is slots, never final wording.

| id | view | example | shows |
|---|---|---|---|
| V01 | the update screen, outlook (H05) | C04, 10 Apr 2028 | "your outlook moved; nothing to do"; the work-optional goal from about 70 to about 54 percent funded; the cause: house view, the assumptions review of 1 April; "assumptions as of 1 Apr 2028"; no accept |
| V02 | the update screen, review (H05) | C01, 12 May 2027 | the instalments before and after; two causes: your numbers (the raise) and house view (a fourth fund in the equity core); accept |
| V03 | the update screen, urgent (H05) | C01, 22 Sep 2027 | the Hold in plain words; the SIP keeps running until accepted; the new split; accept |
| V04 | plan history | C12 | entries by date with size and cause; "an update was withdrawn" on 16 Dec 2027 |
| V05 | the letter, an email | REL12 | what changed, why, and when this plan takes it up (the date of the next review) |
| V06 | the saved reveal (X01) | a person who saved a reveal on 12 Oct 2027 and comes back on 20 Apr 2028 | "sketched on 12 Oct 2027"; sketch again; the nudges quote the saved numbers until then (LQ35) |

In spec.states and not drawn: the update screen reading "nothing changes for you" (a note); Home with an update
waiting at review and at urgent size (H01e); an order screen that no longer offers a fund on Hold (E03, E11); the
locked card for a holder without verified holdings at an Exit (G12a); the sample plan with "built on assumptions as
of <date>" (R12).

### 5.6 The surface map

Drawn on L00 and named in the preview's surfaces panel.

| lane | client screens that show a number from it | staff views | content and messages |
|---|---|---|---|
| assumptions | R08 and G01 (the lines), R09 (new sketches), G03 and the plan tabs, H10, H05 | L15; M03's plan versions tab | the sample plans (R12); the letter |
| cohorts | G11, G13, G14, H05 | L15, L03 | the sample plans; the letter |
| funds | G12, G13, G14, E03, E11, H05 | L15, L04 | the sample plans; the Hold and Exit messages; the call lines |
| risk scoring | D09, G11, H05 | L15 | - |
| market inputs | G13 (the timing text) | L15, L07 | - |

## 6. Example content (typed, not generated)

One example year so that the screens agree with each other: the logic at launch (6.1), twelve releases (6.2), four
clients (6.3), a handful of figures (6.4). Launch is 1 Feb 2027 (the board's target). A working day is Monday to
Friday; public holidays are not modelled. The year is compressed: it holds more change than a real year is likely to
(on the 7 Oct 2026 call an equity return expectation was said to have moved once in four years). LQ16 holds the real
cadence.

### 6.1 Logic content at launch (REL01; rehearsal values throughout)

REL01 is the one time five lane versions publish together: as-1, co-1, fu-1, rs-1 and the launch market values
(MI00).
Values already on the board's L screens are kept as they are; anything new is a rehearsal value.

Assumptions lane (as-1): the L02 rows on the board with their values (returns 6.5 / 7 / 9 / 8 / 11 for liquid debt,
debt, hybrid, commodities, equity; REITs and InvITs as the board reads, 9 in the arithmetic; expense inflation 6,
education inflation 8; income growth 8; life expectancy 85; emergency months 6; work-optional age 60; EMI ceiling 30;
glide path 3), one typed row per value, plus per row: domain (planning or investment), route (4.4), limits,
cadence, last reviewed, used in (screen ids). Limits: a return between 0 and 20 and an inflation rate between 0 and 15
(hard); a move of 0.5 or more
asks for a typed reason (soft). The tolerance bands (4.5), the stale cap and the thresholds and buffers of the
market rule (L07 on the board: "thresholds editable in L02") sit in this lane.

Risk scoring lane (rs-1): Conservative 8 to 15, Moderate 16 to 24, Aggressive 25 to 32 (the board's L03
placeholders). These ranges are the boundaries of the risk band dimension: they are shown and edited on L03 in a
risk scoring draft and follow that lane's route.

Cohorts lane (co-1): two dimensions, nine cohorts, seven portfolios, seven map rows. A band owns its upper bound:
Short is years <= 1, Medium is 1 < years <= 3, Long is years > 3.

| dimension | source field | bands |
|---|---|---|
| risk band | the questionnaire score (D08a to D08h), ranges from the risk scoring lane | Conservative, Moderate, Aggressive |
| horizon | years to the goal (D07a, D07b) | Short up to 1, Medium 1 to 3, Long over 3 |

| portfolio | liquid debt / debt / hybrid / commodities / equity / REITs and InvITs | sleeves it names | cohorts pointing at it |
|---|---|---|---|
| MP1 Short | 100/0/0/0/0/0 | liquid | Short, any risk band (one map row with "any") |
| MP2 Medium conservative | 20/70/10/0/0/0 | liquid; debt, near; hybrid | Conservative x Medium |
| MP3 Medium moderate | 10/60/30/0/0/0 | liquid; debt, near; hybrid | Moderate x Medium |
| MP4 Medium aggressive | 10/50/40/0/0/0 | liquid; debt, near; hybrid | Aggressive x Medium |
| MP5 Long conservative | 10/40/20/10/20/0 | liquid; debt, far; hybrid; commodities; equity core | Conservative x Long |
| MP6 Long moderate | 0/15/10/10/65/0 | debt, far; hybrid; commodities; equity core | Moderate x Long |
| MP7 Long aggressive | 0/5/5/10/80/0 | debt, far; hybrid; commodities; equity core | Aggressive x Long |

A mix must sum to 100; a move of 5 points or more on one class asks for a typed reason (soft; LQ22).

Funds lane (fu-1): every fund is synthetic and named by category, "Seed <category> Fund NN", in the seed's ISIN
scheme; no real fund name appears. Fund statuses: approved, hold, exit, retired. A holding outside the list is classed
known and not approved, legacy hold, or unknown. Every fund carries a minimum SIP of Rs 500 and an exit-load window
of 12 months (rehearsal values on synthetic funds). The unknown-ISIN queue of L04b holds two examples: one
worth Rs 80,000 bought Mar 2024, one worth Rs 50,000 bought Aug 2023.

| sleeve | asset class | used by | funds and weights at launch |
|---|---|---|---|
| liquid | liquid debt | MP1 to MP5 | one liquid fund 100 |
| debt, near | debt | MP2, MP3, MP4 | one short duration fund 100 |
| debt, far | debt | MP5 to MP8 | short duration 60, gilt 40 |
| hybrid | hybrid | MP2 to MP8 | one hybrid fund 100 |
| commodities | commodities | MP5 to MP9 | one gold ETF 100, bought through {I03} |
| equity core | equity | MP5 to MP9 | index 50, flexi cap 30, mid cap 20 |
| none | REITs and InvITs | - | no sleeve: the class is 0 in every portfolio |

Guards and constraints (L09; rehearsal values): at most 60 percent in one fund of a sleeve that has more than one;
one-fund sleeves are drawn with LQ20; the equity ceiling per risk band is Conservative 30, Moderate 80, Aggressive
100; a class with no sleeve is 0. Direct shares are not in the rehearsal's sleeves; L09's second row is drawn with
no data.

Market inputs lane: the board's L07 values at launch (Nifty PE 22.4, 10-year G-sec 7.0, repo 6.0, FD reference 6.8)
are MI00, published inside REL01; each month's entry is one release of this lane and its id is the version id.
Buffer: 1.0 either side of 18 and of 25, so the rule moves up past 26 and comes back under 24. The PE by month
(assumption), MI01 to MI15: 22.4, 22.9, 23.3, 24.1, 25.6, 24.8, 24.2, 24.9, 25.4, 26.4, 26.1, 25.2, 24.6, 23.8,
23.5. MI05 crosses 25 inside the buffer (no rule change); MI10 passes 26 (the rule for new deployment actions moves
to "stagger strongly"); MI14 falls under 24 (the rule returns). The other three values barely move in the examples.

Reference personas: two are typed for the preview's panel f, a Moderate with a goal 5 years out and a Moderate who
deploys the whole surplus into one long goal; each shows its mix and instalments before and after the draft. Under
LQ34 they are also sample plans of R12.

Staff: Principal officer 01, Logic analyst 01, Logic analyst 02 (4 to 27 Oct 2027), Compliance 01, Ops 01, Support
01, Call centre 01, Adviser 01 to 06, Read only 01 (from 3 Mar 2027).

### 6.2 The example year (typed rows for the register on L08 and the calendar on L12)

Staff are written by seat: PO is Principal officer 01, LA is Logic analyst 01, CO is Compliance 01.

| date | id | lane | what | drafted -> reviewed -> published | route | walkthrough |
|---|---|---|---|---|---|---|
| 25 Jan 2027 | REL01 | all | launch content (6.1) | LA -> PO -> PO | new plans | - |
| first working day, Feb 2027 to Apr 2028 | MI01 to MI15 | market inputs | the month's four values; MI09 is entered on 6 Oct 2027, three working days late | LA -> PO -> PO | new plans and new deployment actions | - |
| 3 Mar 2027 | - | seats | Read only 01 added | PO | - | - |
| 1 Apr 2027 | - | assumptions | annual review: reviewed, no change | PO | - | - |
| 10 May 2027, effective 10:00 | REL02 (fu-2) | funds | a large cap fund joins the equity core: 45 / 25 / 15 / 15 (index, flexi cap, mid cap, large cap) | LA -> PO -> PO | quiet | - |
| 16 Jun 2027, effective 10:00 | REL03 (fu-3) | funds | two unknown ISINs classified: one known and not approved, one legacy hold | LA -> PO -> PO | quiet, at the holders' next rebuild | - |
| 15 Jul 2027 | - | seats | access review 1: Adviser 06, idle 90 days, is suspended | PO | - | - |
| 20 Jul 2027 | EN2 | engine | the engine version moves and changes no output; it has no draft, review or route here (LQ46), so snapshots show it moving on its own | - | - | - |
| 9 Aug 2027, effective 09:30 | REL04 (fu-4) | funds | routine Hold on the mid cap fund; the sleeve rescales to 53 / 29 / 18 (index, flexi cap, large cap) | LA -> PO -> PO | Hold, routine; waves from 10:00 | - |
| 22 Sep 2027, effective 10:40 | REL05 (fu-5) | funds | urgent Hold on the flexi cap fund, placed alone; the rescale (75 / 25) breaches L09, weights set to 60 / 40 (index, large cap) | PO alone; ratification due 24 Sep, given 27 Sep by LA | Hold, urgent | Y02 |
| 27 Sep 2027, effective 15:00 | REL06 (fu-6) | funds | a second flexi cap fund joins: 50 / 25 / 25 (index, large cap, flexi cap B) | LA -> PO -> PO | quiet | Y02 |
| 4, 15 and 27 Oct 2027 | - | seats | Logic analyst 02 added on 4 Oct; access review 2 on 15 Oct; Logic analyst 02 revoked on 27 Oct | PO | - | - |
| 5 Nov 2027 | - | funds | quarterly review: reviewed, no change | PO | - | - |
| 8 Nov 2027, effective 10:00 | REL07 (co-2) | cohorts | the horizon dimension gains "Very long: over 7" (Long becomes 3 to 7); MP8 Very long moderate 0/10/5/10/75/0 and MP9 Very long aggressive 0/0/0/10/90/0 added; three map rows (Conservative x Very long points at MP5) | PO -> LA -> PO | quiet, with the letter | Y03 |
| 30 Nov 2027, effective 16:00 | REL08 (co-3) | cohorts | MP6 keyed 0/24/10/10/56/0 in error (0/15/10/8/67/0 was meant) | LA -> PO -> PO | quiet, no letter proposed | Y04 |
| 16 Dec 2027 | - | cohorts | REL08 paused 11:05, withdrawn 11:40; rebuilds use co-2 until the correction | PO | - | Y04 |
| 17 Dec 2027, effective 12:00 | REL09 (co-4) | cohorts | the correction: MP6 at 0/15/10/8/67/0 | LA -> PO -> PO | correction; its explanation is LQ23 | Y04 |
| 3 Jan 2028, effective 10:00 | REL10 (rs-2) | risk scoring | thresholds move by one point: Conservative 8 to 16, Moderate 17 to 25, Aggressive 26 to 32 | LA -> PO -> PO; CO acknowledges | at the next questionnaire | - |
| 14 Jan 2028 | - | seats | access review 3 | PO | - | - |
| 14 Feb 2028, effective 10:00 | REL11 (fu-7) | funds | the mid cap fund moves from Hold to Exit | LA -> PO -> PO | Exit; batches on 14 to 18 Feb | - |
| 21 to 25 Feb 2028 | - | cohorts | a draft adding a dimension, goal priority, is previewed and discarded | LA | - | Y03 |
| 20 Mar 2028, effective 1 Apr 2028 00:00 | REL12 (as-2) | assumptions | equity return 11.0 to 10.0 (the example given on the 7 Oct 2026 call); expense inflation 6.0 to 6.5 | LA -> PO -> PO; CO acknowledges | quiet, with the letter | Y01 |
| 12 Apr 2028 | - | seats | access review 4 | PO | - | - |

Review cadence (rehearsal values; LQ16): assumptions yearly, due 1 April; cohorts yearly, due the first Monday of
November; funds quarterly, due the first Monday of May, August, November and February; risk scoring yearly, due the
first working day of January; market inputs monthly, the first working day; the access review quarterly.

### 6.3 Example clients (typed)

Four examples, used by L15, L15a, L15b, L11 and the client views. The amounts add up and agree across screens; they
come from a rough run of stand-in arithmetic made while this plan was written and are typed here as examples. They
are not engine output and never stand in for a client's number. First names from seed/names.json; no phone, email,
PAN or date of birth.

C01: Moderate (score 20), DIWM, executing through the app; goals: work optional in 2048, a home upgrade in 2033.

| date | what happened | size and causes | versions on the snapshot | instalments after it, Rs a month |
|---|---|---|---|---|
| 8 Feb 2027 | first plan, on Rs 40,000 a month | first plan | as-1, co-1, fu-1, rs-1, EN1 | equity core 26,000 (index 13,000, flexi cap 7,800, mid cap 5,200); debt 6,000 (short duration 3,600, gilt 2,400); hybrid 4,000; gold 4,000 |
| 12 May 2027 | review; a raise takes the surplus to Rs 46,000 | review; your numbers (the raise) and house view (REL02: a fourth fund in the equity core) | fu-2 | equity core 29,900 (index 13,400, flexi cap 7,500, mid cap 4,500, large cap 4,500); debt 6,900 (4,100, 2,800); hybrid 4,600; gold 4,600 |
| 9 Aug 2027 | REL04: routine Hold on the mid cap fund | review; house view | fu-4, EN2 | equity core 29,900 (index 15,800, flexi cap 8,700, large cap 5,400); the rest unchanged |
| 22 Sep 2027 | REL05: urgent Hold on the flexi cap fund; a call task on 25 Sep, the call and the acceptance on 27 Sep | urgent; house view | fu-5 | equity core 29,900 (index 17,900, large cap 12,000); the rest unchanged |
| 8 Nov 2027 | review on co-2: the work-optional goal moves to MP8 | review; house view (REL07), and REL06 for the new fund in the split | co-2, fu-6 | equity core 32,400 (index 16,200, large cap 8,100, flexi cap B 8,100); debt 5,600 (3,400, 2,200); hybrid 3,400; gold 4,600 |
| 6 Feb 2028 | review | note | co-4, fu-6 | unchanged |
| 15 Feb 2028 | REL11: the mid cap fund moves to Exit | urgent; a sell action for the mid cap units, with an exit-load flag | fu-7 | unchanged |

C04: Moderate (score 21), DIWM, executing through the app; the whole surplus of Rs 35,000 a month goes to one
work-optional goal.

| date | what happened | size and causes |
|---|---|---|
| 15 Apr 2027 | first plan; the goal about 68 percent funded | first plan |
| 11 Jan 2028 | review on co-4: the goal moves to MP8 | review; house view (REL07) |
| 10 Apr 2028 | review on as-2 | outlook: the goal from about 70 to about 54 percent funded; instalments unchanged at Rs 35,000; house view (REL12) |
| 12 Apr 2028 | calls the adviser, who opens L15 | - |

C11: Moderate (score 20), DIWM, executing through the app; a home upgrade in 2032.

| date | what happened | size and causes |
|---|---|---|
| 6 Dec 2027 | review on co-3, the wrong mix: equity falls from 65 to 56 percent of the mix | review; house view (REL08); accepted; SIPs changed on 8 Dec |
| 16 Dec 2027 10:50 | raises a ticket: why did the equity share fall | - |
| 17 Dec 2027 | REL09, the correction | review, with an action that undoes the cut in equity; house view (REL09); accepted 18 Dec |

C12: Moderate (score 18), DIY, executing through the app; a home upgrade in 2033.

| date | what happened | size and causes |
|---|---|---|
| 15 Dec 2027 | review on co-3 | review; not accepted; the update is open on the phone the next morning |
| 16 Dec 2027 11:40 | REL08 withdrawn; the plan is rebuilt on co-2 | note; plan history reads "an update was withdrawn" |
| 12 Mar 2028 | review on co-4 | note |

### 6.4 Example figures (typed; illustrative; per 1,000 plan holders unless it says otherwise)

They come from a rough run over synthetic people and from assumptions. They are a plausible picture for the screens,
not evidence, and each screen that shows one says so.

| figure | value | shown on |
|---|---|---|
| an assumptions change like REL12, by size: note, outlook, review | 330, 540, 130 | L05, L11b, Ops page |
| the quiet route, per week: plans rebuilt, review-size updates, outlooks | about 60, 8, 33 | L05, L11b, Ops page |
| the same release pushed on day one | 130 review-size updates and 540 outlooks at once | L05, Ops page |
| existing plans rebuilt on a quiet release by day 14, 30, 60, 90, 120 | about 5, 18, 45, 73, 86 in 100 | L11b, L08 |
| clients running a SIP into one fund of the equity core; holding an open action that names it; holding units only | 500; 270; 20 | L04a, L06a, L11 |
| an urgent Hold accepted by day 2, by day 7 | 300, 425 of the 500 | L11 |
| call tasks on day 3 under the three-day rule; if every DIWM client were called | 105; 300 | L11, Ops page |
| tickets after an urgent Hold | 40 | L11, Ops page |
| a new horizon band like REL07, by size: review, outlook, note | 660, 60, 280 | L05, Walkthroughs page |
| plans built on a wrong release in its 16 days | about 14, plus the first plans built in those days | L11a |
| clients who would change risk band at their next questionnaire after REL10 | about 93; none on the day | L03 |
| goals per cohort at launch: Conservative Short, Medium, Long | 20, 85, 395 | L03, L14 |
| goals per cohort at launch: Moderate Short, Medium, Long | 50, 213, 988 | L03, L14 |
| goals per cohort at launch: Aggressive Short, Medium, Long | 30, 128, 593 | L03, L14 |
| goals in the new band after REL07: Conservative, Moderate, Aggressive Very long | 290, 725, 435 (taken out of Long) | L03a, L05 |
| storage per plan holder a year | about 2.5 MB: 8 snapshots at 60 KB and 5 PDFs at 400 KB | Tech page |
| a preview over every active plan at 1.5 seconds a plan, for 1,000, 10,000 and 100,000 plans | one at a time: 25 minutes, 4.2 hours, 41.7 hours; twenty at a time: 1.3 minutes, 12.5 minutes, 2.1 hours | Tech page |

A cohort with fewer than 30 goals per 1,000 plan holders is marked thin (rehearsal value): Conservative x Short at
launch; about five of the twenty-four cohorts in the draft of L03b.

## 7. The tech plan (DV3: the Tech page)

For Raafiya and Gaurav. Tables first. Board page key "logic_tech", a comment box per section. The sections below are
the page; they go into data/logic_tech.json as sections, with the figures of 6.4.

### 7.1 Access: where each rule is enforced

| control | rule | enforced by | record |
|---|---|---|---|
| identity | one staff identity, signed in through {I14} with its MFA, as decided for M03 on 7 Oct 2026 | the panel's server, on every request | a sign-in row |
| seat | a staff member holds one or more of ten fixed seats; no user-defined role; no exception for one person | an allowlist the server reads (LQ9) | staff_seats |
| permission | seat by action, taken from the write events of data/logic_screens.json | the server, on every request; the screen only mirrors it | an audit row; a refusal is a row too |
| two people | the author is not the reviewer; the publisher holds the Principal officer seat; nobody is both on one release, whatever seats they hold | the server, on the release record | releases |
| second factor | a check not older than a set number of minutes at publish, schedule, pause, withdraw, urgent Hold, ratify, any seat change and export (LQ29, LQ41) | {I14} | the audit row carries it |
| urgent path | one action by the Principal officer; ratification due two working days on | the server | releases.ratify_due, ratified_by |
| masking | client names are left out for a masked seat in previews and the monitor; an unmask needs a typed reason | the server leaves the field out; the screen cannot reveal it | an audit row |
| sessions | an idle timeout; a session ends at once on suspend or revoke (LQ41) | the server checks the seat on every request, not only at sign-in | - |
| operating seats | giving someone the Logic analyst or Principal officer seat takes effect when compliance acknowledges it (LQ42) | the server | staff_seats, audit |
| the client side | no logic endpoint answers a client's token; the panel is a separate staff web app, desktop only (L01 on the board) | routing and the token type | - |
| access review | each quarter every staff row is kept, changed or removed | the Principal officer on L13 | access_reviews |

How many people (7 Oct 2026 call): at launch two operators, one of whom can publish, plus compliance and read only.
The two-person rule needs both operators for every release except an urgent Hold; LQ7 holds what happens when the
publisher is away.

### 7.2 How a change reaches a plan

1. Versions. Each lane has immutable versions. A release makes one live from its effective time. The live version of
   a lane at a time is the latest release with an effective time not after it that is neither paused nor superseded.
2. The pin. A client's plan is their snapshot in force, and the snapshot carries the five lane versions and the
   engine version. Nothing else pins a plan. Risk scoring is stamped as of the client's last questionnaire, not as
   live (rule 10), so a plan can read rs-1 after rs-2 is live; L15 shows both. The board already stamps two of them on
   a plan (G01: assumptions_version,
   instrument_set_version); cohorts, risk scoring and market inputs are added.
3. Read path. Every plan screen in the app reads the snapshot in force, and H05 the waiting one. None calls
   the engine when it opens (rule 19). Net worth today is the one exception: holdings and prices at the last refresh.
4. Rebuild. The inputs on file, the as-of time, the live lane versions go to the engine; the result is stored as a
   snapshot, compared with the one in force, sized (4.5) and shown.
5. Triggers. A review completed (Q01, Q05), a life event (Q06), a sharpen, the annual confirmation (Q04), a
   questionnaire retake, a staff edit or a forced re-run (M03), a push, a stale-cap open, a withdraw, a correction.
6. Quiet route. Nothing runs at publish. The surfaces job runs at the effective time (rule 21).
7. Push. The route selects plans: a running SIP into a fund, an open action naming it, a verified holding of it, a
   snapshot in force built on a named release. The rollout job rebuilds them by the wave plan; it is idempotent per
   client and release, can be paused and resumed, and retries a failed client.
8. Scheduled release. It goes live by its effective time alone: the resolver in point 1 compares times. No job has
   to succeed at midnight for new plans to be right.
9. Stale cap. Checked when the app opens: a latest snapshot more than the cap behind a live assumptions, cohorts or
   funds release is rebuilt on the inputs on file.
10. Pause, withdraw, correct. Pause marks the release; the resolver skips it. Withdraw rebuilds, on the release
    before, every plan with an update built on the paused one and not accepted, and marks the old snapshot
    withdrawn. A correction is a release whose rollout selects every plan whose snapshot in force was built on the
    paused one.
11. Timing. A rebuild in flight keeps the versions it read at its start. A client holding an update when it is
    withdrawn sees the notice on the next screen. A draft is rebased when its lane's live version moves.
12. Blocks. An overdue annual confirmation blocks a rebuild (Q04 on the board); a lapsed account is frozen. LQ43
    holds whether a pushed update gets through the first.

What moves and when (4.3) and the life cycle (4.7) are drawn here again as tables.

### 7.3 Cohorts as data

| object | holds | changed by |
|---|---|---|
| dimension | a name, the input field it reads, its bands with bounds | a cohorts draft; a new field needs an app release |
| band | a label and a range; the bands of a dimension tile its range | a cohorts draft; the score ranges of the risk band by a risk scoring draft |
| cohort map row | one band or "any" per dimension, and a portfolio | a cohorts draft |
| model portfolio | a mix over six classes; the sleeve that fills each class | a cohorts draft |
| sleeve | funds and weights for one class | a funds draft |

- Resolving a goal: read the band of each dimension from the client's inputs; take the map rows that match on every
  dimension (a band or "any"); the row naming the most bands wins. Coverage is proved on the draft, so exactly one
  row always wins.
- The coverage proof enumerates every combination of bands; the count is the product of the band counts: 3 x 3 = 9
  at launch, 3 x 4 = 12 after REL07, 3 x 4 x 2 = 24 in the discarded draft. Twenty cohorts (the number guessed on the
  7 Oct 2026 call) is two dimensions more finely cut, or three dimensions.
- "Any" rows keep the map shorter than the cohort count: 7 rows for 9 cohorts, 10 for 12.
- Portfolios are fewer than cohorts and sleeves fewer than portfolios, so a fund change is one edit however many
  cohorts exist.
- A thin cohort is one with few goals in it; the preview marks them. A cut that the book cannot fill is a draft to
  discard (L03b).
- History of one cohort is read from the cohorts lane's versions: the row that covered it and that row's portfolio
  in each release. No per-cohort version is stored.
- What needs an app release: a dimension on a field the app does not yet ask for. LQ5 holds a ceiling on dimensions
  and bands.
- The plan JSON contract (W03) carries cohort and portfolio per goal in every snapshot.

### 7.4 Records: what is stored, and what each record answers

| record | written | holds | append-only | class | the question it answers |
|---|---|---|---|---|---|
| release | at publish | every value of the lane, the diff, who drafted, reviewed and published, why, the route, the preview, the signed note | yes | regulated | what logic was in force on a date, and why |
| snapshot | at every rebuild | the inputs used (id and hash), the as-of time, the five lane versions, the engine version, cohort and portfolio per goal, the outputs, the actions, the diff with causes, the size, what the client did | yes | regulated | what was this client advised on a date, and on which logic |
| PDF | for every snapshot a client was shown at first-plan, review or urgent size | the rendered plan, with the version of the copy | yes, under a lock in {I17} | regulated | what did the client see |
| reveal snapshot | at each sketch | the two numbers, the assumptions version | yes | regulated or operational: LQ24 | what was a prospect shown |
| interaction | shown, read, accepted, seen, withdrawn, message, call | who, when, which snapshot, which channel and slot | yes | regulated | when did they see it and what did they do |
| audit row | every write and every refused write on the panel | who, seat, when, what, before, after, reason, the second-factor check | yes | regulated | who changed what |
| draft, preview, review | during the workflow | the tables below | frozen onto the release at publish | operational | how a release came about |
| incident, access review | when made | the tables below | yes | regulated | what went wrong; who had access |
| monitor figures | derived | counts over snapshots and interactions | no | derived | - |

- Store the output, do not promise to recompute it: the engine version and the copy both change between the day of
  the advice and the day of the question.
- A hash on every snapshot and release. The app's own database role can insert into these tables and cannot update
  or delete.
- Retention classes (logic plan, 8 Oct 2026): regulated (kept as the Retention row of the nine records says; LQ24),
  operational (to be decided: how long), derived (rebuildable; not kept). A deletion request (S25) leaves regulated
  records in place.
- Drill-downs the screens need: by client (L15: every snapshot in order, or the one in force on a date); by release
  (L11, L08: every plan built on it, what each client was shown and did); by date (L08: the live version of every
  lane that day); by fund (L04: who was advised into it and still runs a SIP); by cohort (L03: its history).
- Which system holds the snapshot of record is LQ17; the proposal is the app.
- Sizes: per plan holder a year, 8 snapshots x 60 KB plus 5 PDFs x 400 KB, about 2.5 MB. Per year: 2.5 GB at 1,000
  plan holders, 25 GB at 10,000, 250 GB at 100,000; kept five years or more, five times that (LQ28).

Tables the app would hold (a proposal of what must be stored; the physical schema is Gaurav's and Spinach's):

| table | key fields |
|---|---|
| lanes | lane, version, release_id, live_from, live_to, paused_at |
| assumptions | version, key, label, value, unit, domain, route_default, hard_min, hard_max, soft_step, cadence, last_reviewed_at, next_due, used_in, rationale |
| scoring | version, band, score_from, score_to |
| dimensions | version, dimension_id, name, source_field, bands (id, label, lower, upper) |
| model_portfolios | version, portfolio_id, name, mix (six classes), sleeves (one per class used), rationale_internal, rationale_client |
| cohort_map | version, row_id, bands (a band id or "any" per dimension), portfolio_id, specificity |
| sleeves | version, sleeve_id, asset_class, funds (isin, weight), lead_fund |
| instruments | isin, name, asset_class, category, min_sip, exit_load_months, status (approved, hold, exit, retired), rationale_internal, rationale_client |
| instrument_status | isin, from_status, to_status, urgency, release_id, at |
| holding_classes | isin, class (known and not approved, legacy hold, unknown), release_id, facts added by ops |
| market_inputs | release_id (MI00 to MI15), month, values, rule_outcome (thresholds and buffers are assumptions rows) |
| guards | version, lane, key, value |
| drafts | draft_id, lane, based_on, opened_at, author, items (row, from, to, rationale), validation (check, result, reason), proposal (route, effective_at, reason slot, letter), state history, rebased_at, discarded_at |
| previews | preview_id, draft_id, run_at, seconds, the ten panels of L05 |
| reviews | draft_id, reviewer, at, outcome, comment, panels_opened, compliance_ack (who, at) |
| releases | release_id, lane, version, author, reviewer, publisher, drafted_at, reviewed_at, published_at, effective_from, route, urgency, wave_plan, reason_internal, reason_client_slot, letter, signed_at, second_factor_at, status, paused_at, withdrawn_at, corrects, preview_id, ratify_due, ratified_by, ratified_at |
| urgent_requests | request_id, isin, asked_by, asked_at, outcome (placed, declined), decided_by, decided_at, reason |
| calendar | item_id, lane or row, cadence, opens_at, due, done_at, outcome (changed, no change), signed_by |
| sample_plans | persona_id, release_id, generated_at, as-of line |
| staff_seats | staff_id, label, seats, status (active, suspended, revoked), added_by, added_at, acknowledged_by, last_sign_in, ended_at |
| access_reviews | review_id, at, by, rows (staff_id, last_sign_in, writes since last review, outcome) |
| incidents | incident_id, release_id, opened_at, by, what happened, who was reached, what was done |
| audit | at, staff_id, seat, action, object, before, after, reason, refused (true or false), second_factor (true or false) |
| engine_versions | version, live_from |
| inputs | inputs_id, person_id, at, why (first plan, review, life event, annual, staff edit), monthly_surplus, investable_corpus, the goal list as it stood, hash |
| reveal_snapshots | person_id, at, the two numbers at 50 and at 65, assumptions version, saved |
| snapshots | snapshot_id, person_id, built_at, trigger (initial, review, life_event, sharpen, annual, retake, staff_edit, forced_rerun, push, stale_open, withdraw, correction), lane versions (risk scoring as of the last questionnaire), engine_version, inputs_id, as_of, per goal: cohort, portfolio, pot, required, deployed, funded share; per sleeve: amount and the funds version its split was last restated on; instalment per fund; actions (isin, kind, from, to, flag); size; cause per line (with the release where the cause is house view); bytes (data, pdf); shown_at, read_at, accepted_at or seen_at, withdrawn_at, superseded_by, in_force (true or false), status |
| interactions | person_id, at, kind (shown, read, accepted, seen, withdrawn_notice, message, call_task, call_done, ticket, order_not_offered, rebuild_blocked), release_id, snapshot_id, channel, slot, reason |
| letters | release_id, queued_at, queued_by, sent_at, slot, recipients |
| jobs | job_id, kind (preview, rollout, surfaces, withdraw, correction, stale_check, export), release_id or draft_id, started_at, ended_at, items, failures, retries |
| job_items | job_id, person_id, attempt, at, result (built, failed) |

### 7.5 What {I04} must do

Said on the 7 Oct 2026 call, to be verified: the engine keeps central values as defaults, copies them to each client,
lets one client's copy be changed, and recalculates a client at that client's review. That holds a client's numbers
steady between reviews, which is the aim of rule 2. Whether the review then reads the central value of the day or
the client's copy was said both ways (LQ18). What is open is the list below.

| the engine must | why | open item |
|---|---|---|
| take the logic values with each run, or say which lane versions it ran on | the pin and the versions must have one home | LQ17 |
| run on a stored input snapshot, not only on live client data | previews, withdraws and corrections run old inputs again | LQ18 |
| take an as-of time | a correction and a dry run are dated | LQ18 |
| run as a dry run that writes nothing | the preview | LQ18 |
| run a batch of clients, several at once | a preview over every active plan; a push | LQ27 |
| take a key that makes a repeated run harmless | a retried push must not build twice | - |
| return its own version | stamped on every snapshot | W03 |
| return cohort and portfolio per goal, the instalment per fund, the actions | the snapshot's contents | W03 |
| not recalculate when a plan is only read | rule 19 | LQ18 |
| say what it does with an amount under a fund's minimum SIP | conflicts in the preview | LQ44 |
| refresh every client's copy without a person doing it client by client | a thousand clients cannot be edited by hand (7 Oct 2026 call) | LQ17 |
| say whether one client's values can differ from the lane's, and who may do that | a client-wise change is possible today | LQ32 |

### 7.6 Jobs

Run time uses 1.5 seconds a plan (assumption; LQ27).

| job | started by | does | at 1,000 / 10,000 / 100,000 plans | when it fails |
|---|---|---|---|---|
| preview | the author, on L05 | a dry run of the draft against every active plan; frozen onto the release at publish | one at a time: 25 minutes / 4.2 hours / 41.7 hours; twenty at a time: 1.3 minutes / 12.5 minutes / 2.1 hours | cancel and rerun; a plan that fails is listed as a conflict |
| rollout | a pushed release | rebuilds the plans its route selects, by the wave plan | by the wave plan | retry per client; pause and resume |
| surfaces | a release's effective time | regenerates the assumption lines and the sample plans | a handful of plans | the old version stays up until the new one is good |
| withdraw | the Principal officer, on L11 | rebuilds on the release before | small | retry per client |
| correction | a correction's publish | rebuilds every plan built on the paused release | small | as rollout |
| stale check | each app open | rebuilds one plan past the cap | one plan | the open goes ahead on the old plan; tried again at the next open |
| register export | Principal officer, Compliance | writes the advice register for a period | - | - |

To be decided with LQ27: a quick preview on a fixed sample of plans and the six personas while editing, and the full
run before submit.

### 7.7 What the app does at run time

- No new order is made for a fund on Hold or at Exit from the publish moment (E03 and E11 as drawn; if execution
  leaves the app through a link, the fund is left out of the portfolio the link carries; LQ36). A running instalment
  is never stopped by the app on its own.
- A rebuild reads the live version of each lane at its start and never mixes two versions of one lane; a paused
  release is skipped; a scheduled release is live from its effective time, not before.
- Plan screens read the stored snapshot (rule 19). "Assumptions as of <date>" is printed from the snapshot.
- The saved reveal and its nudges read the stored reveal snapshot (rule 21).

### 7.8 Events out, one way

To {I14}: plan_updated with its size and causes; update_accepted; update_seen (new, for an outlook); update_withdrawn
(new); the call task for an urgent update not accepted. To {I13}: the same, and the panel's own view and write
events. The letter is sent from {I14} to a list the app supplies. No event carries a logic value.

### 7.9 Launch and later, failure cases, open items

- The launch cut of 4.9, as a table with a comment box per row (LQ37).
- The failure cases that touch tech, each with what the system should do: the failed rebuild in a rollout, the
  rebuild during a pause, the update withdrawn while open, the three releases picked up at once, the stale-cap
  rebuild, the blocked rebuild, the revoked session, the rebased draft, the first plan between publish and effective
  time.
- Open items for tech: LQ9, LQ11, LQ17, LQ18, LQ19, LQ24, LQ27, LQ28, LQ29, LQ36, LQ41, LQ43, LQ44, LQ46.

## 8. Access page (DV4): the access write-up

Board page key "logic_access". This is the write-up asked for on the 7 Oct 2026 call ("what kind of roles, what kind
of access, what kind of permissions"), across the logic panel and the admin screens. It is written so that, once the
operating seats accept it, it can go to Spinach as it stands; sending it is Vatsal's call and not part of this plan.
The page and its data file carry seat names only.

In this order:
1. Principles: a few people (7 Oct 2026 call); fixed seats; two people on every release; the server decides, the
   screen only mirrors; everything written down.
2. The seats: the ten, one line each on what the seat is for.
3. Permissions by action: 4.8.
4. Permissions by screen: 5.4 for L00 to L15 and, read only from data/admin_screens.json, the role and writes of M03,
   M07 and M10, in one table. The table is built from the role fields; it is not typed twice.
5. Approval: 4.6 as a table; who can author, review, acknowledge, publish; the urgent path; LQ7.
6. Sign-in and the second factor: {I14} with its MFA as decided for M03 on 7 Oct 2026; the check asked again at the
   guarded actions (rule 15; LQ29). L01 on the board reads "same auth as the app with role claims"; the proposal is
   one staff identity for both panels and none shared with clients (LQ9).
7. Sessions, masking, audit rows, the access review: 7.1.
8. The app: one kind of user; what a client can do differs by tier, which is entitlement and already on each
   screen (LQ40).
9. Open items: LQ7, LQ9, LQ29, LQ40, LQ41, LQ42, LQ45.

## 9. Walkthroughs page (DV5)

Board page key "logic_walk". For the two operating seats first. Plain tables; each step names the side screen that
shows it, as a link into the Logic tab.
1. The call table of section 1 with all five columns: what was asked on 7 Oct 2026, by which side ("Spinach", or a
   first name of the team as a cause), the proposed answer, where it is drawn.
2. The design in one place: the rules (4.2), what moves and when (4.3), the approval workflow (4.6), the change life
   cycle (4.7), the routes (4.4), the sizes (4.5).
3. The four walkthroughs below. Each ends with three short lists typed from section 6: what the client saw, what ops
   saw, what was stored.

Y01. The annual assumptions (REL12)

| n | at | seat | screen | action and result |
|---|---|---|---|---|
| 1 | 1 Mar 2028 | - | L12 | the annual review opens a month ahead of 1 April |
| 2 | 10 Mar | Logic analyst | L02a | draft: equity return 11.0 to 10.0, expense inflation 6.0 to 6.5; 65 typed for inflation by a slip is refused at the field; each real move needs a typed reason |
| 3 | 10 Mar | Logic analyst | L05 | validation passes; preview: per 100 plans about 33 note, 54 outlook, 13 review; the funded share is what moves; surfaces: the assumption lines, new sketches, the sample plans; the quiet route against a push on day one |
| 4 | 10 Mar | Logic analyst | L05 | proposes the quiet route, effective 1 Apr 2028 00:00, with the letter; submits |
| 5 | 14 Mar | Compliance | L10 | acknowledges |
| 6 | 17 Mar | Principal officer | L10 | opens every preview panel; approves |
| 7 | 20 Mar | Principal officer | L06 | publishes with the effective time 1 Apr 2028 00:00; passes the second-factor check; the release shows as scheduled (L06b) |
| 8 | 1 Apr 00:00 | the system | L08 | as-2 goes live; the assumption lines and the sample plans regenerate; the letter, queued by ops, goes out at 09:00 (V05) |
| 9 | 10 Apr | client C04 | V01 | C04's review: the outlook moved; nothing to accept |
| 10 | 12 Apr | Adviser | L15 | C04 calls; the adviser reads the versions C04 is on and the cause on the last update |
| 11 | 28 Apr | Principal officer | L11b | four weeks live: about one existing plan in six has rebuilt on it; most of the 90 days is still to run |

Y02. An urgent Hold (REL05, then REL06)

| n | at | seat | screen | action and result |
|---|---|---|---|---|
| 1 | 22 Sep 2027 09:50 | Logic analyst | L04a | opens the fund's exposure: advised into it, running SIPs, open actions, holders |
| 2 | 10:05 | Logic analyst | L04a | requests an urgent Hold; the Principal officer is notified (LQ25) |
| 3 | 10:40 | Principal officer | L06a | places the Hold alone; the rescale to 75 / 25 breaches L09 and the screen asks for weights; sets 60 / 40; picks the client reason slot; passes the second-factor check; compliance and the Logic analyst are notified |
| 4 | 10:40 | the app | V03 | no new order for the fund from this moment; a running SIP keeps running until its client accepts |
| 5 | 10:45 | Principal officer, Ops | L11 | urgent updates go at once to every client running a SIP into it: push and WhatsApp now, email next morning; one rebuild fails at 10:46 and succeeds on retry at 10:52 |
| 6 | 24 Sep 18:00 | - | L10a, L01a | two working days pass with no ratification: the Hold stays in force and shows as overdue (LQ30) |
| 7 | 25 Sep | the system | L11 | call tasks are created for DIWM clients who have not accepted after three days; C01 is one |
| 8 | 27 Sep 09:20 | Logic analyst | L10a | ratifies the Hold, one working day late |
| 9 | 27 Sep | Adviser | L15 | the call; C01 accepts |
| 10 | 27 Sep | Logic analyst, then Principal officer | L04, L05, L10, L06 | REL06 by the two-person path: a second flexi cap fund joins at 50 / 25 / 25; quiet route, so a client who accepted 60 / 40 last week is not asked to change again |

Y03. A new cohort (REL07), and a dimension that is not added

| n | at | seat | screen | action and result |
|---|---|---|---|---|
| 1 | 1 Nov 2027 | Principal officer | L12, L03a | the yearly cohort review falls due; opens a draft; adds the band "Very long: over 7" to the horizon dimension (data, no app release) |
| 2 | 1 Nov | Principal officer | L14 | adds MP8 and MP9 with their rationale |
| 3 | 1 Nov | Principal officer | L03a | adds two map rows: Moderate x Very long to MP8 and, by a slip, Conservative x Very long to MP8 as well; forgets the Aggressive row |
| 4 | 1 Nov | Principal officer | L05a | validation fails twice: coverage (Aggressive x Very long has no row) and a guard (MP8 holds 75 percent equity; the Conservative ceiling is 30); adds the row to MP9 and repoints Conservative x Very long at MP5; passes |
| 5 | 2 Nov | Principal officer | L05 | preview: the migration (MP6 to MP8, MP7 to MP9); per 100 plans about 66 review, 6 outlook, 28 note, each at its own review; no sells; proposes the quiet route with the letter |
| 6 | 5 Nov | Logic analyst | L10 | reviews, because the author is the Principal officer; approves |
| 7 | 8 Nov 09:45 | Principal officer | L06 | publishes, effective 10:00; push is not offered for a cohort change |
| 8 | 8 Nov 20:00 | client C01 | L15 | C01's review that evening: the work-optional goal moves to MP8; a review-size update |
| 9 | 21 Feb 2028 | Logic analyst | L03b | a draft that adds a dimension, goal priority (must have, the rest): twenty-four cohorts; coverage passes on the "any" rows; the preview marks about five thin cohorts |
| 10 | 25 Feb 2028 | Logic analyst | L05 | discards the draft with a reason: it splits the book too thin |

Y04. A wrong number gets through (REL08, then REL09)

| n | at | seat | screen | action and result |
|---|---|---|---|---|
| 1 | 29 Nov 2027 | Logic analyst | L14a | draft: MP6 keyed 0/24/10/10/56/0 where 0/15/10/8/67/0 was meant; the sum is 100 |
| 2 | 29 Nov | Logic analyst | L05 | validation passes: the sum holds and 56 is under the Moderate ceiling; the soft limit flags a 9-point move on two classes and a reason is typed; the reference persona row shows equity down 9 points |
| 3 | 30 Nov | Principal officer | L10 | approves; the screen records that the reference personas panel was not opened |
| 4 | 30 Nov 16:00 | Principal officer | L06 | publishes; quiet route |
| 5 | 6 Dec | client C11 | L15b | C11's review rebuilds on it and is accepted; the SIPs are changed on 8 Dec |
| 6 | 15 Dec | client C12 | L15b | C12's review rebuilds on it; not accepted |
| 7 | 16 Dec 10:50 | Logic analyst | L11a | Support passes on C11's ticket, which asks why the equity share fell; the Logic analyst opens the biggest movers |
| 8 | 16 Dec 11:05 | Principal officer | L11a | pause: rebuilds go back to co-2 |
| 9 | 16 Dec 11:40 | Principal officer | L11a | withdraw: every update built on co-3 and not yet accepted is replaced by a rebuild on co-2; C12, with the update open on the phone, sees "an update was withdrawn" (V04) |
| 10 | 17 Dec 12:00 | Logic analyst, then Principal officer | L14a, L05, L10, L06 | REL09, the correction, by the two-person path; every plan built on co-3 is rebuilt at once; C11 gets an action that undoes the cut in equity |
| 11 | 17 Dec | Compliance | L08a | the incident entry: what happened, who was reached, what was done (LQ23) |

The page closes Y04 with "what could have stopped it", each line an open item (LQ22).

## 10. Ops page (DV6)

For the Ops seat. Plain words, short lines, one step at a time, so a reader who is not technical follows it unaided.
Collegial wording ("note it on the page and we look at it together"), never an order. Board page key "logic_ops".

1. What each kind of change sets in motion: one row per route in 4.4: what the client gets (channel, slot, when),
   what the call centre gets (tasks, when), what support should expect (tickets; example figures), what ops does
   before, on the day and after.
2. Before a release goes out: a checklist per route, drawn as a table, with the section's comment box for notes: the
   message slots it uses exist and are approved in {I11}; the push copy is in {I15}; the letter is queued in {I14};
   the help entry for the change is in {I15}; the call centre has its lines; support has the plain reason; the day
   is not a peak day on the calendar.
3. What the numbers could look like, from 6.4, per 1,000 plan holders: an urgent Hold (500 urgent updates, 105 call
   tasks on day 3 against 300 if every DIWM client were called, 40 tickets); an assumptions change on the quiet
   route (about 8 updates to accept and 33 outlooks a week) against the same change pushed on day one (130 and 540
   at once).
4. The letter: what it is, who queues it, and the two timings of LQ33 with their volumes: on the effective date to
   every plan the release will change (670 in 1,000 for an assumptions change like REL12), or to each client as
   their plan takes it up (about 41 a week).
5. What is new on the ops side, each row "to be decided": copy slots for the update screen at each size, for the
   outlook card, for the plan history entries, for "an update was withdrawn" and for the letter; an urgent ladder
   beside the S11 ladder; the client reason slots and who edits them (LQ10); a task type for an urgent update not
   accepted; a tag tying a ticket to a release; mirrored fields on the Contact (an update waiting and its size, the
   date of the last plan update); events (plan_updated gains size and causes; update_seen and update_withdrawn are
   new); a saved view per release.
6. The unknown-ISIN queue (L04b): what ops adds (the name on the statement, the category if printed) and what
   happens next.
7. Seats: how a seat is asked for, added, suspended and removed; what the access review looks at (L13).
8. Open items for ops: LQ10, LQ13, LQ14, LQ31, LQ33, LQ35.

## 11. Checks

The schema checks live in the builder (scripts/build_logic_wireframes.py validates data/logic_screens.json on every
build, as the admin builder does); the content checks live in scripts/check_logic.py, run by hand after the build
like check_phase9.py (12.0). The shapes the checks read are pinned in 12.1 (A0) and 12.11 (C1): a mix is one cell
"a/b/c/d/e/f", sleeve weights one cell "60/40", an instalment cell "<sleeve> <amount> (<fund> <amount>, ...)",
a staff date "10 Mar 2028". The visual pass is Vatsal's (phase D). A phase is not done while any of these fails.
- data/logic_screens.json passes the validator the board runs on data/screens_v02.json (schema; every btn and link
  target is a screen that exists, here or on the board).
- Every screen names all ten seats in role; every write names its seats and its event; no team name; vendor names as
  {I..} tokens.
- Every "LQ" id on a screen or a page is defined in 4.10, and every item of 4.10 appears on the screen or page it
  lands on.
- Every walkthrough step names a screen that exists. Every example date for a staff action is a working day.
- Every six-class mix and every set of sleeve weights on a screen sums to 100; a sleeve's funds add up to its
  amount in the examples of 6.3.
- No real fund name, no real person as an actor, no contact detail. The pages pass build_site.FORBIDDEN.
- `python3 scripts/build_site.py`, then check_phase9.py and check_site.py with no FAIL. No file under data/seed/,
  docs/seed/, docs/review/, the audience files, data/screens_v02.json, data/admin_screens.json or
  data/v02/freeze.json changes. Existing pages do not change except the nav on the main board.
- A visual pass at laptop width (the panel is desktop only; the pages must still open on a phone).

## 12. Phases and commits

Rebuilt for /run-plan on 8 Oct 2026 (plan-ready pass). Nothing was added to the scope: the three phases of the first
draft are split into runs an agent can finish cold, each with a check that says when it is done. The letters keep
their meaning: A is the side wireframes, B the four pages, C the board links and the checks, D is Vatsal's look. One
commit per phase, message "logic <phase>: <what changed and why>", on main, no push: Vatsal looks at the pages on
his machine and says when they go up (phase D). A phase stages only the files it names; the untracked items at the
repo root and under inputs/ are never added. Every call made in this section that the first draft had left open
carries the cause "logic plan, 8 Oct 2026"; Vatsal vetoes by reply.

Firm rules carried into every phase (CLAUDE.md and section 0): ASCII, Rs, first names, a cause on every row, no
regex and no word or phrase rules, stdlib only, no network, no vendor call, no message sent. No edit to
data/screens_v02.json, data/admin_screens.json, data/v02/freeze.json, data/gaps.json, data/tracker.json, anything
under data/seed/, docs/seed/, docs/review/, docs/audiences/ or inputs/. If a phase seems to need code beyond what
its steps name, it stops and reports instead of writing it.

### 12.0 Calls made for the executor (logic plan, 8 Oct 2026, from reading the repo)

- The board's builder cannot draw a second file: build_site.build_wire_v02 loads data/screens_v02.json by a literal
  (build_site.py:973), sq_refs_blob() reloads it (:384), and the page emits no WIRE_OPTS, so its board page key is
  fixed at "wireframes_v02". The Logic tab comes from scripts/build_logic_wireframes.py, a stripped copy of
  scripts/build_admin_wireframes.py (the 5.1 fallback), hooked into build_site.main() after build_admin_split.
  What goes from the copy: the seed helpers and build_bundle (build_admin_wireframes.py:83-344), the run and person
  bar, the ADMIN_RUNS, ADMIN_STATES and ADMIN_PLACEMENT blobs, admin_core.js and the ADMIN_SCREEN_FILES includes, the
  synthetic-people banner. What stays: the validation (adapted, A0), build_page with its own WIRE_OPTS, the shared
  renderer, the page shell and the comment box.
- Grouping on the left of the Logic tab: the renderer groups by sec through SECTIONS (renderer_v02.js:123). The data
  keeps sec L and V; each screen carries a group field; the builder sets the page's sec to the group as
  build_admin_wireframes.build_page does for "MZ". No renderer change.
- Open items: data/gaps.json's v02 list reaches no review or audience file, but build_brief.py:625-630 puts its open
  rows in docs/admin_brief.html section 5, the pack sent to Spinach on 7 Oct 2026. Appending LQ1 to LQ46 there would
  change an existing page and show Spinach the logic work before the merge, against section 0 and section 11. So
  the LQ items live in data/logic_gaps.json (written in A0, because the screens' dev lines and the checks read it)
  and are shown on the logic pages only. data/gaps.json is not touched. No tracker row and no note on W04: the
  Tracker is on the review link (docs/review/tracker.html); progress goes in the one-line daily update.
- The content checks of section 11 live in scripts/check_logic.py, run by hand after the build like check_phase9.py,
  never inside build_site.py. It is a third piece of new code (the header allowed two); the checks need a home and a
  check script is the repo's pattern. The builders keep their own schema validation, as the admin builder does.
- The page builder draws one comment box per section (the first draft's phase table). 7.9's "a comment box per row"
  on the launch cut table is not built: one box per section keeps the builder at its size.
- The nav fold ("if one more tab grows the header at 1,512 px") is a visual judgment no script makes. C2 adds the
  one tab; phase D decides the fold. The tab row already wraps (.tabs flex-wrap, build_site.py:85), so a long header
  shows a second row, never a broken page.
- Links on the pages into the Logic tab are typed, never detected: a table cell written as a two-item list
  [text, href] renders as a link; a plain string renders as text.
- Dates the checks read are typed in full ("10 Mar 2028": day, three-letter month, year). The walkthrough tables of
  section 9 write "10 Mar"; the page carries the year on every step.
- Each phase's rebuild uses its own builder (python3 scripts/build_logic_wireframes.py or
  python3 scripts/build_logic_pages.py). The full python3 scripts/build_site.py runs only in A0, C1 and C2, so a
  content phase in flight never breaks another phase's build.
- The coder on every phase is opus (Opus 5.5), the floor for any coding agent; sonnet never codes (Vatsal,
  8 Oct 2026). The metadata lines below carry it.

### 12.1 Phase A0: the scaffold

Goal: the Logic tab builder exists, draws 39 stub screens from data/logic_screens.json, and the open items file exists.

Touches: scripts/build_logic_wireframes.py (new), scripts/build_site.py (LOGIC_PAGES, logic_subnav(), one import and
call in main()), data/logic_screens.json (new), data/logic_gaps.json (new), docs/logic_wireframes.html (generated).

Steps:
1. In scripts/build_site.py, next to SEED_PAGES (:199): LOGIC_PAGES = [("logic_wireframes.html", "Logic tab"),
   ("logic_tech.html", "Tech"), ("logic_access.html", "Access"), ("logic_walk.html", "Walkthroughs"),
   ("logic_ops.html", "Ops")] and logic_subnav(current) shaped like seed_subnav(), label "Logic panel:". No change to
   TABS, REVIEW_TABS or FORBIDDEN. In main(), after build_admin_split.main(): import build_logic_wireframes and call
   its main(), with a one-line comment in the file's style.
2. Copy scripts/build_admin_wireframes.py to scripts/build_logic_wireframes.py and strip it as 12.0 says. Page
   options: page "logic_wireframes", key "yeslyf_logic_wire_v01", version "logic side v0.1", exportTitle
   "# yeslyf logic panel side wireframes - review comments", exportFile "yeslyf_logic_side_review_v01.md". Header:
   site.header("logic_wireframes.html", "logic panel side wireframes: proposed, not yet merged into Wireframes v0.2",
   export_label="Export comments"); the bar carries site.logic_subnav("logic_wireframes.html"); the banner reads
   "side wireframes: proposed, not yet merged into Wireframes v0.2. The design is proposed, to be confirmed at the
   logic panel review (to be decided: the review date). Every logic value is a rehearsal value and every count a
   typed example." SECTIONS on the page are the seven groups in this order and with these labels: start "Start",
   logic "Logic", change "Change", records "Records", access "Access", reference "Reference", client "Client views".
   DROPPED, SPLIT, STATES empty; REASONS from data/compliance_reasons.json; INTEGRATIONS as the admin page; FREEZE
   None. The builder prints one line: "logic wireframes: 39 screens (33 panel, 6 client views), validation PASS".
3. Validation in the builder (adapted from validate_admin_screens), each failure named; the build stops on any:
   - ids exactly, in this order: L01, L01a, L02, L02a, L03, L03a, L03b, L14, L14a, L04, L04a, L04b, L09, L07, L05,
     L05a, L05b, L10, L10a, L06, L06a, L06b, L11, L11a, L11b, L08, L08a, L15, L15a, L15b, L12, L13, L00, V01, V02,
     V03, V04, V05, V06;
   - keys: id, sec, title, tier, frame, template, path, purpose, ui, spec, compliance, events, v02, freeze, role,
     writes, group; spec keys fields, logic, branches, states, dev (forward optional);
   - sec L for L ids, V for V ids; frame desktop for L, phone for V; path in aa, manual, both; template in the set
     used by data/screens_v02.json; group in the seven; tier a list;
   - role has exactly the ten seats in this order: Principal officer, Logic analyst, Compliance, Adviser, Call centre,
     Ops, Support, Read only, Marketing, Finance; values in act, read, "read, own people", "read masked", none;
   - writes is a list of {action, event, seats}; seats a subset of the ten; event listed in events; events non-empty;
   - spec.logic[0] equals "Seats: " + "; ".join(seat + " " + value over the ten seats), and spec.logic[1] equals
     "Writes: " + "; ".join(action + " (" + event + "; " + ", ".join(seats) + ")") or "Writes: none";
   - every btn and link target in ui and every branch target resolves to an id in data/logic_screens.json or
     data/screens_v02.json (the admin builder's approach);
   - compliance has review and reasons, reasons from data/compliance_reasons.json; v02.status in changed, new, kept;
     freeze.status "open" with a non-empty reason list;
   - the team-name and vendor-string check kept from the admin builder (its NAMES_UI and word_hit), site.FORBIDDEN
     absent, site.check_ascii on the page.
4. data/logic_screens.json: {"source": "PLAN_logic_panel_v03.md, 8 Oct 2026", "note": one line, "sections":
   [["L", "Logic panel"], ["V", "Client views"]], "groups": the seven [code, label] pairs, "screens": the 39 stubs},
   json.dumps(indent=2) plus a newline. A stub: id; sec; title (the 5.2 screen name; a variant adds ", " and the state
   phrase of its 5.3 "Drawn" line, so L01a is "Home, an urgent day"); tier ["ALL"] for L; frame; template T-table for
   L, for V: V01 to V03 T-card-stack (H05), V04 T-list, V05 T-msg, V06 T-card (X01); path "both"; purpose, one line
   from 5.3; ui []; spec {fields [], logic [the two derived lines], branches [], states [], dev []}; compliance for L
   {"review": false, "reasons": ["internal"], "checks": ["No user-facing copy; nothing to review."]}, for V01 to V05
   advice language and for V06 advertising code, review true, checks copied from data/compliance_reasons.json; tier
   for V01 to V05 ["DIY", "DIWM"], V06 ["ALL"]; events ["<id>_view"]; v02 {"status": the 5.2 column read as changed,
   new or kept, variants as their base, V new; "causes": ["Vatsal, 8 Oct 2026"]}; freeze {"status": "open",
   "since": "8 Oct 2026", "cause": "Vatsal, 8 Oct 2026", "reason": ["proposed, to be confirmed at the logic panel
   review"], "owed": []}; role from the 5.4 table row of its base ("-" is none, "masked" is "read masked", "own" is
   "read, own people"); writes []; group from 5.2.
5. data/logic_gaps.json: {"source": "PLAN_logic_panel_v03.md 4.10", "note": one line, "items": 46 rows
   {id, item (the 4.10 text, which starts "to be decided: " or "to be verified: "), lands_on (a list: screen ids;
   "Tech page" as "logic_tech", "Access page" as "logic_access", "client views" as "V"), status "open", cause
   "Vatsal, 8 Oct 2026 (logic side wireframes)"}}, json.dumps(indent=1) plus a newline.
6. python3 scripts/build_site.py; the checks below; commit "logic A0: the Logic tab builder, 39 stub screens and the
   open items file (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_wireframes.py` -> exit 0; last line "logic wireframes: 39 screens (33 panel, 6 client
  views), validation PASS".
- `python3 -c "import json;d=json.load(open('data/logic_screens.json'))['screens'];print(len(d),sum(len(s['role'])==10 for s in d),sum(s['ui']==[] for s in d))"`
  -> "39 39 39".
- `python3 -c "import json;print(len(json.load(open('data/logic_gaps.json'))['items']))"` -> 46.
- `python3 scripts/build_site.py` -> exit 0 (about 2 minutes).
- `python3 scripts/check_phase9.py | grep -c PASS` -> 19; `python3 scripts/check_site.py | grep -c PASS` -> 3.
- `git status --short` -> the pre-existing untracked items plus exactly: M scripts/build_site.py, ?? or A for
  scripts/build_logic_wireframes.py, data/logic_screens.json, data/logic_gaps.json, docs/logic_wireframes.html.
  Nothing under docs/review/, docs/audiences/, docs/seed/ or data/ besides the two new files.
- `grep -c 'Logic panel:' docs/logic_wireframes.html` -> 1; `grep -c 'logic_wireframes' docs/review/index.html` -> 0.

Metadata: depends_on [] . weight heavy . live_model no . coder opus . verify_class sample . kind seam-design
- [x] A0 done

### 12.2 Phase A1: the start and logic groups, 14 screens

Goal: L01, L01a, L02, L02a, L03, L03a, L03b, L14, L14a, L04, L04a, L04b, L09, L07 drawn from 5.3 and section 6.

Touches: data/logic_screens.json (these 14 entries only), docs/logic_wireframes.html (generated).

Steps:
1. For each screen fill ui, spec.fields, spec.logic (the two derived lines first, then a variant's state line, then
   the checks of its 5.3 entry), spec.branches, spec.states (every state, drawn or not), spec.dev (its LQ items in
   the exact 4.10 wording; "gap, to be decided" lines where the build finds one), writes (action, event
   "<base id>_<action in lower snake>", seats) with each event added to events, and the forward line where 5.3 gives
   one. The role field is already set; do not change it.
2. ui rows use the board's grammar as in data/screens_v02.json ("table" rows as ["table", [cols], [rows]], text,
   btn, link). Every screen that shows an example carries the note row "Example values: rehearsal values and
   illustrative figures per 1,000 plan holders; nothing here is decided." Mixes are typed as one cell "a/b/c/d/e/f"
   (six classes in the 6.1 order), sleeve weights as one cell with slashes ("60/40"); fund names only from 6.1
   ("Seed <category> Fund NN"); staff only as "Principal officer 01", "Logic analyst 01" and the other seats of 6.1.
3. What the plan leaves unsaid is settled in the smallest way that keeps 4.2 and section 6 consistent, written into
   the screen, and listed in the phase report with the cause "logic plan, 8 Oct 2026".
4. python3 scripts/build_logic_wireframes.py; the checks below; commit "logic A1: the start and logic groups drawn,
   14 screens (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_wireframes.py` -> exit 0, "validation PASS".
- `python3 -c "import json;d=json.load(open('data/logic_screens.json'))['screens'];print(sorted(s['id'] for s in d if s['ui']))"`
  -> exactly the 14 ids above.
- `git status --short` -> the A0 state plus M data/logic_screens.json, M docs/logic_wireframes.html only.

Metadata: depends_on [A0] . weight heavy . live_model no . coder opus . verify_class sample . kind transcription
- [ ] A1 done

### 12.3 Phase A2: the change group, 11 screens

Goal: L05, L05a, L05b, L10, L10a, L06, L06a, L06b, L11, L11a, L11b drawn from 5.3, 4.4 to 4.7 and section 6.

Touches: data/logic_screens.json (these 11 entries only), docs/logic_wireframes.html (generated).

Steps: as A1 steps 1 to 3 for these screens; the preview's ten panels on L05 are rows, with panels c, i, j marked
"later" per 4.9; figures from 6.4. Then python3 scripts/build_logic_wireframes.py and commit "logic A2: the change
group drawn, 11 screens (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_wireframes.py` -> exit 0, "validation PASS".
- `python3 -c "import json;d=json.load(open('data/logic_screens.json'))['screens'];print(len([s for s in d if s['ui']]))"`
  -> 25, and the filled ids are the A1 set plus the 11 above.
- `git status --short` -> M data/logic_screens.json, M docs/logic_wireframes.html only (beyond the committed state).

Metadata: depends_on [A1] . weight heavy . live_model no . coder opus . verify_class sample . kind transcription
- [ ] A2 done

### 12.4 Phase A3: the records, access and reference groups, 8 screens

Goal: L08, L08a, L15, L15a, L15b, L12, L13, L00 drawn from 5.3, 5.6 and section 6.

Touches: data/logic_screens.json (these 8 entries only), docs/logic_wireframes.html (generated).

Steps: as A1 steps 1 to 3 for these screens. L08 types the 6.2 rows; L15 types the 6.3 rows, each instalment cell in
the form "<sleeve> <amount> (<fund> <amount>, <fund> <amount>); <sleeve> <amount>" with amounts as in 6.3
("26,000"), or "unchanged"; L00 carries the life cycle of 4.7 and the surface map of 5.6. Then
python3 scripts/build_logic_wireframes.py and commit "logic A3: the records, access and reference groups drawn, 8
screens (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_wireframes.py` -> exit 0, "validation PASS".
- the filled count -> 33, the filled ids the A2 set plus the 8 above (the A2 one-liner).
- `git status --short` -> M data/logic_screens.json, M docs/logic_wireframes.html only.

Metadata: depends_on [A2] . weight heavy . live_model no . coder opus . verify_class sample . kind transcription
- [ ] A3 done

### 12.5 Phase A4: the client views, 6 screens

Goal: V01 to V06 drawn from 5.5, 4.5 and 6.3, each linking to the board screen it would change.

Touches: data/logic_screens.json (these 6 entries only), docs/logic_wireframes.html (generated).

Steps: as A1 steps 1 to 3; copy is slots, never final wording ("[slot: what changed]"); each view's branches point
at its board target (H05, H01e, E03, E11, G12a, R12, X01 as 5.5 says). Then python3 scripts/build_logic_wireframes.py
and commit "logic A4: the six client views drawn (logic plan, 8 Oct 2026)". The phase report lists what was settled
with the cause "logic plan, 8 Oct 2026" and the two questions for Vatsal: whether the operating seats stay
"Principal officer 01" and "Logic analyst 01", and whether a state that matters is missing from the 39 (phase D).

Done-criteria:
- `python3 scripts/build_logic_wireframes.py` -> exit 0, "validation PASS".
- the filled count -> 39 (the A2 one-liner); `python3 -c "import json;d=json.load(open('data/logic_screens.json'))['screens'];print(sum(1 for s in d if s['id'].startswith('V') and s['frame']=='phone' and s['ui']))"`
  -> 6.
- `git status --short` -> M data/logic_screens.json, M docs/logic_wireframes.html only.

Metadata: depends_on [A3] . weight heavy . live_model no . coder opus . verify_class sample . kind transcription
- [ ] A4 done

### 12.6 Phase B0: the page builder and four skeleton pages

Goal: scripts/build_logic_pages.py renders a page from a JSON file of sections inside the board's shell; the four
data files exist as skeletons and render.

Touches: scripts/build_logic_pages.py (new), scripts/build_site.py (one import and call in main(), after
build_logic_wireframes), data/logic_tech.json, data/logic_access.json, data/logic_walk.json, data/logic_ops.json
(new), docs/logic_tech.html, docs/logic_access.html, docs/logic_walk.html, docs/logic_ops.html (generated).

Steps:
1. The data shape, one file per page: {"page": the board page key (logic_tech, logic_access, logic_walk,
   logic_ops), "title", "audience": one line, "sections": [{"id": a short anchor such as "t1", "heading",
   "lines": [strings], "tables": [{"cols": [...], "rows": [[cell, ...]]}], "open_items": ["LQ17", ...],
   "derived": "seat_by_screen"}]}. A cell is a string, or a two-item list [text, href] drawn as a link. lines,
   tables, open_items and derived are optional. json.dumps(indent=1) plus a newline.
2. The builder, about 200 lines, stdlib only, importing build_site as site like build_seats.py: for each file,
   site.head, site.header("logic_wireframes.html", "<title>: proposed, not yet merged into Wireframes v0.2",
   export_label="Export comments"), site.logic_subnav(its html name), the two banner lines of A0 step 2, then per
   section an h2 with the id as anchor, the lines as paragraphs, the tables through site.table_html, the open items
   as "<id> <item>" rows read from data/logic_gaps.json, the derived table, and one comment box bound to the section
   id through the comment script copied from build_seats.py (yeslyfBoard.init with the file's page key, attach per
   section). site.FORBIDDEN applied, site.check_ascii run. The derived table "seat_by_screen": one row per screen of
   data/logic_screens.json (base screens and variants, in file order) and then M03, M07 and M10 from
   data/admin_screens.json; one column per seat in the A0 order, the admin screens' missing seats shown as "-";
   values as stored. Every line and cell passes through build_brief.tokens(text, integrations_by_id) with
   integrations_by_id built as build_brief.py:716 builds it, so {I04} renders as "I04 <vendor>" and no vendor name is
   typed. The builder prints one line: "logic pages: 4 built".
3. Skeletons: each file with its page key, title (Tech, Access, Walkthroughs, Ops), audience line from section 0 and
   one section {"id": "<letter>0", "heading": "Sections follow", "lines": ["to be filled: phase B1 to B4"]}; the
   Access skeleton also carries a section with "derived": "seat_by_screen" so the derived table is proven here.
4. Hook into build_site.main() as A0 did; run python3 scripts/build_logic_pages.py (not build_site.py); the checks;
   commit "logic B0: the page builder and four skeleton pages (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_pages.py` -> exit 0, last line "logic pages: 4 built".
- `ls docs/logic_tech.html docs/logic_access.html docs/logic_walk.html docs/logic_ops.html | wc -l` -> 4.
- `grep -c 'build_logic_pages' scripts/build_site.py` -> 2 (the import and the call).
- `grep -c '<table' docs/logic_access.html` -> at least 1, and `grep -c 'M10' docs/logic_access.html` -> at least 1
  (the derived table carries the admin screens).
- `python3 scripts/check_site.py | grep -c PASS` -> 3 (export and noindex on the new pages).
- `wc -l scripts/build_logic_pages.py` -> under 260.
- `git status --short` -> M scripts/build_site.py plus the nine new files above and nothing else beyond the
  committed state.

Metadata: depends_on [A0] . weight heavy . live_model no . coder opus . verify_class sample . kind seam-design
- [ ] B0 done

### 12.7 Phase B1: the Tech page

Goal: data/logic_tech.json carries section 7 as nine sections (7.1 to 7.9) with the figures of 6.4; the page renders.

Touches: data/logic_tech.json, docs/logic_tech.html (generated).

Steps: type 7.1 to 7.9 into nine sections with ids t1 to t9, tables first as section 7 says; 7.9's launch cut table
from 4.9 with one comment box for the section (12.0); open_items of t9: LQ9, LQ11, LQ17, LQ18, LQ19, LQ24, LQ27,
LQ28, LQ29, LQ36, LQ41, LQ43, LQ44, LQ46; "to be verified" and "to be decided" lines in their exact form; vendors
only as {I..} tokens (the builder renders them). No change to the builder in B1 to B4. python3
scripts/build_logic_pages.py; commit "logic B1: the Tech page (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_pages.py` -> exit 0.
- `python3 -c "import json;d=json.load(open('data/logic_tech.json'));print(len(d['sections']),[s['id'] for s in d['sections']])"`
  -> 9 and t1 to t9.
- `grep -c 'to be filled' docs/logic_tech.html` -> 0; `grep -c '{I' docs/logic_tech.html` -> 0 (every token rendered).
- `git status --short` -> M data/logic_tech.json, M docs/logic_tech.html only.

Metadata: depends_on [B0] . weight light . live_model no . coder opus . verify_class sample . kind transcription
- [ ] B1 done

### 12.8 Phase B2: the Access page

Goal: data/logic_access.json carries section 8 in its nine-part order; part 4 is the derived table; the page renders.

Touches: data/logic_access.json, docs/logic_access.html (generated).

Steps: nine sections a1 to a9 in section 8's order; a3 is the 4.8 table; a4 is {"derived": "seat_by_screen"} with the
5.4 note lines ("own" is read, own people; what the Logic analyst sees on L08 and L13); a5 the 4.6 workflow as a
table; a9 open_items LQ7, LQ9, LQ29, LQ40, LQ41, LQ42, LQ45. Seat names only, no person. python3
scripts/build_logic_pages.py; commit "logic B2: the Access page (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_pages.py` -> exit 0.
- the section one-liner -> 9 and a1 to a9; `grep -c 'to be filled' docs/logic_access.html` -> 0.
- `grep -o '>L[0-9][0-9][a-z]*<' docs/logic_access.html | sort -u | wc -l` -> 33, `grep -o '>V0[1-6]<'
  docs/logic_access.html | sort -u | wc -l` -> 6, `grep -c '>M07<' docs/logic_access.html` -> 1 (the derived table
  carries every screen once).
- `git status --short` -> M data/logic_access.json, M docs/logic_access.html only.

Metadata: depends_on [B0] . weight light . live_model no . coder opus . verify_class sample . kind transcription
- [ ] B2 done

### 12.9 Phase B3: the Walkthroughs page

Goal: data/logic_walk.json carries the call table, the design in one place and the four walkthroughs; the page renders.

Touches: data/logic_walk.json, docs/logic_walk.html (generated).

Steps: six sections: w1 the section 1 table with its five columns; w2 the design (4.2, 4.3, 4.6, 4.7, 4.4, 4.5 as
lines and tables); w3 to w6 Y01 to Y04 from section 9, each table with the columns n, at, seat, screen, action and
result, the "at" cell a full date ("10 Mar 2028"), the seat cell a seat name or "-", the screen cell a link
[id, "logic_wireframes.html#<id>"], and the three closing lists (client, ops, stored) as lines. python3
scripts/build_logic_pages.py; commit "logic B3: the Walkthroughs page (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_pages.py` -> exit 0.
- the section one-liner -> 6 and w1 to w6; `grep -c 'to be filled' docs/logic_walk.html` -> 0.
- `grep -o 'logic_wireframes.html#L[0-9a-z]*' docs/logic_walk.html | sort -u | wc -l` -> at least 10 (the steps link
  into the Logic tab).
- `git status --short` -> M data/logic_walk.json, M docs/logic_walk.html only.

Metadata: depends_on [B0] . weight light . live_model no . coder opus . verify_class sample . kind transcription
- [ ] B3 done

### 12.10 Phase B4: the Ops page

Goal: data/logic_ops.json carries section 10 as eight sections in plain words; the page renders.

Touches: data/logic_ops.json, docs/logic_ops.html (generated).

Steps: eight sections o1 to o8 in section 10's order; o1 one row per route of 4.4; o2 the checklist tables; o3 and o4
the figures of 6.4; o5 every row starting "to be decided: "; o8 open_items LQ10, LQ13, LQ14, LQ31, LQ33, LQ35.
Collegial wording, never an order. python3 scripts/build_logic_pages.py; commit "logic B4: the Ops page (logic plan,
8 Oct 2026)".

Done-criteria:
- `python3 scripts/build_logic_pages.py` -> exit 0.
- the section one-liner -> 8 and o1 to o8; `grep -c 'to be filled' docs/logic_ops.html` -> 0.
- `git status --short` -> M data/logic_ops.json, M docs/logic_ops.html only.

Metadata: depends_on [B0] . weight light . live_model no . coder opus . verify_class sample . kind transcription
- [ ] B4 done

### 12.11 Phase C1: the checks of section 11, green

Goal: scripts/check_logic.py runs the content checks of section 11 over the five data files and passes; the full
build passes; the protected files are unchanged.

Touches: scripts/check_logic.py (new); fixes only in data/logic_screens.json, data/logic_tech.json,
data/logic_access.json, data/logic_walk.json, data/logic_ops.json and their generated pages.

Steps:
1. Write scripts/check_logic.py, stdlib only, in the shape of check_phase9.py (numbered checks, "PASS n: <what>" or
   "FAIL n: <what>", exit 1 on any FAIL). The nine checks:
   1. schema and targets: build_logic_wireframes.validate_logic_screens() (or its name) raises nothing;
   2. seats and writes: every screen's role has the ten seats; every write names seats and an event listed in
      events; every event on a screen starts with its base id;
   3. open items both ways: every "LQ" token in any spec.dev line, any page line, table cell or open_items list is
      an id in data/logic_gaps.json, and every item of data/logic_gaps.json appears (its id in spec.dev) on every
      screen its lands_on names, or (its id in open_items) on the page it names, or on at least one V screen for "V";
   4. walkthroughs: in data/logic_walk.json every table whose columns are n, at, seat, screen, action and result has
      a screen cell whose link text is an id in data/logic_screens.json and a seat cell that is one of the ten seats
      or "-";
   5. working days: every "at" cell of those tables parses with datetime.strptime("%d %b %Y") and its weekday is
      Monday to Friday;
   6. sums: on L14, L14a, L03, L03a, L03b, L04, L04a and L05 every table cell that is digits and "/" only splits on
      "/" to six numbers summing to 100 (a mix) or to two or more numbers summing to 100 (sleeve weights);
   7. instalments: on L15, L15a and L15b every cell holding "(" is read as sleeve parts split on ";", each part's
      amount the last whole number before "(" and its fund amounts the whole numbers inside the brackets (tokens
      split on spaces, commas stripped), and the fund amounts sum to the sleeve amount;
   8. names: no fund name from the board's L04 and L09 table rows (read from data/screens_v02.json at run time)
      occurs in data/logic_screens.json (check 4 already keeps every actor a seat); site.FORBIDDEN absent from the
      five pages;
   9. protected files: `git status --short -- data/seed docs/seed docs/review docs/audiences data/screens_v02.json
      data/admin_screens.json data/v02/freeze.json data/gaps.json data/tracker.json` is empty (subprocess, as
      check_phase9.py runs the validator).
2. Run it; fix content where it fails (a fix to a check is allowed only when the check misreads a shape 12.0 pins,
   said in the report); rerun until 9 PASS.
3. python3 scripts/build_site.py; check_phase9.py and check_site.py; commit "logic C1: the section 11 checks as
   scripts/check_logic.py, green (logic plan, 8 Oct 2026)".

Done-criteria:
- `python3 scripts/check_logic.py | grep -c PASS` -> 9, exit 0; `grep -c FAIL` -> 0.
- `python3 scripts/build_site.py` -> exit 0; `python3 scripts/check_phase9.py | grep -c PASS` -> 19;
  `python3 scripts/check_site.py | grep -c PASS` -> 3.
- `git status --short` -> only scripts/check_logic.py new and the logic data and pages modified; nothing under
  docs/review/, docs/audiences/, docs/seed/, data/seed/.

Metadata: depends_on [A4, B1, B2, B3, B4] . weight heavy . live_model no . coder opus . verify_class sample .
kind seam-design
- [ ] C1 done

### 12.12 Phase C2: the board links

Goal: the main board carries a "Logic panel" tab after "Admin seed"; the Changelog tab carries the logic rows; PLAN.md
carries the status section; the review link and the audience files are unchanged.

Touches: scripts/build_site.py (TABS, the label lookup at :914, the changelog tuple at :909-910, one CSS class),
data/changelog_logic.json (new), PLAN.md (section 27 appended), every main-board page under docs/ regenerated by
the nav change.

Steps:
1. TABS: insert ("logic_wireframes.html", "Logic panel") after ("admin_wireframes.html", "Admin seed"), with a
   comment in the file's style ("Logic panel added 8 Oct 2026 (PLAN_logic_panel_v03.md C2): one tab for the five
   logic pages, which link each other through logic_subnav()"). REVIEW_TABS unchanged.
2. The label lookup dict(TABS + SEED_PAGES) at :914 gains LOGIC_PAGES. The changelog tuple at :909-910 gains
   ("changelog_logic.json", "c-logic", "Logic panel side wireframes"); a c-logic CSS rule like c-sq's.
3. data/changelog_logic.json in the schema of changelog_seed.json: {source, note, rows}, five rows dated 8 Oct 2026
   (one per logic page: what it is, pages [its href], cause "Vatsal, 8 Oct 2026") and one row for data/logic_gaps.json
   (the 46 open items, pages ["logic_tech.html", "logic_access.html", "logic_ops.html"], cause "Vatsal, 8 Oct 2026
   (logic side wireframes)"). Hand-formatted like the other changelog files.
4. PLAN.md: append "## 27. Status, <date> (logic panel side wireframes, PLAN_logic_panel_v03.md)" in the shape of
   section 26: why, what was built (the 39 screens, the four pages, the checks), what is open (phase D, the LQ
   items, the fold), what is owed by people (the two questions for Vatsal, the logic panel review date).
5. python3 scripts/build_site.py; the checks; commit "logic C2: the Logic panel tab, the changelog rows and the
   status section (logic plan, 8 Oct 2026)". The handoff is the closure ritual's.

Done-criteria:
- `python3 scripts/build_site.py` -> exit 0.
- `python3 scripts/check_phase9.py | grep -c PASS` -> 19 (its nav literal still holds); `python3
  scripts/check_site.py | grep -c PASS` -> 3; `python3 scripts/check_logic.py | grep -c PASS` -> 9.
- `grep -c '>Logic panel<' docs/index.html` -> 1; `grep -c '>Logic panel<' docs/review/index.html` -> 0;
  `grep -rc 'logic_' docs/audiences/ | grep -v ':0'` -> empty.
- `grep -c 'c-logic' docs/changelog.html` -> at least 1.
- `grep -c '^## 27. Status' PLAN.md` -> 1.
- `git status --short -- docs/review docs/audiences docs/seed data/seed` -> empty.

Metadata: depends_on [C1] . weight heavy . live_model no . coder opus . verify_class complete . kind seam-design
- [ ] C2 done

### 12.13 Phase D: Vatsal's look (HUMAN-GATED)

Goal: Vatsal opens the five pages on his machine and decides what only he can.

What he decides:
1. The visual pass at laptop width: the panel is desktop only; the pages must still open on a phone. Whether the
   "Logic panel" tab grows the header at 1,512 px; if it does, "Admin seed" and "Logic panel" fold under one tab
   with two sub-nav rows (a follow-up change, not in this plan).
2. The two questions from A4: whether the operating seats stay "Principal officer 01" and "Logic analyst 01";
   whether a state that matters is missing from the 39.
3. Anything settled under the cause "logic plan, 8 Oct 2026" that he vetoes.
4. When the pages go up: the push is his word, never the executor's.

Metadata: depends_on [C2] . weight light . live_model no . coder none . verify_class prose . kind human-gate
- [ ] D done

## 13. After acceptance (not in this plan)

The team comments under their names on the five pages. A later plan applies what was accepted: because the side
screens are already in the board's schema, accepted screens move into section L of data/screens_v02.json as they
are, each with its cause ("approved by <first name>, <date>"); then the freeze register entries, M03's plan versions
tab, the H05 forms for the four sizes, the S11 ladder and its urgent sibling, the changes to L06's publish rule and
Q01's "also runs on a publish" line, tracker W04 delivered, and a pack for Spinach in the shape of the admin brief
with the access write-up, the approval workflow and the change life cycle in front. Rehearsal values and examples do
not travel: the merge carries shapes, never values.

## 14. Placeholders and to be verified

- Every logic value on these pages is a rehearsal value until W04 and W30 deliver the real ones.
- Every count and amount is a typed example until there are plan holders to count.
- The launch date of 1 Feb 2027 is the board's target; the example dates move with it.
- Prices never appear. Minimum SIP and exit-load windows per fund are rehearsal values on synthetic funds.
- to be verified: LQ11, LQ12, LQ13, LQ18, LQ19, LQ24, LQ27, LQ28, LQ29, LQ36, LQ38, LQ43.
