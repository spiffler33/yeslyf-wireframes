# yeslyf journey wireframes v0.1 - team review
Exported 9/9/2026, 2:57:42 PM

## Quick reveal (pre-paywall)
- **R08 Sketching your paths**
  I am assuming we can change inflation rate at any point in back end

## Paywall and checkout
- **P04 Pay**
  Subject to regulatory approvals on payment types

## Data collection
- **D03 Loans and dues**
  Don't we need screens for when each loan is clicked - the next screen? Also, need field for other loans like loans to friend etc
- **D04 Insurance**
  Same ques - don't ne need screens within each clicks?

## Outputs: clarity, plan, investment plan
- **G04 Plan: emergency fund**
  Emergency funds should be for 6 months as basic rule

## Execution
- **E03 Place a mutual fund order**
  I am not sure how this integration (and hence screens) will look like
- **E04 ETFs and stocks via smallcase**
  Not sure how we will connect to brokers here or at smallcase end

## Living dashboard
- **H06 Vault**
  May be we want to include rationale for investment products recommended to them
- **H08 Community**
  IS community tab always available in the app - is it at homepage or in menu options or yet to be decided?

## Lifecycle and reviews
- **Q03 Subscription: cancel, failed payment, lapsed**
  Have to check regulations of refund policy as RIA

## Returning-user states
- **N01 Returning-user state machine**
  More nudges should be planned rather than just 2-3, we may call them also offline

## Logic panel (built by devs)
- **L02 Assumptions**
  Will need bucket for reits/invits 
- **L03 Buckets and cohorts**
  Cash wont be in recommended asset allocation. Shortest/safest would be debt funds.
- **L04 Instrument universe**
  Where do we tag instrument to category? Where do we keep rules like within Equity bucket, shares should not be more than 40% or each product should not be more than 20%
- **L07 Market inputs (simple)**
  What does commentary mean here?
- **L05 Staging and impact preview**
  Where are the calculations done to allocate investment plan to users?
- **L08 Audit and versions**
  Need to check from regulatory angle what all need to be saved for audit purposes
