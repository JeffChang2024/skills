---
name: content-engine
description: AI video production, script writing, and image generation via MCP. Generate video scripts, AI images, and short-form or long-form videos from any topic. Free tools (pricing, quotes, status) require no credentials. Paid tools require USDC on Base via x402 — the agent must explicitly approve each payment.
version: 1.4.0
metadata:
  openclaw:
    requires:
      env:
        - CONTENT_ENGINE_URL
        - WALLET_PRIVATE_KEY
    emoji: "\U0001F3AC"
    homepage: https://content-engine-app.fly.dev
    categories:
      - content-creation
      - video-generation
      - ai-writing
      - automation
      - media-production
    tags:
      - video
      - script-writing
      - image-generation
      - text-to-video
      - ai-content
      - generative-ai
      - x402
      - usdc
      - pay-per-use
      - mcp
tools:
  - name: get_pricing
    description: Get live USDC pricing for all operations (free)
  - name: get_quote
    description: Get exact cost quote with per-stage breakdown before paying (free)
  - name: get_queue_status
    description: Check queue position and daily budget remaining (free)
  - name: get_content
    description: Get full content item details including video URL (free)
  - name: get_content_status
    description: Lightweight status poll for pipeline progress (free)
  - name: create_script
    description: Generate AI video script from topic (paid — x402 USDC)
  - name: create_image
    description: Generate image from text prompt (paid — x402 USDC)
  - name: create_video
    description: Generate video from completed script (paid — x402 USDC)
  - name: run_full_pipeline
    description: End-to-end script + video from topic (paid — x402 USDC)
  - name: publish_content
    description: Publish to YouTube, X, TikTok, Instagram, LinkedIn (paid — x402 USDC)
---

# Content Engine

AI-powered content creation as a service. Generate scripts, images, and videos from any topic.

This is an **MCP server** accessible via Streamable HTTP transport. Any MCP-compatible client can connect to it directly — no proprietary CLI or binary required. Free tools work without credentials. Paid tools use the x402 protocol for per-request USDC payments.

## Connection

Content Engine is a standard MCP server. Connect using any MCP client that supports Streamable HTTP transport.

**MCP endpoint:** `https://content-engine-x402.fly.dev/mcp`

**Server discovery:** `https://content-engine-x402.fly.dev/.well-known/mcp.json`

No special binary, CLI tool, or SDK is required. The server follows the MCP specification and works with any compliant client.

## Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONTENT_ENGINE_URL` | Yes | MCP server URL. Default: `https://content-engine-x402.fly.dev` |
| `WALLET_PRIVATE_KEY` | For paid tools | Private key for an EVM wallet holding USDC on Base. Used by the x402 client library to sign payment authorizations. **Only needed if calling paid tools.** Free tools work without it. |

**Important:** `WALLET_PRIVATE_KEY` gives the x402 client library the ability to sign USDC transfer authorizations. This key should be for a dedicated agent wallet with limited funds — not a primary wallet. See the Payment section for details on how funds are protected.

## Payment — How It Works

Paid tools use the [x402 payment protocol](https://www.x402.org/) for USDC payments on the Base network (EIP-155 chain 8453).

### The agent controls every payment

**No funds are ever auto-debited.** The payment flow is:

1. Agent calls a paid tool (e.g. `create_script`)
2. Server responds with **HTTP 402 Payment Required** containing the exact USDC amount, recipient wallet, and network
3. The agent's x402 client library reads the 402 response and **presents the payment for authorization** — the agent decides whether to sign
4. If the agent authorizes, the client signs a USDC transfer for the exact amount specified and retries the request with the signed payment proof
5. Server verifies the payment, settles the transaction on-chain, and processes the request

**Each payment is explicit, per-request, and for an exact amount.** The server cannot withdraw funds, charge more than the stated amount, or initiate payments. The agent (or its x402 client) must actively sign each transaction.

### What the agent needs

To make paid calls, the agent's HTTP client must support x402. The recommended approach:

```typescript
import { wrapFetch } from "@x402/fetch";
import { createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";

// Create wallet from the dedicated agent wallet key
const account = privateKeyToAccount(process.env.WALLET_PRIVATE_KEY);
const wallet = createWalletClient({ account, chain: base, transport: http() });

// Wrap fetch — paid requests are handled via 402 → sign → retry
const x402fetch = wrapFetch(fetch, wallet, "eip155:8453");
```

The wrapped `fetch` handles the 402 challenge-response cycle. Free tools work with plain `fetch` — no wallet needed.

### Cost control

- Call `get_quote` (free) before any paid tool to see the exact USDC price and per-stage breakdown
- Call `get_pricing` (free) to see all current rates
- Call `get_queue_status` (free) to check daily budget remaining
- Use a dedicated wallet with limited USDC to cap total exposure
- Use sandbox mode to test without any payment (see below)

## Typical Pricing

Pricing is dynamic — costs vary based on video duration, narration, and effects.

| Operation | Typical Cost (USDC) | Varies By |
|-----------|-------------------|-----------|
| Script generation | $0.10–$0.20 | Prompt complexity |
| Image generation | $0.15 | Fixed per image |
| Video generation | $0.50–$2.00 | Duration, shots, talking heads |
| Full pipeline (60s) | $1.50–$2.00 | Duration, narration, effects |
| Publishing | $0.10–$0.15 | Fixed |

Always call `get_quote` with your parameters for the exact price.

## Sandbox Mode (Free Testing)

Test the full API flow without payment, wallet, or USDC. Send `Authorization: Bearer sandbox` with any paid request to receive a mock response with the real cost quote attached.

```bash
# Get a quote (always free, no auth needed)
curl -X POST https://content-engine-x402.fly.dev/agent/quote \
  -H "Content-Type: application/json" \
  -d '{"operation":"script","duration_seconds":60}'

# Test a paid endpoint in sandbox mode (no payment, no wallet needed)
curl -X POST https://content-engine-x402.fly.dev/agent/script \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sandbox" \
  -d '{"topic":"How AI is changing music production"}'
```

Sandbox mode returns:
- The **exact USDC price** you would pay
- A **per-stage cost breakdown** showing which AI services are used
- The **response structure** your agent should expect from real calls
- Mock IDs (`content_id`, `jobId`, `transactionId`) matching the real format

Sandbox mode does **not** create content, charge USDC, require a wallet, or count toward rate limits.

## Available Tools

### Free (no payment or credentials required)

| Tool | Description |
|------|-------------|
| `get_pricing` | Live USDC pricing for all operations |
| `get_quote` | Exact cost quote with per-stage breakdown for specific parameters |
| `get_queue_status` | Queue position, active jobs, daily budget remaining |
| `get_content` | Full content item details including video URL and metadata |
| `get_content_status` | Lightweight status poll (pipeline stage + completion %) |

### Paid (x402 USDC — agent approves each payment)

| Tool | Description |
|------|-------------|
| `create_script` | Generate AI video script from topic. Returns `content_id` for tracking. |
| `create_image` | Generate image from text prompt via Runway ML. Supports style and aspect ratio. |
| `create_video` | Generate video from a completed script. Requires `content_id` from `create_script`. |
| `run_full_pipeline` | End-to-end: script + video from a single topic. Fastest path to finished video. |
| `publish_content` | Publish to YouTube, X, TikTok, Instagram, LinkedIn. |

## Typical Workflow

### Quick path
```
get_quote(operation="full_pipeline") → run_full_pipeline → poll get_content_status → get_content
```

### Step-by-step path
1. `get_quote operation="script"` — See exact price
2. `create_script topic="..."` — Generate script, save returned `content_id`
3. `get_content_status content_id="..."` — Poll until complete
4. `get_quote operation="video"` — See exact price for video
5. `create_video content_id="..."` — Generate video
6. `get_content_status content_id="..."` — Poll until ready (1–5 min)
7. `get_content content_id="..."` — Retrieve video URL and metadata

## Important Notes

- Video generation takes 1–5 minutes. Always poll `get_content_status` rather than assuming instant completion.
- The `content_id` (UUID) returned by creation tools is the key for all subsequent operations.
- Pricing is dynamic — always call `get_quote` before paid operations to see the exact cost.
- Use sandbox mode (`Authorization: Bearer sandbox`) to test without spending USDC.
- Use a dedicated agent wallet with limited funds — do not use a primary wallet.
