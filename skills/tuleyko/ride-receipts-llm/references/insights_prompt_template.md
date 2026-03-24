# Insights prompt template (ride-receipts-llm)

Use this when the user asks for ride-history insights, trends, anomalies, summaries, or exploratory analysis from `data/rides.sqlite`.

## Interaction model

Insights are delivered in two phases: a high-level overview first, then user-directed deep dives. Do not dump everything at once.

## Phase 1 — High-level overview

Run a small set of aggregate queries and present a structured summary with these sections in order:

### Dataset
- Total rides, date range covered
- Rides per provider (count + %)
- Currencies seen with ride counts per currency

### Spending
- Total spend per currency (do not mix currencies)
- Average fare per provider per currency
- Most expensive single ride

### Geography
- Top 5 pickup locations
- Top 5 dropoff locations
- Most repeated route (pickup → dropoff)

### Time
- Busiest month
- Busiest day of week (if timestamps are parseable)

### Data quality
- Count of rides missing amount, pickup, or dropoff
- Any other notable gaps (only mention if material)

### What to explore next

End phase 1 by offering the user a numbered list of deep-dive options. Always include at least:

1. Monthly spending trends (by provider or currency)
2. Commute patterns and repeated routes
3. Time-of-day / day-of-week analysis
4. Provider comparison (fares, distances, durations)
5. Outliers and anomalies
6. City or country breakdown

Say: "Pick a number or ask me anything else about your rides."

## Phase 2 — Deep dives

When the user picks an option or asks a follow-up:

- Query only what is needed for that topic.
- Present results concisely — short tables are fine, raw SQL is not.
- After each deep dive, offer to explore another angle or ask if they're done.

## Rules

- Always query `data/rides.sqlite` first. Never guess.
- Keep currencies separate unless the user explicitly asks for FX conversion.
- Do not show SQL to the user.
- Keep output scannable: use short bullet points and small tables, not paragraphs.
- If location strings vary for what is likely the same place, group them and note the ambiguity.
- Flag data quality issues only when they materially affect a conclusion.
