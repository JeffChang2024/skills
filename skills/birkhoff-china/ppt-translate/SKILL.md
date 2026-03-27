---
name: translate-ppt
description: "Translate Chinese PowerPoint presentations to English while preserving all images, charts, shapes, and media content. Adjusts fonts to Calibri and optimizes layout for professional business presentations. Use when the user asks to translate a PPT/PPTX file from Chinese to English, or mentions PPT translation, slide translation, or presentation localization."
---

# Translate PPT

Translate Chinese PowerPoint presentations (.pptx) to English with professional business styling.

## Overview

This skill translates Chinese PPTX files to English while:
- Preserving all non-text content (images, charts, shapes, tables, SmartArt, media)
- Adjusting fonts to Calibri family for consistent business styling
- Optimizing text box sizing and layout for English text (typically longer than Chinese)
- Maintaining original slide masters, layouts, animations, and transitions

## Prerequisites

- Python 3.8+
- Required packages: `python-pptx`, `openai`
- OpenAI API key set as environment variable `OPENAI_API_KEY`, or provide via `--api-key`

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install python-pptx openai
   ```

2. **Run translation:**
   ```bash
   python .qoder/skills/translate-ppt/scripts/translate_ppt.py <input.pptx> [output.pptx]
   ```
   
   If output path is not specified, defaults to `<input_name>_en.pptx`.

## Translation Rules

- **Translate:** All text content (titles, body text, notes, table cells, grouped shape text)
- **Preserve:** Images, charts data, embedded media, hyperlinks, original formatting
- **Mixed content:** Only translate Chinese portions of mixed Chinese/English text

## Font & Layout Adjustments

| Element | Font | Style |
|---------|------|-------|
| Titles | Calibri | Bold |
| Body text | Calibri | Regular |

- Maintain original font sizes (with auto-shrink if text overflows)
- Adjust text box width up to 20% if English text is significantly longer
- Preserve original color scheme and text formatting (bold, italic, underline)

## Business Style Guidelines

- Consistent Calibri font family throughout
- Clean, professional spacing
- Preserved slide master/layout templates
- All animations and transitions intact

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--font` | Override default font | Calibri |
| `--model` | LLM model to use | gpt-4o |
| `--api-base` | Custom API base URL | OpenAI default |
| `--api-key` | API key (alternative to env var) | `OPENAI_API_KEY` |
| `--batch-size` | Text segments per API call | 20 |
| `--verbose`, `-v` | Enable detailed logging | False |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key missing | Set `OPENAI_API_KEY` environment variable or use `--api-key` |
| Corrupt PPTX | Verify file opens in PowerPoint; try saving as new file first |
| Font not found | Ensure Calibri is installed on your system |
| API rate limits | Reduce `--batch-size` or add delay between calls |

## Reference

See [reference.md](reference.md) for detailed API documentation and architecture.
