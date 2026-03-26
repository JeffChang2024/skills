---
name: amazon-backend-report
description: "Amazon Seller Central backend data report auto-analysis agent. Automatically analyze business reports, inventory reports, advertising reports, and financial reports from Amazon Seller Central to surface actionable insights. Triggers: amazon backend report, seller central report, business report, inventory report, amazon data analysis, seller central analytics, amazon performance report, sales report analysis, fba report, advertising report analysis, financial report"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-backend-report
---

# Amazon Backend Report Analyzer

Automatically analyze Amazon Seller Central reports — business performance, inventory health, advertising, and financial data — and surface the insights that matter most for your business.

Paste your exported report data. The agent processes it, identifies anomalies, highlights opportunities, and outputs a clear performance summary with prioritized action items.

## Commands

```
report business <data>            # analyze business report (traffic + conversion)
report inventory <data>           # analyze inventory health report
report advertising <data>         # analyze advertising performance report
report financial <data>           # analyze financial/payment report
report fba <data>                 # analyze FBA performance and fees
report returns <data>             # analyze returns and refunds report
report search-terms <data>        # analyze search term report from ads
report compare <period1> <period2> # compare two time periods
report digest                     # generate weekly management digest
report save <period>              # save analysis to workspace
```

## What Data to Provide

- **Report data** — paste CSV/text data from any Seller Central report
- **Time period** — which date range the report covers
- **Historical baseline** — prior period data for comparison (if available)
- **Goals** — your targets (revenue, ACOS, margin, etc.)
- **ASIN list** — specific products to focus on

## Report Analysis Framework

### Business Report Analysis

**Key metrics in Business Report:**
```
Column              What to track               Benchmark
Sessions            Unique visitors             Growing week-over-week
Page Views          Total product page views     Ratio to sessions
Buy Box %           % of time you own Buy Box   >90%
Units Ordered       Units sold per period       Week-over-week trend
Unit Session %      Conversion rate             >10% (varies by category)
Ordered Product Sales Revenue by ASIN           Growing trend
```

**Conversion rate diagnostic:**
```
CVR < 5%:    Listing issue — images, bullets, or price problem
CVR 5-10%:   Below average — improve weakest listing element
CVR 10-15%:  Good — optimize further for incremental gains
CVR > 15%:   Excellent — scale traffic with ads
```

**Sessions dropping:**
- External algorithm change
- Out-of-stock event caused ranking loss
- Competitor improved listing quality
- Seasonal demand shift
- Ad spend reduced

**Sessions growing, revenue not growing:**
- Price decreased (more traffic, same revenue)
- Conversion rate dropped (traffic quality changed)
- Returns increased (inflating gross revenue, but refunds eating margin)

### Inventory Health Report Analysis

**Key inventory metrics:**
```
Metric                  Target              Action if violated
Days of Supply          30-60 days          Reorder if <30 days
Inventory Age (0-90d)   >90% of stock       Monitor aging inventory
Inventory Age (91-180d) <10% of stock       Run promotions to clear
Inventory Age (180d+)   <2% of stock        Deep discount or removal
Stranded Inventory      0 units             Fix listing issues immediately
Unfulfillable Units     0 units             Remove or dispose
Excess Inventory        <30 days excess     Reduce reorder quantity
```

**Long-term storage fee risk:**
- Units stored >181 days incur additional fees ($1.50/cubic foot/month)
- Units stored >365 days: $6.90/cubic foot/month
- Action: identify aging SKUs and run promotions before 181-day mark

**Inventory planning dashboard:**
```
ASIN | Units | Daily Sales | Days Cover | Reorder Point | Order Now?
BXXX |  450  |    15/day   |   30 days  |  150 units    |  ⚠ Yes
BYYY |  800  |    10/day   |   80 days  |  100 units    |  ✓ No
BZZZ |   50  |     5/day   |   10 days  |   75 units    |  🚨 Urgent
```

### Advertising Report Analysis

**Search Term Report (most important ad report):**
```
Analysis steps:
1. Sort by Spend descending — find where budget is going
2. Find terms with high spend, zero conversions → Negative match
3. Find terms with conversions, good ACOS → Add to Exact campaign
4. Find terms with high impressions, 0 clicks → Review bid or relevance
5. Compute true ACOS per term: Ad Spend / Ad Sales × 100
```

**ACOS benchmarks by action:**
```
ACOS < 15%: Raise bids — underinvesting in profitable keywords
ACOS 15-25%: Maintain — at break-even or profitable range
ACOS 25-35%: Review — marginal, may be justified for ranking
ACOS > 35%: Reduce bids or pause — unprofitable
```

**Campaign performance buckets:**
```
Bucket                  ACOS    Impressions  Conversions
Stars:                  <20%    High         High        → Scale budget
Cash Cows:              <20%    Low          Moderate    → Increase bids
Potential:              20-35%  High         Low         → Improve listing
Underperformers:        >35%    Any          Low         → Reduce or pause
```

### Financial Report Analysis

**Key financial metrics:**
```
Metric                  Formula                           Target
Gross Revenue           Sum of product sales              —
Amazon Fees             Referral + FBA + storage + ads    <40% of revenue
Returns/Refunds         Refund amount / gross revenue     <5%
Net Revenue             Gross - Returns - Fees            —
Net Margin              Net Revenue / Gross Revenue       >20%
```

**Fee percentage benchmarks by category:**
```
Category        Referral    FBA        Total Fees  Net Margin Target
Electronics     8%          $5-8       18-22%      >25%
Home & Kitchen  15%         $4-6       22-26%      >20%
Clothing        17%         $3-5       22-26%      >20%
Beauty          15%         $3-5       21-25%      >22%
```

**Cash flow planning:**
```
Disbursement cycle: Every 14 days (typically)
Reserved amount: Amazon holds ~7 days of sales as reserve
Working capital needed: 45-60 days of COGS (production + freight + reserve)
```

### Weekly Management Digest Format

```
WEEK OF [DATE] — PERFORMANCE DIGEST

📊 REVENUE
  This week: $XX,XXX | Last week: $XX,XXX | Change: +/-X%
  YTD: $XXX,XXX | YTD goal: $XXX,XXX | On track: Yes/No

📦 INVENTORY
  Total units: X,XXX | Days of supply: XX days
  ⚠ Low stock: [ASIN list]
  🚨 Urgent reorder: [ASIN list]

📢 ADVERTISING
  Ad spend: $X,XXX | ACOS: XX% | ROAS: X.Xx
  Best performer: [term] at X% ACOS
  Worst performer: [term] at X% ACOS — ACTION NEEDED

⚠ ALERTS
  [List of any anomalies detected]

✅ TOP 3 ACTIONS THIS WEEK
  1. [Highest priority action]
  2. [Second priority]
  3. [Third priority]
```

## Workspace

Creates `~/backend-reports/` containing:
- `business/` — business report analyses by period
- `inventory/` — inventory health tracking
- `advertising/` — ad performance archives
- `financial/` — financial summaries
- `digests/` — weekly management digests

## Output Format

Every report analysis outputs:
1. **Performance Summary** — key metrics vs. prior period with trend indicators
2. **Anomaly Detection** — unusual patterns that require attention
3. **Inventory Status** — stock health with specific reorder actions
4. **Ad Performance** — ACOS summary with specific optimization actions
5. **Financial Health** — margin and fee analysis
6. **Priority Action List** — top 5 actions ranked by expected business impact
7. **Next Week Forecast** — projected performance based on current trends
