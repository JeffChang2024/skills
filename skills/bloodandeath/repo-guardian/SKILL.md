---
name: repo-guardian
description: >
  Automated GitHub PR review governance and repository maintenance automation.
  Use when reviewing pull requests with dual-model consensus, enforcing merge
  gates, auto-merging approved PRs, and triaging repo state on a cron schedule.
  Not for implementing issue fixes end-to-end (use gh-issues) or general GitHub
  CLI operations (use the github skill). Designed for your-org/your-repo
  repo but works on any GitHub repository.
version: 1.0.0
---

# Repo Guardian — Dual-Model PR Review & Issue Triage

Automated repository maintenance with cross-model review consensus.

## Scope & Boundaries

Repo Guardian handles **PR review governance and repo maintenance automation**:
reviewing PRs, enforcing quality via dual-model consensus, auto-merging when
approved, and triaging repository state.

It is **not** the issue-to-fix implementation pipeline. If the job is to fetch
issues, spawn coding agents, implement fixes, open PRs, and monitor review
feedback, use **gh-issues** instead.

It is also **not** a general-purpose GitHub CLI toolkit. For direct `gh` CLI
operations such as listing PRs, commenting, checking CI, or making ad hoc API
queries, use the **github** skill.

## NOT For

- **Implementing issue fixes end-to-end** — fetching issues, spawning coding agents, writing code, and opening PRs belongs to the **gh-issues** skill
- **General GitHub CLI operations** — listing PRs, commenting, checking CI, or ad-hoc `gh` queries belong to the **github** skill
- **Code authoring or refactoring** — Repo Guardian reviews and gates merges; it does not write new code

## What It Does

Every 6 hours (configurable), Repo Guardian:

1. **Checks for open PRs** on the target repo
2. **Reviews each PR** with two independent models (Opus + GPT-5.4)
3. **Merges** if both models approve
4. **Requests changes** if either model finds issues
5. **Optionally prepares follow-up remediation** for review-discovered issues
6. **Checks for open issues** and triages them for the appropriate next step

## Cron Setup

```bash
# Run the guardian script via OpenClaw cron
# Add to ~/.openclaw/cron/jobs.json:
{
  "repo-guardian": {
    "schedule": "0 */6 * * *",
    "agent": "keats",
    "message": "Run repo-guardian for your-org/your-repo",
    "skill": "repo-guardian"
  }
}
```

Or run manually:
```bash
bash <skill_dir>/scripts/guardian.sh your-org/your-repo
```

## Review Process

### PR Review (Dual-Model Consensus)

```
Open PR detected
  │
  ├─→ Opus reviews (security, architecture, correctness)
  ├─→ Sonnet reviews (code quality, edge cases, tests)
  │   (fallback: Haiku if Sonnet unavailable)
  │
  ├─ Both APPROVE → auto-merge (squash)
  ├─ One APPROVE, one REQUEST_CHANGES → post review comments, do not merge
  ├─ Both REQUEST_CHANGES → post review comments, do not merge
  └─ Either finds CRITICAL issue → post comments + label "needs-fix"
```

### Issue Triage

```
Open issue detected
  │
  ├─ Assess complexity and routing (ready for automation vs needs human)
  ├─ Ready for implementation: hand off to the issue-fix pipeline (gh-issues)
  └─ Complex or unclear: add label "needs-human", post analysis comment
```

## Review Criteria

Each model evaluates independently against:

1. **Correctness** — Does the code do what the PR claims?
2. **Security** — Any vulnerabilities, secret exposure, injection risks?
3. **Tests** — Are changes tested? Do existing tests still pass?
4. **Scope** — Does the PR stay within its stated purpose?
5. **Quality** — Code style, error handling, edge cases, naming

Each model returns a structured verdict:
```json
{
  "verdict": "APPROVE|REQUEST_CHANGES|CRITICAL",
  "summary": "One-line summary",
  "findings": [
    {"severity": "critical|major|minor", "file": "...", "line": 0, "issue": "...", "fix": "..."}
  ],
  "confidence": "high|medium|low"
}
```

## Configuration

Environment variables (set in shell or `.env`):
- `GH_TOKEN` — GitHub token with repo access (required)
- `GUARDIAN_REPO` — Default repo (e.g., `your-org/your-repo`)
- `GUARDIAN_AUTO_MERGE` — Enable auto-merge on consensus (`true`/`false`, default: `true`)
- `GUARDIAN_AUTO_FIX` — Enable auto-fix for issues (`true`/`false`, default: `false`)
- `GUARDIAN_MAX_PRS` — Max PRs to review per run (default: `5`)
- `GUARDIAN_MAX_ISSUES` — Max issues to process per run (default: `3`)

## Safety

- **Never force-pushes** or modifies protected branches
- **Squash merges only** — clean history
- **Labels PRs** with review status for audit trail
- **Posts review comments** with model attribution (which model said what)
- **Requires dual consensus** — single model cannot merge alone
- **Skips PRs by org members** marked with `skip-guardian` label
- **Dry-run mode** available (`--dry-run` flag)

## Models Used

| Role | Primary | Fallback |
|------|---------|----------|
| Reviewer A | anthropic/claude-opus-4-6 | anthropic/claude-sonnet-4-6 |
| Reviewer B | anthropic/claude-sonnet-4-6 | anthropic/claude-haiku-4-5 |
| Issue triage | anthropic/claude-sonnet-4-6 | anthropic/claude-haiku-4-5 |

> **Note:** GPT-5.4 (`openai-codex/gpt-5.4`) can be used as Reviewer B if the OpenAI Codex agent is configured and available in your deployment. When using GPT, set Reviewer B primary to `openai-codex/gpt-5.4` with fallback `anthropic/claude-sonnet-4-6`.

## Requirements

- `gh` CLI authenticated
- `GH_TOKEN` with repo access
- OpenClaw with Opus + GPT agents configured
