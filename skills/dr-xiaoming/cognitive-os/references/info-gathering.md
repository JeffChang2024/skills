---
name: info-gathering
description: |
  Intelligence collection and synthesis engine for structured information retrieval. Activate when:
  (1) task involves facts, data, or time-sensitive information that must be verified, (2) research
  or competitive analysis is needed, (3) multiple sources must be cross-validated, (4) user asks to
  "search for", "find out about", "research", "gather info on", or "what's the latest on",
  (5) strategic-thinking routes through info sufficiency gate and determines external data is needed.
  NOT for: questions answerable from existing context/memory, casual conversation, or when user
  explicitly says to skip search. This skill is called by strategic-thinking as the information layer.
---

# Info Gathering — Intelligence Collection Engine

## Core Identity

An **intelligence analyst** with this value chain:
```
Vague need → Precise query → Parallel search → Denoise → Cross-validate → Structured delivery
```

## Query Input Protocol

Ideal structured input (callers should provide as much as possible):

| Field | Description |
|-------|-------------|
| 📌 Target | What to find |
| 🔑 Keywords | Core terms + synonyms |
| 👤 Entities | Specific names, orgs, products, brands |
| ⏱️ Time range | e.g. "last 6 months" |
| 📚 Preferred sources | e.g. "academic papers", "exclude social media" |
| 📊 Expected format | e.g. "data visualization", "overview", "detailed cases" |
| 💡 Context | Why this is being searched (helps prioritize) |
| ⭐ Priority | Order of importance if multiple queries |

**Input quality gate**: If target is unclear → request clarification before searching. If scope is unclear → proceed with reasonable defaults.

## Search Strategy Engine

### Query Decomposition

Complex queries MUST be split into focused sub-queries and parallelized:

```
1. Identify query dimensions
   Example: "Brand X market performance" →
   [Brand overview, Market share, Competitor comparison, User sentiment, Recent dynamics]

2. For each dimension: generate optimized search terms
3. Parallel execute (no dependencies → simultaneous)
4. Serial execute (has dependencies → sequential)
```

### Search Term Optimization

| Strategy | Action |
|----------|--------|
| Synonym expansion | Generate synonyms and related terms |
| Qualifiers | Add site:, filetype:, year limits |
| Noise exclusion | Identify and exclude noise terms |
| Multilingual | Search in both Chinese and English for coverage |

### Search Tool Selection

| Info Type | Primary Tool | Notes |
|-----------|-------------|-------|
| News/current events | Web search | Timeliness priority |
| Encyclopedia/concepts | Web search | Authority priority |
| Academic/research | Web search (academic mode) | Specify academic sources |
| Images | Image search | Visual reference |
| Video | Video search | Tutorials/cases |
| Geographic/location | Map API | POI/routes/distance |
| Enterprise/business | Web search | Combine official site + media reports |

## Result Processing Pipeline

```
Raw results → [Denoise] → [Fact Extract] → [Cross-validate] → [Structured Output]
```

### Stage 1: Denoise
Filter out: irrelevant results, expired content, low-credibility sources, duplicates, ads/SEO spam.

### Stage 2: Fact Extraction
From each result extract: core claim, data points, source, publish date, confidence assessment.

### Stage 3: Cross-Validation

| Supporting sources | Confidence | Annotation |
|-------------------|------------|------------|
| ≥2 independent reliable | **HIGH** | State directly |
| 1 reliable | **MEDIUM** | "According to [source]…" |
| 0 independent verification | **LOW** | "Unverified" + source |
| Sources contradict | **CONFLICT** | Present all perspectives + analysis |

## Output Template

Every info gathering output MUST follow this structure:

```markdown
## Collection Summary

### Core Findings
- [Finding 1] — Confidence: High [Source1, Source2]
- [Finding 2] — Confidence: Medium [Source3]
- [Finding 3] — Confidence: Low (no independent verification)

### Key Data
| Metric | Value | Source | Date | Confidence |

### Information Conflicts (if any)
- Source A says X, Source B says Y
- Analysis: Lean toward X because…

### Information Gaps
- Could not find reliable info on [XX]
- Suggestion: [supplementary search direction]

### Full Source List
[1] [Org] "Title", Date, URL
[2] …
```

## Source Credibility Tiers

| Priority | Type | Examples |
|----------|------|---------|
| 1 | Official | Government sites, corporate announcements, SEC filings |
| 2 | Authoritative reports | Gartner, IDC, iResearch, BNEF |
| 3 | Mainstream media | Bloomberg, Reuters, Financial Times, 财新 |
| 4 | Professional media | 36Kr, TechCrunch, The Information |
| 5 | Other | Blogs, forums, social media (must annotate) |

## Quality Control

| Category | Check |
|----------|-------|
| Completeness | All query dimensions covered? Gaps annotated? |
| Accuracy | Every fact has source? Key data cross-validated? Data current? |
| Usability | Structured per template? Redundancy removed? Caller can use directly? |
| Honesty | Confidence annotated? Conflicts fully presented? No unsourced assertions? |

## Search Strategy Patterns

| Pattern | Use When | Method |
|---------|----------|--------|
| A: Breadth-first | Unfamiliar domain | Wide keywords → build framework → targeted deep dives |
| B: Depth-first | Clear direction | Single dimension → layer by layer → trace to original source |
| C: Comparative | Competitor analysis | Parallel search objects → unified dimension extraction → structured comparison table |
| D: Timeline | Event tracking, trend analysis | Search by time periods → extract key nodes → build timeline → identify turning points |
| E: Verification | Fact-checking | Extract claim → search original source → seek counter-evidence → judge veracity |

## Error Handling

| Error | Action |
|-------|--------|
| Search tool failure | Try alternative → if none, report with caveat "based on existing knowledge, unverified in real-time" |
| No results | Widen scope → change terms (synonyms/English) → split into smaller sub-queries |
| Low quality results | Escalate: "Results insufficient for reliable conclusion. Suggest: narrow scope / specify authority sources / accept lower confidence" |
| Conflicting info | Present all perspectives transparently with analysis |
