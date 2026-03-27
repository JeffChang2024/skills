---
name: table-ocr
description: "Table OCR - extract tables from scanned PDFs or images using MinerU OCR with table recognition. Use when documents have image-embedded tables."
homepage: https://mineru.net
metadata: {"openclaw": {"emoji": "📄", "requires": {"bins": ["mineru-open-api"], "env": ["MINERU_TOKEN"]}, "primaryEnv": "MINERU_TOKEN", "install": [{"id": "npm", "kind": "node", "package": "mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via npm"}, {"id": "go", "kind": "go", "package": "github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via go install", "os": ["darwin", "linux"]}]}}
---

# Table Ocr

Convert and extract content from .pdf / images (.png/.jpg/.jpeg/.webp) using MinerU (`mineru-open-api`).

## Install

```bash
npm install -g mineru-open-api
# or via Go (macOS/Linux):
go install github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api@latest
```

## Quick Start

```bash
# Extract tables from PDF (requires token)
mineru-open-api extract report.pdf -o ./out/

# With explicit table flag and OCR for scanned docs
mineru-open-api extract scanned.pdf --ocr --table -o ./out/
```

## Authentication

Token required for `extract` and `crawl`:

```bash
mineru-open-api auth            # Interactive token setup
export MINERU_TOKEN="your-token" # Or via environment variable
```

Create token at: https://mineru.net/apiManage/token

## Capabilities

- Supports local files and URLs
- Requires token (`mineru-open-api auth` or `MINERU_TOKEN` env)
- Supported input: .pdf / images (.png/.jpg/.jpeg/.webp)
- Language hint with `--language` (default: `ch`, use `en` for English)
- Page range with `--pages` (where applicable)

## Notes

- Table recognition requires `extract` with token. Use `--ocr` for scanned content and `--table` for table detection (both enabled by default in extract).
- Output goes to stdout by default; use `-o <dir>` to save to file
- Binary formats (docx) require `-o` flag (cannot stream to stdout)
- All progress/status messages go to stderr
- MinerU is an open-source project by OpenDataLab (Shanghai AI Lab): https://github.com/opendatalab/MinerU
