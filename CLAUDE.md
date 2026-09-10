# CLAUDE.md - standing rules for this repository (v2, 10 Sep 2026)

This repo holds the yeslyf product board, the wireframes, and the admin/CRM spec for House of Alpha's yeslyf app.
spiff (Vatsal) directs the work. Read plan_v2.md for what to build now; PLAN.md sections 1 to 6 still describe the
repo, the data layer and the history. These rules override both where they conflict.

## People and voice
- First names only: Bhuvanaa, Harish, Gaurav, Kajal, Somil, Vatsal (spiff). No titles, no surnames, never "founders".
  Reviewer identities in the comment controls: the five names above, plus "Spinach" (the UI/UX studio) and
  "Compliance" (the compliance reviewers). Never invent a person's name.
- Tone in generated pages: plain, short, no sales language, no praise. Sentence case. Plain hyphens, no em dashes.
- ASCII only in files and pages. No emojis. Currency as "Rs", never the rupee symbol. Brand as "yeslyf", lowercase,
  everywhere, including at the start of a sentence.
- The app copy speaks in the first person as the yeslyf adviser voice (the V5 script). No adviser is named in copy.

## Attribution
- The Meeting, Gaps and Inputs tabs are frozen as of 9 Sep 2026. They keep the v1 rules they were built under
  (positions carry the first name of who said it and a reference; the ownership map sets defaults; "Vatsal
  recommendation" only on gaps and dependency blocks). Do not edit their content; only mark them frozen.
- For v0.2 pages the ownership map is retired. The team spoke in the meeting; product decisions after it are
  Vatsal's. Every change carries a cause and nothing else: a brief item ("brief T1"), a review row ("row 59"), or
  "Vatsal, 10 Sep 2026". No owner markers, no "to confirm" markers, no working drafts, no names on callouts.
  A callout names the item, never a person.
- Where plan_v2.md and the meeting brief disagree, plan_v2.md wins and the cause reads "Vatsal, 10 Sep 2026
  (supersedes brief <item>)". Both are shown on the Changelog tab.
- Unconfirmed vendor, regulatory or cost facts are written as "to be verified: <the item>". Never as facts, never
  with a person's name.
- Never write "we recommend". Never write "recommendation" on v0.2 pages. A gap found during the build is written
  "gap, to be decided" and appended to gaps.json with the screen it came from.
- The frozen tabs' attribution is not transferable: never move a position to another name, never merge two
  people's positions into one unattributed line.

## Files
- inputs/ is read-only. Never edit, rename, or reformat anything in it.
- data/*.json is the single source of truth. Pages are generated; never hand-edit docs/.
- Keep the v0.1 HTML files intact under docs/v01/ and serve them as-is; they must stay byte-identical to inputs/v01/.
- Screen IDs (A01, R09, N01, L04...) are permanent. New screens get the next free number in their section (E07, L09,
  N02). Instances of a repeated layout get a letter suffix on their parent (D02a to D02j, H01a to H01k, D08a to
  D08h). Never renumber. A dropped screen keeps its ID with status "dropped" and a pointer to where its content
  went; it never renders in the flow; every branch to it is rerouted and logged.
- Every screen carries a template tag (appendix F of plan_v2.md) so the studio can count unique layouts and total
  screens separately.
- Returning-user state IDs S1 to S15 are permanent; new states get the next free number. S26 is not used.
- A link whose target is its own screen is an in-place action (expander, upload, download) and its spec logic says
  what it does. A self-link standing in for a screen that must exist is a bug.
- Every screen carries at least one event name (appendix D of plan_v2.md) and a compliance flag with a reason
  category (appendix G). No screen without both.
- Review rows keep their numbers 1 to 73. New inputs append. The second review round writes to the "v02_comments"
  sheet tab and never to the first-round tabs.

## Working discipline
- Commit after every phase and after every generated rebuild; messages say what changed and why.
- Before writing a parser for a file, check its real type with `file`; several .docx files in inputs are plain text.
- Extract data from the v0.1 HTML by evaluating the embedded script in a Node vm context, not by regex.
- Validate before building: every screen has an ID, a template, a path set, events and a compliance flag; every
  state has a landing screen, a primary action, a ladder and an exit; every branch resolves.
- If a rule here would be broken by something in plan_v2.md or in a prompt, stop and say so instead of doing it.
- Ask spiff only when blocked; batch questions; at most three at a time. Otherwise proceed and report.
- Secrets never go in the repo: no sheet endpoint URL in committed files (the page reads it from localStorage or a
  config field), no tokens, no personal data beyond first names.

## What not to do
- Do not redesign the wireframes' visual style; low-fi grey is intentional. Spinach owns visual design.
- Do not add frameworks, bundlers, or dependencies beyond Python 3 and Node for scripts.
- Do not invent positions, prices, vendor facts, call counts, or minutes. Prices are "Rs ___". Included calls are
  "N". Minutes are "about N minutes". Unconfirmed facts are "to be verified: <item>".
- Do not name an adviser on any screen. Do not draw a DIFM card on the paywall or an in-app DIFM upsell.
- Do not add a partner ask, a partner share, or a partner state anywhere.
- Do not collapse repeated layouts into one representative screen; draw every instance and tag the template.
