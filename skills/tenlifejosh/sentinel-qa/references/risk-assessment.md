# Risk Assessment — Reference Guide

Reputational risk, legal exposure, trust damage potential, and business impact assessment
before anything goes public. The framework for knowing when to stop and when to ship.

---

## TABLE OF CONTENTS
1. The Risk Framework
2. Legal Risk Categories
3. Reputational Risk Assessment
4. Platform Risk (TOS Compliance)
5. Trust Damage Scenarios
6. The Risk Matrix
7. Risk Escalation Criteria
8. Common Risk Scenarios
9. Risk Mitigation Strategies
10. Pre-Ship Risk Checklist

---

## 1. THE RISK FRAMEWORK

### Risk vs. Caution
Risk assessment is NOT about being overly cautious or blocking everything that's not perfect.
It IS about identifying:
1. **Legal risks**: Things that could result in FTC violations, copyright claims, false advertising suits
2. **Reputational risks**: Things that could go viral negatively or damage the brand
3. **Trust risks**: Things that could cause buyers to feel deceived or disappointed
4. **Platform risks**: Things that could get accounts banned or content removed

Most content has **zero significant risk**. Don't block shipping for hypothetical concerns.
Flag real risks. Approve everything that doesn't have real, specific risks.

### The Two Questions
Before blocking anything, answer:
1. **What specifically could go wrong?** (Be concrete — not "someone might be offended")
2. **How likely is it, and what's the impact?** (Rare + minor = don't block)

If you can't answer #1 concretely → approve.

---

## 2. LEGAL RISK CATEGORIES

### HIGH RISK — Block and Escalate

**False Advertising / FTC Violations**
```
Red flags (any of these = STOP):
- "Guaranteed results" with no qualifying language
- Specific income/result claims without verified proof:
  "Make $10,000 in your first month"
  "Lost 30 pounds in 2 weeks"
  "Your site will rank #1 in 90 days"
- Testimonials that imply typical results without disclosure
- Claims about government approval or clinical proof that don't exist

FTC-compliant versions:
"Typical results vary. In our beta test, X% of users achieved Y."
"Joshua earned $X — your results will depend on your effort and market."
"*Results not typical. This is one customer's experience."
```

**Copyright Infringement**
```
Red flags:
- Images sourced from Google Images without licensing
- Statistics or charts reproduced from paid research
- Long quotes (100+ words) from books/articles without attribution
- Music in videos without licensing
- Logos or trademarks of other companies used without permission

Safe harbors:
- Images from Unsplash, Pexels, Pixabay (free commercial license)
- Facts are not copyrightable (but specific expression is)
- Short quotes with attribution (fair use — but not a guarantee)
- Our own original content and photography
```

**Defamation**
```
Red flags:
- False statements of fact about named individuals or companies
- "Competitor X does Y" without verifiable proof
- Client stories that could identify someone who hasn't consented
- Negative reviews of competitors that could be characterized as defamation

Safe practices:
- Opinions clearly labeled as opinions ("In my experience...")
- Factual claims only when verifiable
- Competitor comparisons factual and verifiable
```

### MEDIUM RISK — Flag and Fix

**Misleading Claims (Not False, But Unclear)**
```
Examples:
- "Thousands of customers" when we have 200
- "Industry-leading" without defined metric
- "As seen in [publication]" without full context
- Implying endorsement that doesn't exist

Fix: Add qualifier. "200+ customers." "Used by entrepreneurs in X niches." 
```

**Privacy Concerns**
```
Examples:
- Sharing customer email addresses or contact info
- Publishing customer names/stories without consent
- Including screenshots with identifiable personal information
- Location details that reveal where someone lives/works
```

---

## 3. REPUTATIONAL RISK ASSESSMENT

### The Virality Test
For any public content, ask: If this got 100,000 views with no context, how would it look?

Worst cases to check:
- Could this be screenshot and shared with a misleading headline?
- Could the first 5 words be quoted out of context to mean something different?
- Could this be interpreted as offensive by any reasonable group of people?
- Could someone with bad intentions weaponize this content?

### The Three Audiences Test
Every piece of content is seen by:
1. **Target audience**: People you're trying to reach → Is it valuable?
2. **Skeptics**: People who disagree or distrust you → Does it hold up to scrutiny?
3. **Journalists/critics**: People looking for a story → Is there anything exploitable?

Content should be designed to pass all three, not just the first.

### The Time Test
Would you be comfortable with this being publicly associated with your name in 5 years?
If not → revise or don't ship.

---

## 4. PLATFORM RISK (TOS COMPLIANCE)

### Twitter/X Community Standards
```
RISK: Account suspension / content removal
VIOLATIONS TO AVOID:
- Spam (mass identical posts, artificial engagement)
- Misleading information about products/outcomes
- Coordinated inauthentic behavior
- Harassment or threats
- Explicit content without Content Warning
```

### Gumroad Terms of Service
```
PROHIBITED CONTENT:
- Adult content (without age verification)
- Counterfeit digital products
- Copyrighted material sold without license
- Products with false claims
- Products violating US law

RISK FLAGS:
- "100% guaranteed results" in product description
- Health claims that could be medical advice
- Products that imply official affiliation (government, academic)
```

### Email CAN-SPAM Compliance
```
REQUIREMENTS (every commercial email):
- [ ] Accurate "From" name and address
- [ ] Not misleading subject line
- [ ] Physical postal address in footer
- [ ] Clear unsubscribe mechanism
- [ ] Unsubscribes honored within 10 days

RISK: FTC fines up to $50,120 per email for violations
```

---

## 5. TRUST DAMAGE SCENARIOS

### The Trust Ledger
Trust is built slowly and lost quickly. Each output either adds or subtracts:

**Trust Additions (+):**
- Delivered exactly what was promised
- Acknowledged a mistake openly
- Provided genuine value without asking for anything
- Was honest about limitations

**Trust Subtractions (-):**
- Product didn't deliver what description implied: -5 to -20
- Obvious AI content without disclosure: -3
- Factual error not corrected: -5 to -15
- False urgency (fake countdown timer): -10
- Broken links or failed downloads: -5

**Trust Destroyers (game over):**
- Charging for a product that's actually free elsewhere: -100
- Fake testimonials: -100
- Data breach or privacy violation: -100

### Customer Trust Thresholds
```
First-time buyer expectations:
- Product MUST match the description exactly
- Download MUST work on first try
- Confirmation email MUST arrive within minutes
- Any deviation from these = negative review risk

Repeat buyer expectations:
- Product quality improvement expected over time
- Customer support responsiveness expected
- Consistent brand experience expected
```

---

## 6. THE RISK MATRIX

### Scoring Each Risk

```
Probability Scale:
  1: Very unlikely (<5% chance)
  2: Unlikely (5-20% chance)
  3: Possible (20-50% chance)
  4: Likely (50-80% chance)
  5: Very likely (>80% chance)

Impact Scale:
  1: Negligible (no real effect)
  2: Minor (minor annoyance, small cost)
  3: Moderate (meaningful damage, moderate cost)
  4: Severe (significant damage, high cost)
  5: Critical (existential to business/reputation)

Risk Score = Probability × Impact

0-4:   Low risk    → Note but don't block
5-9:   Medium risk → Recommend mitigation
10-15: High risk   → Block until mitigated
16-25: Critical    → Block + escalate to founder
```

### Risk Scoring Examples

```
Scenario: Email with wrong first name variable unfilled
  Probability of issue: 3 (possible — depends on list quality)
  Impact: 2 (minor — looks sloppy, some unsubscribes)
  Risk Score: 6 — Medium → Block, fix variable

Scenario: Product description claims "100% guaranteed results"
  Probability of FTC issue: 2 (unlikely to be flagged on first offense)
  Impact: 5 (critical — FTC fines, platform bans, reputation)
  Risk Score: 10 — High → Block, rewrite claims

Scenario: Social post references competitor negatively
  Probability of backlash: 3 (depends on how known the competitor is)
  Impact: 3 (moderate — audience takes sides)
  Risk Score: 9 — Medium → Revise or remove competitor mention
```

---

## 7. RISK ESCALATION CRITERIA

### Escalate to Hutch (Do Not Handle Autonomously):

**Immediate escalation:**
- Any potential FTC violation (income claims, health claims)
- Any real copyright infringement concern
- Any scenario involving customer data privacy
- Legal claims or threats
- Content that could genuinely harm a third party
- Account at risk of permanent suspension

**Same-day escalation:**
- Risk score 16+ on any single asset
- New platform/channel where TOS is unclear
- Content involving faith/religion in ways that could divide
- Anything that would make a reasonable person uncomfortable seeing it associated with TLC

### Handle Autonomously (Don't Escalate):
- Minor copy issues, tone mismatches, style preferences
- Technical failures (broken links, wrong file version)
- Missing elements from checklist
- Brand inconsistencies
- Risk score under 10

---

## 8. COMMON RISK SCENARIOS

### Scenario 1: Income Claim in Product Copy
"Use this system to build a $5,000/month business."

**Risk**: FTC violation. Income claims require disclaimers and proof.
**Fix**: 
```
"Use this system to build a business — [Your Name] used this exact framework to reach $5K/month.
Results depend on your effort, market, and execution. See full disclaimer at [link]."
```

### Scenario 2: AI-Generated Testimonial
Fake or AI-generated testimonial in product listing.

**Risk**: FTC violation (paid/fake endorsements must be disclosed). Platform TOS violation.
**Fix**: Only use real testimonials from real customers. Include first name + context.
If no testimonials yet → say so honestly ("Be the first reviewer").

### Scenario 3: "As Seen In" Without Context
"As featured in Forbes, Entrepreneur, Business Insider."

**Risk**: Misleading if the "feature" was a guest post or paid placement.
**Fix**: "Joshua was featured in [publication]" with specific article link. 
Or: remove if no clear, genuine feature exists.

### Scenario 4: Statistics Without Source
"70% of small businesses fail in the first year because of [our specific problem]."

**Risk**: If the stat is wrong or the connection to your product isn't supported, it's misleading.
**Fix**: "According to [source, year], 70% of small businesses fail in year one. 
The #1 reason cited: [specific reason we address]."

---

## 9. PRE-SHIP RISK CHECKLIST

Run before ANY public-facing content goes live:

```
LEGAL:
- [ ] No unqualified "guaranteed results" claims
- [ ] No income/earnings claims without proof and disclaimers
- [ ] No copyright-protected material used without license
- [ ] No competitor defamation
- [ ] CAN-SPAM compliant (for emails)
- [ ] Platform TOS compliant

REPUTATIONAL:
- [ ] Passes the "headline test" (can't be twisted into a bad story)
- [ ] Would not embarrass the company if screenshotted without context
- [ ] Consistent with our stated values and past positions
- [ ] No private information disclosed without consent

TRUST:
- [ ] Claims are honest and deliverable
- [ ] Product/offer does what the copy says
- [ ] No fake urgency or manufactured scarcity
- [ ] No dark patterns or manipulative framing

RISK SCORE:
- [ ] Risk Matrix score calculated for any flagged items
- [ ] All items 10+ escalated to founder
- [ ] All items 5-9 mitigated before shipping
- [ ] Items under 5 noted but not blocking
```
