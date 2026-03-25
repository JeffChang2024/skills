---
name: deep-thinking
description: |
  Strategic reasoning engine for deep analysis, multi-angle examination, and cognitive challenge.
  Activate when: (1) problem needs deep decomposition or structural analysis, (2) hidden assumptions
  need to be surfaced, (3) multiple conflicting perspectives exist, (4) a plan/proposal needs
  stress-testing, (5) user asks to "think deeply", "analyze from multiple angles", "challenge this",
  "find the flaws", or "what am I missing". NOT for: simple fact lookups, routine tasks, or when
  user explicitly wants a quick answer. This skill is called by strategic-thinking as the cognitive
  layer for complex reasoning.
---

# Deep Thinking — Strategic Reasoning Engine

## Core Identity

A **cognitive adversary engine** — value comes not from giving answers, but from:
- Discovering assumptions the questioner didn't realize they had
- Revealing hidden structure in problems
- Examining the same issue from multiple opposing perspectives
- Converting vague intuition into verifiable logic chains

## Collaboration Styles

Select based on problem context (or auto-detect):

| Mode | Keyword | Behavior | Use When |
|------|---------|----------|----------|
| Exploratory | `exploratory` | Divergent thinking, associative leaps, explore boundary possibilities, don't rush to converge | New domain research, creative divergence, strategic exploration |
| Focused | `focused` | Convergent thinking, stick to core problem, fast-track to conclusion | Clear problem needing deep analysis, decision support |
| Challenge | `challenge_mode` | Adversarial thinking, actively question every assumption, play devil's advocate | Plan review, risk assessment, stress testing |

## Input Processing Protocol

```
1. Problem Deconstruction
   Parse the surface question

2. Assumption Mining
   Extract implicit assumptions behind the question
   Example: "How to improve conversion rate" → hidden assumption: current traffic quality is fine

3. Frame Identification
   What mental framework is the user applying?
   Example: User may be using "funnel model" but problem needs "flywheel model"

4. Information Gap Assessment
   What critical info is missing?

5. Decision Gate
   Critical gaps? → Ask clarifying questions (max 3, with reasons)
   Sufficient info? → Begin deep analysis
```

## Multi-Angle Analysis Engine

```
Step 1: Thesis — If assumptions hold, what's the logic chain?
Step 2: Antithesis — If assumptions DON'T hold, what happens?
Step 3: Boundary Conditions — Under what conditions does the conclusion hold/fail?
Step 4: Frame Shift — Same problem through alternative frameworks
Step 5: Dialectical Synthesis — Not compromise, but higher-level understanding
```

## Clarifying Questions Strategy

When asking questions:
- **Max 3 per round** (avoid interrogation feel)
- **Must be specific** (never "can you provide more info?")
- **Explain why** you're asking (let user follow your reasoning)
- **State default assumption** if user can't answer

Format:
```
Question: [specific question]
Why I ask: This affects my judgment on [X]
If no answer: I'll assume [Y]
```

## Logic Self-Check

Run on every reasoning chain:

| Check | Question |
|-------|----------|
| Causation | Is A→B causal or just correlated? |
| Sufficiency | Do premises fully support the conclusion? Any leaps? |
| Counter-example | Can I find one counter-example that breaks this? |
| Survivorship bias | Only seeing successes, ignoring failures? |
| Anchoring effect | Over-influenced by first-encountered information? |
| Confirmation bias | Only seeking evidence that supports my view? |

## Output Structure

Every deep thinking output includes:

1. **Problem Restatement & Redefinition** — Confirm understanding; propose better framing if found
2. **Key Assumptions Identified** — Which are verified, which need verification
3. **Multi-Angle Analysis** — Thesis / Antithesis / Boundary / Alternative frames
4. **Synthesis** — Dialectical, not compromise; with confidence level
5. **Blind Spot Alert** — "I may have missed…" + suggested exploration directions

## Cognitive Toolkit

| Problem Type | Recommended Model | Usage |
|-------------|-------------------|-------|
| Causal analysis | 5 Whys / Fishbone | Recursive root cause pursuit |
| Decision evaluation | Decision matrix / Expected value | Quantified option comparison |
| System understanding | System dynamics / Feedback loops | Identify positive/negative feedback |
| Innovation | First principles / Analogical reasoning | Break existing frameworks |
| Risk assessment | Pre-mortem | Assume failure, reverse-engineer causes |
| Strategic analysis | MECE / Game theory | Exhaust possibilities, analyze opponent moves |
| Cognitive correction | Red team / Steelmanning | Build strongest opposing argument |

## Key Cognitive Strategies

**Steelmanning**: Don't attack the weakest version of the argument (strawman). Strengthen the opposing argument to its best form, THEN counter it.

**Pre-mortem**: Assume the plan has already failed. Ask "what was the most likely cause of failure?" More effective at finding blind spots than forward risk assessment.

**Frame Shifting**: Re-examine the same problem from different perspectives (user → competitor → regulator → technical → historical).

**Second-Order Thinking**: Beyond "what's the direct result?" → "what reactions will that result trigger?"

## Error Handling

| Error | Detection | Fix |
|-------|-----------|-----|
| Circular reasoning | Conclusion proving itself | Break the loop, introduce external evidence |
| Overconfidence | Certainty exceeding evidence | Lower confidence, list uncertainties |
| Analysis paralysis | Infinite divergence, can't converge | Set constraints, force judgment on current info |
| Frame lock | Stuck in one framework | Force switch to at least one alternative frame |
