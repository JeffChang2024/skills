---
name: graph-polymarket-mcp
description: "Ask any Polymarket question — get live odds, trader P&L, leaderboards, open interest, and resolution data from 8 subgraphs. 20 tools, no auth needed to start."
version: 1.3.0
homepage: https://github.com/PaulieB14/graph-polymarket-mcp
metadata:
  clawdbot:
    emoji: "🔮"
    requires:
      bins: ["node"]
      env: ["GRAPH_API_KEY"]
    primaryEnv: "GRAPH_API_KEY"
---

# Graph Polymarket MCP

Ask any question about Polymarket prediction markets. Get back live data from 8 specialized subgraphs — odds, volumes, trader performance, open interest, resolution status.

## Try it

- `"What are the hottest Polymarket markets right now?"`
- `"Show me the top 10 traders by profit"`
- `"Open interest on the US election markets"`
- `"Has the Fed rate decision market been disputed?"`
- `"What's trader 0xabc's P&L and win rate?"`
- `"Daily volume trends for the last 30 days"`

## 20 tools available

| Tool | What it does |
|------|-------------|
| `get_global_stats` | Platform totals — markets, volume, fees, trades |
| `get_market_data` | Market outcomes, odds, resolution status |
| `get_top_traders` | Leaderboard by PnL, win rate, volume |
| `get_account_pnl` | Any trader's P&L, win rate, profit factor, max drawdown |
| `get_trader_profile` | Full profile — first seen, CTF events, USDC flows |
| `get_daily_stats` | Daily volume, fees, trader counts |
| `get_market_positions` | Top holders for an outcome token with P&L |
| `get_user_positions` | A user's current token positions |
| `get_market_open_interest` | Top markets by USDC locked |
| `get_oi_history` | Hourly OI snapshots for a market |
| `get_global_open_interest` | Total platform-wide OI |
| `get_orderbook_trades` | Recent fills with maker/taker filtering |
| `get_recent_activity` | Splits, merges, redemptions |
| `get_market_resolution` | UMA oracle resolution status |
| `get_disputed_markets` | Markets disputed during resolution |
| `get_market_revisions` | Moderator interventions |
| `get_trader_usdc_flows` | USDC deposit/withdrawal history |
| `list_subgraphs` | All 8 Polymarket subgraphs |
| `get_subgraph_schema` | Full GraphQL schema for any subgraph |
| `query_subgraph` | Custom GraphQL query against any subgraph |

## Install

```bash
GRAPH_API_KEY=your-key npx graph-polymarket-mcp
```

Get a free API key at [The Graph Studio](https://thegraph.com/studio/) (free tier: 100K queries/month).

## External Endpoints

| Endpoint | Data sent | Purpose |
|----------|-----------|---------|
| `gateway.thegraph.com` | GraphQL queries with your API key | Queries 8 Polymarket subgraphs |

No other endpoints are contacted. No data is stored locally.

## Security & Privacy

- **Runs locally** via `npx` — no remote server needed
- **Your API key stays local** — only sent to The Graph Gateway
- **No persistent storage** — no database, no local files written
- **Open source** — full code at [github.com/PaulieB14/graph-polymarket-mcp](https://github.com/PaulieB14/graph-polymarket-mcp)

## Model Invocation Note

This skill may be invoked autonomously by your AI agent when it detects a prediction market question. Disable the skill to opt out.

## Trust Statement

By using this skill, GraphQL queries are sent to `gateway.thegraph.com` using your API key. Only install if you trust The Graph's decentralized network with your query data.

## Links

- GitHub: https://github.com/PaulieB14/graph-polymarket-mcp
- npm: https://www.npmjs.com/package/graph-polymarket-mcp
- The Graph: https://thegraph.com
