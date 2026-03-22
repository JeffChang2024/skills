# Failure Logging — Reference Guide

The Failure-to-Rule system: how to document QA failures so they improve the process
rather than just getting fixed and forgotten.

---

## 1. THE FAILURE-TO-RULE SYSTEM

### Philosophy
Every failure is information. A fixed bug that's not understood will happen again.
The Failure-to-Rule system converts individual failures into systemic improvements.

### The Four Steps
```
1. CATCH: QA review catches the failure
2. DOCUMENT: Log what failed, where, why
3. ANALYZE: Is this a one-off or systemic?
4. IMPROVE: Update the checklist, SOP, or template
```

---

## 2. FAILURE LOG FORMAT

```markdown
## Failure Log Entry — [YYYY-MM-DD]

**ID:** F-[YYYYMMDD]-[NNN]  (e.g., F-20240115-001)
**Asset:** [Name of the asset that failed]
**Asset Type:** [Product / Email / Social / etc.]
**Caught By:** Sentinel Agent
**Caught At:** [Review stage — pre-publish, audit, post-launch]

### What Failed
[Specific description of the failure, quoting exact text or describing the exact issue]

### Failure Category
Choose one:
- [ ] Content (missing/wrong content)
- [ ] Technical (broken file, link, functionality)
- [ ] Brand (off-voice, off-visual)
- [ ] Legal/Risk (compliance or exposure issue)
- [ ] Process (workflow failure that allowed this to happen)
- [ ] Version (wrong version shipped or referenced)

### Root Cause
[One sentence: why did this happen?]
Examples:
- "Template not updated before use"
- "File not tested after upload"
- "Creator assumed X but Y was true"
- "No checklist step covered this scenario"

### Impact
- Was this caught before shipping? YES / NO
- If caught after shipping: [How many customers affected?] [How long was it live?]
- Severity: CRITICAL / HIGH / MEDIUM / LOW

### Resolution
[What was done to fix it]
[Date fixed]

### Systemic Risk Assessment
- Has this happened before? YES / NO (if YES: how many times?)
- Could this same failure happen on other assets? YES / NO

### Rule/Process Update Required
- [ ] Update creation checklist to include: [specific step]
- [ ] Update QA checklist to include: [specific check]
- [ ] Update SOP [name]: [what to change]
- [ ] Update template: [which template, what change]
- [ ] No process change needed (one-off)

**Assigned To:** [Who will make the process update]
**Due:** [Date]
```

---

## 3. FAILURE PATTERN ANALYSIS

### Monthly Failure Pattern Review
At the end of each month, review all failure log entries:

```
PATTERN ANALYSIS QUESTIONS:
1. What type of failure happened most? (Content / Technical / Brand / etc.)
2. What stage was it caught? (Before or after shipping?)
3. Which asset type has the most failures?
4. Which creator/agent appears most in failures?
5. Are the same root causes repeating?

ACTION TRIGGERS:
- Same failure type 3+ times in 30 days → Update the checklist
- Same root cause 2+ times → Update the SOP or template
- Any failure caught AFTER shipping → Tighten pre-publish gate
- Same agent in 3+ failures → Review their creation process
```

### Failure Categories Dashboard
```
Monthly Summary:
- Total QA reviews conducted: XX
- Reviews approved first pass: XX (XX%)
- Reviews requiring revision: XX (XX%)
- Reviews rejected: XX (XX%)
- Failures caught before shipping: XX (XX%)
- Failures caught after shipping: XX

Top failure categories this month:
1. [Category]: XX occurrences
2. [Category]: XX occurrences
3. [Category]: XX occurrences

Process improvements made this month:
- [Change 1]
- [Change 2]
```

---

## 4. RULE CREATION TEMPLATE

When a failure warrants a new rule:

```
## New QA Rule — [Rule ID]

**Triggered by failure:** [Failure log ID]
**Date added:** [Date]

**Rule:** [One sentence — specific and actionable]

**Checklist addition:**
Add to [which checklist], section [which section]:
- [ ] [Exact checklist item text]

**Rationale:**
[2-3 sentences explaining why this rule exists and what it prevents]

**Example of what this catches:**
❌ FAILS this check: [Specific example]
✅ PASSES this check: [Specific example]
```

---

## 5. FAILURE LOG INDEX

Maintain a running index in `memory/sentinel-failures.json`:

```json
{
  "failures": [
    {
      "id": "F-20240115-001",
      "date": "2024-01-15",
      "asset": "FamliClaw v1.0",
      "type": "Content",
      "severity": "HIGH",
      "caught_before_shipping": true,
      "root_cause": "Template placeholder not replaced",
      "rule_created": "FLC-001",
      "resolved": true
    }
  ],
  "rules_created": 3,
  "total_failures": 7,
  "caught_before_shipping": 6,
  "caught_after_shipping": 1
}
```
