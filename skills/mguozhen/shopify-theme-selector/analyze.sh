#!/usr/bin/env bash
# shopify-theme-selector — Theme recommendation and evaluation for Shopify stores
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: theme: <niche, budget, and goals>"
  echo "Example: theme: recommend for pet accessories store \$200 budget high conversion"
  exit 1
fi

SESSION_ID="theme-$(date +%s)"

PROMPT="You are a Shopify store design expert with deep knowledge of themes, conversion rate optimization, and niche-specific UX patterns. Recommend and evaluate themes for: ${INPUT}

## 1. Niche Design Requirements
For this store type, critical design elements are:
- Layout type: single product / catalog / brand story / hybrid
- Visual hierarchy priority: [product / brand / trust / urgency]
- Key conversion elements needed: [list 5]
- Color psychology recommendation: [palette]
- Typography style: [recommendation]
- Mobile UX requirements: [specific to niche]

## 2. Top 5 Theme Recommendations
Score each theme /100:

**#1 Recommendation: [Theme Name]** (Score: X/100)
- Price: Free / $[price]
- Best for: [use case]
- Conversion features: [list]
- Page speed (Google rating): [fast/average/slow]
- Mobile score: [X/10]
- Customization difficulty: [easy/medium/hard]
- Why it wins for this niche: [specific reason]
- Main limitation: [one weakness]

**#2: [Theme Name]** (Score: X/100)
[Same format]

**#3: [Theme Name]** (Score: X/100)
[Same format]

**#4: [Theme Name]** (Score: X/100)
[Same format]

**#5: [Theme Name]** (Score: X/100)
[Same format]

## 3. Free vs Paid Decision Framework
**Go free if:**
- [Criteria 1]
- [Criteria 2]
- [Criteria 3]

**Invest in paid ($180-$380) if:**
- [Criteria 1]
- [Criteria 2]
- [Criteria 3]

**ROI calculation:** A paid theme that improves CVR by 0.5% on $X/month revenue pays back in X months.

## 4. Conversion Feature Checklist
Must-have features for this niche — verify before buying:
- [ ] Sticky Add-to-Cart button
- [ ] Product image zoom / 360 view
- [ ] Variant swatches (color / size)
- [ ] Bundle / frequently bought together
- [ ] Countdown timer support
- [ ] Trust badges section
- [ ] Reviews integration (Yotpo/Judge.me)
- [ ] Quick view / quick add
- [ ] Mega menu for collections
- [ ] Video support in hero / PDP
- [ ] Size guide popup
- [ ] Back-in-stock notifications
- [ ] Custom metafields display
→ Score your top pick: X/14 features native

## 5. First-Week Customization Priority
In order of conversion impact, customize:
1. [Change] → [Why it matters]
2. [Change] → [Why it matters]
3. [Change] → [Why it matters]
4. [Change] → [Why it matters]
5. [Change] → [Why it matters]
6. [Change] → [Why it matters]
7. [Change] → [Why it matters]

## 6. Recommended App Stack (to complete theme)
Apps that fill gaps in even the best themes:
| Need | App | Free/Paid | Priority |
|------|-----|-----------|----------|
| Reviews | | | |
| Upsell | | | |
| Email capture | | | |
| Size guide | | | |
| Loyalty | | | |
| Search | | | |

## 7. Page Speed Optimization
After theme install, do this before launch:
- Image compression workflow (tool + settings)
- App audit (remove unused apps — each adds 100-300ms)
- Lazy loading configuration
- Font optimization
- Third-party script management
→ Target: Core Web Vitals score >70 on mobile

## 8. Common Theme Mistakes to Avoid
Top 7 mistakes Shopify store owners make with themes — with fixes."

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
echo "  SHOPIFY THEME RECOMMENDATION"
echo "  Store: ${INPUT}"
echo "================================================"
echo ""
echo "$REPORT"
echo ""
echo "================================================"
echo "  Powered by Shopify Theme Selector"
echo "  clawhub.ai/mguozhen/shopify-theme-selector"
echo "================================================"
