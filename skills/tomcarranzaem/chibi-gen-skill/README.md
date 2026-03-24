# Chibi Character Generator

Generate adorable chibi character images from a text description using AI. Powered by the Neta talesofai API, this skill returns a direct image URL instantly — ready to use in any workflow.

---

## Install

**Via npx skills:**
```bash
npx skills add TomCarranzaem/chibi-gen-skill
```

**Via ClawHub:**
```bash
clawhub install chibi-gen-skill
```

---

## Usage

```bash
# Generate with default chibi prompt
node chibigen.js

# Generate with a custom description
node chibigen.js "a chibi wizard with purple robes and a glowing staff"

# Specify size
node chibigen.js "chibi knight in shining armor" --size portrait

# Use a reference image (picture_uuid from a previous generation)
node chibigen.js "same character, different pose" --ref <picture_uuid>

# Pass token directly
node chibigen.js "chibi cat girl" --token YOUR_NETA_TOKEN
```

The script prints a single image URL to stdout on success.

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `square`, `portrait`, `landscape`, `tall` | `square` | Output image dimensions |
| `--token` | string | — | Neta API token (overrides env/file lookup) |
| `--ref` | picture_uuid | — | Reference a previous image for style inheritance |

### Size dimensions

| Name | Width | Height |
|------|-------|--------|
| `square` | 1024 | 1024 |
| `portrait` | 832 | 1216 |
| `landscape` | 1216 | 832 |
| `tall` | 704 | 1408 |

---

## About Neta

[Neta](https://www.neta.art/) (by TalesofAI) is an AI image and video generation platform with a powerful open API. It uses a **credit-based system (AP — Action Points)** where each image generation costs a small number of credits. Subscriptions are available for heavier usage.

### Register & Get Token

| Region | Sign up | Get API token |
|--------|---------|---------------|
| Global | [neta.art](https://www.neta.art/) | [neta.art/open](https://www.neta.art/open/) |
| China  | [nieta.art](https://app.nieta.art/) | [nieta.art/security](https://app.nieta.art/security) |

New accounts receive free credits to get started. No credit card required to try.

### Pricing

Neta uses a pay-per-generation credit model. View current plans on the [pricing page](https://www.neta.art/pricing).

- **Free tier:** limited credits on signup — enough to test
- **Subscription:** monthly AP allowance via Stripe
- **Credit packs:** one-time top-up as needed

### Set up your token

```bash
# Step 1 — get your token:
#   Global: https://www.neta.art/open/
#   China:  https://app.nieta.art/security

# Step 2 — set it
export NETA_TOKEN=your_token_here

# Step 3 — run
node chibigen.js "your prompt"
```

Or pass it inline:
```bash
node chibigen.js "your prompt" --token your_token_here
```

> **API endpoint:** defaults to `api.talesofai.cn` (works with all token types).  
> Override with `NETA_API_URL=https://api.talesofai.cn` if using a global Open Platform token.


---

## Default Prompt

When no prompt is provided, the skill uses:

> full body chibi character, big head small body proportions, adorable kawaii style, expressive large eyes, pastel color palette, clean line art, white background, high quality anime illustration

---

Built with [Claude Code](https://claude.ai/claude-code) · Powered by [Neta](https://www.neta.art/) · [API Docs](https://www.neta.art/open/)