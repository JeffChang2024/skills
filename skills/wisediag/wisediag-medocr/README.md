---
name: wisediag-medocr
description: "PDF & Image OCR — Convert a single PDF or image to Markdown with high-accuracy OCR, table recognition and text extraction. Usage: Upload a file and say Use WiseOCR to OCR this."
registry:
  homepage: https://github.com/wisediag/WiseOCR
  author: wisediag
env_vars:
  - WISEDIAG_API_KEY
credentials:
  required: true
---

# ⚠️ Privacy Warning

**IMPORTANT - READ BEFORE INSTALLING:**

This tool **uploads your file to WiseDiag's cloud servers** for OCR processing.

**Do NOT use with sensitive or confidential documents** unless:
- You trust WiseDiag's data handling policies
- You accept that file contents will be transmitted and processed remotely

**For sensitive documents, use offline/local OCR tools instead.**

---

# WiseOCR (OpenClaw Skill, powered by WiseDiag)

A high-accuracy OCR tool that converts a **single PDF or image file** into Markdown format.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)

## Features

- **PDF and image support**: jpg, jpeg, png, webp, gif, bmp, tiff
- **Single file processing**: one PDF or image per command
- Table recognition and structured formatting
- Multi-column layout support
- Automatic file saving with input filename

## Installation

```bash
pip install -r requirements.txt
```

## 🔑 API Key Setup (Required)

**Get your API key:**
👉 [https://console.wisediag.com/apiKeyManage](https://s.wisediag.com/xsu9x0jq)

```bash
# Temporary (current terminal session)
export WISEDIAG_API_KEY=your_api_key_here

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export WISEDIAG_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc
```

## CLI Usage

**You MUST use the provided script to process files. Do NOT call any API or HTTP endpoint directly.**

```bash
cd scripts

# PDF
python3 wiseocr.py -i "/path/to/report.pdf"

# Image
python3 wiseocr.py -i "/path/to/scan.png"

# If the input file has been copied or renamed, use -n to preserve the original filename
python3 wiseocr.py -i "/tmp/ocr_input.pdf" -n "my_report"

# Specify output directory
python3 wiseocr.py -i input.pdf -o ~/my_ocr_results

# Higher quality rendering
python3 wiseocr.py -i input.pdf --dpi 300
```

The Markdown result is saved to `~/.openclaw/workspace/WiseOCR/{name}.md` automatically. If `-n` is provided, the output uses that name; otherwise it falls back to the input filename. No additional saving is needed.

## Arguments

| Flag | Description |
|------|-------------|
| `-i, --input` | Input file: PDF or image — single file path (required) |
| `-n, --name` | Output filename stem (recommended when input file is renamed/copied) |
| `-o, --output` | Output directory (default: ~/.openclaw/workspace/WiseOCR) |
| `--dpi` | PDF rendering DPI, 72-600 (default: 200) |

## Troubleshooting

**"WISEDIAG_API_KEY is not set" error:**
Make sure you've set the environment variable correctly. Run `echo $WISEDIAG_API_KEY` to check.

**"Authentication failed" error:**
Your API key may be invalid or expired. Visit [https://console.wisediag.com/apiKeyManage](https://s.wisediag.com/xsu9x0jq) to check or regenerate your key.

## Data Privacy

Files are sent to WiseDiag's OCR API for processing and are not permanently stored. Results are returned directly to you.

## License

MIT
