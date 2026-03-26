---
name: amazon-keyword-reverse-lookup
description: "Amazon keyword reverse lookup engine. Find all keywords driving traffic to any ASIN, uncover hidden long-tail opportunities, build CPC ad keyword lists, and optimize listings with data-driven keyword intelligence. Triggers: keyword reverse lookup, asin keyword, amazon keyword research, reverse asin, listing keywords, cpc keyword, ppc keyword, amazon seo keyword, keyword spy, traffic keywords, search terms, backend keywords, keyword extraction"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-keyword-reverse-lookup
---

# Amazon Keyword Reverse Lookup Engine

The keyword intelligence engine behind your Amazon Listing optimization and CPC ad targeting. Given an ASIN or product description, uncover every keyword driving traffic — from high-volume head terms to long-tail conversion gold.

## Commands

```
reverse <asin>                    # extract keyword profile for an ASIN
reverse bulk <asin1,asin2,...>    # batch keyword extraction for multiple ASINs
keyword gap <your-asin> <comp>    # find keywords competitor ranks for but you don't
keyword rank check <asin> <kw>    # estimate ranking for specific keyword
keyword cluster <list>            # group keywords by semantic theme
keyword priority                  # score and rank keywords by opportunity
cpc suggest <keyword>             # CPC bid suggestions based on competition
backend generate <product>        # generate backend search terms (249 chars)
listing inject <title> <kws>      # naturally inject keywords into listing copy
keyword save <product>            # save keyword research to workspace
```

## What Data to Provide

- **ASIN** — the product to reverse-lookup
- **Competitor ASINs** — to find keyword gaps
- **Product title/bullets** — for keyword extraction from listing
- **Category** — for benchmark search volumes
- **Seed keywords** — terms you already know (to expand from)
- **Budget context** — CPC budget range for bid suggestions

## Keyword Research Framework

### Keyword Tier Classification

**Tier 1 — Head Terms** (Primary keywords):
- Monthly searches: 10,000+
- Competition: Very High
- Use in: Title (first 60 chars), backend
- Strategy: Must rank here eventually, but may need 6-12 months

**Tier 2 — Core Keywords** (Secondary keywords):
- Monthly searches: 1,000-10,000
- Competition: Medium-High
- Use in: Title, bullet points, backend
- Strategy: Primary target for new listings — achievable with 50+ reviews

**Tier 3 — Long-tail Keywords** (Conversion keywords):
- Monthly searches: 100-1,000
- Competition: Low-Medium
- Use in: Description, backend, PPC exact match
- Strategy: Launch focus — win these first to build velocity

**Tier 4 — Niche Keywords** (Discovery keywords):
- Monthly searches: <100
- Competition: Very Low
- Use in: Backend search terms, PPC broad match
- Strategy: Passive traffic, zero cost to rank for

### Keyword Extraction from Listing Text

From a product title/bullets, extract keywords by:
1. Identify product type (noun phrase)
2. Extract all modifiers (size, color, material, use case)
3. Generate all meaningful combinations
4. Add related synonyms and alternative terms
5. Add use-case and problem-based phrases

Example for "Stainless Steel Water Bottle 32oz":
```
Primary: water bottle, stainless steel water bottle
Modifiers: 32oz, large, insulated, vacuum, leak-proof, BPA free
Use cases: hiking, gym, sports, outdoor, camping, travel
Problem-based: keeps water cold, hot coffee thermos
Synonyms: tumbler, flask, canteen, hydration bottle
Long-tail: 32oz insulated water bottle, stainless steel gym bottle leak proof
```

### Reverse Lookup Logic (Manual ASIN Analysis)

When given an ASIN, analyze by:
1. Extract all words from title, bullets, description
2. Generate keyword permutations
3. Identify brand terms vs. generic terms
4. Cross-reference with category common keywords
5. Score by estimated commercial intent

### Keyword Gap Analysis

Given your ASIN vs. competitor ASIN:
```
Your keywords:       [A, B, C, D, E]
Competitor keywords: [B, C, D, F, G, H]
Gap keywords:        [F, G, H] — competitor has these, you don't
Unique to you:       [A, E] — your advantage, protect these
```

### CPC Bid Intelligence

**Bid estimation by competition level:**
```
Very High competition (Tier 1): $1.50 - $3.00+ CPC
High competition (Tier 2):      $0.80 - $1.50 CPC
Medium competition (Tier 3):    $0.30 - $0.80 CPC
Low competition (Tier 4):       $0.10 - $0.30 CPC
```

**Bid strategy by campaign type:**
- Exact match: Bid at estimated CPC
- Phrase match: Bid at 80% of exact
- Broad match: Bid at 60% of exact
- Auto campaign: Start at $0.50, scale based on ACOS

### Backend Search Terms (249 Characters)

Rules for backend keyword field:
- No commas needed — spaces work
- No repeat words — every character counts
- Include misspellings of your product name
- Include complementary product terms
- No ASINs, brand names of competitors, or prohibited terms
- Use singular forms only (Amazon pluralizes automatically)

**Template:**
```
[synonyms] [materials] [use cases] [compatible items] [problem solved] [occasion] [demographic]
```

### Listing Keyword Injection

**Title formula:**
`[Brand] [Primary Keyword] [Key Feature] [Size/Variant] [Secondary Keyword]`

**Bullet point structure:**
- Bullet 1: Primary keyword + biggest benefit
- Bullet 2: Secondary keyword + feature proof
- Bullet 3: Long-tail keyword + use case
- Bullet 4: Trust signal (certifications, compatibility)
- Bullet 5: Guarantee / customer promise + brand keyword

## Keyword Scoring Matrix

Score each keyword on 4 factors (1-5):
1. **Search volume** — how many searches per month
2. **Relevance** — how closely it matches your product
3. **Competition** — how hard to rank (5=very easy)
4. **Intent** — how likely searcher is to buy (5=high purchase intent)

**Priority Score = (Volume + Relevance + Competition + Intent) / 4**
Focus first on keywords scoring 4.0+

## Workspace

Creates `~/keyword-research/` containing:
- `by-asin/` — keyword profiles per ASIN
- `campaigns/` — PPC keyword lists by match type
- `gaps/` — competitor gap analysis files
- `backend/` — generated backend search term strings

## Output Format

Every keyword research outputs:
1. **Master Keyword Table** — full keyword list with tier, volume estimate, competition, priority score
2. **Top 10 Priority Keywords** — highest opportunity, recommended to target first
3. **Backend Search Terms** — ready-to-paste 249-character string
4. **PPC Campaign Structure** — exact/phrase/broad keyword groups with bid suggestions
5. **Listing Optimization Notes** — which keywords are missing from current listing
