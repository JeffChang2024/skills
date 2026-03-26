---
name: amazon-brand-analytics
description: "Amazon brand analytics and market opportunity mining agent. Analyze brand-level data, identify market opportunities, track brand performance trends, and make data-driven decisions for product selection, operations, and advertising. Triggers: amazon brand analytics, brand analysis, market opportunity, brand performance, amazon trends, brand registry analytics, search query performance, repeat purchase, market basket, demographics analytics, brand intelligence"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-brand-analytics
---

# Amazon Brand Analytics

Mine Amazon's brand analytics data for market opportunities, competitor intelligence, and product selection signals. Turn search query data, purchase patterns, and demographic insights into strategic decisions.

## Commands

```
brand analyze <brand>             # full brand performance analysis
brand opportunity <category>      # identify market opportunities in category
brand search-queries <data>       # analyze search query performance report
brand repeat-purchase <data>      # analyze customer loyalty metrics
brand market-basket <asin>        # find what customers buy together
brand demographics <data>         # analyze buyer demographics
brand compare <brand1> <brand2>   # head-to-head brand comparison
brand trends <category>           # identify trending brands/products
brand whitespace <market>         # find unserved market segments
brand report <brand>              # comprehensive brand intelligence report
```

## What Data to Provide

- **Brand Analytics report data** — paste exported data from Brand Analytics dashboard
- **Search Query Performance** — top queries, click share, conversion share
- **Repeat Purchase data** — repurchase rates by ASIN
- **Market Basket data** — what customers also buy
- **Competitor brand names** — for competitive brand analysis
- **Category context** — which category to analyze

## Brand Analytics Framework

### Search Query Performance Analysis

Amazon Brand Analytics shows top search terms that lead to your brand's page views.

**Key metrics:**
```
Metric              What it means               Benchmark
Search Query Volume Top searches in category     Track changes monthly
Click Share         Your clicks / total clicks   Target >5% on key terms
Conversion Share    Your conversions / total      Should exceed click share
```

**Click Share vs Conversion Share analysis:**
- Click Share > Conversion Share → listing or pricing issue (traffic not converting)
- Conversion Share > Click Share → strong listing, expand visibility
- Both low → ranking issue, invest in ads or SEO to appear more

**Opportunity identification:**
- High volume terms where your brand has 0% click share → keyword target
- Terms where competitor has >30% click share → competitive threat
- Terms with high search volume but low competition → blue ocean

### Market Opportunity Mining

Use search query data to find opportunities:

```
Step 1: Find terms with high search volume (top 1000 in category)
Step 2: Check which brands dominate each term (click share)
Step 3: Identify terms with fragmented click share (<10% for any brand)
Step 4: Cross-reference with your product ability to serve that need
Step 5: Score opportunity: Volume × (1 - Max click share) = Opportunity Score
```

**Blue Ocean Criteria:**
- Top brand has <15% click share
- Search volume rank in top 500
- Your product can serve the need
- Estimated conversion opportunity exists

### Repeat Purchase Rate Analysis

Brand loyalty signals by product type:
```
Product Type           Expected Repeat Rate    Your Target
Consumables (30-day):  30-50%                  >40%
Consumables (90-day):  20-40%                  >30%
Durable goods:         5-15%                   >10%
Seasonal items:        15-25%                  >20%
```

**Low repeat purchase rate causes:**
1. Product quality disappointment
2. Better alternative found (competitor won)
3. Category not naturally repurchasable
4. Customer service issue
5. Pricing increased after first purchase

**High repeat purchase signals:**
- Strong product-market fit
- Subscription candidate
- Invest in Subscribe & Save

### Market Basket Intelligence

What customers buy with your product reveals:
- **Bundle opportunities** — sell complementary products together
- **Competitive threats** — if customers buy your product WITH a competitor's, they may switch
- **Category adjacency** — expand product line to items customers already buy

**Bundle strategy from market basket:**
```
If your item frequently bought with Item X:
→ Create bundle of Your Item + Item X (15-20% discount vs. buying separately)
→ Use Item X keywords in your backend search terms
→ Target buyers of Item X with Sponsored Products
```

### Demographic Analysis

Amazon Brand Analytics shows buyer demographics (age, income, education, gender):

**Using demographic data:**
```
If buyers skew 45-64 female, high income:
→ Adjust imagery to show aspirational, quality-focused lifestyle
→ Price premium positioning viable
→ Focus on quality and trustworthiness in copy
→ Facebook/Pinterest ads may supplement Amazon ads

If buyers skew 25-34 male, medium income:
→ Feature-focused copy and specs
→ Value proposition important
→ Reddit and YouTube integration
```

### Competitor Brand Intelligence

For a competitor brand, estimate using Brand Analytics signals:

**Proxy metrics:**
- Search terms they dominate (high click share) = their strength
- Terms they don't appear on = their weakness / your opportunity
- Categories where they appear = their product range
- Review volume growth rate = their investment level

### Brand Performance Trending

Track monthly to identify patterns:
```
Month | Click Share (main kw) | Conversion Share | Top New Keywords
Jan   | 8.2%                  | 10.1%            | [term A, term B]
Feb   | 9.1%                  | 11.3%            | [term C]
Mar   | 7.8%                  | 9.2%             | [none]
Apr   | 6.2%                  | 7.8%             | [none]

Trend: Declining → investigate competitor gains or listing issues
```

### Whitespace Identification

Finding underserved market segments:
```
Segment example: "organic dog treats for senior dogs"
Step 1: Search volume meaningful (>1,000/month estimate)
Step 2: Existing results: generic dog treats not optimized for seniors
Step 3: Conversion data: broad terms converting but specific terms underserved
Step 4: Product feasibility: can create differentiated product
Result: WHITESPACE OPPORTUNITY
```

## Workspace

Creates `~/brand-analytics/` containing:
- `search-queries/` — monthly search query performance snapshots
- `opportunities/` — identified market opportunities
- `competitors/` — competitor brand profiles
- `demographics/` — buyer profile reports
- `reports/` — full brand intelligence reports

## Output Format

Every brand analysis outputs:
1. **Search Query Performance Summary** — top 10 opportunity terms with click/conversion gap
2. **Market Opportunity Ranking** — top 5 whitespace opportunities with scoring
3. **Competitive Threat Map** — which brands are gaining in your key terms
4. **Customer Loyalty Metrics** — repeat purchase rate vs. benchmark
5. **Bundle Opportunities** — top 3 market-basket-driven bundle ideas
6. **Demographic Profile** — buyer profile summary with marketing implications
7. **Monthly Action Plan** — 5 prioritized brand growth actions
