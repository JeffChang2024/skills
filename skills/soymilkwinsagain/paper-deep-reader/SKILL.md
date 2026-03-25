---
name: paper-deep-reader
slug: paper-deep-reader
version: 2.0.0
description: Very helpful in deep-reading one selected research paper, journal article, arXiv paper, working paper, or technical report and produce a rigorous markdown reading note, technical summary, critique, or implementation memo. Always use when the task requires reconstructing equations, notation, derivations, theorems, estimators, algorithms, empirical identification, experiments, figures, tables, appendix evidence, assumptions, limitations, or literature context across fields such as machine learning, statistics, physics, economics, quantitative finance, systems, and related technical disciplines. Not for shallow abstract rewrites, casual summaries, or broad multi-paper surveys.
metadata:
  openclaw:
    emoji: "🔎"
---

# Paper Deep Reader

Use this skill to read **one selected paper deeply** and turn it into a **durable, evidence-based note**.

This skill is for **serious paper reading**, not for rewriting the abstract in cleaner prose.

## First load

Before drafting, read these core references:

- `{baseDir}/references/reading-workflow.md`
- `{baseDir}/references/note-template-base.md`
- `{baseDir}/references/output-contract.md`
- `{baseDir}/references/checklists/general.md`

Then load the **closest adapter** and its **matching checklist**.

### Adapters

- `{baseDir}/references/adapters/theory-math-stats.md`
- `{baseDir}/references/adapters/ml-method.md`
- `{baseDir}/references/adapters/empirical-econ.md`
- `{baseDir}/references/adapters/systems.md`
- `{baseDir}/references/adapters/physics.md`
- `{baseDir}/references/adapters/quant-finance.md`

### Domain / type checklists

- `{baseDir}/references/checklists/theory-math-stats.md`
- `{baseDir}/references/checklists/ml.md`
- `{baseDir}/references/checklists/empirical.md`
- `{baseDir}/references/checklists/systems.md`
- `{baseDir}/references/checklists/physics.md`
- `{baseDir}/references/checklists/quant.md`

Load more than one adapter or checklist when the paper is genuinely mixed.

## Primary objective

Produce a note that lets a strong graduate student answer all of the following without reopening the paper:

1. What problem does the paper study?
2. Why does that problem matter?
3. What is the paper's main move?
4. How does the technical mechanism work step by step?
5. What assumptions, approximations, or identification logic are doing the real work?
6. What evidence actually supports the main claims?
7. What is genuinely strong, weak, narrow, or reusable about the paper?

## Non-goals

Do **not** use this skill for:

- shallow abstract rewrites
- vague praise or hype language
- multi-paper literature reviews unless the user explicitly requests a survey
- papers you have not actually read beyond title and abstract

## Operating principle

Treat paper reading as **reconstruction plus judgment**.

Your job is not only to say what the authors claim. Your job is to reconstruct the paper's intellectual structure, trace claims to evidence, and record where a careful reader should trust, doubt, reuse, or extend the work.

## Required execution protocol

Follow this sequence.

### 1. Build a paper map before prose

Before writing the note, identify:

- research question
- problem setting
- paper type
- field or domain
- key technical objects
- main claim(s)
- where the paper's intellectual load actually lives

Write a short internal map in this form:

> The paper studies __ in the setting __. Its main move is __. It claims gains in __, supported by __. The key technical objects are __. The paper type is __ and the domain is __.

If you cannot write this map, keep reading before drafting.

### 2. Route the paper before analyzing it

Classify the paper along **two axes**.

#### Paper type

Choose one primary type and optional secondary type:

- theory
- methods / ML / statistics
- empirical / economics / social science
- systems
- survey / synthesis
- mixed

#### Domain

Choose the closest domain emphasis:

- machine learning / AI
- statistics / probability
- economics / econometrics
- quantitative finance
- physics
- computer systems
- general scientific / interdisciplinary

Then load the matching adapter and checklist. Let the routing decision change what you emphasize in the note.

### 3. Read in passes

Do not read linearly from top to bottom unless the paper is unusually simple.

#### Pass A: framing

Read title, abstract, introduction, conclusion, and figure/table captions.
Goal: identify what the authors want the reader to believe.

#### Pass B: technical core

Read the model, method, theory, derivation, or design sections carefully.
Reconstruct the main equations, estimators, algorithms, proof ideas, or identification logic.

#### Pass C: evidence

Read experiments, empirics, case studies, benchmarks, robustness checks, and appendix evidence that bears on the main claims.

#### Pass D: limits and context

Read limitations, related work selectively, and appendix sections needed to judge the claims fairly.

Do **not** stop at the main body if a central claim is only supported in the appendix or supplement.

### 4. Use the scripts to reduce drift

If the scripts in `{baseDir}/scripts/` are available, use them as a structured drafting aid.

Recommended order:

1. `scaffold_note.py`
2. `build_paper_map.py`
3. `build_notation_table.py`
4. `build_claim_matrix.py`
5. `build_limitation_ledger.py`
6. `render_final_note.py`

Use the scripts to create first drafts of the note scaffold and internal artifacts. Then review and correct them against the paper. The scripts are helpers, not authorities.

### 5. Prefer scripted artifacts when the note will be saved

When the user wants a saved markdown note, prefer this flow:

- scaffold the note from `{baseDir}/references/note-template-base.md`
- draft the paper map
- draft the notation table when notation is nontrivial
- draft the claim-evidence matrix for the main claims
- draft the limitation ledger
- render the final note and then revise it manually for accuracy and pedagogy

If the note is short and purely conversational, you may skip the scripts, but you must still follow the same intellectual protocol.

## Mandatory internal outputs

Before finalizing the note, build these internal structures. They can remain implicit unless the user asks for them, but the final note must reflect them.

### A. Paper map

A compact statement of problem, setting, contribution, and evidence.

### B. Notation table

When notation is nontrivial, record:

- symbol
- meaning
- type / shape / domain
- units if relevant
- where it first matters

### C. Claim-evidence matrix

For each major claim, record:

- the claim itself
- whether it is the authors' stated claim or your inference
- what evidence supports it
- where that evidence appears
- how strong the support is
- any caveat or missing check

### D. Limitation ledger

Separate:

- limitations explicitly acknowledged by the paper
- limitations you infer as a careful reader

## Core rules

1. **Read before judging.** Never infer the entire contribution from title and abstract alone.
2. **Separate authors' claims from your evaluation.** Mark the distinction clearly.
3. **Preserve the mathematical spine.** Keep the note anchored in equations, estimators, theorem statements, algorithms, identification logic, or system tradeoffs when relevant.
4. **Trace claims to evidence.** Strong statements require concrete support from sections, figures, tables, appendices, proofs, or benchmarks.
5. **Explain mechanisms, not just outcomes.** Answer why the method or argument should work and when it should fail.
6. **Prefer exactness over praise.** Replace words like “powerful,” “novel,” or “impressive” with concrete statements.
7. **Do not hide uncertainty.** If the paper is unclear, underspecified, overstated, or weakly evidenced, say so directly.
8. **Use scripts as drafts, not verdicts.** Heuristic extraction must always be checked against the paper.

## Adapter rule

Always keep the common structure from the base template, then expand or tighten sections using the routed adapter.

- Use one adapter for a clean single-domain paper.
- Use two adapters when the paper is genuinely mixed, such as theory + empirical or ML method + systems.
- Do not bolt on irrelevant sections just to satisfy a template. Only insert domain-specific material when it improves faithfulness.

## Writing contract for the final note

Follow the output contract in `{baseDir}/references/output-contract.md`. Use the base note template as the default scaffold, then adapt it to the routed paper type and domain.

## Evidence rule

For every important conclusion in the note, ask:

1. What exact claim is being made?
2. What exact evidence supports it?
3. Against what baseline, null, counterfactual, or prior result?
4. Under what setting, sample, regime, or benchmark?
5. What important check is still missing?

Do not write “the paper shows” unless you can answer those questions.

## Appendix rule

Use appendices and supplements actively when they carry critical load.

You must read appendix material when any of the following is true:

- the main theorem relies on omitted proof ideas that matter for interpretation
- the main empirical or experimental claim is only fully documented there
- important ablations, robustness checks, or implementation details are moved out of the main body
- the paper's caveats or failure cases are discussed only there

## Style rules

- Write in markdown using headings and short paragraphs.
- Use bullets sparingly and only when they clarify structure.
- Use displayed math for important equations.
- Use code blocks for pseudocode, estimators, algorithm sketches, or implementation caveats.
- Prefer durable notes over compressed notes.
- Keep the prose pedagogical, precise, and non-hyped.

## Saving behavior

When the user asks for a saved note, create a markdown file.

Default behavior:

- save to the user-specified directory if one is given
- otherwise save next to the paper as `detailed-note.md`

## Final self-check

Do not finalize until the note passes:

- the general checklist at `{baseDir}/references/checklists/general.md`
- the routed domain / type checklist(s)

## Quick references

- Workflow: `{baseDir}/references/reading-workflow.md`
- Output contract: `{baseDir}/references/output-contract.md`
- Note template: `{baseDir}/references/note-template-base.md`
- Script usage: `{baseDir}/scripts/README.md`
- Adapters: `{baseDir}/references/adapters/`
- Checklists: `{baseDir}/references/checklists/`
