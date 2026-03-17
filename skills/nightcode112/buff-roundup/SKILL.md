---
name: buff-roundup
description: Auto-invest spare change from every transaction. Rounds up payments to the nearest dollar and invests the difference into BTC, ETH, or SOL via Jupiter on Solana. All fee logic enforced server-side. SDK is a thin API client — no secrets, no sensitive logic. REST API for any language.
required_credentials:
  - name: BUFF_API_KEY
    description: "API key for authenticating with the Buff API. Get one at buff.finance/dashboard"
    sensitive: true
  - name: BUFF_WALLET_PUBKEY
    description: "Your Buff wallet public key (Solana address)"
    sensitive: false
  - name: BUFF_PLAN
    description: "Round-up tier: seed ($0.05), sprout ($0.10), tree ($0.50), forest ($1.00)"
    sensitive: false
permissions:
  - network: "Connects to buff.finance API (HTTPS). All fee calculation and swap routing handled server-side."
  - storage: "None — stateless API client"
---

# Buff — Round-Up Investing Protocol

Buff rounds up every Solana transaction and auto-invests the spare change into crypto assets. All fees are enforced server-side — the SDK is a thin API client with no sensitive logic.

## Quick Start

```bash
npm install buff-protocol-sdk
```

```typescript
import { Buff } from "buff-protocol-sdk"

const buff = new Buff({
  apiKey: process.env.BUFF_API_KEY,
  plan: "sprout",
  investInto: "BTC",
})

// Calculate a round-up
const breakdown = await buff.calculateRoundUp(4.73)
// $4.73 → $4.80 = $0.07 round-up

// Get wrap instructions (server builds transfer instructions with fees)
const { instructions, breakdown } = await buff.getWrapInstructions(
  27.63, userPubkey, buffWalletPubkey
)
// Append instructions to your transaction, sign, send
```

## Auto-Invest

```typescript
// Check if threshold reached
const acc = await buff.getAccumulator(walletPubkey)

// Build swap transactions (server-side via Jupiter)
const result = await buff.buildSwap(walletPubkey)
if (result.ready) {
  for (const swap of result.transactions) {
    // Sign the transaction, then execute
    await buff.executeSwap(signedTx)
  }
}
```

## Multi-Asset Allocation

```typescript
buff.setAllocations([
  { asset: "BTC", pct: 60 },
  { asset: "ETH", pct: 40 },
])
```

## Plan Tiers

| Plan | Rounds to | Fee |
|------|-----------|-----|
| Seed | $0.05 | 1.00% |
| Sprout | $0.10 | 0.75% |
| Tree | $0.50 | 0.50% |
| Forest | $1.00 | 0.25% |

## REST API

No SDK needed — any language, any agent:

```bash
# Calculate round-up
curl -X POST https://buff.finance/api/roundup \
  -H "x-api-key: YOUR_KEY" \
  -d '{"txValueUsd": 27.63, "plan": "tree"}'

# Get wrap instructions (server builds transfer with fees enforced)
curl -X POST https://buff.finance/api/wrap \
  -H "x-api-key: YOUR_KEY" \
  -d '{"txValueUsd": 27.63, "userPubkey": "...", "buffWalletPubkey": "..."}'

# Build swap transaction
curl -X POST https://buff.finance/api/swap/build \
  -H "x-api-key: YOUR_KEY" \
  -d '{"buffWalletPubkey": "...", "targetAsset": "BTC"}'

# Check portfolio
curl https://buff.finance/api/portfolio/WALLET_ADDRESS
```

## Security

- All fee calculation and treasury addresses are **server-side only**
- The SDK contains **zero sensitive logic** — it's just HTTP calls
- No funds are moved without explicit user signing
- Fees cannot be bypassed — the server builds all transfer instructions

## Verifying Server-Built Transactions

Before signing any transaction returned by the Buff API, agents and developers **should verify**:

1. **Deserialize the instructions** returned by `/api/wrap` (base64 JSON containing programId, keys, data)
2. **Check that transfers only go to your Buff wallet** (user investment) and the known Buff treasury (`4pWnqVxtSfrMo2XK6AarW3rDNoN7UfAMEyHF8Y9KZGHf`)
3. **Verify amounts match the breakdown** — `userInvestmentLamports` + `buffFeeLamports` should equal `roundUpLamports`
4. **For swaps**, verify the unsigned transaction from `/api/swap/build` contains only Jupiter swap instructions for the expected token pair and amount
5. **Use a scoped/rotatable API key** and test with small amounts first
6. **Compare the breakdown** from `/api/roundup` (informational) with `/api/wrap` (executable) — they should match for the same inputs

## Links

- Docs: https://buff.finance/docs
- Dashboard: https://buff.finance/dashboard
- API Reference: https://buff.finance/docs/api/rest
- GitHub: https://github.com/nightcode112/Buff
