---
name: openclaw-doctor
version: 1.0.0
description: >
  macOS Gateway 24/7 watchdog with 4-layer health checks and auto-repair.
  Monitors: L1 process alive, L2 HTTP port, L3 WebSocket communication (1006 detection),
  L4 macOS sleep prevention (caffeinate). Deploys as a LaunchAgent running every 5 minutes.
  Use when: setting up Gateway high-availability on macOS, diagnosing Gateway disconnections,
  preventing Mac sleep from killing the assistant, or automating Gateway recovery.
  NOT for: Linux/systemd setups, Windows, or non-Gateway health checks.
metadata:
  openclaw:
    requires:
      os: [macos]
      commands: [curl, pgrep, launchctl, caffeinate]
---

# OpenClaw Doctor — macOS Gateway 看门狗 v2

24/7 health watchdog for OpenClaw Gateway on macOS. Detects and auto-repairs four layers of failure.

## Why

OpenClaw Gateway is the message bridge — if it dies, the AI assistant goes silent. Common failure modes on macOS:

| Layer | Failure | Symptom |
|-------|---------|---------|
| L1 | Process crash | Complete silence |
| L2 | HTTP port stuck | Complete silence |
| L3 | WebSocket 1006 disconnect | Process alive, HTTP OK, but **messages don't arrive** (sneakiest!) |
| L4 | Mac sleep/hibernate | All connections die after lid close or idle timeout |

## Architecture

```
LaunchAgent (every 5 min)
  → L1: pgrep + launchctl (process alive?)
  → L2: curl HTTP probe (port responding?)
  → L3: Log scan for WS 1006 errors (communication healthy?)
  → L4: caffeinate keepalive (prevent sleep)
  → Auto-repair with minimum intervention principle
```

### Repair Strategy (escalating)

| Failure | Action | Rationale |
|---------|--------|-----------|
| Process down | `openclaw doctor --repair` → restart Gateway | Process crashed |
| HTTP unreachable | Restart Gateway | Port stuck |
| WS frequent disconnect | Restart Node first → then full restart | WS layer issue, Node restart usually sufficient |
| Post-sleep recovery | Gateway + Node dual restart | All connections need rebuild |

## Setup

### 1. Copy the script

```bash
cp scripts/doctor.sh ~/.openclaw/doctor.sh
chmod +x ~/.openclaw/doctor.sh
```

### 2. Configure (optional)

Environment variables for customization:

```bash
# In ~/.bashrc or ~/.zshrc (if non-default)
export OPENCLAW_DOCTOR_GATEWAY_URL="http://127.0.0.1:18789"  # default
export OPENCLAW_DOCTOR_SERVICE_NAME="ai.openclaw.gateway"     # default
export OPENCLAW_DOCTOR_NODE_SERVICE="ai.openclaw.node"        # default
```

### 3. Install LaunchAgent

Edit `references/ai.openclaw.doctor.plist` — replace `REPLACE_WITH_HOME` with your actual home directory path (e.g. `/Users/yourname`).

```bash
# Copy and customize the plist
cp references/ai.openclaw.doctor.plist ~/Library/LaunchAgents/ai.openclaw.doctor.plist
sed -i '' "s|REPLACE_WITH_HOME|$HOME|g" ~/Library/LaunchAgents/ai.openclaw.doctor.plist

# Load the service
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.doctor.plist
```

### 4. Verify

```bash
# Manual test run
bash ~/.openclaw/doctor.sh

# Check logs
tail -10 ~/.openclaw/logs/doctor.log

# Confirm caffeinate is running
pgrep -la caffeinate

# Confirm LaunchAgent is loaded
launchctl list | grep doctor
```

## Logs

Location: `~/.openclaw/logs/doctor.log`

| Prefix | Meaning |
|--------|---------|
| HEARTBEAT | Periodic health confirmation (hourly) |
| ALERT | Anomaly detected |
| DIAGNOSIS | Fault classification |
| ACTION | Repair in progress |
| RESOLVED | Fault repaired |
| CRITICAL | All repair attempts failed |
| INFO | General info (e.g. caffeinate started) |

Auto-rotates at 5MB (keeps last 1000 lines).

## Troubleshooting

**Process alive + HTTP OK but messages don't arrive?**
→ WS disconnect. Check: `grep "1006" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | tail -10`

**Disconnects every night?**
→ Mac sleep. Verify caffeinate: `pgrep -la caffeinate`

**Doctor itself not running?**
→ Check LaunchAgent: `launchctl list | grep doctor`. Reload if missing.

**Temporarily disable:**
```bash
launchctl bootout gui/$(id -u)/ai.openclaw.doctor
```

## Files

- `scripts/doctor.sh` — Main watchdog script
- `references/ai.openclaw.doctor.plist` — LaunchAgent template

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-03-07 | Initial: process check + HTTP probe + Gateway restart |
| v2 | 2026-03-23 | WS health check + Mac sleep prevention + layered repair + Node restart |
