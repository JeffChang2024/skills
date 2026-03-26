---
name: saturnday
version: 1.5.0
description: Governed AI software execution — scan code for 75+ security, quality, and DevOps checks. Build projects from a brief with per-commit governance, or auto-fix findings. Covers Python, TypeScript, Dockerfiles, Terraform, Kubernetes, GitHub Actions, GitLab CI, and Jenkins. Supports Claude Code, Codex, and Cursor. Requires pip install saturnday.
homepage: https://www.saturnday.dev
source: https://github.com/honouralexwill/saturnday
license: MIT
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - git
    optional_bins:
      - node
    optional_env:
      - ANTHROPIC_API_KEY
      - OPENAI_API_KEY
      - CURSOR_API_KEY
    install:
      - cmd: pip install saturnday
      - cmd: echo "Saturnday installed. Run 'saturnday version' to verify."
    notes: >
      Scan mode requires only python3 and git. Guard mode requires python3, git, and optionally node for TypeScript checks.
      Run mode requires python3, git, and at least one AI backend API key or CLI tool (claude, codex, or agent).
      All API keys are optional — set only the one for your chosen backend.
      Run and Guard modes modify the target repository (git commits, evidence directories).
      Run mode transmits repository contents to the chosen AI backend for code generation.
---

# Saturnday

Govern AI-built software from scan to build to repair — all from the terminal. Saturnday runs 50+ security and quality checks, builds projects from a brief with ticketed execution and per-commit governance, and auto-fixes findings with evidence.

**Requires:** `pip install saturnday` (Python 3.10+)

Verify installation:
```bash
saturnday version
```

If saturnday is not installed, run:
```bash
pip install saturnday
```

---

## Three Modes

Saturnday has three modes. Choose based on the task:

| Mode | When to use | Command |
|------|-------------|---------|
| **Scan** | Check a skill or repo for issues | `python scripts/scan.py <path>` |
| **Guard** | Full governance on a git repo | `python scripts/guard.py <path>` |
| **Run** | Build a project from a brief | `python scripts/run.py <path> --brief "..."` |

---

## Mode 1: Scan

**Use when:** checking an OpenClaw skill for security risks, hallucinated imports, fake tests, or quality issues before installing or publishing.

```bash
python scripts/scan.py <skill-directory-path>
```

Or directly:
```bash
saturnday scan --skill <skill-directory-path> --output /tmp/scan-results --format both
```

### What it checks
- 19 Python security checks (SQL injection, auth bypass, CSRF, XSS, hardcoded secrets)
- 19 TypeScript security checks
- Hallucinated import detection (packages that don't exist)
- No-assert and fake test detection
- Dead code (cross-file analysis)
- Dependency declaration verification
- Project hygiene (README, LICENSE)
- Dockerfile checks (unpinned images, root user, secrets in build, missing dockerignore)
- GitHub Actions (SHA pinning, broad permissions, pull_request_target, plaintext secrets)
- GitLab CI (secrets in YAML, docker-in-docker patterns)
- Jenkins (hardcoded credentials)
- Terraform (hardcoded credentials, public CIDR)
- Kubernetes (privileged containers, unpinned images, secrets in manifests)
- Optional Trivy integration for deep IaC analysis

### Output
```
Disposition: PASS or FAIL
Findings: list with check name, severity, file, line, description
Evidence: timestamped directory with full results
```

---

## Mode 2: Guard

**Use when:** running full governance on any git repository — before merging, before deploying, or for audit.

```bash
python scripts/guard.py <repo-path>
```

For staged changes only (pre-commit):
```bash
python scripts/guard.py <repo-path> --staged
```

Or directly:
```bash
saturnday governance --repo <path> --full
```

### What it checks
All 50+ checks: security (SQL injection, XSS, CSRF, auth bypass, hardcoded secrets, WebSocket security, OAuth, token handling, rate limiting, IDOR, user enumeration, cookie security), AI-specific (hallucinated imports, fake tests, dead code, placeholders), quality (syntax, dependencies, Python version compat, code quality, blast radius, project hygiene, typosquat detection).

### Ratchet baselines
Prevent regressions:
```bash
saturnday baseline generate --repo <path>
```

### Policy exemptions
Create `.saturnday-policy.yaml`:
```yaml
expected_findings:
  - declared_not_installed
  - package_not_importable
```

---

## Mode 3: Run

**Use when:** building a project from a description. This is the full governed execution pipeline.

```bash
python scripts/run.py <project-directory> --brief "build a REST API with auth and tests" --backend anthropic
```

Or interactively:
```bash
cd <project-directory>
saturnday start
```

### Backends

| Backend | Value | Auth |
|---------|-------|------|
| Claude Code CLI | `claude-cli` | Claude Pro subscription |
| Codex CLI | `codex-cli` | OPENAI_API_KEY |
| Cursor CLI | `cursor-cli` | CURSOR_API_KEY |
| OpenAI API | `openai` | OPENAI_API_KEY |
| Anthropic API | `anthropic` | ANTHROPIC_API_KEY |

### What happens during a run

1. **Planning** — 3-stage planner generates tickets with acceptance criteria and scope constraints
2. **Execution** — each ticket executed sequentially, 50+ governance checks after every commit
3. **Retry** — if governance fails, revert, feed findings back, retry (up to 3 attempts)
4. **Ungoverned commit** — if a ticket still fails after retries and auto-repair, the code is committed with a `[GOVERNANCE: review required]` tag so the project stays complete
5. **Auto-repair** — after all tickets, ungoverned and failed tickets go through the repair pipeline again
6. **Definition of done** — evaluates whether plan goals are met
7. **Review report** — for ungoverned tickets: `review-required.md` with findings, remediation tips, and copy-paste fix prompts for each ticket
8. **Evidence** — timestamped directory with per-ticket results, governance evidence, analytics

### Resume interrupted runs
```bash
saturnday resume --repo <path> --backend anthropic
```

---

## When to Use Each Mode

- **"Scan this skill before I install it"** → Scan
- **"Check this repo for security issues"** → Guard
- **"Build me a project from this description"** → Run
- **"Audit this codebase"** → Guard
- **"Fix the findings"** → use `saturnday repair --repo <path>` directly

## Prerequisites

- `pip install saturnday` (Python 3.10+)
- Node.js 18+ (for TypeScript checks)
- Git (for Guard and Run modes)
- At least one AI coder backend for Run mode
