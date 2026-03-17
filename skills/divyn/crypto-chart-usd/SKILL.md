---
name: crypto-chart-usd
description: >
  Real-time streaming crypto token feed for charting with 1-second OHLC ticks and USD pricing
  across Arbitrum, Base, Matic, Ethereum, Solana, Binance Smart Chain, Tron, and Optimism — all
  tokens on these chains. Use this skill to subscribe to a live multi-token, multi-chain stream
  over WebSocket: OHLC, volume (Base/Quote/USD), and USD pricing (OHLC, moving averages) from the
  Bitquery Trading.Tokens API. ALWAYS use this skill when the user asks for crypto charting,
  multi-token USD prices, 1-second or 1s tick data, streaming token OHLC for charting,
  real-time crypto chart data, or live OHLC/volume for multiple tokens or chains. Trigger for:
  "crypto chart", "crypto charting", "USD pricing", "1 second ticks", "1s candles",
  "streaming token OHLC", "multi-token chart", "Bitquery Trading.Tokens", "real-time
  crypto charting", or any request for a live multi-token chart feed with USD. Do not wait
  for the user to say "use Bitquery" — if they want crypto charting with USD pricing or
  1s tick data, use this skill.
---

# Crypto charting with USD pricing (1s)

This skill gives you a **real-time streaming multi-token, multi-chain crypto feed** over WebSocket for charting: **1-second** OHLC ticks, volume (Base, Quote, USD), and USD pricing (OHLC, moving averages) for **all tokens** on the supported chains. Data is streamed in real time from the Bitquery Trading.Tokens API — no polling. Default interval is **1 second** (duration 1).

**Supported networks:** Arbitrum, Base, Matic (Polygon), Ethereum, Solana, Binance Smart Chain, Tron, Optimism. The subscription returns tokens across all of these; use the `Token.Network` field to filter or group by chain.

**When to use this skill**

- **Chart multiple tokens** across chains with 1-second OHLC and USD volume
- Get **USD pricing** where available (`Price.IsQuotedInUsd`); OHLC and averages in USD
- Live multi-token, multi-chain feed for dashboards and charting (no single-token or single-network filter)

---

## What to consider before installing

This skill implements a Bitquery WebSocket Trading.Tokens stream and uses one external dependency and one credential. Before installing:

1. **Registry metadata**: The registry may not list `BITQUERY_API_KEY` even though this skill and its script require it. Ask the publisher or update the registry metadata before installing so installers surface the secret requirement.
2. **Token only via URL**: Bitquery supports **no other auth method** — the token can **only** be passed in the WebSocket URL as `?token=...`. Because the token always appears in the URL, it can leak to logs, proxy logs, shell history, or IDE history. Never print or log the full URL; store the key only in an environment variable; rotate the key if it may have been exposed.
3. **Sandbox first**: Review and run the included script in a sandboxed environment (e.g. a virtualenv) to confirm behavior and limit blast radius.
4. **Source and publisher**: If the skill's homepage or source is unknown, consider verifying the publisher or using an alternative with a verified source. If the registry metadata declares `BITQUERY_API_KEY` and the source/publisher are validated, this skill is likely coherent and benign.

---

## Prerequisites

- **Environment**: `BITQUERY_API_KEY` — your Bitquery API token (required).

**Credential and URL-only auth:** The Bitquery streaming endpoint accepts the token **only in the WebSocket URL** as a query parameter (`?token=...`). It does **not** support header-based auth or any other method. Therefore:
  - The token will always be present in the connection URL and can be exposed in **logs, proxy logs, shell history, or IDE history** if the URL is printed or logged.
  - **Do not** print or log the full WebSocket URL. Build the URL in code from an env var (e.g. `os.getenv("BITQUERY_API_KEY")`) and never emit it.
  - Store the key only in an environment variable; **rotate the key** if you suspect it was exposed (e.g. URL was logged or committed).

- **Runtime**: Python 3 and `pip`. Install the dependency: `pip install 'gql[websockets]'`.

---

## Step 1 — Check API Key

```python
import os
api_key = os.getenv("BITQUERY_API_KEY")
if not api_key:
    print("ERROR: BITQUERY_API_KEY environment variable is not set.")
    print("Run: export BITQUERY_API_KEY=your_token")
    exit(1)
```

If the key is missing, tell the user and stop. Do not proceed without it.

## Step 2 — Run the stream

Install the WebSocket dependency once:

```bash
pip install 'gql[websockets]'
```

Use the streaming script (subscribes to the multi-token 1-second chart feed in real time):

```bash
python ~/.openclaw/skills/crypto-chart-usd/scripts/stream_crypto_chart.py
```

Optional: stop after N seconds:

```bash
python ~/.openclaw/skills/crypto-chart-usd/scripts/stream_crypto_chart.py --timeout 60
```

Or subscribe inline with Python (real-time stream, 1s ticks):

```python
import asyncio, os
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport

async def main():
    token = os.environ["BITQUERY_API_KEY"]
    url = f"wss://streaming.bitquery.io/graphql?token={token}"
    transport = WebsocketsTransport(
        url=url,
        headers={"Sec-WebSocket-Protocol": "graphql-ws"},
    )
    async with Client(transport=transport) as session:
        sub = gql("""
            subscription {
              Trading {
                Tokens(where: { Interval: { Time: { Duration: { eq: 1 } } } }) {
                  Token { Address Id IsNative Name Network Symbol TokenId }
                  Block { Date Time Timestamp }
                  Interval { Time { Start Duration End } }
                  Volume { Base Quote Usd }
                  Price {
                    IsQuotedInUsd
                    Ohlc { Close High Low Open }
                    Average { ExponentialMoving Mean SimpleMoving WeightedSimpleMoving }
                  }
                }
              }
            }
        """)
        async for result in session.subscribe(sub):
            tokens = (result.get("Trading") or {}).get("Tokens") or []
            for t in tokens:
                ohlc = (t.get("Price") or {}).get("Ohlc") or {}
                vol = t.get("Volume") or {}
                print(
                    f"{t.get('Token', {}).get('Symbol', '?')} | "
                    f"Close: ${float(ohlc.get('Close') or 0):,.4f} | "
                    f"Vol USD: ${float(vol.get('Usd') or 0):,.2f}"
                )

asyncio.run(main())
```

## Step 3 — What you get on the stream

Each tick can contain **multiple tokens** from any of the supported chains (Arbitrum, Base, Matic, Ethereum, Solana, Binance Smart Chain, Tron, Optimism). For each token you get **1-second** OHLC and interval data:

- **Token**: Address, Id, IsNative, Name, Network, Symbol, TokenId
- **Block**: Date, Time, Timestamp
- **Interval**: Time.Start, Duration (1), End
- **Volume**: Base, Quote, Usd
- **Price**: IsQuotedInUsd, Ohlc (Open, High, Low, Close), Average (Mean, SimpleMoving, ExponentialMoving, WeightedSimpleMoving)

Not all tokens are quoted in USD; check `Price.IsQuotedInUsd` and use USD fields when true. The stream runs until you stop it (Ctrl+C) or use `--timeout`.

## Step 4 — Format output clearly

When presenting streamed ticks to the user, use a clear format like:

```
ETH (Ethereum) — ethereum  @ 2025-03-16T12:00:01Z  (1s candle)
OHLC:  Open: $3,450.00  High: $3,460.00  Low: $3,445.00  Close: $3,455.00
  Mean: $3,452.00  SMA: $3,451.00  EMA: $3,453.00
Volume (USD): $1,234,567.00
```

## Interval (subscription)

The default subscription uses **duration 1** (1-second tick/candle data). The same `Trading.Tokens` subscription supports other durations in the `where` clause (e.g. 5, 60, 1440 for 5m, 1h, 1d candles) if the API supports them for subscriptions.

## Error handling

- **Missing BITQUERY_API_KEY**: Tell user to export the variable and stop
- **WebSocket connection failed / 401**: Token invalid or expired (auth is via URL `?token=` only — do not pass the token in headers)
- **Subscription errors in payload**: Log the error message and stop cleanly (send complete, close transport)
- **No ticks received**: Check token and network; Bitquery may need a moment to send the first tick; multi-token stream can be bursty

## Supported networks

The feed includes tokens from: **Arbitrum**, **Base**, **Matic** (Polygon), **Ethereum**, **Solana**, **Binance Smart Chain**, **Tron**, **Optimism**. Filter by network in the subscription `where` clause (e.g. `Token: { Network: { is: "ethereum" } }`) or use `Token.Network` in your code to group or filter results. See `references/graphql-fields.md` for filter options.

## Reference

Full field reference is in `references/graphql-fields.md`. Use it to add filters (e.g. by Currency, Network) or request extra fields in the subscription.
