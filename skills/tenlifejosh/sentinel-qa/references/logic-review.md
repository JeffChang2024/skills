# Logic Review — Reference Guide

Internal consistency checks, contradiction detection, factual accuracy verification, and
claims substantiation. Making sure the content is true, consistent, and makes sense.

---

## 1. THE LOGIC REVIEW PURPOSE

Logic review is different from proofreading or style review. It asks:
- Is this internally consistent? (No contradictions)
- Is this factually accurate? (Claims are true)
- Does the argument hold together? (The logic chain is sound)
- Are the numbers right? (Math and statistics are correct)

---

## 2. INTERNAL CONSISTENCY CHECKS

### Contradiction Detection
```
Read the full asset and flag any place where:
1. The same fact is stated differently in two places
   "Perfect for families with young kids" vs. "Designed for parents of teenagers" → Contradiction
   
2. A promise in one section conflicts with a limitation in another
   "Works for any business" [headline] vs. "Best for service businesses under $1M revenue" [fine print]
   
3. Numbers don't add up
   "5 chapters covering 12 topics" → count the topics, is it actually 12?
   "47 pages" → verify the page count matches
   
4. Timeline/sequence is off
   Step 3 says "after completing the worksheet from Step 5" → wrong order
   "Submit by January 1st" in a February email
```

### The Internal Cross-Reference Check
```
For any reference to another part of the document:
- "See page 14 for..." → does page 14 have what's referenced?
- "As discussed in Chapter 3..." → is it in Chapter 3?
- "Use the template in Appendix A" → does Appendix A exist with that template?
- "See the FAQ section below" → is there an FAQ section below?
```

---

## 3. FACTUAL ACCURACY

### Claim Verification Protocol

For every factual claim, apply this test:

```
LEVEL 1: Verify it exists
"Studies show X" → find the study
"According to [source]" → find the source
"X% of businesses do Y" → find the data

LEVEL 2: Verify it's current
Statistics older than 3 years should be re-verified
"As of 2020..." in a 2024 document may be outdated

LEVEL 3: Verify it means what you imply
"50% of marriages end in divorce" cited in context of financial planning
→ Does this stat actually support the point being made?
→ Or is it being used misleadingly?
```

### Common False Facts to Watch For
```
FREQUENTLY MISQUOTED STATISTICS:
- "It costs 5x more to acquire a new customer than retain one" (real but often misattributed)
- "Humans have an 8-second attention span" (this study was misrepresented)
- "Only 8% of New Year's resolutions succeed" (origin unclear)
- "Most small businesses fail in the first year" (real, but often exaggerated)

APPROACH: If you can't find the primary source in 2 minutes → remove the claim or qualify it.
"Many entrepreneurs report..." is better than a false citation.
```

---

## 4. MATH & NUMBERS VERIFICATION

### Number Audit
```
Check every number in the document:
- Page counts: Does "47 pages" match actual page count?
- Prices: Do "save 20%" calculations add up correctly?
- Lists: Does "3 ways to..." have exactly 3 ways?
- Time estimates: Are "5-minute exercises" actually ~5 minutes?
- "Worth $200" claims: Is the stated value defensible?
```

### Pricing Math
```
If a product claims pricing:
"$97 value for just $27" → Is the $97 value defensible?
"Save $20 today" → $X original - $20 = $Y sale price, do the numbers work?
"3 payments of $19" → Is $57 the correct total (or is it $57 vs advertised total)?
```

---

## 5. ARGUMENT & LOGIC FLOW

### The Argument Chain Check
For persuasive content (sales copy, proposals, pitches):
```
Map the argument:
1. PROBLEM: Is the problem stated clearly and accurately?
2. CONSEQUENCE: Is the consequence of the problem real and relevant?
3. SOLUTION: Does our solution actually address the stated problem?
4. PROOF: Does the proof (testimonials, data) actually support the claims?
5. CTA: Does the call to action logically follow from the argument?

If any link in the chain is weak → the whole argument fails.
```

### The Scope Consistency Check
```
If the product is "for beginners," the content should be beginner-appropriate:
- Technical jargon not defined → mismatch
- Assumes advanced knowledge → mismatch
- Too simple for stated audience → also a mismatch

If the product is "comprehensive," it should be comprehensive:
- Missing obvious topics for the subject → mismatch
- Shallow coverage of key topics → mismatch
```

---

## 6. LOGIC REVIEW VERDICT

### Output Format
```
LOGIC REVIEW FINDINGS:

CONTRADICTIONS:
1. [Location 1]: States "[Exact quote 1]"
   [Location 2]: States "[Exact quote 2]"
   Conflict: [Describe the contradiction]
   Fix: [Which version is correct, or how to reconcile]

UNVERIFIED CLAIMS:
1. Claim: "[Exact quote]"
   Issue: Could not verify source
   Recommendation: [Remove | Qualify | Source]

MATH ERRORS:
1. [Location]: States [wrong calculation]
   Actual: [correct calculation]
   Fix: Update to [correct number]

INTERNAL REFERENCE FAILURES:
1. [Location]: References [something] at [destination]
   Issue: [Destination doesn't exist / has different content]
   Fix: [Update reference or create missing content]

VERDICT: 
- LOGIC PASS: No significant logic issues found
- LOGIC FAIL: [Number] issues found — list above must be resolved before shipping
```
