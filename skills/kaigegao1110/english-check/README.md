# English Check

![Version](https://img.shields.io/badge/version-1.0.3-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Brief, practical English corrections for grammar, word choice, collocations, and idiom errors.

## Installation

```bash
# Via ClawhHub
clawdhub install english-check

# Via Git
git clone https://github.com/KaigeGao1110/english-check ~/.openclaw/workspace/skills/english-check
```

## Quick Start

Type `//en ` followed by your English text:

```
//en I already send the report to Oleg yesterday
```

## What It Does

- Corrects grammar errors
- Fixes word choice mistakes
- Improves collocations
- Fixes idiom misuse
- Adjusts register when needed

## Correction Format

Each correction includes:
1. Original sentence
2. Corrected version
3. Brief explanation (1 sentence)

## Examples

```
//en Can you please confirm if you received my email?
✅ (correct - no change needed)

//en I want to discuss about the project tomorrow.
Correction: I want to discuss the project tomorrow.
Why: "Discuss" is a transitive verb — it takes a direct object without "about."

//en The system is working very good.
Correction: The system is working very well.
Why: "Well" is the adverb form modifying the verb "working."
```

## Design Principles

- **Brief** — one correction per message, short explanation
- **Practical** — focus on errors that affect clarity
- **Non-intrusive** — only correct real issues, not style preferences
- **Educational** — show the pattern, not just the fix

## For AI Agents

Install into your OpenClaw workspace skills directory.

## Language

All corrections are written in **English**.
