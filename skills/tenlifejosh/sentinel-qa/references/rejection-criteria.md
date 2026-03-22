# Rejection Criteria — Reference Guide

What automatically fails QA with no revision option — hard stops that require a complete restart
or escalation. These criteria exist to protect the company from serious harm.

---

## 1. AUTO-REJECT — HARD STOPS (No Revision Path)

These conditions result in immediate REJECTED verdict with escalation to Hutch.
Do not attempt to fix these yourself — they require founder judgment.

### Legal Hard Stops
```
LH-1: Unqualified guaranteed results claims
  "Guaranteed to earn $X" / "Guaranteed weight loss" / "Guaranteed first-page Google ranking"
  → REJECT + ESCALATE: FTC violation risk
  
LH-2: Identifiable customer data published
  Customer name + email + purchase data visible in public content
  → REJECT + ESCALATE: Privacy violation, potential GDPR/CCPA issue
  
LH-3: Clearly copyrighted material (images, text, data)
  Copyrighted stock images downloaded without license
  Substantial reproduction of another's work without permission
  → REJECT + ESCALATE: Copyright infringement

LH-4: Content about a specific person that could be defamatory
  False factual statements about identifiable individuals
  → REJECT + ESCALATE: Defamation risk
```

### Business Hard Stops
```
BH-1: File is completely corrupted or empty
  File opens to blank pages, unreadable, or error state
  → REJECT: Return to creator, regenerate from source
  
BH-2: Wrong product file uploaded
  Listing for Product A contains Product B's file
  → REJECT: Serious customer experience failure + reputation risk
  
BH-3: Price is $0.00 on a paid product
  Product accidentally set to free
  → REJECT: Immediate revenue impact
  
BH-4: Product contains another company's confidential content
  Internal documents, private communications, proprietary third-party content
  → REJECT + ESCALATE
```

---

## 2. AUTO-REJECT — FIX BEFORE RE-REVIEW

These conditions mean REJECTED, but can be fixed and re-submitted without escalation.

```
FR-1: Placeholder text present anywhere in public-facing content
  [PLACEHOLDER], Lorem ipsum, [CLIENT NAME], TBD, INSERT X HERE
  → REJECT: Fix all placeholders, re-submit

FR-2: Broken primary download link or purchase flow
  Main product file not downloadable, purchase page errors
  → REJECT: Fix technical issue, verify flow, re-submit

FR-3: Duplicate/wrong version file uploaded
  Old version of product uploaded; version on cover doesn't match filename
  → REJECT: Upload correct file, verify, re-submit

FR-4: Missing required legal element in email
  No unsubscribe link OR no physical address in commercial email
  → REJECT: Add required elements, re-submit

FR-5: Obvious factual error with material impact
  Wrong company name, wrong price stated in copy, wrong date for an event
  → REJECT: Correct the error, re-submit
```

---

## 3. REJECTION THRESHOLD MATRIX

| Asset Type | Auto-Reject Threshold |
|---|---|
| New product launch | Any single hard stop item |
| Email to full list | Any hard stop + any missing legal element |
| Social media post | Legal hard stops only |
| Product update | Hard stops + wrong file issues |
| KDP submission | Any single hard stop + file specification failures |

---

## 4. REJECTION REPORT FORMAT

When issuing a REJECTED verdict:

```
❌ QUALITY ASSURANCE — REJECTED

Asset: [Name]
Date: [Date]
Reviewer: Sentinel Agent

REJECTION REASON(S):
1. [Rejection criterion code] — [Description]
   Specific finding: [Exact quote or location]
   Required action: [What must be done]

ESCALATION REQUIRED: YES / NO
Escalate to: Hutch [if YES]
Escalation reason: [Why founder needs to see this]

RE-SUBMISSION PROCESS:
1. Address all rejection reasons listed above
2. Re-submit to Sentinel for new review
3. Confirm all fixes in re-submission message
4. Do not attempt to ship this asset until APPROVED verdict received

This asset CANNOT ship in its current state.
```

---

## 5. REJECTION PATTERN LOG

Track rejections to find systemic issues:

```
If the same rejection criterion fires 3+ times in 30 days:
  → Systemic process problem, not individual error
  → Update the creation process (template, SOP, checklist)
  → Notify the creating agent of the pattern
  → Create preventive step to catch this before QA review

Example: FR-1 (placeholder text) fires 4 times in January
  → Creator is using templates and forgetting to fill placeholders
  → Fix: Add "search for [brackets]" as final step in creation SOP
  → Fix: Add pre-submit checklist to template itself
```
