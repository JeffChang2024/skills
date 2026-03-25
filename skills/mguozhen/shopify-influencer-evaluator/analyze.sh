#!/usr/bin/env bash
# shopify-influencer-evaluator — KOL/influencer strategy for Shopify brands
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: influencer: <niche or @handle or campaign goal>"
  echo "Example: influencer: yoga mat store micro influencer strategy"
  exit 1
fi

SESSION_ID="influencer-$(date +%s)"

PROMPT="You are an influencer marketing expert for Shopify DTC brands. Build a full influencer marketing strategy for: ${INPUT}

## 1. Influencer Tier Strategy
Recommend the optimal mix for this niche:
| Tier | Followers | Count | Budget % | Expected ROAS |
|------|-----------|-------|----------|---------------|
| Mega (1M+) | ... | ... | ... | ... |
| Macro (100K-1M) | ... | ... | ... | ... |
| Micro (10K-100K) | ... | ... | ... | ... |
| Nano (1K-10K) | ... | ... | ... | ... |

## 2. Influencer Scoring Matrix
Score each candidate across (1-10):
- Audience relevance to niche
- Engagement rate quality (comments vs likes ratio)
- Content authenticity score
- Past brand collaboration track record
- Audience demographics fit
- Price-to-value ratio
→ Total score /60 = hire threshold: 42+

## 3. Platform Selection
Rank platforms for this niche (Instagram / TikTok / YouTube / Pinterest / Blog):
- Primary platform: [why]
- Secondary platform: [why]
- Skip: [why]

## 4. Campaign Structure Options
**Option A — Gifting Program**
- Who to target, what to send, expected conversion
**Option B — Paid Collaboration**
- Rate benchmarks, deliverables, exclusivity terms
**Option C — Affiliate/Commission**
- Commission rate, cookie window, tracking setup

## 5. Outreach Templates
**DM Script (Instagram/TikTok):**
[150-word personalized DM template]

**Email Script:**
Subject: [subject line]
[300-word email template]

## 6. Content Brief Template
What to brief the influencer:
- Key messages (3 points)
- Mandatory mentions
- Hashtags and @tags
- Do's and Don'ts
- Deliverable specs (format, length, posting time)

## 7. ROI Projection
Assuming \$1,000 budget:
- Expected total reach
- Estimated CTR and clicks
- Conversion rate assumption
- Projected revenue and ROAS
- Break-even analysis

## 8. Tracking & Attribution Setup
- Discount code naming convention
- UTM parameter structure
- Tracking spreadsheet columns
- 30-day performance review checklist

## 9. Top 10 Platforms to Find Influencers
List the best tools/platforms to discover influencers in this niche, with pros/cons."

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
payloads = data.get('payloads', [])
texts = [p.get('text','') for p in payloads if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)

if [ -z "$REPORT" ]; then
  echo "Error: Could not generate report."
  exit 1
fi

echo ""
echo "================================================"
echo "  INFLUENCER MARKETING STRATEGY"
echo "  Target: ${INPUT}"
echo "================================================"
echo ""
echo "$REPORT"
echo ""
echo "================================================"
echo "  Powered by Shopify Influencer Evaluator"
echo "  clawhub.ai/mguozhen/shopify-influencer-evaluator"
echo "================================================"
