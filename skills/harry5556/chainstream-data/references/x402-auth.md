# x402 Pay-per-Query Authentication

Alternative to API Key subscription. Pay with USDC on Base or Solana — no account registration needed.

## Overview

x402 authentication has two phases:

1. **Purchase** (one-time): pay USDC to buy a quota plan via `/x402/purchase`
2. **Wallet Auth** (every request): sign a message with your wallet to prove ownership

## Phase 1: Purchase a Plan

```bash
# First call returns 402 with payment requirements
curl -X POST https://api.chainstream.io/x402/purchase \
  -H "Content-Type: application/json" \
  -d '{"plan": "nano", "network": "eip155:8453", "walletAddress": "0xYOUR_WALLET"}'

# Sign USDC payment, then retry with payment proof
curl -X POST https://api.chainstream.io/x402/purchase \
  -H "Content-Type: application/json" \
  -H "X-Payment: <base64-payment-proof>" \
  -d '{"plan": "nano", "network": "eip155:8453", "walletAddress": "0xYOUR_WALLET"}'
```

### Plans

| Plan | Price (USDC) | Quota (CU) | Duration |
|------|-------------|------------|----------|
| nano | $1.00 | 50,000 | 30 days |
| micro | $5.00 | 350,000 | 30 days |
| starter | $20.00 | 1,500,000 | 30 days |
| growth | $50.00 | 4,000,000 | 30 days |
| pro | $150.00 | 15,000,000 | 30 days |
| business | $500.00 | 55,000,000 | 30 days |

### Supported Networks

| Network | Chain ID | USDC Contract | Environment |
|---------|----------|---------------|-------------|
| Base | `eip155:8453` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Production |
| Base Sepolia | `eip155:84532` | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | Testnet |
| Solana Mainnet | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | Production |
| Solana Devnet | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` | `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU` | Testnet |

## Phase 2: Wallet Signature Auth

Every API call after purchase must include 5 wallet auth headers:

| Header | Value | Description |
|--------|-------|-------------|
| `X-Wallet-Address` | `0xAddr` or Base58 | Wallet that purchased the plan |
| `X-Wallet-Chain` | `evm` or `solana` | Chain type (NOT network ID) |
| `X-Wallet-Signature` | hex or base58 | Signature of the message |
| `X-Wallet-Timestamp` | Unix seconds | Current timestamp |
| `X-Wallet-Nonce` | unique string | Unique per request |

### Signature Message Format

```
chainstream:{chain}:{address}:{timestamp}:{nonce}
```

- **EVM**: sign with EIP-191 `personal_sign` → 65-byte hex signature (`0x` prefix)
- **Solana**: sign with ed25519 → 64-byte base58 signature
- **Timestamp window**: 300 seconds — older timestamps are rejected
- **Nonce**: must be unique per request (server enforces via Redis)

### Example (curl)

```bash
TIMESTAMP=$(date +%s)
NONCE=$(uuidgen)
MESSAGE="chainstream:evm:0xYOUR_WALLET:${TIMESTAMP}:${NONCE}"
SIGNATURE="0x..."  # EIP-191 personal_sign of MESSAGE

curl -H "X-Wallet-Address: 0xYOUR_WALLET" \
  -H "X-Wallet-Chain: evm" \
  -H "X-Wallet-Signature: ${SIGNATURE}" \
  -H "X-Wallet-Timestamp: ${TIMESTAMP}" \
  -H "X-Wallet-Nonce: ${NONCE}" \
  "https://api.chainstream.io/v2/token/search?keyword=PUMP&chain=sol"
```

## SDK with Coinbase Agent Wallet

The SDK handles both phases automatically when `walletSigner` is configured.

### TypeScript

```typescript
import { ChainStreamClient } from '@chainstream-io/sdk';
import { CdpAgentkit } from '@coinbase/agentkit';

const agentkit = await CdpAgentkit.configureWithWallet({
  cdpApiKeyName: process.env.CDP_API_KEY_ID,
  cdpApiKeyPrivateKey: process.env.CDP_API_KEY_SECRET,
  networkId: 'base-mainnet',
});
const wallet = await agentkit.getWallet();

const client = new ChainStreamClient('', {
  walletSigner: {
    getAddress: async () => (await wallet.getDefaultAddress()).getId(),
    getChain: () => 'evm',
    signPayment: async (req) => {
      const transfer = await wallet.createTransfer({
        amount: Number(req.maxAmountRequired) / 1e6,
        assetId: 'usdc',
        destination: req.payTo,
      });
      await transfer.wait();
      return transfer.getTransactionHash();
    },
    signMessage: async (msg) => wallet.signMessage(msg),
  },
});

// Both x402 purchase and per-request wallet auth happen automatically
const results = await client.token.search({ keyword: 'PUMP', chain: 'sol' });
```

### Python

```python
from chainstream import ChainStreamClient

class WalletSigner:
    def __init__(self, wallet):
        self.wallet = wallet
    def get_address(self):
        return self.wallet.get_default_address().address_id
    def get_chain(self):
        return "evm"
    def sign_payment(self, req):
        transfer = self.wallet.transfer(
            amount=int(req["maxAmountRequired"]) / 1e6,
            asset_id="usdc", destination=req["payTo"])
        transfer.wait()
        return transfer.transaction_hash
    def sign_message(self, msg):
        return self.wallet.sign_message(msg)

client = ChainStreamClient(wallet_signer=WalletSigner(wallet))
results = client.token.search(keyword="PUMP", chain="sol")
```

### Go

```go
signer := &CdpSigner{wallet: cdpWallet}
client, _ := chainstream.NewChainStreamClientWithWalletSigner(signer, nil)
// WalletSigner interface: GetAddress(), GetChain(), SignPayment(), SignMessage()
```

## Per-Tool Pricing (USDC)

| Tool | Price |
|------|-------|
| tokens/search | $0.001 |
| tokens/analyze | $0.003 |
| tokens/price_history | $0.002 |
| tokens/discover | $0.002 |
| tokens/compare | $0.005 |
| wallets/profile | $0.005 |
| wallets/activity | $0.002 |
| market/trending | $0.001 |
| dex/quote | $0.001 |
| dex/swap | $0.005 |
| kyt/assess_risk | $0.01 |
| trading/backtest | $0.05 |
| Default (unlisted) | $0.001 |
