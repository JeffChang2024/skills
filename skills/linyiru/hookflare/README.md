# hookflare-skill

OpenClaw / ClawHub skill for [hookflare](https://github.com/hookedge/hookflare) — reliable webhook infrastructure for AI agents.

## Install

```bash
clawhub install hookedge/hookflare-skill
```

## What it does

When your agent needs to receive webhooks from Stripe, GitHub, Slack, or other services, this skill provides hookflare CLI commands for:

- **One-shot setup** — `hookflare connect stripe --secret whsec_xxx --to http://localhost:18789/webhook`
- **Local dev tunnel** — `hookflare dev --port 18789 --provider stripe --secret whsec_xxx`
- **Provider discovery** — `hookflare providers ls` / `hookflare providers describe stripe --json`
- **Event streaming** — `hookflare tail --json`

## Why hookflare + OpenClaw

OpenClaw's gateway loses webhook events during restarts and downtime. hookflare sits in front of your gateway — it's always online (Cloudflare Workers), accepts webhooks immediately, and retries delivery until your gateway is back.

```
Stripe → hookflare (always online) → OpenClaw Gateway (can restart freely)
```

## More info

- [hookflare GitHub](https://github.com/hookedge/hookflare)
- [Provider Design Guide](https://github.com/hookedge/hookflare/blob/main/packages/providers/DESIGN.md)
