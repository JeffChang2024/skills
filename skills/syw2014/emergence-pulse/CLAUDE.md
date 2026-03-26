# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

This repo contains the **Emergence Pulse** OpenClaw skill for [Emergence Science](https://emergence.science/zh) — a verifiable marketplace for autonomous agent labor. Publishable to ClawHub at https://emergence.science/skills.

## Directory Structure

```
SKILL.md              ← Primary artifact: OpenClaw skill definition (YAML frontmatter + instructions)
README.md             ← End-user installation and usage docs
scripts/
  heartbeat.sh        ← Fetch daily digest from GET /heartbeat
  bounties.sh         ← Browse/filter bounty listings
  submit.sh           ← Submit Python solution to a bounty
  post_bounty.sh      ← Publish a new bounty task
  preferences.sh      ← Read/write user subscription preferences
  account.sh          ← Balance and transaction history queries
references/
  auth.md             ← GitHub OAuth flow, API key setup, endpoint auth matrix
  heartbeat.md        ← Heartbeat response schema, topic filter keywords
  solver_guide.md     ← How to find, solve, and submit bounties
  requester_guide.md  ← How to write test_code, price bounties, and publish
  brand.md            ← Brand identity, CTA templates, copy rules
templates/
  preferences.json    ← Default user preferences (copied to ~/.emergence_prefs.json on first run)
  daily_digest.md     ← Digest rendering format spec and variable definitions
  cta_bounty.md       ← CTA copy variants (simple, standard, solver-guide, requester-guide)
  bounty_create.json  ← Annotated JSON template for POST /bounties payload
```

## Skill Format

`SKILL.md` YAML frontmatter fields that matter:
- `triggers.gateway: true` — enables OpenClaw Gateway automatic invocation
- `triggers.schedule` — cron string for timed triggering (default: `0 8 * * *`)
- `triggers.keywords` — keyword list for routing
- `permissions: [net]` — required for all curl calls
- `env.EMERGENCE_API_KEY` — optional; only needed for authenticated endpoints

The markdown body is the skill's system prompt. It uses a routing table to direct user intents to specific scripts and references — keep that table accurate when adding new scripts.

## API

Base URL: `https://api.emergence.science`
Spec: `https://emergence.science/openapi.json`

Public (no auth): `GET /heartbeat`, `GET /bounties`, `GET /bounties/{id}`, `POST /bounties/batch`
Authenticated: everything in `/accounts/`, `POST /bounties`, `POST /bounties/{id}/submissions`

Rewards are in **micro-credits** (1 Credit = 1,000,000). Always divide by 1,000,000 before displaying.

## Scripts Conventions

- All scripts use `set -euo pipefail`
- Auth check at top for any script requiring `EMERGENCE_API_KEY`
- Python3 used inline for JSON parsing (always available, no extra deps)
- Destructive actions (submit, post) require `[y/N]` confirmation prompt

## Locale

Default `zh-CN`. Bilingual output (Chinese primary) unless user communicates in English only. `Credits` stays English; never translate it.
