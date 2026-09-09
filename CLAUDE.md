# CLAUDE.md - standing rules for this repository

This repo holds the yeslyf product board, the wireframes, and the admin/CRM spec for House of Alpha's yeslyf app.
spiff (Vatsal) directs the work. Read PLAN.md for what to build. These rules override PLAN.md where they conflict.

## People and voice
- First names only: Bhuvanaa, Harish, Gaurav, Kajal, Somil, Vatsal (spiff). No titles, no surnames, never "founders".
- Attribution is sacred. A position carries the name of the person who said it and a reference. Never move a position
  to another name, never merge two people's positions into one unattributed line, never write "we recommend".
- "Vatsal recommendation" is written only on gaps (things nobody raised) and on dependency blocks. Nowhere else.
- Owner of a workstream holds the default. The ownership map in PLAN.md section 2 decides who that is; do not infer.
- Tone in generated pages: plain, short, no sales language, no praise. Sentence case. Plain hyphens, no em dashes.
- ASCII only in files and pages. No emojis. Currency as "Rs", never the rupee symbol.

## Files
- inputs/ is read-only. Never edit, rename, or reformat anything in it.
- data/*.json is the single source of truth. Pages are generated; never hand-edit docs/.
- Keep the v0.1 HTML files intact under docs/v01/ and serve them as-is.
- Screen IDs (A01, R09, N01, L04...) are permanent. New screens get the next free number in their section
  (H10, H11, D03a, L09, L00). Never renumber.
- Review rows keep their numbers 1 to 73. New inputs append.

## Working discipline
- Commit after every phase and after every generated rebuild; messages say what changed and why.
- Before writing a parser for a file, check its real type with `file`; several .docx files in inputs are plain text.
- Extract data from the v0.1 HTML by evaluating the embedded script in a Node vm context, not by regex.
- Validate before building: every open item has an owner and at least one named position; every input row has a
  status; every option lists holders or is marked "possible form".
- If a rule here would be broken by something in PLAN.md or in a prompt, stop and say so instead of doing it.
- Ask spiff only when blocked; batch questions; at most three at a time. Otherwise proceed and report.
- Secrets never go in the repo: no sheet endpoint URL in committed files (the page reads it from localStorage or a
  config field), no tokens, no personal data beyond first names.

## What not to do
- Do not redesign the wireframes' visual style; low-fi grey is intentional. Spinach owns visual design.
- Do not add frameworks, bundlers, or dependencies beyond Python 3 and Node for scripts.
- Do not invent positions, prices, or vendor facts. Prices are "Rs ___" placeholders. Vendor capabilities that are not
  confirmed (for example smallcase Gateway mutual-fund support) are written as conditions to verify, with the name of
  who verifies.
- Do not write anything that reads as a decision taken on someone else's behalf.
