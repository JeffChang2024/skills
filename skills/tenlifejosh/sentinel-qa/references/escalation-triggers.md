# Escalation Triggers — Reference Guide

When to stop and get Hutch's judgment vs. handle autonomously. The decision framework
for knowing when human oversight is required.

---

## 1. ESCALATION PHILOSOPHY

### The Core Rule
Escalate when:
1. **Stakes are too high** for an agent error to be recoverable
2. **Legal, financial, or reputational risk** is material
3. **Contradictory signals** require judgment calls above agent authority
4. **New situations** that no existing rule covers

Don't escalate when:
1. The right answer is clear in existing guidelines
2. The fix is purely technical and reversible
3. The issue is editorial (style, voice, minor improvements)
4. The decision is within normal operating parameters

### The Reversibility Test
Can this be undone easily if we get it wrong?
- YES → handle autonomously
- NO (or "with difficulty") → consider escalating
- Impossible to undo → always escalate

---

## 2. IMMEDIATE ESCALATION — STOP EVERYTHING

These situations require contacting Hutch before ANY further action:

```
ESC-1: Any suspected legal violation
  Copyright infringement, FTC violation, defamation risk
  → Stop asset | Document issue | Contact Hutch immediately

ESC-2: Customer data exposure
  Customer PII in public content, database breach, privacy violation
  → Stop all activity | Document scope | Contact Hutch immediately

ESC-3: Platform account at risk of suspension
  TOS violation notice from Gumroad, Amazon, Twitter/X
  → Stop all activity on that platform | Contact Hutch immediately

ESC-4: Financial discrepancy > $100
  Revenue doesn't match platform reports
  Money leaving account unexpectedly
  → Document discrepancy | Contact Hutch immediately

ESC-5: Content about real, named individuals
  Anything that could harm a specific person's reputation
  → Stop | Document | Contact Hutch
```

---

## 3. SAME-DAY ESCALATION

Escalate to Hutch within the same day (not emergency, but needs human judgment):

```
SD-1: New platform or channel where TOS is unclear
  We've never published to this platform before; unclear what's allowed
  → Pause, ask Hutch before proceeding

SD-2: Strategic pricing decision outside normal range
  Price significantly above or below our normal range without clear rationale
  → Pause, present Hutch with options and recommendation

SD-3: Content that could be politically divisive
  Anything touching elections, political parties, controversial social issues
  → Pause, ask Hutch before publishing

SD-4: Response to a public complaint or negative review
  Any public-facing response to customer criticism
  → Draft response, present to Hutch before posting

SD-5: Partnership or collaboration content
  Content created with or about another person/company
  → Verify Hutch approves before shipping
```

---

## 4. ROUTINE ESCALATION (INCLUDE IN NEXT INTERACTION)

Include in the next natural conversation with Hutch, don't interrupt:

```
RE-1: Repeated quality failures from specific agent
  Same agent failing QA 3+ times on similar issues
  → Mention in next conversation: "Pattern noticed with [Agent]"

RE-2: Process improvement recommendations
  "The current X process is causing Y failures consistently"
  → Note in next conversation or update HEARTBEAT.md

RE-3: Competitive intelligence worth attention
  During audits, noticed competitor significantly improved their product
  → Mention to Hutch during next check-in

RE-4: Opportunity spotted during routine review
  "The product we just audited is underpriced vs. market"
  → Note in next conversation
```

---

## 5. ESCALATION COMMUNICATION FORMAT

When escalating to Hutch:

```
🚨 ESCALATION: [Brief description]

Severity: [IMMEDIATE / SAME-DAY / ROUTINE]

What's happening:
[2-3 sentences, facts only]

What I've already done:
[Any actions taken so far]

What I need from you:
[Specific decision or approval needed]

Options (if applicable):
A) [Option A with brief pro/con]
B) [Option B with brief pro/con]
My recommendation: [Which option and why]

Time sensitivity:
[Any deadline or urgency context]
```

---

## 6. HANDLE AUTONOMOUSLY — REFERENCE LIST

These situations do NOT require escalation (handle and document):

- Typos, grammar errors, style improvements
- Missing elements that are clearly defined in standards
- Broken links (fix and verify)
- Wrong file version (upload correct version)
- Minor formatting issues
- Placeholder text (return to creator to fill)
- Technical failures with clear fix path
- Brand consistency issues (correct and proceed)
- Missing tags, categories, metadata (add and proceed)
