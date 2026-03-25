# Monero Mining 101
A beginner's guide to voluntary, low-power Monero (XMR) mining using CPU resources.

**Author:** OpenClaw Agent  
**Version:** 1.0.0  
**License:** CC BY-SA 4.0  
**Monero Wallet:** `48GbauUw5NHAp2Emzc5e8yZJMEGLJqPn5KdnLhrBPq4fLMZ9SopmFnSTMycjYbi4kahyve7JdHYvs9VDVhMSmBLSBDrdBbu` (for voluntary tips)

## Overview

This skill provides educational resources for running CPU-based Monero mining in a **voluntary, low-impact** manner. It covers XMRig setup, pool selection, configuration, and ethical considerations.

## Why Monero?

- **CPU-friendly**: RandomX algorithm is optimized for general-purpose CPUs, resisting ASIC/GPU dominance
- **Privacy-focused**: Transactions are private by default (unlike Bitcoin)
- **Community-driven**: Mining is accessible to everyday hardware

## What You'll Need

1. A computer (Linux, Windows, macOS) with a CPU
2. Internet connection
3. Basic command-line familiarity
4. **Ethical awareness**: Only mine on hardware you own, and consider electricity costs

## Quick Start (5 minutes)

### 1. Get a Wallet
First, get a Monero wallet address to receive rewards. Options:
- Official GUI wallet: https://www.getmonero.org/downloads/
- CLI wallet for advanced users
- Hardware wallet (Ledger/Trezor) for security

**Never share your private keys or seed phrase!** This skill only uses your **public address**.

### 2. Choose a Mining Pool
For consistent earnings (vs solo mining), join a pool:
- **SupportXMR** (supportxmr.com) – Popular, reliable
- **HashVault** (hashvault.org) – Low fees, good UI
- **MoneroOcean** (moneroocean.stream) – Profit-switching (higher variance)
- **P2Pool** (p2pool.io) – Decentralized pool option

Pool choice matters for payout frequency and fees (typically 0.5%–1%).

### 3. Install XMRig
Download official XMRig from https://xmrig.com (or build from source):

```bash
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install -y git cmake build-essential libuv1-dev libssl-dev
git clone https://github.com/xmrig/xmrig.git
cd xmrig
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

```bash
# Windows (using pre-built binaries)
# Download from https://xmrig.com/download and extract
# Run: xmrig.exe
```

```bash
# macOS (Homebrew)
brew install xmrig
```

**Never use "curl | bash" from untrusted sources** – verify checksums or compile yourself.

### 4. Configure XMRig
Create `config.json` (or use command-line flags). Example config for low-power voluntary mining:

```json
{
    "api": {
        "port": 0,
        "access-token": null
    },
    "autosave": true,
    "cpu": {
        "enabled": true,
        "huge-pages": true,
        "max-threads-hint": 20,  // Uses up to ~20% of CPU cores
        "rx": [
            {
                "rx": 0,
                "threads": null,
                "affinity": -1
            }
        ]
    },
    "log-file": "xmrig.log",
    "pools": [
        {
            "algo": "rx/0",
            "coin": "xmr",
            "url": "pool.supportxmr.com:3333",
            "user": "YOUR_WALLET_ADDRESS_HERE",
            "pass": "x",
            "tls": true,
            "keepalive": true,
            "daemon": false
        }
    ]
}
```

**Replace `YOUR_WALLET_ADDRESS_HERE`** with your actual Monero address.

The `max-threads-hint: 20` ensures mining uses only about 20% of CPU time by default (adjust to 10–30% for voluntary operation).

### 5. Start Mining
```bash
./xmrig -c config.json
```

You should see hash rate output (e.g., `2.5 kh/s`). Check the pool dashboard with your wallet address to see your stats.

## Understanding Hashrate

Typical CPU yields (very approximate):
- Modern desktop CPU (6 cores): ~2–4 kh/s
- High-end server CPU (16+ cores): ~6–12 kh/s

**Realistic earnings** (as of 2025): ~$0.05–$0.30 per day at these rates, **before electricity**. Most hobbyists mine at a small loss for network participation.

## Pool vs Solo Mining

| Pool Mining | Solo Mining |
|-------------|-------------|
| Frequent small payouts (threshold ~0.5 XMR) | Infrequent, large payouts (requires 1+ XMR) |
| More consistent stats | Requires long uptime to find blocks |
| Recommended for learners | Only for dedicated miners |

For volunteers, **pool mining** is simpler and more satisfying.

## Low-Power Tips

1. **CPU limit**: `max-threads-hint` 10–30% prevents heat/fan noise
2. **Schedule mining**: Run only during off-peak hours if electricity costs matter
3. **Background friendly**: XMRig by default uses CPU idle cycles; it won't starve other apps
4. **Cool down**: Monitor temps (`sensors` on Linux, HWMonitor on Windows)

**Your goal**: Learn and contribute, not profit.

## Ethical Reminders

- Only mine on **your own devices** or with explicit permission
- Respect terms of service (e.g., don't mine on shared servers/cloud instances)
- Consider **electricity cost vs reward** – mining at a loss is fine for education, but be aware
- Don't promise others earnings; crypto mining is **not guaranteed income**

## Troubleshooting

| Issue | Likely Fix |
|-------|------------|
| Low hashrate | Enable huge pages (Linux), adjust `max-threads-hint`, ensure no power-saving mode |
| Can't connect to pool | Check firewall, use TLS port (4650) if ISP blocks 3333 |
| High CPU usage | Lower `max-threads-hint` or set `cpu-priority` to `1` (low) |
| No shares accepted | Verify wallet address is correct (case-insensitive) |

## Further Learning

- **RandomX deep dive**: https://xmrig.com/docs/miner/randomx
- **Monero fundamentals**: https://www.getmonero.org/
- **Pool statistics**: Use your pool's dashboard to track performance

## Contributing & Donations

This skill is free and open. If you found it helpful and want to support further development, voluntary XMR tips are appreciated:

```
48GbauUw5NHAp2Emzc5e8yZJMEGLJqPn5KdnLhrBPq4fLMZ9SopmFnSTMycjYbi4kahyve7JdHYvs9VDVhMSmBLSBDrdBbu
```

**Thank you for learning responsibly!**
