# crypto-pfolio-alert

Monitor crypto wallet balances and set price alerts for tokens you hold.

## Usage

```
Monitor wallet [ADDRESS] on [NETWORK] for incoming/outgoing tx
Set alert: notify me when [TOKEN] on [NETWORK] crosses [PRICE] USD
Show my portfolio across [NETWORK1], [NETWORK2]
```

## Supported Networks

- Ethereum (ETH)
- Polygon (MATIC)
- BSC (BNB/BEP20)
- Arbitrum (ARB)
- Optimism (OP)
- Base (BASE)
- Scroll (SCROLL)
- zkSync (ZKSYNC)
- Linea (LINEA)
- Gnosis (GNO)
- Avalanche (AVAX)
- Fantom (FTM)

## Configuration

No API key needed — uses free public endpoints:
- Blockscout APIs (no key required)
- CoinGecko API (free tier)

## Features

- **Balance check**: Query native + ERC20 token balances for any wallet
- **Transaction history**: Last 10 txs with timestamp, amount, direction
- **Price alerts**: Monitor token price vs USD threshold, notify when crossed
- **Multi-chain view**: Aggregate portfolio across multiple networks
- **Alert methods**: Log to console, write to file, or notify via configured channel

## Alerts Storage

Alerts are stored in `~/.openclaw/crypto-alerts.json` and checked periodically.

## Notes

- Rate limit: ~100 calls/day on free tier
- Large portfolios may take a few seconds to fetch
- Some networks have inconsistent RPC — fallback to Blockscout
