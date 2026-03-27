---
name: agent-cost-monitor
version: 1.1.0
description: Real-time token usage and cost tracking across all your OpenClaw agents — alerts, budgets, and optimization tips
emoji: 💰
tags:
  - cost
  - monitoring
  - tokens
  - budget
  - optimization
  - multi-agent
---

# Agent Cost Monitor — Know What Your Agents Cost

Track token usage, costs, and efficiency across all your OpenClaw agents in real-time. Get alerts before you blow your budget.

## Triggers

Activate this skill when:
- User asks "how much am I spending?" or "which agent uses the most tokens?"
- User asks about rate limits, token usage, or budget warnings
- A cron job fires with the cost-report payload
- Suspected runaway agent (unusually high token burn)
- Weekly or daily cost-hygiene review

## NOT For

- **Billing management** — paying invoices, updating payment methods, or managing API subscriptions (do that directly in provider dashboards)
- **Model pricing research** — looking up current API rates or comparing provider costs (use web search for that)
- **Session debugging** — diagnosing why a session crashed or behaved incorrectly (use error recovery protocol)

## The Problem

Running multiple agents is powerful — but expensive if you're not watching:
- Which agent is burning the most tokens?
- Are heartbeats wasting money on expensive models?
- Is caching actually saving you anything?
- When will you hit your weekly rate limit?

## What This Skill Does

When triggered (via cron or manually), the agent:
1. Checks `session_status` for each agent
2. Calculates per-agent and total costs
3. Compares against budget thresholds
4. Sends alerts if limits are approaching
5. Suggests optimization moves

## Usage

Ask your monitoring agent (or any agent with this skill):

```
"Give me a cost report for all agents"
"Which agent used the most tokens today?"
"Am I going to hit my rate limit this week?"
```

### Automated Daily Report (Cron)

```json5
{
  "name": "Daily Cost Report",
  "schedule": { "kind": "cron", "expr": "0 20 * * *", "tz": "Europe/Berlin" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run a cost report across all agents. Check session_status for each. Report: total tokens, cost per agent, top spender, budget warnings. Send summary to user."
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce" }
}
```

## Cost Report Format

When generating a report, use this structure:

```markdown
## 💰 Agent Cost Report — [Date]

### Per-Agent Breakdown
| Agent | Model | Tokens (24h) | Est. Cost | Status |
|-------|-------|-------------|-----------|--------|
| Central | Opus 4.6 | 125K | $1.87 | ⚠️ High |
| Techops | Opus 4.6 | 89K | $1.33 | ✅ Normal |
| Atlas | Sonnet 4.5 | 45K | $0.27 | ✅ Low |
| Closer | Haiku 4.5 | 23K | $0.02 | ✅ Minimal |
| Heartbeats | Ollama | 12K | $0.00 | ✅ Free |

### Summary
- **Total 24h:** 294K tokens (~$3.49)
- **Projected weekly:** ~$24.43
- **Budget:** $20/week → ⚠️ 122% projected

### Recommendations
1. Move Techops from Opus → Sonnet for routine tasks (-40% cost)
2. Increase heartbeat interval from 15m → 30m
3. Enable context pruning on Atlas (idle sessions burning cache)
```

## Model Cost Reference

Use these rates for estimation (as of 2026):

### Anthropic (Claude OAuth / API)
| Model | Input/1M | Output/1M | Cache Read/1M | Cache Write/1M |
|-------|----------|-----------|---------------|----------------|
| Opus 4.6 | $5.00 | $25.00 | $0.50 | $6.25 |
| Sonnet 4.5 | $3.00 | $15.00 | $0.30 | $3.75 |
| Haiku 4.5 | $1.00 | $5.00 | $0.08 | $1.25 |

### Free Options
| Model | Cost | Use For |
|-------|------|---------|
| Ollama (local) | $0 | Heartbeats, simple tasks |
| Gemini OAuth | $0* | Fallback (rate limited) |

*Free tier with rate limits

## Optimization Playbook

### Quick Wins (Do These First)

1. **Heartbeats on Ollama**
```json5
{ "heartbeat": { "model": "ollama/llama3.2:3b" } }
```
Saves: 100% of heartbeat costs (can be $5-10/week with Opus)

2. **Haiku Cache Retention Off**
```json5
{ "anthropic/claude-haiku-4-5": { "params": { "cacheRetention": "none" } } }
```
Saves: Cache write costs on cheap model (not worth caching)

3. **Context Pruning**
```json5
{ "contextPruning": { "mode": "cache-ttl", "ttl": "5m" } }
```
Saves: Stale context re-reads on every turn

4. **Opus/Sonnet Cache Retention Long**
```json5
{ "anthropic/claude-opus-4-6": { "params": { "cacheRetention": "long" } } }
```
Saves: Re-sending system prompt every turn (biggest single saving)

### Model Tiering (Biggest Impact)

| Task Type | Use This | Not This | Saving |
|-----------|----------|----------|--------|
| Coordination, complex reasoning | Opus | — | Justified |
| Finance, data analysis | Sonnet | Opus | -40% |
| Sales drafts, marketing copy | Haiku | Sonnet | -67% |
| Heartbeats, health checks | Ollama | Any paid | -100% |
| Tweet drafts | Haiku or Grok | Opus | -80% |

### Session Management

- **Daily reset**: Sessions auto-clear at a set hour (reduces token accumulation)
```json5
{ "session": { "reset": { "mode": "daily", "atHour": 4, "idleMinutes": 45 } } }
```
- **Memory flush**: Save important context before compaction
```json5
{ "compaction": { "memoryFlush": { "enabled": true } } }
```

## Alert Thresholds

### Decision Rules

Apply these rules when generating a cost report:

| Condition | Action |
|-----------|--------|
| Any agent exceeds $2.00/day | 🚨 Immediate alert — name the agent |
| Projected weekly > 100% of budget | 🚨 Immediate alert — include top spender |
| Projected weekly 80–100% of budget | ⚠️ Warning — include optimization suggestions |
| Projected weekly 60–80% of budget | 📊 Note in report — no alert required |
| Projected weekly < 60% of budget | ✅ No action — include in report only |
| Any single session > 50K tokens in one turn | ⚠️ Flag as possible runaway |
| Opus used for routine/heartbeat tasks | 💡 Recommend downgrade to Haiku/Ollama |

### Default Budget Configuration

Store in memory (or agent AGENTS.md) and reference when generating reports:

```markdown
## Budget Alerts
- Daily budget: $5.00 (warn at 80% = $4.00)
- Weekly budget: $20.00 (warn at 70% = $14.00)
- Per-agent daily max: $2.00
- Alert channel: Telegram DM
```

Adjust these thresholds per-deployment in the monitoring agent's memory file.

## Durable Output

When running as a cron job or generating a formal report, **write the output to a file** in addition to sending it to chat:

```bash
REPORT_DIR=$WORKSPACE/memory/cost-reports
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/$(date +%Y-%m-%d).md"
# Write the formatted report to $REPORT_FILE
```

Reference path: `$WORKSPACE/memory/cost-reports/YYYY-MM-DD.md`

This allows the principal to review historical cost trends and gives the agent a durable record for pattern detection.

## Integration with DevOps Agent

If you have a DevOps/monitoring agent (e.g. your DevOps agent), add to its AGENTS.md:

```markdown
## Cost Monitoring
- Run daily cost report at 20:00
- Alert if any agent exceeds $2/day
- Weekly summary every Monday 09:00
- Track trends: is usage going up or down?
```

## FAQ

**Q: Does this skill make API calls?**
A: No. It uses OpenClaw's built-in `session_status` tool. No external APIs, no additional costs.

**Q: How accurate are cost estimates?**
A: Based on published model pricing. Actual costs may vary with caching hits. Estimates are conservative (slightly high).

**Q: Can I track costs per conversation?**
A: Not directly. Costs are tracked per session. Use `sessions_list` to see per-session token counts.

**Q: Works with non-Anthropic models?**
A: Yes. Token counts work for all providers. Cost estimation requires known pricing (add custom rates in the cost reference section).

## Changelog

### v1.1.0
- Generalized all agent names in examples
- No specific setup references

### v1.0.0
- Initial release
