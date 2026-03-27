#!/usr/bin/env bash
# shopify-google-ads — Google Ads & Shopping campaigns strategy for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: google ads strategy: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-google-ads-$(date +%s)"

PROMPT="You are a Shopify Google Ads expert specializing in Search, Shopping, and Performance Max campaigns for ecommerce. Analyze and build a complete Google Ads strategy for: ${INPUT}

Produce a complete Google Ads strategy report with these sections:

## 1. Campaign Architecture
- Recommended campaign types (Search, Shopping, PMax, Display)
- Budget allocation percentages across campaigns
- Campaign naming convention and structure
- Geographic and language targeting recommendations

## 2. Keyword Strategy
- Top 20 high-intent keywords with estimated CPC and volume
- Match type recommendations (broad, phrase, exact) by funnel stage
- Negative keyword list (30+ terms to exclude)
- Competitor keyword opportunities

## 3. Google Shopping Feed Optimization
- Product title formula for maximum visibility
- Required and recommended attributes checklist
- Image requirements and best practices
- Feed update frequency and error prevention

## 4. Bidding & Budget Strategy
- Starting bid strategy (manual CPC vs tCPA vs tROAS)
- Recommended daily budgets by campaign
- Bid adjustments for device, location, time of day
- When to switch to Smart Bidding and conversion thresholds needed

## 5. Audience Targeting & Remarketing
- Remarketing list setup (site visitors, cart abandoners, purchasers)
- Customer match strategy using email lists
- In-market and affinity audience overlays
- Similar audience expansion tactics

## 6. Ad Copy & Extensions
- 15 RSA headline options with keyword insertion tips
- 4 description line templates
- Must-have extensions: sitelinks, callouts, structured snippets, price
- A/B testing framework for ad copy

## 7. 90-Day Launch & Optimization Plan
- Immediate actions (week 1): account setup, feed submission, campaign launch
- Short-term (month 1): data collection, bid adjustments, search term mining
- Long-term (month 3+): ROAS scaling, PMax asset testing, competitor conquesting

Include specific ROAS benchmarks by niche, average CPC ranges, and conversion rate expectations. Be specific with numbers and actionable steps tailored to Shopify stores."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
