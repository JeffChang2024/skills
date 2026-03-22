---
name: openforge
description: >
  Staged, multi-model PRD execution for OpenClaw. Write a PRD with phased sections,
  model routing, and validation gates — OpenForge executes it across local and cloud
  models with automatic escalation, scope verification, quality checks, and learning
  accumulation. Route simple tasks to cheap models, hard tasks to powerful ones, and
  reviews to premium reasoning.
version: 1.1.0
---

# OpenForge

OpenForge turns structured PRD documents into staged, multi-model execution runs.
Each phase routes to the right AI model — local models for simple coding, cloud models
for complex work, premium models for review — with automatic escalation, per-task quality
checks, and accumulated learning across tasks.

## Requirements

- Python >= 3.11
- `uv` (astral.sh package manager)
- `git`
- `openclaw`

## Quick Start

```bash
# 1. Install (one-time)
bash <skill_dir>/scripts/install.sh

# 2. Validate a PRD
<skill_dir>/scripts/openforge validate path/to/prd.md

# 3. Preview execution plan
<skill_dir>/scripts/openforge plan path/to/prd.md --cwd /path/to/project

# 4. Execute
<skill_dir>/scripts/openforge run path/to/prd.md --cwd /path/to/project
```

## CLI Commands

### `validate`
Check PRD syntax, routing, and path overlaps.
```bash
<skill_dir>/scripts/openforge validate path/to/prd.md
<skill_dir>/scripts/openforge validate path/to/prd.md --json
<skill_dir>/scripts/openforge validate path/to/prd.md --lenient
```

### `plan`
Show execution plan without dispatching.
```bash
<skill_dir>/scripts/openforge plan path/to/prd.md
<skill_dir>/scripts/openforge plan path/to/prd.md --cwd /path/to/project --json
```

### `run`
Execute the PRD.
```bash
<skill_dir>/scripts/openforge run path/to/prd.md --cwd /path/to/project
<skill_dir>/scripts/openforge run path/to/prd.md --cwd . --max-escalation 3
<skill_dir>/scripts/openforge run path/to/prd.md --cwd . --allow-dirty
<skill_dir>/scripts/openforge run path/to/prd.md --cwd . --phase scaffold
<skill_dir>/scripts/openforge run path/to/prd.md --cwd . --force-executor cloud
```

### `resume`
Resume an interrupted run.
```bash
<skill_dir>/scripts/openforge resume <run-id>
<skill_dir>/scripts/openforge resume <run-id> --force
```

### `status` / `list`
Inspect runs.
```bash
<skill_dir>/scripts/openforge status <run-id>
<skill_dir>/scripts/openforge status <run-id> --json
<skill_dir>/scripts/openforge list
<skill_dir>/scripts/openforge list --json
```

## PRD Format

PRDs are markdown documents with labeled YAML blocks for machine-readable config.

Required sections: `# PRD: <title>`, `## Objective`, `## Scope` (with `### In Scope`),
`## Routing`, and one or more `## Phase: <id>` sections with task blocks.

Each task can declare:
- `reads:` — files the agent should examine
- `produces:` — files the agent may modify (enforced at runtime)
- `checks:` — quality commands that must pass after the agent completes
- `check:` — shorthand for a single check command

See `templates/` for examples:
- `prd-simple.md` — single stage, minimal
- `prd-full.md` — multi-stage with all features
- `prd-review-only.md` — review existing code

See `references/prd-format.md` for the complete format specification.

## Model Routing

The routing table maps executor aliases to OpenClaw agents:

```yaml
aliases:
  local:
    agent: openforge-local
    fallback: openforge-cloud
    context: 8192
  cloud:
    agent: openforge-cloud
    fallback: openforge-cloud-fallback
  review:
    agent: openforge-review
```

Each phase declares which executor alias to use. Different tiers get different prompts:
- **local** — surgical, code-only, small context budget
- **cloud** — full project context, self-critique, progress awareness
- **review** — evaluative framing, structured output, non-coding
- **cheap** — extraction and parsing only

See `references/model-routing.md` for routing strategies.

## Key Features

### Escalation Cascade
Tasks retry on failure with automatic model escalation:
- Attempt 1-2: primary agent
- Attempt 3+: fallback agent (if defined)
- All attempts exhausted: halt with details

### Per-Task Quality Checks
Tasks can declare `check:` commands that must pass. Failed checks trigger retries
with the error output included as context.

### Learning Accumulation
Completed task summaries are accumulated and included in subsequent prompts.
Later tasks benefit from earlier discoveries about the codebase.

### Structured Completion Detection
Agents write result envelopes (`.openforge/results/{task_id}.json`) with structured
status, decisions, and files modified. Fallback: git diff detection.

### Scope Enforcement
Modified files are verified against declared `produces:` paths. Undeclared modifications
halt the run with a security alert.

### Auto-Commit
Each successful task is automatically committed with a standardized message:
`openforge({phase}): {summary}`

### Tier-Aware Context Assembly
Prompts are built with priority-ordered sections, trimmed to fit model context budgets.
Includes file contents, project conventions, git history, and prior task learnings.

## Security Model

OpenForge enforces declared `produces` paths and runs validators with a sanitized
environment (allowlist model). Secrets are scanned before prompt construction and
redacted from both prompts and artifacts.

Secret scanning happens in three stages: (1) file patterns checked before reading,
(2) content redacted before prompt assembly, (3) final assembled prompt scanned as a
safety net. Git log output is also redacted.

The executor temporarily modifies the agent's workspace in `~/.openclaw/openclaw.json`
during task dispatch and restores the original value afterward (even if dispatch fails).

**Honest limits:**
- Not a sandbox — agents run with user permissions
- Does not protect against malicious PRDs
- Secret detection is regex-based (novel patterns may not be caught)
- Validator confinement is subprocess-level, not OS-level

See `references/security.md` for the full threat model.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tasks completed, all validators passed |
| 1 | Invalid PRD or configuration error |
| 3 | Escalation exhausted or run halted |
| 6 | Security violation (scope escape or secret detected) |

## Known Limitations (v1)

- Sequential execution only (no parallel tasks)
- No automatic fix generation from review findings
- Review phases produce findings but remediation requires follow-up
- Agents must be pre-registered in OpenClaw

## Agent Configuration

See `config/agents.example.json` for example OpenClaw agent definitions.
Run `scripts/install.sh` to register default agents.

## Changelog

### v1.1.0
- **Security fix:** Secrets are now scanned and redacted BEFORE prompts are dispatched to agents. File patterns are checked before reading, content is redacted before assembly, and the final prompt is scanned as a safety net.
- **Security fix:** Agent workspace in `~/.openclaw/openclaw.json` is now restored to its original value after each task dispatch (including on failure or timeout). Config is reloaded fresh before restore to avoid clobbering concurrent changes.
- **Security fix:** Large files are now truncated and shown inline (redacted) instead of instructing agents to read raw files from the working tree.
- **Security fix:** Directory listings now filter out files matching secret file patterns.
- **Security fix:** Convention files are redacted before prompt inclusion.
- **Hardening:** Config writes are atomic (temp file + rename). JSON parse failures are handled defensively.
- **Expanded secret file patterns:** Added `id_rsa*`, `id_ed25519*`, `id_ecdsa*`, `id_dsa*`, `.npmrc`, `.pypirc`, `.netrc`, `.docker/config.json`, `.aws/credentials`, `*.pfx`.
