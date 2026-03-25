---
id: <% tp.date.now('YYYYMMDDHHmmss') %>
created: <% tp.date.now('YYYY-MM-DD') %>
updated: <% tp.date.now('YYYY-MM-DD') %>
source: 
title: 
authors: 
year: 
venue: 
status: 
doi: 
url: 
fields: []
tags:
  - reading-note
---

# {{title}}

## Citation
- **Authors:** 
- **Venue / status:** 
- **Year:** 
- **Source / link:** 
- **Keywords:** 

## One-paragraph summary
A compact statement of the problem, the central move, the main result, and why the paper matters.

## Paper map
- **Research question:** 
- **Problem setting / regime:** 
- **Paper type:** theory / method / empirical / systems / survey / mixed
- **Main contribution(s):** 
- **Key technical objects:** 
- **Where the intellectual load sits:** 

## Why this paper matters
Explain the gap it addresses, why nearby approaches were insufficient, and what changed here.

## Problem setup
- **Task / scientific question:** 
- **Inputs / outputs:** 
- **State variables / latent variables:** 
- **Assumptions / constraints:** 
- **Data / environment / regime:** 
- **Target quantity / estimand / objective:** 

## Main idea
State the core idea twice:

1. **Plain-language version:**
2. **Technical version:**

## Technical core

### Notation table
| Symbol | Meaning | Type / shape / domain | Units / scale | First appears where |
|---|---|---|---|---|
|  |  |  |  |  |

### Core equations / estimators / laws
Write the smallest set of formulas needed to preserve the paper's mathematical spine.

$$
\text{Insert key equation(s) here}
$$

Explain each term, the role it plays, and what would break if it were changed or removed.

### Step-by-step mechanism
Reconstruct the method, derivation, argument, or workflow in order.

1. 
2. 
3. 

### Theoretical claims / proof ideas
Record theorem statements, assumptions, proof strategy, convergence logic, identification logic, or limiting argument when relevant.

### Complexity / efficiency / scaling / identification
Note computational complexity, sample complexity, scalability, resource tradeoffs, or identification requirements.

## Evidence

### Claim–evidence matrix
| Claim | Stated by authors or my inference? | Evidence source (section / figure / table / theorem) | Strength | Caveat |
|---|---|---|---|---|
|  |  |  |  |  |

### Experimental / empirical / observational design
Describe datasets, benchmarks, samples, regimes, environments, hardware, or institutional setting.

### Main results
Summarize the most important figures, tables, empirical estimates, or quantitative outcomes.

### Ablations / robustness / stress tests
Explain what these checks actually show and what they fail to show.

### Baselines and fairness
Were the comparisons strong and fair? Were there hidden compute, data, or tuning advantages?

## Limitations and failure modes
Be specific. Include hidden assumptions, weak evidence, narrow regime validity, approximation error, instability, or external-validity concerns.

## Relationship to other work
Name the closest families of work and explain the connection: extends, relaxes, contradicts, simplifies, or reinterprets.

## Open questions
What should be tested, generalized, relaxed, formalized, or implemented next?

## Implementation / reproduction notes
Use this section when reproduction details matter.

```python
# pseudocode, training loop sketch, estimator outline,
# simulation procedure, replication steps, or caveats
```

## What I learned from this paper
List the most reusable ideas, distinctions, proof tricks, design patterns, or empirical lessons.

## Verdict
A concise evaluation of what is genuinely strong, what is weak, and whether this paper should influence future work.
