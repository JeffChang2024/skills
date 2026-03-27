# PPT Translation Tool - Technical Reference

## Architecture Overview

The translation pipeline consists of four main stages:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. Extraction  │───▶│  2. Batching    │───▶│  3. Translation │───▶│  4. Application │
│                 │    │                 │    │                 │    │                 │
│ - Parse PPTX    │    │ - Collect text  │    │ - LLM API call  │    │ - Replace text  │
│ - Recurse shapes│    │ - Filter CJK    │    │ - Retry logic   │    │ - Adjust fonts  │
│ - Extract runs  │    │ - Batch by size │    │ - Map responses │    │ - Resize boxes  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Text Extraction

### Shape Hierarchy Traversal

The PPTX structure follows a hierarchical model:

```
Presentation
└── Slides[]
    ├── Slide
    │   ├── Shapes[]
    │   │   ├── Shape (with text_frame)
    │   │   ├── GroupShape
    │   │   │   └── Shapes[] (recursive)
    │   │   ├── Table
    │   │   │   └── Rows[]
    │   │   │       └── Cells[]
    │   │   │           └── TextFrame
    │   │   └── Picture/Chart/Media (skip)
    │   └── NotesSlide (optional)
    │       └── NotesTextFrame
```

### Extraction Algorithm

```python
def extract_texts(shape, path=""):
    texts = []
    
    if shape.has_text_frame:
        for para_idx, para in enumerate(shape.text_frame.paragraphs):
            for run_idx, run in enumerate(para.runs):
                texts.append({
                    "text": run.text,
                    "path": path,
                    "para_idx": para_idx,
                    "run_idx": run_idx,
                    "font": run.font
                })
    
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for child_idx, child in enumerate(shape.shapes):
            texts.extend(extract_texts(child, f"{path}/group[{child_idx}]"))
    
    if shape.has_table:
        for row_idx, row in enumerate(shape.table.rows):
            for col_idx, cell in enumerate(row.cells):
                texts.extend(extract_texts(
                    cell, 
                    f"{path}/table[{row_idx},{col_idx}]"
                ))
    
    return texts
```

## Grouped Shapes and Tables

### Grouped Shapes (GroupShape)

GroupShapes contain nested shapes that must be processed recursively:

- Access via `shape.shapes` iterator
- Each child shape maintains its own coordinate system relative to the group
- Text frames within grouped shapes are processed identically to top-level shapes
- Groups can be nested (groups within groups)

### Tables

Tables require cell-by-cell processing:

```python
for row in table.rows:
    for cell in row.cells:
        # Each cell has a text_frame
        process_text_frame(cell.text_frame)
        # Enable word wrap for English text
        cell.text_frame.word_wrap = True
```

- Table structure (rows/columns) is preserved
- Cell formatting (borders, fill) is preserved
- Only text content within cells is translated

## Translation Batching Strategy

### Text Collection Phase

1. Traverse all slides and shapes
2. Collect text segments with metadata:
   - Original text
   - Slide index
   - Shape path (for reconstruction)
   - Paragraph and run indices
   - Font properties

3. Filter segments:
   - Skip empty strings
   - Skip pure ASCII/alphanumeric (no Chinese)
   - Use CJK Unicode range detection:
     - U+4E00-U+9FFF (CJK Unified Ideographs)
     - U+3400-U+4DBF (CJK Extension A)
     - U+F900-U+FAFF (CJK Compatibility Ideographs)

### Batch Translation

```python
# Group segments into batches
def create_batches(segments, batch_size=20):
    for i in range(0, len(segments), batch_size):
        yield segments[i:i + batch_size]

# Translate batch
def translate_batch(batch, client, model):
    texts = [s["text"] for s in batch]
    numbered_text = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": numbered_text}
        ]
    )
    
    # Parse numbered response
    translations = parse_numbered_response(response.choices[0].message.content)
    return translations
```

### Response Mapping

Translations are mapped back using the stored metadata:

```python
for segment, translation in zip(batch, translations):
    slide = prs.slides[segment["slide_idx"]]
    shape = locate_shape(slide, segment["path"])
    run = shape.text_frame.paragraphs[segment["para_idx"]].runs[segment["run_idx"]]
    run.text = translation
```

## Font Replacement Logic

### CJK Font Detection

```python
CJK_FONTS = {
    'SimSun', '宋体',
    'SimHei', '黑体',
    'Microsoft YaHei', '微软雅黑',
    'KaiTi', '楷体',
    'FangSong', '仿宋',
    'STSong', 'STHeiti', 'STKaiti', 'STFangsong',
    'NSimSun', '新宋体',
    'PMingLiU', 'MingLiU',
    'DengXian', '等线',
    'Source Han Sans', 'Noto Sans CJK',
}

def is_cjk_font(font_name):
    if not font_name:
        return True  # Default to replacing unset fonts
    return font_name in CJK_FONTS or any(
        cjk in font_name.lower() 
        for cjk in ['song', 'hei', 'kai', 'fang', 'ming', 'gothic', 'yuan']
    )
```

### Font Replacement Rules

1. **Title Detection:**
   Shapes are detected as titles using the placeholder type:
   ```python
   from pptx.enum.shapes import PP_PLACEHOLDER
   
   def is_title_shape(shape) -> bool:
       ph = getattr(shape, "placeholder_format", None)
       if ph is None:
           return False
       try:
           return ph.type in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE, PP_PLACEHOLDER.SUBTITLE)
       except Exception:
           return False
   ```

2. **Replacement:**
   ```python
   if is_cjk_font(run.font.name):
       run.font.name = target_font  # Calibri
       if segment.is_bold or is_title:
           run.font.bold = True
   
   # Title placeholders always get bold Calibri
   if is_title:
       run.font.name = target_font
       run.font.bold = True
   ```

3. **Preservation:**
   - Font size (unless auto-resize needed)
   - Color (RGB, theme color)
   - Bold/italic/underline/strikethrough (for non-title text)
   - Hyperlink URL

## Text Box Auto-Resize Algorithm

### Overflow Detection

English text is typically 1.3-1.8x longer than Chinese. The auto-resize is triggered when:

```python
len(translated_text) > len(original_text) * 1.5
```

### Resize Strategies

The `adjust_text_box_size` function is called from `apply_translation` after setting the translated text. It applies the following strategies:

1. **Word Wrap (always enabled):**
   ```python
   text_frame.word_wrap = True
   ```

2. **Auto-fit (when text is significantly longer):**
   ```python
   from pptx.enum.text import MSO_AUTO_SIZE
   if len(translated_text) > len(original_text) * 1.5:
       try:
           text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
       except:
           pass
   ```

3. **Width Expansion (freestanding shapes only):**
   ```python
   # Only for shapes not in groups or tables
   if not is_grouped and not is_in_table:
       current_width = shape.width
       max_width = 9144000  # ~10 inches in EMU
       new_width = min(int(current_width * 1.2), max_width)
       if new_width > current_width:
           try:
               shape.width = new_width
           except:
               pass
   ```

4. **Font Size Reduction (last resort, non-title text only):**
   ```python
   if not is_title:
       for para in text_frame.paragraphs:
           for run in para.runs:
               if run.font.size and run.font.size > Pt(10):
                   try:
                       new_size = max(Pt(10), run.font.size - Pt(1))
                       run.font.size = new_size
                   except:
                       pass
   ```

### Invocation

The function is called once per shape from `apply_translation`:

```python
# In apply_translation, after setting run.text:
if not segment.shape_path.startswith("notes") and "table[" not in segment.shape_path:
    adjust_text_box_size(target, segment.text, segment.translated, is_title)
```

Note: Text box adjustment is skipped for notes and table cells to avoid layout issues.

## API Configuration

### OpenAI Client Setup

```python
from openai import OpenAI

client = OpenAI(
    api_key=api_key or os.environ.get("OPENAI_API_KEY"),
    base_url=api_base  # Optional, for compatible endpoints
)
```

### System Prompt

```
You are a professional translator specializing in business and technical content. 
Translate Chinese text to English following these rules:
1. Maintain original meaning, tone, and intent
2. Use professional business English for formal content
3. Preserve formatting markers (bullet points, numbering)
4. Do not translate proper nouns unless they have standard English equivalents
5. Return ONLY the translation, no explanations

Input format: Numbered list of text segments
Output format: Same numbered list with English translations
```

### Retry Logic

The `translate_batch` function implements inline retry with exponential backoff:

```python
def translate_batch(segments, client, model, verbose=False):
    texts = [seg.text for seg in segments]
    numbered_text = "\n".join(f"{i+1}. {text}" for i, text in enumerate(texts))
    
    for attempt in range(MAX_RETRIES):  # MAX_RETRIES = 3
        try:
            response = client.chat.completions.create(...)
            return parse_numbered_response(response.choices[0].message.content, len(segments))
        except RateLimitError:
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                sleep(wait_time)
            else:
                return [seg.text for seg in segments]  # Fallback to original
        except APIError:
            if attempt < MAX_RETRIES - 1:
                sleep(1)
            else:
                return [seg.text for seg in segments]  # Fallback to original
        except Exception:
            return [seg.text for seg in segments]  # Fallback to original
```

On failure after all retries, the function falls back to returning the original (untranslated) text to ensure the presentation remains usable.

## Error Handling

### Error Categories

| Error Type | Handling Strategy |
|------------|-------------------|
| Missing API Key | Exit with clear message before processing |
| Invalid PPTX | Try-catch on `Presentation()` load, suggest re-saving |
| API Timeout | Retry with backoff, skip batch on final failure |
| Partial Translation | Log warning, keep original text for failed segments |
| Font Not Found | Silently skip, use default font |

### Progress Logging

```python
print(f"Translating slide {slide_idx + 1}/{total_slides}...")
if verbose:
    print(f"  - Extracted {len(segments)} text segments")
    print(f"  - Batched into {len(batches)} API calls")
```

## Performance Considerations

- **Batch Size:** 20 segments balances API efficiency vs. token limits
- **Memory:** Stream process large presentations (process slide-by-slide)
- **Rate Limiting:** Add delays between batches for large files
- **Caching:** Consider caching translations for repeated segments
