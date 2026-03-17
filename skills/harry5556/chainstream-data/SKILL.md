---
name: chainstream-data
description: Query and analyze on-chain data across Solana, BSC, Base, Ethereum. Use when searching tokens, analyzing wallet PnL, tracking market trends, monitoring real-time trades, assessing token risk, or building data pipelines. Also covers KYT compliance, webhooks, and WebSocket streaming.
metadata: {"clawdbot":{"emoji":"📊","requires":{"anyBins":["curl","npx"]},"os":["linux","darwin","win32"]}}
---

# ChainStream Data

AI-native on-chain big data infrastructure providing real-time trading data, token analytics, wallet profiling, and market intelligence across Solana, BSC, Base, and Ethereum via 80+ REST API endpoints, 18 MCP tools, and WebSocket streaming.

## When to Use

- Searching for tokens by name, symbol, or contract address across multiple chains
- Analyzing token metrics: price, volume, holders, liquidity, security score
- Profiling wallets: portfolio holdings, realized/unrealized PnL, net worth
- Tracking market trends: hot tokens, new listings, graduating tokens, top gainers
- Monitoring real-time trades and price movements via WebSocket
- Assessing address risk and transaction compliance (KYT/KYA)
- Setting up webhooks for on-chain event notifications
- Building data pipelines with batch token/wallet queries

## Setup

### MCP Server Connection

```json
{
  "mcpServers": {
    "chainstream": {
      "url": "https://mcp.chainstream.io/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Authentication

**Bearer Token** (API Key subscription):

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.chainstream.io/v2/token/search?keyword=PUMP&chain=sol
```

**x402 Micropayment** (no account needed — see [chainstream-x402](../chainstream-x402/) skill):

```bash
curl -H "X-Payment: <base64-payment-proof>" \
  https://api.chainstream.io/v2/token/search?keyword=PUMP&chain=sol
```

**OAuth 2.0 Client Credentials**:

```bash
curl -X POST https://dex.asia.auth.chainstream.io/oauth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"YOUR_ID","client_secret":"YOUR_SECRET","audience":"https://api.dex.chainstream.io","grant_type":"client_credentials"}'
```

**x402 Pay-per-Query** (no account needed, USDC on Base/Solana):

Two-phase flow: (1) purchase plan with USDC, (2) sign every request with wallet.

```typescript
import { ChainStreamClient } from '@chainstream-io/sdk';

const client = new ChainStreamClient('', {
  walletSigner: {
    getAddress: async () => wallet.getDefaultAddress(),
    getChain: () => 'evm',
    signPayment: async (req) => { /* USDC transfer for plan purchase */ },
    signMessage: async (msg) => wallet.signMessage(msg), // per-request: "chainstream:evm:{addr}:{ts}:{nonce}"
  },
});
// SDK handles both x402 purchase and per-request wallet auth automatically
```

Per-request wallet auth headers: `X-Wallet-Address`, `X-Wallet-Chain` (`evm`/`solana`), `X-Wallet-Signature`, `X-Wallet-Timestamp`, `X-Wallet-Nonce`. Signature message: `chainstream:{chain}:{address}:{timestamp}:{nonce}`. See [x402 Auth Reference](references/x402-auth.md) for full details.

## MCP Tools Quick Reference

### tokens/search — Find tokens

```bash
# MCP tool call
{"tool": "tokens/search", "arguments": {"query": "PUMP", "chain": "sol", "limit": 5}}
```

```typescript
import { ChainStreamClient } from '@chainstream-io/sdk';
const client = new ChainStreamClient('YOUR_TOKEN');
const results = await client.token.search({ keyword: 'PUMP', chain: 'sol' });
```

### tokens/analyze — Deep token analysis

```bash
{"tool": "tokens/analyze", "arguments": {"chain": "sol", "address": "TOKEN_ADDRESS", "sections": ["overview","metrics","holders","security"]}}
```

```typescript
const analysis = await client.token.getToken({ chain: 'sol', tokenAddress: 'TOKEN_ADDRESS' });
const security = await client.token.getSecurity({ chain: 'sol', tokenAddress: 'TOKEN_ADDRESS' });
```

### wallets/profile — Wallet PnL and holdings

```bash
{"tool": "wallets/profile", "arguments": {"chain": "sol", "address": "WALLET_ADDRESS", "include": ["holdings","pnl","net_worth"]}}
```

```typescript
const pnl = await client.wallet.getPnl({ chain: 'sol', walletAddress: 'WALLET_ADDRESS' });
const netWorth = await client.wallet.getNetWorth({ chain: 'sol', walletAddress: 'WALLET_ADDRESS' });
```

### market/trending — Hot and new tokens

```bash
{"tool": "market/trending", "arguments": {"chain": "sol", "category": "hot", "limit": 10}}
```

```typescript
const hot = await client.ranking.getHotTokens({ chain: 'sol', duration: '24h' });
const newTokens = await client.ranking.getNewTokens({ chain: 'sol' });
```

### kyt/assess_risk — Address compliance

```bash
{"tool": "kyt/assess_risk", "arguments": {"address": "0x...", "chain": "eth"}}
```

```typescript
const risk = await client.kyt.getAddressRisk({ address: '0x...' });
```

## All 18 MCP Tools

| Tool | Description | Risk |
|------|-------------|------|
| `tokens/search` | Search tokens by name, symbol, or address | L0 |
| `tokens/analyze` | Full analysis: price, volume, holders, security, liquidity | L0 |
| `tokens/price_history` | OHLCV candlestick data for charting | L0 |
| `tokens/discover` | Discover tokens by on-chain metrics (volume, price change) | L0 |
| `tokens/compare` | Side-by-side comparison of up to 5 tokens | L0 |
| `wallets/profile` | Holdings, realized/unrealized PnL, net worth | L1 |
| `wallets/activity` | Recent transfers and trade history | L1 |
| `market/trending` | Hot, new, migrated, graduating, stock tokens | L0 |
| `trades/recent` | Recent on-chain trades by token or wallet | L0 |
| `kyt/assess_risk` | KYT address risk assessment (Chainalysis) | L2 |
| `webhooks/manage` | Create, list, delete webhook endpoints | L1 |
| `blockchain/info` | Supported chains and DEX protocol info | L0 |
| `dex/quote` | Get swap quote (read-only) | L0 |
| `dex/swap` | Execute token swap on DEX | L3 |
| `dex/create_token` | Create token on launchpad | L3 |
| `trading/backtest` | Backtest a trading strategy | L2 |
| `trading/execute` | Execute trade with Elicitation confirmation | L3 |
| `transaction/send` | Broadcast signed transaction | L3 |

Risk levels: L0 read-only, L1 sensitive data, L2 analysis/cost, L3 requires user confirmation (Elicitation).

## Data API Categories

### Token (25+ endpoints)

Core token data at `/v2/token/`:

```bash
# Search tokens
GET /v2/token/search?keyword=PUMP&chain=sol

# Token detail
GET /v2/token/{chain}/{tokenAddress}

# Price, K-line, holders, security, liquidity
GET /v2/token/{chain}/{tokenAddress}/price
GET /v2/token/{chain}/{tokenAddress}/candles?resolution=1h&limit=100
GET /v2/token/{chain}/{tokenAddress}/holders
GET /v2/token/{chain}/{tokenAddress}/security
GET /v2/token/{chain}/{tokenAddress}/liquiditySnapshots

# Batch operations
GET /v2/token/{chain}/multi?addresses=ADDR1,ADDR2
GET /v2/token/{chain}/marketData/multi?addresses=ADDR1,ADDR2
```

### Wallet (15+ endpoints)

Wallet analytics at `/v2/wallet/`:

```bash
# PnL analysis
GET  /v2/wallet/{chain}/{walletAddress}/pnl
POST /v2/wallet/{chain}/{walletAddress}/calculate-pnl
GET  /v2/wallet/{chain}/{walletAddress}/pnl-by-token

# Net worth
GET /v2/wallet/{chain}/{walletAddress}/net-worth
GET /v2/wallet/{chain}/{walletAddress}/net-worth-chart
GET /v2/wallet/{chain}/{walletAddress}/tokens-balance

# Activity
GET /v2/wallet/{chain}/{walletAddress}/transfers
GET /v2/wallet/{chain}/{walletAddress}/balance-updates
```

### Trade (4 endpoints)

```bash
GET /v2/trade/{chain}                      # Recent trades
GET /v2/trade/{chain}/activities           # Trade activities
GET /v2/trade/{chain}/top-traders          # Top traders by PnL
GET /v2/trade/{chain}/trader-gainers-losers # Gainers and losers
```

### Ranking (5 endpoints)

```bash
GET /v2/ranking/{chain}/hotTokens/{duration}  # Hot tokens (1h/6h/24h)
GET /v2/ranking/{chain}/newTokens             # New token listings
GET /v2/ranking/{chain}/finalStretch          # About to graduate
GET /v2/ranking/{chain}/migrated              # Migrated tokens
GET /v2/ranking/{chain}/stocks                # Stock-type tokens
```

### KYT Compliance (16 endpoints)

```bash
POST /v2/kyt/address                          # Register address
GET  /v2/kyt/addresses/{address}/risk         # Address risk score
POST /v2/kyt/transfer                         # Register transfer
GET  /v2/kyt/transfers/{id}/summary           # Transfer risk summary
GET  /v2/kyt/transfers/{id}/alerts            # Transfer alerts
POST /v2/kyt/withdrawal                       # Register withdrawal
GET  /v2/kyt/withdrawal/{id}/fraud-assessment # Fraud assessment
```

### Webhook (7 endpoints)

```bash
GET    /v2/webhook/endpoint              # List endpoints
POST   /v2/webhook/endpoint              # Create endpoint
PATCH  /v2/webhook/endpoint              # Update endpoint
DELETE /v2/webhook/endpoint/{id}         # Delete endpoint
GET    /v2/webhook/endpoint/{id}/secret  # Get signing secret
POST   /v2/webhook/endpoint/{id}/secret/rotate  # Rotate secret
```

## SDK Quick Start

### TypeScript

```typescript
import { ChainStreamClient } from '@chainstream-io/sdk';

const client = new ChainStreamClient('YOUR_TOKEN', {
  serverUrl: 'https://api.chainstream.io',
  streamUrl: 'wss://realtime-dex.chainstream.io/connection/websocket',
  autoConnectWebSocket: false,
});

const token = await client.token.getToken({ chain: 'sol', tokenAddress: 'ADDRESS' });
const pnl = await client.wallet.getPnl({ chain: 'sol', walletAddress: 'ADDRESS' });
```

### Python

```python
from chainstream.openapi_client import ApiClient, Configuration
from chainstream.openapi_client.api import TokenApi, WalletApi

config = Configuration(host="https://api.chainstream.io")
config.access_token = "YOUR_TOKEN"
api = ApiClient(configuration=config)

token_api = TokenApi(api)
result = token_api.search(keyword="PUMP", chain="sol")
```

### Go

```go
import chainstream "github.com/chainstream-io/chainstream-go-sdk/v2"

client, _ := chainstream.NewClient(chainstream.ClientOptions{
    AccessToken: "YOUR_TOKEN",
})
token, _ := client.Token.GetToken(ctx, "sol", "ADDRESS")
pnl, _ := client.Wallet.GetPnl(ctx, "sol", "WALLET_ADDRESS")
```

### Rust

```rust
use chainstream_sdk::{ChainStreamClient, ChainStreamClientOptions};

let client = ChainStreamClient::new("YOUR_TOKEN", None);
// Use openapi client for REST calls
// Use client.stream for WebSocket subscriptions
```

## WebSocket Streaming

Connect to real-time data feeds:

```typescript
const client = new ChainStreamClient('YOUR_TOKEN', { autoConnectWebSocket: true });
await client.stream.connect();

// Subscribe to token price candles
const unsub = client.stream.subscribeTokenCandles(
  { chain: 'sol', token: 'ADDRESS', resolution: '1m' },
  (candle) => console.log(`Price: ${candle.c}, Volume: ${candle.v}`)
);

// Subscribe to new token listings
client.stream.subscribeNewToken(
  { chain: 'sol' },
  (token) => console.log(`New: ${token.n} (${token.s})`)
);

// Subscribe to wallet PnL updates
client.stream.subscribeWalletPnl(
  { chain: 'sol', wallet: 'ADDRESS' },
  (pnl) => console.log(`PnL: ${pnl.piu}`)
);
```

**WebSocket URL**: `wss://realtime-dex.chainstream.io/connection/websocket?token=YOUR_TOKEN`

Available channels: candles, token stats, holders, new tokens, supply, liquidity, rankings, wallet balance, wallet PnL, trades, pool balance. See [websocket-streams.md](references/websocket-streams.md) for the full channel reference.

## SaaS Dashboard

ChainStream also provides a web dashboard at [app.chainstream.io](https://app.chainstream.io) for managing API keys, monitoring usage, and configuring webhooks:

- **API Key Management**: create, revoke, configure scopes (kyt.read, kyt.write, webhook.read, webhook.write)
- **Usage Metrics**: request counts, response times, quota consumption, route stats — filterable by API key and time range (1H/1D/7D/30D)
- **WebSocket Metrics**: connection counts, CU usage, data volume, IP stats
- **Plan & Billing**: view current subscription, purchase CU, order history, invoices
- **Webhook Management**: create/edit/delete endpoints, configure events, test, rotate secrets
- **KYT Service**: address verification, transfer/withdrawal risk records, credit purchase
- **Audit Logs**: organization-level activity logging with export

Use the dashboard for account management. Use the API/MCP/SDK for programmatic data access. For keyless access, see the [chainstream-x402](../chainstream-x402/) skill.

## Response Formats

Control response verbosity with `response_format`:

| Format | Tokens | Use Case |
|--------|--------|----------|
| `concise` | ~500 | Default for AI agents, 5-10 records with key metrics |
| `detailed` | ~2000-5000 | Full data including top holders, recent trades, K-lines |
| `minimal` | ~100 | IDs and values only, for batch processing |

## Tips

- Default to `response_format: "concise"` when querying via MCP to minimize token usage. Switch to `detailed` only when the user explicitly needs full data.
- Token search is fuzzy — searching "pump" matches PUMP, PumpFun, PumpSwap, etc. Use the contract address for exact matches.
- Batch endpoints (`/multi`) save API calls when querying multiple tokens. Pass up to 50 addresses comma-separated.
- WebSocket subscriptions are billed at 0.005 Unit per byte of data pushed. Unsubscribe when done to avoid unnecessary costs.
- KYT/KYA calls are billed separately in USD ($0.25/risk assessment, $1.25/address registration), not deducted from your Unit quota.
- The `top-traders` and `trader-gainers-losers` endpoints are expensive but valuable for smart money tracking. Cache results when possible.
- All timestamps in API responses are Unix milliseconds. K-line `resolution` values: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`.
- For historical PnL calculations, use `POST calculate-pnl` which triggers an async job. Poll the result or use the WebSocket PnL channel.
- The `security` endpoint checks for honeypot, mint authority, freeze authority, and top holder concentration — essential before any trade.
- Rate limits vary by plan. Free tier: 10 req/s. Starter: 50 req/s. Pro: 200 req/s. Enterprise: 1000 req/s.

## References

- [Complete API Endpoints](references/api-endpoints.md) — all 80+ Data API endpoints with parameters
- [Query Examples](references/query-examples.md) — 20+ real-world query patterns with MCP, REST, and SDK code
- [WebSocket Streams](references/websocket-streams.md) — all subscription channels, message formats, and examples
- [API Schema](references/api-schema.md) — supported chains, response formats, error codes, billing units
- [x402 Auth](references/x402-auth.md) — x402 pay-per-query: plans, wallet signature auth, SDK setup, per-tool pricing

## Related Skills

- [chainstream-quant](../chainstream-quant/) — DeFi operations: swap, bridge, launchpad, trading backtest
