# yeslyf journey wireframes v0.1 - team review
Exported 09/09/2026, 13:55:14

## Read me first
- **X00 How to read this file**
  all execution happens via smallcase GW only

## Entry and identity
- **A01 First open**
  in four minutes --> in the next few minutes.
  
  use this screen to sort of welcome and prime the user
- **A02 Mobile number**
  pre-fill via mobile fetch based on permissions.
  
  
  don't need to explain why we are collecting mobile and not email 
  
  Show a T&C here itself
- **A03 OTP**
  resend with exponential backoff. limited to 3 retries.
  
  Simillarly, change number should also be limited to 3 attempts.
- **A04 Welcome video**
  Rather than auto generate captions. The video itself should have captions. We can then use that to highlight keywords as needed. 
  Skip should be allowed immediately rather than a 5 second delay. instead, show a confirmation modal if needed (e.g. The video explains how you can live a Yes life today and tomorrow. Are you sure you want to skip? Y/N).
  
  To account for slow networks, I would actually suggest bundling the video into the app itself. That way there will not be any network calls. When the videos are updated, we can publish new builds (or possibly build a config which will tell the app to load local video or fetch from source)

## Quick reveal (pre-paywall)
- **R01 Name and age**
  First Name --> Name
  if we're blocking under 18, then at the time of login itself, there should have been a T&C
- **R02 Household and city**
  Just Me | Me + Partner
  and Kids | And Parents
  
  Row 1 is a single select. If in row 1, you've selected 'Me + Partner', then row 2 becomes visible and allows multi-select
  
  these 4 blocks (with multi- select) in row 2 handles all the scenarios. 
  
  Why is city needed? 
- **R04 Total saved and invested**
  needs better verbiage 'other than the home you live in' is getting missed in all the text
- **R07 What matters at 50 / 65**
  this screen should have others 'type your own'
- **R09 The reveal**
  integration with martech as this will be a high likelihood drop off point
- **R10 Video: the 5 Alphas**
  how will we explain? AI generated video? 
- **R11 Video: the bridge**
  Generic Video? 
- **R12 Sample plan preview**
  I think that the sequencing of R09, R10, R11, R12 and X01 needs to be revisited. If a user has been convinced and wants to move forward then he should be taken to paywall and expectation setting should be done. If a user chooses not to move forward, then you can show a sample plan to entice them to understand what they are missing out. 
- **X01 Reveal saved (not paid)**
  where does 'see what members are saying' take you?

## Paywall and checkout
- **P03 Agreement and eSign**
  nice
- **P04 Pay**
  introduce coupon?

## Onboarding hub
- **O01 Meet your adviser / meet yeslyf**
  more info should be shown for Priya / Harish. add weight to the Advisor

## Data collection
- **A07 Fetching**
  multiple OTP journeys to be handled when working via AA. Consent to discover, Then consent to fetch per provider

## Outputs: clarity, plan, investment plan
- **G01 Building your plan**
  duplicate what was done for R08

## Adviser calls (DIWM)
- **K04 Book a review call (a la carte)**
  should not offer book a review to a DIY customer. One off calls are expensive as advisor needs a full context. 

## Execution
- **E02 One-time investing setup**
  prefill nominee to spouse
- **E05 Guided action outside the app**
  assume that we will also need screens to upload. then some section to view uploaded documents?

## Living dashboard
- **H02 Net worth growth**
  will we be able to show market movement growth? if not, I assume that this screen can be tweaked
- **H05 Your plan was updated**
  where will this be surfaced from? notifications?
- **H06 Vault**
  Entry Point?
- **H08 Community**
  I don't think this should be shown. if needed, give a menu to access community or some highlights 
  
- **H09 Profile and settings**
  can a member rebuild thier plan? what happens to old data/p[lans? how often will we allow this?

## Returning-user states
- **N01 Returning-user state machine**
  each of these potential drop off points should also feed into martech

## Admin (bought tools)
- **M01 Admin stack (bought, not built)**
  tool:appsmith? Spinach

## Logic panel (built by devs)
- **L04 Instrument universe**
  ISIN weights are a subset to category weights in L03 (cash / debt / hybrid / commodities / equity)
