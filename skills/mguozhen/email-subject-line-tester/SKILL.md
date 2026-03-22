---
name: email-subject-line-tester
description: "Email subject line optimization agent. Generates 10 subject line variants for any email, scores each by open rate predictors (urgency, personalization, curiosity, length, emoji use), and recommends the top 3 for A/B testing. Triggers: subject line, email subject, subject line tester, subject line generator, email open rate, ab test email, subject line optimization, email copywriting, subject line ideas, newsletter subject, email marketing subject"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/email-subject-line-tester
---

# Email Subject Line Tester

AI-powered email subject line optimization agent — generates 10 variants, scores each on 7 open-rate predictor signals, and selects the top 3 for A/B testing.

Describe your email's topic, audience, and goal. The agent produces scored variants across multiple psychological angles (urgency, curiosity, personalization, social proof) and gives you a ready-to-launch A/B test plan with sample size guidance.

## Commands

```
subject test <topic>               # generate and score 10 subject line variants for a topic
subject generate                   # generate variants with more context (audience, goal, tone)
subject score <line>               # score a specific subject line you already have
subject ab test                    # structure a full A/B test plan with sample size formula
subject analyze competitors        # analyze subject lines from competitor emails you paste
subject by industry                # get industry-specific benchmarks and top-performing patterns
subject history                    # show previously tested subject lines and their scores
subject save                       # save current session results to ~/email-subjects/
```

## What Data to Provide

The agent works with:
- **Topic description** — "promotional email for 30% off summer sale, audience is past buyers"
- **Draft subject lines** — paste your own for scoring and improvement suggestions
- **Competitor examples** — paste subject lines from competitor emails for pattern analysis
- **Audience details** — industry, demographic, relationship (subscriber, buyer, lead), engagement tier
- **Email goal** — promotional, transactional, re-engagement, newsletter, event invite

No integrations required. Works entirely from your descriptions.

## Workspace

Creates `~/email-subjects/` containing:
- `memory.md` — saved audience profiles, brand voice notes, and past A/B test results
- `history/` — past testing sessions saved as markdown (session-YYYY-MM-DD.md)
- `benchmarks.md` — industry benchmark reference updated during sessions

## Analysis Framework

### 1. The 7 Open-Rate Predictor Signals

Each subject line is scored 0-10 on each signal; total score is out of 70:

**Signal 1 — Urgency Words**
- Time-limited language: "today only", "ends tonight", "last chance", "24 hours left"
- Quantity scarcity: "only 3 left", "limited spots", "while supplies last"
- Diminishes with overuse — flag if brand history shows urgency fatigue

**Signal 2 — Personalization Tokens**
- Name token {{first_name}} adds 2-5% open rate lift on average
- Behavioral personalization: "You left something behind", "Based on your last order"
- Segment-specific language (buyer vs. subscriber vs. VIP)

**Signal 3 — Question Format**
- Open questions create curiosity loops: "What's your biggest email mistake?"
- Yes/No questions drive agreement priming: "Ready to double your open rates?"
- Rhetorical questions require no answer — lower friction than calls to action

**Signal 4 — Number Inclusion**
- Specific numbers outperform vague claims: "Save $47" beats "Save money"
- Odd numbers slightly outperform round numbers in most studies
- List-format subject lines: "5 mistakes killing your open rates"

**Signal 5 — Emoji Presence**
- Single relevant emoji adds novelty in crowded inboxes; more than 2 reduces credibility
- Emoji at start of subject performs differently than at end (test both)
- Inappropriate for B2B enterprise, legal, financial contexts — flag by industry

**Signal 6 — Character Length**
- Optimal range: 30-50 characters for desktop and mobile rendering
- Under 20 characters: too vague, loses context
- Over 60 characters: truncated on mobile (58% of opens are mobile)
- Preheader pairing: subject + preheader combined should tell the full story in 90 characters

**Signal 7 — Power Words**
- High-engagement triggers: "exclusive", "secret", "proven", "free", "new", "you"
- Spam-trigger words to avoid: "100% free", "act now", "cash bonus", "no cost", "winner"
- Run spam filter check on every generated variant

### 2. Industry Benchmark Reference

| Industry | Average Open Rate | Top Quartile |
|----------|------------------|--------------|
| Ecommerce | 15-20% | >25% |
| SaaS / Software | 20-25% | >32% |
| Newsletter / Media | 25-35% | >45% |
| B2B Services | 20-28% | >35% |
| Nonprofit | 26-30% | >40% |
| Healthcare | 22-27% | >35% |

### 3. Spam Trigger Detection
- Scan each variant against known spam trigger word list
- Flag phrases that increase spam folder placement risk
- Check for ALL CAPS usage (more than 2 consecutive caps words triggers filters)
- Check for excessive punctuation (!!!  or ???)

### 4. Mobile Preview Check
- Simulate rendering at 40 characters (iPhone lock screen) and 58 characters (Gmail mobile)
- Flag subject lines that truncate at an awkward word break
- Suggest preheader text that completes the message naturally when subject is truncated

### 5. A/B Test Setup Guidance
- Minimum sample size formula: n = (Z^2 × p × (1-p)) / E^2
  - Z = 1.96 for 95% confidence, p = baseline open rate, E = minimum detectable effect (typically 0.02)
  - Example: 25% baseline, detect 2pp lift → n = 2,401 per variant
- Test only one variable per test (subject line only, never combine with send time changes)
- Recommended test split: 20% / 20% test, 60% winner send
- Minimum test duration: 4 hours before declaring winner (allow for time-zone spread)

## Output Format

Every `subject test` run outputs:
1. **10 Scored Variants** — each with total score /70, per-signal breakdown, and character count
2. **Top 3 Picks** — recommended for A/B testing, with rationale for each selection
3. **Spam Flag Report** — any variants with trigger words highlighted
4. **Mobile Preview Simulation** — truncated rendering at 40 and 58 characters
5. **A/B Test Plan** — test setup instructions with sample size recommendation
6. **Preheader Suggestions** — paired preheader for each top-3 variant

## Rules

1. Always generate exactly 10 variants before scoring — never fewer
2. Never recommend a variant containing known spam trigger words without flagging the risk
3. Score every variant on all 7 signals — no signal may be skipped
4. Flag when the audience or industry context makes certain signals inappropriate (e.g., emoji in B2B financial services)
5. Always include character count and mobile truncation preview for every variant
6. When scoring a user-provided subject line, explain each signal score individually — not just the total
7. Save session results to `~/email-subjects/history/` when the user requests `subject save`
