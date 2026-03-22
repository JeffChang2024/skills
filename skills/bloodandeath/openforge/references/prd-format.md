# PRD Format Reference

## Overview

An OpenForge PRD is a Markdown document with a strict structure. Machine-readable content lives in **labeled fenced YAML blocks**. The parser is line-oriented (not CommonMark).

## Fence Info-String Grammar

```
info_string := "yaml" SP label
label       := label_type [ ":" label_id ]
label_type  := "routing" | "phase" | "task" | "stage-validators"
label_id    := [a-z0-9][a-z0-9_-]*
SP          := " " (exactly one space)
```

- Labels are **case-sensitive**, always lowercase.
- Unlabeled `yaml` fences → parse error.
- `label_id` is required for `phase` and `task`. Optional for `routing` and `stage-validators`.
- Duplicate same-type labels → parse error.
- Unknown keys in YAML → parse error (strict mode) or warning (`--lenient`).

## Required Document Structure

Headings must appear in this order:

| Heading | Required | Notes |
|---------|----------|-------|
| `# PRD: <title>` | Yes | Exactly one H1 |
| `## Objective` | Yes | Free text |
| `## Problem` | No | Free text |
| `## Scope` | Yes | Must contain `### In Scope` |
| `### In Scope` | Yes | Bullet list |
| `### Out of Scope` | No | Bullet list |
| `## Routing` | Yes | Contains `yaml routing` block |
| `## Phase: <id>` | Yes (1+) | One or more phases |
| `## Stage Validators` | No | Contains `yaml stage-validators` block |
| `## Acceptance Criteria` | No | Bullet list |

Non-normative sections (e.g., `## Notes`) may appear **after** all normative sections.

## YAML Schemas

### Routing

```yaml
aliases:
  <alias>:
    agent: <string>          # REQUIRED: OpenClaw agent ID
    fallback: <string|null>  # OPTIONAL: fallback agent ID
    context: <int|null>      # OPTIONAL: context window limit (tokens)
```

### Phase

```yaml
stage: <int>                 # REQUIRED: >= 1
executor: <alias>            # REQUIRED: must exist in routing aliases
validator: <string|null>     # OPTIONAL: shell command, exit 0 = pass
validator_timeout: <int>     # OPTIONAL: seconds, default 300
```

### Task

```yaml
id: <string>                 # REQUIRED: unique across PRD, matches [a-z0-9][a-z0-9_-]*
reads: [<path>, ...]         # OPTIONAL (recommended)
produces: [<path>, ...]      # REQUIRED if phase shares a stage with another phase
```

### Stage Validators

```yaml
<stage_number>: <shell_command|null>
```

## Path Rules

- All paths relative to `--cwd`. No absolute paths.
- No `..` segments above `--cwd`.
- Trailing `/` = subtree claim (directory). No trailing `/` = exact file.
- Globs NOT supported. Use subtree claims.
- Normalization: strip `./`, collapse `//`, remove `.` segments.
- POSIX-style (forward slashes) always.

## Overlap Detection

For phases sharing a stage:
- Two exact claims overlap if identical after normalization.
- Exact + subtree overlap if the file is within the subtree prefix.
- Two subtrees overlap if either is a prefix of the other.

Overlap → parse error listing conflicting phases and paths.

At runtime, `git diff` paths are verified against declared `produces:` claims. Undeclared modifications → security halt.
