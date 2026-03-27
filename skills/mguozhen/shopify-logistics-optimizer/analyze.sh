#!/usr/bin/env bash
# shopify-logistics-optimizer — Shipping and logistics optimization for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: logistics optimization: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-logistics-$(date +%s)"

PROMPT="You are a Shopify logistics and shipping optimization expert specializing in carrier management, fulfillment cost reduction, and delivery experience design for ecommerce stores. Build a complete logistics optimization strategy for: ${INPUT}

Produce a complete logistics optimization report with these sections:

## 1. Shipping Cost Audit Framework
- Shipping cost as % of revenue: current vs benchmark for this product category
- Cost breakdown by carrier, service level, and zone
- Dimensional weight analysis: how DIM weight affects your bills
- Surcharge audit: fuel, residential, address correction, peak season charges

## 2. Carrier Selection & Rate Optimization
- USPS vs UPS vs FedEx vs DHL: strengths and weaknesses by package type and zone
- Shopify Shipping discounts: pre-negotiated rates available in Shopify
- Volume discount thresholds: when to negotiate directly vs use a broker
- Regional carriers: OnTrac, LSO, Spee-Dee for zone 2-4 advantages

## 3. Dimensional Weight & Packaging Optimization
- DIM weight formula and how to calculate it
- Right-sizing packaging: 5 steps to audit and optimize box selection
- Poly mailer upgrade: when to switch from boxes for specific product types
- Packaging weight reduction: material substitutions for lighter fulfillment

## 4. Distributed Fulfillment & Zone Skipping
- Customer zip code analysis: where are 80% of your customers located?
- 2-warehouse strategy: East and West coast for next-day to 90% of US
- Zone skipping explanation: pre-sorting bulk shipments closer to customers
- 3PL selection for distributed fulfillment: ShipBob, Deliverr, ShipHero

## 5. Free Shipping Strategy
- Free shipping threshold calculation: where to set the minimum for AOV lift
- Free shipping cost absorption: when it makes sense and when it hurts
- Free shipping promotion A/B test methodology
- Conditional free shipping: member/loyalty exclusive vs public offer

## 6. International Shipping Setup
- DDP (Delivered Duty Paid) vs DDU: customer experience trade-off
- International carrier comparison by destination market
- Customs documentation automation in Shopify
- International return strategy and cost management

## 7. Customer Delivery Experience Optimization
- Immediate actions (week 1): shipping cost audit, carrier rate comparison, packaging review
- Short-term (month 1): implement cheapest carrier for each package type, free shipping threshold test
- Long-term (month 3+): 3PL evaluation, distributed inventory, 20%+ shipping cost reduction

Include specific savings benchmarks: average shipping cost reduction from right-sizing (15-25%), zone skipping savings (20-35%), and negotiated rate improvements for merchants shipping 500+ packages/month."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
