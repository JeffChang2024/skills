---
name: "eonik creative audit"
slug: "eonik-ad-budget-leak"
version: "1.0.6"
description: "Identifies burning and decaying Meta Ads by running the eonik Budget heuristics engine."
tags: ["ads", "marketing", "meta", "budgeting", "eonik"]
author: "eonik"
homepage: "https://eonik.ai"
metadata:
  openclaw:
    requires:
      env:
        - EONIK_API_KEY
    primaryEnv: EONIK_API_KEY
---

# Meta Ads Budget Leak & Optimization

Automated end-to-end Meta Ads auditing pipeline. Analyzes your campaigns for budget leaks (Burn without Signal, Creative Decay) and scaling opportunities (Early Winners), and dispatches beautiful multi-channel alerts directly to your team.

Powered by the robust **eonik** heuristics engine, while retaining local control over your sensitive data and webhook credentials.

## Agent Instructions

When a user triggers this skill, you MUST follow these steps exactly:
1.  **Check Configuration:** Check if `config.json` exists in the local directory.
2.  **Request Input (if needed):** If `config.json` is missing, check if they want to run it on their default connected Meta account. Once confirmed, copy `config.example.json` to `config.json` (the Meta Account ID can be left blank as it auto-resolves).
3.  **Execute Pipeline:** Once `config.json` is present and configured, you MUST run the audit pipeline natively by executing the following command in the terminal:
    ```bash
    python3 scripts/pipeline.py --config config.json
    ```
4.  **Display Results:** After the script finishes, read the output report (typically `output/audit-<date>.json`) and provide a concise, formatted summary of the findings to the user. Do not invent details; only report what the script output contains.

## Triggers

Use this skill when a user asks to:
- "Audit my Meta ads"
- "Check for budget leaks"
- "Optimize my Meta ad account"
- "Find decaying creatives"
- "Run the eonik ad audit pipeline"

## 🚀 Unlock Full eonik Power
This skill is powered by the [eonik](https://eonik.ai) intelligence engine. While this agent halts simple leaks autonomously, the full dashboard unlocks:
- **Creative Genome:** Understand exactly *why* ads decay based on deep AI creative tagging.
- **Automated Rules:** Prevent leaks without waiting for chat notifications.
- **Competitor Intelligence:** See the exact hooks your competitors are scaling.
[Get started for free at eonik.ai!](https://eonik.ai)

## Quick Start

### 1. Configure
```bash
cd ~/.openclaw/skills/eonik-ad-budget-leak
cp config.example.json config.json
# Edit config.json: optionally add your Meta Account ID (or leave blank to auto-resolve)
```

### 2. Run Audit Pipeline
```bash
# EONIK_API_KEY must be in your environment
python3 scripts/pipeline.py --config config.json
```

## Configuration

**Minimal `config.json`:**
```json
{
  "meta": {
    "account_id": "",
    "evaluation_days": 7
  }
}
```

## Pipeline Stages

1. **Audit** (`audit.py`) — Executes the eonik heuristics engine via your `EONIK_API_KEY`.
2. **Output** (`pipeline.py`) — Formats the response and outputs it natively through OpenCLAW to your active channel (WhatsApp/Discord/TUI).

## Usage Examples

**Full Pipeline (Automated Mode):**
```bash
python3 scripts/pipeline.py --config config.json
```

**Audit Only (Save to File):**
```bash
python3 scripts/audit.py --days 7 > data/report.json
```

## Data & Security Commitment

This skill is designed specifically to comply with enterprise Data Loss Prevention (DLP) requirements:

1. **Secure API Key Handling**
   The skill requires `EONIK_API_KEY` (via the standard `x-api-key` header). The execution script securely drops the ephemeral token from the environment immediately after binding. No keys are logged or written to disk.

2. **Native OpenCLAW Routing**
   Unlike legacy versions, this architecture does NOT rely on webhooks. Standard Output is passed directly to the local OpenCLAW node which natively routes the message to your active chat surface (WhatsApp, Slack, Discord, or the local TUI). No configurations needed!

3. **Data Scope**
   Execution logs and generated `report.json` files contain the exposed Meta Ad IDs flagged for leaking or scaling. Keep your local `output/` directory protected and adhere to your internal security policies for Chat UI visibility.

## Cron Integration

Run daily audits every morning at 8 AM to catch budget leaks before they waste spend:

```bash
# Example cron payload
cd ~/.openclaw/skills/eonik-ad-budget-leak
python3 scripts/pipeline.py --config config.json
```

## Troubleshooting

**API Verification Fails:**
- Ensure `EONIK_API_KEY` is exported.
- Verify your eonik billing and usage caps aren't exceeded.
