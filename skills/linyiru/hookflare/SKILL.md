---
name: hookflare
description: "Reliable webhook infrastructure for AI agents. Receive webhooks from Stripe, GitHub, Slack, Shopify, Vercel with signature verification, durable queuing, and automatic retries. Use when: (1) setting up webhook listeners for external services, (2) agent needs real-time events from Stripe/GitHub/Slack, (3) webhooks are being lost during restarts or downtime, (4) need durable event buffering with guaranteed delivery. NOT for: sending outgoing webhooks to customers (use Svix), direct API polling, or cron-based scheduled checks."
metadata:
  openclaw:
    emoji: "🔥"
    requires:
      bins: ["hookflare"]
    install:
      - id: npm
        kind: node
        package: hookflare
        bins: ["hookflare"]
        label: "Install hookflare CLI (npm)"
      - id: brew
        kind: brew
        formula: hookedge/hookflare/hookflare
        bins: ["hookflare"]
        label: "Install hookflare CLI (brew)"
---

# hookflare — Webhook Infrastructure for AI Agents

hookflare receives webhooks from external services, queues them durably, and delivers them to your agent with automatic retries. Your agent never misses an event, even during restarts or downtime.

## Why Use This

Without hookflare, webhooks sent while your OpenClaw gateway is restarting or offline are **lost forever**. Most providers send once and move on. hookflare sits in between — it's always online (Cloudflare Workers, 300+ edge locations), accepts the webhook immediately, and retries delivery to your gateway until it succeeds.

## Quick Start

### Local development (receive webhooks on your machine)

```bash
hookflare dev --port 18789 --provider stripe --secret whsec_xxx
```

This creates a secure tunnel to your OpenClaw gateway. Paste the printed Webhook URL into your Stripe Dashboard. No port forwarding, no IP exposure.

### Production setup (persistent, survives restarts)

```bash
# 1. Deploy hookflare (one-click on Cloudflare, or self-host)
# 2. Configure CLI
hookflare config set api_url https://your-hookflare.workers.dev
hookflare config set token hf_sk_xxx

# 3. Connect a provider to your OpenClaw gateway
hookflare connect stripe \
  --secret whsec_xxx \
  --to http://localhost:18789/webhook \
  --events "payment_intent.*"
```

hookflare returns a Webhook URL — register it in Stripe's dashboard. Events are now durably queued and delivered to your gateway with retries.

## Built-in Providers

```bash
hookflare providers ls
```

| Provider | Events | Use case |
|---|---|---|
| **stripe** | payment_intent, customer, invoice, charge | Payment notifications |
| **github** | push, pull_request, issues, release | Code events, PR review |
| **slack** | message, app_mention, reaction | Team notifications |
| **shopify** | orders, products, customers | E-commerce events |
| **vercel** | deployment, domain | Deploy monitoring |

Discover a provider's events:

```bash
hookflare providers describe stripe --json
```

### Any other webhook service

Not limited to the 5 built-in providers. For any service already sending webhooks to your agent, use generic HMAC verification:

```bash
hookflare connect my-service --secret my_signing_secret --to http://localhost:18789/webhook
```

For services with non-standard signature formats, the community can create custom providers with `defineProvider()` — a single file that defines verification method, event types, and payload schemas. See [Provider Design Guide](https://github.com/hookedge/hookflare/blob/main/packages/providers/DESIGN.md).

## Core Workflows

### Stripe payment alerts

```bash
hookflare connect stripe --secret whsec_xxx --to http://localhost:18789/webhook --events "payment_intent.payment_failed"
```

Agent receives failed payment events and can draft follow-up emails, create support tickets, or alert the team.

### GitHub PR auto-review

```bash
hookflare connect github --secret ghsec_xxx --to http://localhost:18789/webhook --events "pull_request"
```

Agent receives PR events instantly and can review code, post comments, or run checks.

### Multi-provider monitoring

```bash
hookflare connect stripe --secret whsec_xxx --to http://localhost:18789/webhook --name stripe-prod
hookflare connect github --secret ghsec_xxx --to http://localhost:18789/webhook --name github-prod
hookflare connect vercel --secret vsec_xxx --to http://localhost:18789/webhook --name vercel-prod
```

All events flow to your gateway through one durable pipeline. Restart your gateway freely — nothing is lost.

### Monitor events in real-time

```bash
hookflare tail --json
```

Stream events as they arrive. Pipe to scripts or other agents:

```bash
hookflare tail --json | jq '.event_type'
```

## What Happens During Downtime

```
Your gateway goes down at 2:00 AM
  ↓
Stripe sends payment_intent.succeeded at 2:15 AM
  → hookflare accepts (202), queues durably
  ↓
GitHub sends push at 2:30 AM
  → hookflare accepts (202), queues durably
  ↓
hookflare retries delivery every few minutes (exponential backoff)
  ↓
Your gateway comes back at 6:00 AM
  → hookflare delivers both events automatically
  → Agent processes them as if nothing happened
```

No manual replay needed. No events lost. Circuit breaker protects your gateway from being overwhelmed on recovery.

## CLI Reference

```bash
hookflare connect <provider> --secret <s> --to <url> [--events <filter>]
hookflare dev --port <n> [--provider <name>] [--secret <s>]
hookflare providers ls [--json]
hookflare providers describe <name> [--json]
hookflare tail [--json] [--source <id>]
hookflare events ls [--json] [--limit <n>]
hookflare health [--json]
```

All commands support `--json` for structured output and `--dry-run` for validation.

## Key Facts

- Runs on Cloudflare Workers — always online, $0 idle cost
- Retries with exponential backoff up to 24 hours
- Circuit breaker pauses delivery to unhealthy destinations
- Built-in idempotency (no duplicate deliveries)
- Apache 2.0 license, fully open source
- GitHub: https://github.com/hookedge/hookflare
