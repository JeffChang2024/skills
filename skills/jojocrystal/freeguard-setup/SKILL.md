---
name: freeguard-setup
description: Use when a user wants to set up, use, or troubleshoot FreeGuard VPN - guides non-technical users through installation, login, connection, and daily usage with friendly step-by-step instructions
---

# FreeGuard VPN Setup Guide

An agent skill for guiding users through FreeGuard VPN setup and daily usage. Designed for non-technical users — never expose config files, YAML, ports, runtime internals, or code.

## Tone

- Friendly, patient, encouraging
- Use simple language: "open your terminal" not "execute in shell"
- Celebrate progress: "Great, you're logged in!"
- If something fails, reassure: "No worries, let's try another way"
- Never say "mihomo", "YAML", "runtime config", "API port", "proxy port", "GeoIP rule-provider" — these are internal implementation details

## Agent Flow

```dot
digraph setup {
    rankdir=TB;
    start [label="User wants VPN" shape=doublecircle];
    installed [label="Installed?" shape=diamond];
    install [label="Guide installation" shape=box];
    hassub [label="Has subscription?" shape=diamond];
    subscribe [label="Guide purchase" shape=box];
    loggedin [label="Logged in?" shape=diamond];
    login [label="Guide login" shape=box];
    region [label="Ask region\n& apply settings" shape=box];
    auth [label="Guide admin\npermission" shape=box];
    canroot [label="Can grant\nadmin?" shape=diamond];
    sudoconnect [label="sudo connect\n(full protection)" shape=box];
    normalconnect [label="connect\n(standard mode)" shape=box];
    verify [label="Verify & teach\ndaily usage" shape=box];
    done [label="All set!" shape=doublecircle];

    start -> installed;
    installed -> install [label="no"];
    installed -> hassub [label="yes"];
    install -> hassub;
    hassub -> subscribe [label="no"];
    hassub -> loggedin [label="yes"];
    subscribe -> loggedin;
    loggedin -> login [label="no"];
    loggedin -> region [label="yes"];
    login -> region;
    region -> auth;
    auth -> canroot;
    canroot -> sudoconnect [label="yes"];
    canroot -> normalconnect [label="no"];
    sudoconnect -> verify;
    normalconnect -> verify;
    verify -> done;
}
```

## Step 1: Check Environment

Run silently (don't show commands to user):

```bash
freeguard doctor --json
```

From the result, determine:
- **Not installed** → Go to Installation
- **Installed, no subscription** (subscription check warns "no subscription URL found") → Go to Subscribe
- **Installed, has subscription but not logged in** → Go to Login
- **Logged in with subscription** → Go to Region & Connect

Tell the user the current state in friendly terms:
- "Looks like FreeGuard isn't installed yet. Let me help you set it up!"
- "FreeGuard is installed! Now we need to get you a subscription."
- "You have a subscription but aren't logged in yet. Let's fix that."
- "You're already logged in! Let's get you connected."

## Step 2: Installation

Ask the user's operating system if unclear, then provide ONE command:

- **macOS / Linux**: `curl -fsSL https://downloadcli.freeguardvpn.com/cli/install.sh | sh`
- **Windows (PowerShell)**: `irm https://downloadcli.freeguardvpn.com/cli/install.ps1 | iex`
- **macOS with Homebrew**: `brew install planetlinkinc/tap/freeguardvpn`

Tell the user:
> "Copy and paste this into your terminal, then tell me when it's done."

After they confirm, run `freeguard doctor --json` to verify.

## Step 3: Subscribe (if no subscription)

If the user doesn't have a subscription yet, first check available plans silently:

```bash
freeguard subscribe list --json
```

Then present the options in friendly terms:

> "To use FreeGuard VPN, you'll need a subscription. Here are the plans available:
>
> | Plan | Price |
> |------|-------|
> | Weekly | $3.99/week |
> | Monthly | $7.99/month |
> | Yearly | $49.99/year (best value) |
>
> Which plan works for you?"

After the user picks a plan, ask for their email:

> "Great choice! What email address should we use for your account?"

Then create the subscription:

```bash
freeguard subscribe create --plan <price_id> --email <email> --json
```

Map user's choice to price_id from the `subscribe list` response. The command will return a checkout URL.

Tell the user:

> "I've opened a payment page for you. Please complete the payment there, and let me know when you're done."

After they confirm payment, proceed to Login — the email they just used is the same one they'll log in with.

## Step 4: Login

Ask the user how they'd like to log in:

> "How would you like to log in?
> 1. **Email** — I'll send you a verification code
> 2. **Subscription link** — if you have a Clash subscription URL
> 3. **Access token** — if you received one after purchase"

If the user just completed a purchase in Step 3, skip this question and go straight to Email Login using the email they already provided.

### Email Login (most common)

1. Ask: "What's your email address?"
2. Run: `freeguard login --email <email> --send-code --json`
3. Tell user: "A verification code has been sent to your email. Please check your inbox (and spam folder) and tell me the 6-digit code."
4. User provides code
5. Run: `freeguard login --email <email> --code <code> --json`
6. On success: "Great, you're logged in!"
7. On failure: "That code didn't work. Want me to send a new one?"

### URL Login

1. Ask: "Please paste your subscription URL"
2. Run: `freeguard login --url <url> --json`
3. On success: "Logged in successfully!"

### Token Login

1. Ask: "Please paste your access token"
2. Run: `freeguard login --token <token> --json`
3. On success: "Logged in successfully!"

## Step 5: Region & Settings

Ask the user where they are:

> "One more thing — where are you located? This helps optimize your connection for the best speed.
>
> For example: China, Japan, US, Korea, Russia, etc."

Map their answer to a region code:

| User says | Region code |
|-----------|-------------|
| China / mainland / CN | CN |
| US / America / United States | US |
| Japan / JP | JP |
| Korea / KR / South Korea | KR |
| Russia / RU | RU |
| Iran / IR | IR |
| Indonesia / ID | ID |
| UAE / Dubai / AE | AE |
| Other / not listed above | (skip GeoIP) |

Then apply settings silently (run all, don't show commands):

```bash
freeguard config set proxy.tun true --json
freeguard config set proxy.allow_lan true --json
freeguard config set dns.enable true --json
```

Only if user's region matches one of the 8 supported codes above:
```bash
freeguard config set geoip_region <CODE> --json
```
If user's region is NOT in the list, do NOT set geoip_region. Do not mention this to the user — just skip it silently.

Tell the user:
> "I've optimized your settings for the best experience. VPN will protect all apps on this computer (including terminal, remote desktop, etc.) and devices on your local network can share the connection too."

## Step 6: Authorize & Connect

**TUN mode requires administrator/root privileges.** Without it, only apps that respect proxy settings will go through VPN — terminal commands, remote desktop, and many other apps will bypass VPN entirely. So we MUST guide the user to grant permission.

Tell the user:

**macOS / Linux:**
> "To protect all your apps (not just the browser), I need to run with admin privileges. Please enter your password when prompted."

Then connect with sudo:
```bash
sudo freeguard connect --json
```

**Windows:**
> "To protect all your apps, we need to run as Administrator. Please right-click your terminal and select 'Run as Administrator', then tell me when you're ready."

After they confirm, run:
```bash
freeguard connect --json
```

**If user refuses or cannot provide admin access:**
> "No problem! I'll connect in standard mode. Your browser and most apps will still be protected, but some apps like terminal commands may not go through VPN."

Then connect without sudo:
```bash
freeguard connect --json
```

While waiting, tell the user: "Connecting to VPN..."

On success, check stderr for TUN errors:
- If TUN succeeded (no error): "You're connected! All apps on this computer are now protected."
- If TUN failed but proxy works: "You're connected! Most apps are protected. For full system-wide protection, you'll need admin privileges next time."

On failure, check the error:
- **auth_required**: "It seems your login session expired. Let's log in again."
- **core_download_failed**: "There was a download issue. Please check your internet and try again."
- Other: "Something went wrong. Let me run a diagnostic..." → run `freeguard doctor --json`

## Step 7: Verify

Run silently:
```bash
freeguard status --json
```

If connected, tell the user:
> "Everything looks good! Here's what you need to know:
>
> - **Check status**: just ask me 'am I connected?'
> - **Disconnect**: ask me to 'disconnect' or run `freeguard disconnect`
> - **Reconnect**: ask me to 'connect' or run `freeguard connect`
>
> Enjoy your secure internet!"

## Daily Usage Commands

When the user asks about ongoing usage, guide them with these (run commands silently, report results in friendly terms):

| User says | What to do |
|-----------|------------|
| "Am I connected?" / "Status" | `freeguard status --json` → "Yes, you're connected" or "No, you're disconnected" |
| "Connect" / "Turn on VPN" | `freeguard connect --json` → "Connected!" |
| "Disconnect" / "Turn off VPN" | `freeguard disconnect --json` → "Disconnected" |
| "Show nodes" / "Server list" | `freeguard node list --json` → summarize available countries/count |
| "Change country to X" | `freeguard config set preferred_country X --json` then reconnect |
| "Speed test" / "Test connection" | `freeguard node test --all --json` → show top 5 fastest |
| "Check my account" | `freeguard doctor --json` → summarize account status |
| "Something's not working" | `freeguard doctor --json` → diagnose and suggest fixes |
| "Log out" | `freeguard disconnect --json` then `freeguard logout --json` |
| "Share VPN with my phone/device" | Explain: "Your VPN is already sharing! On your other device, set the proxy to this computer's IP address, port 7890" |

## Troubleshooting

When things go wrong, always start with `freeguard doctor --json` and interpret the results:

| Check fails | What to tell user |
|-------------|-------------------|
| Network | "Your internet connection seems to be down. Please check your WiFi or cable." |
| Credentials | "Your login session has expired. Let's log in again." |
| Subscription | "It looks like you need an active subscription. Would you like me to help you pick a plan?" → Go to Step 3 |
| Port in use | "Another app is using the same port. Let me change it." → `freeguard config set proxy.mixed_port 17890 --json` |
| Core Binary | "A component needs to be downloaded. Let me try connecting — it should download automatically." |

## What NOT to Say

Never mention or expose to the user:
- File paths (`~/.freeguard/`, `config.yaml`, `runtime.yaml`)
- Technical terms (mihomo, proxy port, API controller, rule-provider, fake-ip, gvisor)
- YAML configuration contents
- Internal port numbers (9090 API port)
- Enhance engine, runtime config pipeline
- GeoIP MRS files, CDN URLs, rule-set internals
- DNS fallback filters, nameservers configuration

Always translate technical concepts to user-friendly language:
- "mixed port 7890" → "proxy settings"
- "TUN mode" → "system-wide VPN protection"
- "allow LAN" → "share VPN with other devices on your network"
- "GeoIP region CN" → "optimized for your location in China"
- "fake-ip DNS" → "fast DNS"
- "rule-provider" → "smart routing"
