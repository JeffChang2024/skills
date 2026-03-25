---
name: amazon-competitor-spy
description: "Amazon competitor intelligence agent. Tracks competitor ASINs over time — price changes, BSR movements, review count velocity, listing changes, new images/variations. Outputs trend tables and competitive alerts. Triggers: competitor spy, amazon competitor, track competitor, asin tracker, competitor analysis, bsr tracking, price tracking, amazon spy, competitor monitoring, listing changes, review velocity, competitive intelligence"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-competitor-spy
---

# Amazon Competitor Spy

Track competitor ASINs over time and surface competitive intelligence — price shifts, BSR trends, review velocity, and listing changes.

Paste an ASIN or describe a competitor product. The agent tracks changes, computes trends, and alerts you when competitors make significant moves.

## Commands

```
spy add <asin>                     # add an ASIN to your watchlist
spy check                          # run check on all tracked ASINs
spy compare                        # side-by-side competitor comparison matrix
spy price history                  # show price change timeline for tracked ASINs
spy bsr trend                      # 30-day BSR movement analysis
spy review velocity                # reviews/week rate for each tracked ASIN
spy listing diff                   # detect title/bullet/image changes vs. last snapshot
spy report                         # full competitive intelligence report
spy save                           # save current watchlist and snapshots to workspace
```

## What Data to Provide

The agent works with:
- **ASIN list** — paste ASINs directly, one per line or comma-separated
- **Verbal description** — "my competitor is B08XYZ123, they just dropped price to $24.99"
- **Listing data** — paste competitor title, bullets, price, BSR rank from Amazon
- **Historical notes** — "last month their BSR was 3,200, now it's 980"

No API keys needed. No scraping tools required.

## Workspace

Creates `~/amazon-spy/` containing:
- `watchlist.md` — tracked ASINs with metadata and notes
- `snapshots/` — listing snapshots per ASIN (ASIN-YYYY-MM-DD.md)
- `reports/` — generated competitive intelligence reports
- `alerts.md` — triggered alerts log

## Analysis Framework

### 1. ASIN Tracking Setup
- Store ASIN, product title, brand, category, initial price, initial BSR, initial review count
- Record date added and last-checked timestamp
- Tag each ASIN with a competitive tier (direct / indirect / aspirational)
- Link your own ASIN to each competitor for direct comparison

### 2. Price Monitoring (Keepa-Style Logic)
- Track price changes over time with date-stamped entries
- Compute price volatility: (max price − min price) / avg price
- Flag: sustained price drops >10% — potential margin squeeze or launch push
- Flag: price increases >15% — possible supply issues or repositioning
- Identify coupon/promo patterns if mentioned (e.g., "20% off coupon visible")
- Compare competitor price vs. your price: gap analysis (you're $X cheaper/more expensive)

### 3. BSR Trend Analysis (30-Day Window)
- Log BSR data points at each check with timestamps
- Compute BSR velocity: (BSR start − BSR end) / days = ranks gained per day
- Positive velocity = ranking improving (lower BSR number)
- Flag: BSR improvement >500 ranks/week — aggressive launch or promotion detected
- Flag: BSR deterioration >1,000 ranks/week — possible listing suppression or inventory out
- Output sparkline-style trend table with direction indicators (↑↓→)

### 4. Review Velocity Analysis
- Track total review count at each snapshot date
- Compute weekly velocity: (reviews now − reviews at start) / weeks elapsed
- Industry benchmark: healthy launch pace = 10–30 reviews/week
- Flag: velocity >50 reviews/week — possible incentivized review campaign (watch for TOS risk)
- Flag: sudden review drop — potential review removals (negative signal)
- Compute projected total reviews in 30/60/90 days at current velocity

### 5. Listing Change Detection
- Snapshot: title, bullet points (all 5), A+ content presence, image count, video presence
- On `spy listing diff`, compare current snapshot vs. previous snapshot
- Highlight: title keyword changes (competitive repositioning signal)
- Highlight: bullet restructuring (conversion optimization attempt)
- Highlight: new images or video added (brand investment signal)
- Highlight: variation count changes (new sizes/colors = market expansion)

### 6. Competitive Positioning Matrix
- Build a comparison table: Your ASIN vs. each competitor
- Columns: Price | BSR | Reviews | Rating | Images | A+ | Video | Prime
- Score each competitor 1–5 on listing quality
- Identify your advantages and gaps
- Output recommended actions based on gaps found

## Output Format

Every report outputs:
1. **Competitive Snapshot** — current standings table for all tracked ASINs
2. **Movement Alerts** — any significant changes since last check
3. **Trend Charts** — BSR and price trends (text-based sparklines)
4. **Opportunity Flags** — competitor weaknesses you can exploit
5. **Recommended Actions** — prioritized list of competitive responses

## Rules

1. Always ask for the user's own ASIN when adding competitors — context requires knowing your position in the market
2. Never draw conclusions from a single data point — require at least 2 snapshots before declaring a trend
3. Flag data gaps explicitly — if a metric is missing, say so rather than estimating silently
4. Distinguish between correlation and causation — a BSR improvement could be organic or promotional
5. Never recommend matching a competitor's price cut without first checking your own margin floor
6. Save all snapshots to `~/amazon-spy/snapshots/` when `spy save` is called — tracking is only useful if historical data is preserved
7. Alert on anomalies proactively — if velocity data suggests a launch push or suppression event, surface it immediately
