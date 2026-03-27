---
name: html-parse
description: "HTML Parse - parse local HTML files into structured Markdown using MinerU. Preserves document hierarchy. For live web pages, use url-to-markdown (crawl) instead."
homepage: https://mineru.net
metadata: {"openclaw": {"emoji": "📄", "requires": {"bins": ["mineru-open-api"], "env": ["MINERU_TOKEN"]}, "primaryEnv": "MINERU_TOKEN", "install": [{"id": "npm", "kind": "node", "package": "mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via npm"}, {"id": "go", "kind": "go", "package": "github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via go install", "os": ["darwin", "linux"]}]}}
---

# HTML Parse

Parse local HTML files into structured Markdown using MinerU. Preserves document hierarchy. For live web pages, use `mineru-open-api crawl`.

## Install

```bash
npm install -g mineru-open-api
# or via Go (macOS/Linux):
go install github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api@latest
```

## Quick Start

```bash
# Parse a local HTML file (requires token)
mineru-open-api extract page.html -o ./out/

# Parse a remote HTML URL (requires token)
mineru-open-api extract https://example.com/page.html -o ./out/

# Parse a live web page (requires token)
mineru-open-api crawl https://example.com/article -o ./out/
```

## Authentication

Token required:

```bash
mineru-open-api auth             # Interactive token setup
export MINERU_TOKEN="your-token" # Or via environment variable
```

Create token at: https://mineru.net/apiManage/token

## Capabilities

- Supported input: local .html file or remote HTML URL
- HTML requires `extract` or `crawl` (token required)
- HTML is NOT supported by `flash-extract`
- Language hint with `--language` (default: `ch`, use `en` for English)

## Notes

- HTML is NOT supported by `flash-extract` — use `extract` or `crawl`
- For live web pages with dynamic content, use `crawl` instead of `extract`
- Output goes to stdout by default; use `-o <dir>` to save to a file or directory
- All progress/status messages go to stderr; document content goes to stdout
- MinerU is open-source by OpenDataLab (Shanghai AI Lab): https://github.com/opendatalab/MinerU
