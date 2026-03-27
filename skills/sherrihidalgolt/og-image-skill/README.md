# OG Image Generator

Generate stunning **open graph social media preview images** from a text description using AI. Get back a direct image URL instantly — no UI required.

Powered by the [Neta / talesofai](https://talesofai.cn) image generation API.

---

## Install

**Via npx skills:**
```bash
npx skills add SherriHidalgolt/og-image-skill
```

**Via ClawHub:**
```bash
clawhub install og-image-skill
```

---

## Usage

```bash
# Basic — uses the default prompt
node ogimage.js

# Custom prompt
node ogimage.js "dark tech blog banner, neon accents, minimal layout"

# Specify size
node ogimage.js "product launch card" --size square

# Use a reference image (by picture UUID)
node ogimage.js "similar style banner" --ref <picture_uuid>

# Pass token explicitly
node ogimage.js "my prompt" --token sk-xxxx
```

The script prints the image URL to stdout on success:
```
https://cdn.talesofai.cn/artifacts/....png
```

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `square`, `portrait`, `landscape`, `tall` | `landscape` | Output image dimensions |
| `--token` | string | — | API token (overrides env/file lookup) |
| `--ref` | picture UUID | — | Reference image UUID for style inheritance |

### Size dimensions

| Name | Width | Height |
|------|-------|--------|
| `square` | 1024 | 1024 |
| `portrait` | 832 | 1216 |
| `landscape` | 1216 | 832 |
| `tall` | 704 | 1408 |

---

## Token Setup

The script resolves your API token in this order:

1. `--token` CLI flag
2. `NETA_TOKEN` environment variable

**Recommended setup:**
```bash
```

Or export it in your shell profile:
```bash
export NETA_TOKEN=your_token_here
```

---

## Examples

```bash
# OG image for a blog post
node ogimage.js "technology article cover, dark gradient, bold white title text"

# Square social card
node ogimage.js "product announcement, vibrant colors, centered logo" --size square

# Tall Pinterest-style card
node ogimage.js "recipe card, warm tones, food photography style" --size tall
```

---

## Requirements

- Node.js 18+ (uses native `fetch` and top-level `await`)
- A valid `NETA_TOKEN` from [talesofai.cn](https://talesofai.cn)

## Example Output

![Generated example](https://oss.talesofai.cn/picture/ff229882-1b18-48ec-9f2d-c0d98f48f5c6.webp)
