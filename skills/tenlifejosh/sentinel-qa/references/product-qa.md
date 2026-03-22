# Product QA — Reference Guide

Digital product completeness checks, file integrity, no-placeholder verification, naming conventions,
version management, and download verification. The complete product quality protocol.

---

## TABLE OF CONTENTS
1. Product QA Philosophy
2. PDF Product Checklist
3. File Integrity Verification
4. Cover Image Standards
5. Naming Conventions
6. Version Management
7. Download Flow Testing
8. Product Metadata Quality
9. Pricing Verification
10. Quality Tiers by Product Type

---

## 1. PRODUCT QA PHILOSOPHY

### What Product QA Protects
Product QA protects against three categories of failure:

**Category 1: File Failures** (Product doesn't work)
- File won't open
- File is corrupted
- File is wrong version
- File is missing pages or sections

**Category 2: Content Failures** (Product disappoints)
- Placeholder text still present
- Content doesn't match description
- Quality below stated value
- Missing components (exercises, worksheets, etc.)

**Category 3: Commercial Failures** (Purchase experience breaks)
- Wrong price
- Wrong download file
- Download link broken
- Confirmation email not sent
- Purchase confirmation has wrong product name

Any Category 1 failure = automatic rejection (stops here, fix before anything else).
Category 2 and 3 failures = must be addressed before publishing.

---

## 2. PDF PRODUCT CHECKLIST

### File Quality
```
BASIC INTEGRITY:
- [ ] File opens without errors or password prompts
- [ ] All pages load completely (test pages 1, middle, last)
- [ ] File renders correctly in standard PDF viewers (Adobe, Preview, browser)
- [ ] File size is reasonable for content (10-50MB typical for image-heavy PDFs)
- [ ] File is not corrupted (if open in repair mode → reject and regenerate)

VISUAL QUALITY:
- [ ] Cover image is sharp and professional-looking
- [ ] Body text is readable at 100% zoom (minimum 10pt font for body)
- [ ] Images are sharp (not pixelated or blurry at 100% zoom)
- [ ] Colors display correctly (no unexpected color shifts)
- [ ] No pages are blank except intentional blank pages (journals, etc.)
- [ ] Page numbers are present and sequential (if applicable)
- [ ] Headers/footers consistent throughout document

CONTENT COMPLETENESS:
- [ ] All sections mentioned in table of contents exist
- [ ] No "LOREM IPSUM" placeholder text anywhere
- [ ] No [PLACEHOLDER], [TBD], [INSERT X], or bracket-wrapped incomplete text
- [ ] No "Chapter X: [Title]" style unfilled templates
- [ ] Author byline present (where applicable)
- [ ] Copyright notice accurate (year, company name)
- [ ] All exercises/worksheets/templates are complete (not partially filled)
```

### Fillable PDF Products (Journals, Workbooks)
```
FORM FIELDS:
- [ ] All form fields are functional (click to type works)
- [ ] Tab order is logical (moves through fields in reading order)
- [ ] Date fields accept date format
- [ ] Character limits appropriate (don't cut off mid-thought)
- [ ] Fields save when document is saved (not just session)
- [ ] Signature/checkbox fields work correctly

LAYOUT:
- [ ] Writing lines are evenly spaced and correct size for content
- [ ] Checkboxes are appropriate size (minimum 10px)
- [ ] Instructions for filling out are clear
- [ ] There's enough space for expected content
```

### KDP-Specific Checks
```
TRIM & MARGINS:
- [ ] Page size matches selected trim size exactly (e.g., 8.5×11.000 for 8.5×11 trim)
- [ ] Interior margins meet minimum requirements for page count:
      <150 pages: inside ≥0.375"
      150-300 pages: inside ≥0.500"
      300-500 pages: inside ≥0.625"
- [ ] No content falls in the gutter/spine area
- [ ] No content bleeds off the page edge

TECHNICAL:
- [ ] Fonts are embedded (verify in Acrobat: File → Properties → Fonts)
- [ ] Color mode: Grayscale for B&W print (not RGB, not CMYK)
- [ ] Color mode: CMYK for color print
- [ ] No spot colors or ICC profiles that could cause issues
- [ ] Image resolution 300 DPI minimum
- [ ] File size under 650MB
- [ ] PDF version 1.3–1.7 (not PDF 2.0)
- [ ] Page count is even (add blank back page if needed)
- [ ] First page is odd-numbered (right-hand page)
```

---

## 3. FILE INTEGRITY VERIFICATION

### Checksum Verification
```python
import hashlib
from pathlib import Path

def get_file_hash(filepath: Path) -> str:
    """Generate MD5 hash of file for integrity verification."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_file_integrity(filepath: Path, expected_hash: str) -> bool:
    """Verify file matches expected hash."""
    actual_hash = get_file_hash(filepath)
    return actual_hash == expected_hash

# Usage workflow:
# 1. When creating final file: record_hash(filepath)  → store hash
# 2. Before publishing: verify_file_integrity(filepath, stored_hash)
# If hash mismatch → file was modified after "final" version was declared → investigate
```

### File Metadata Check
```python
from pathlib import Path
import os
from datetime import datetime

def audit_file_metadata(filepath: Path) -> dict:
    """Audit file metadata to verify it's the right version."""
    stat = filepath.stat()
    return {
        'filename': filepath.name,
        'size_bytes': stat.st_size,
        'size_mb': round(stat.st_size / 1024 / 1024, 2),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': filepath.suffix,
        'is_empty': stat.st_size == 0,
    }

def check_pdf_page_count(filepath: Path) -> int:
    """Get page count of PDF without opening it visually."""
    from pypdf import PdfReader
    reader = PdfReader(str(filepath))
    return len(reader.pages)
```

---

## 4. COVER IMAGE STANDARDS

### Platform Requirements
```
GUMROAD PRODUCT COVER:
  Recommended: 1280×720px (16:9)
  Minimum: 640×360px
  Format: JPG or PNG
  Max size: 10MB
  
KDP PAPERBACK COVER (full wrap):
  Must match KDP cover calculator output exactly
  Color mode: CMYK
  Resolution: 300 DPI minimum
  Format: PDF
  Bleed: 0.125" on all edges
  
GUMROAD PROFILE / THUMBNAIL:
  Size: 300×300px (square)
  Format: JPG or PNG

SOCIAL MEDIA PREVIEW (when sharing link):
  Twitter/X: 1200×675px (16:9) or 1080×1080px
  Facebook/Instagram: 1080×1080px
  LinkedIn: 1200×627px
```

### Cover Quality Standards
```
VISUAL QUALITY:
- [ ] Text is readable at thumbnail size (50px height view)
- [ ] Title text is the largest/most prominent element
- [ ] Author/brand name is visible but secondary
- [ ] Color contrast ratio meets accessibility (4.5:1 for normal text)
- [ ] Image does not look like stock photography (authentic > generic)
- [ ] No blurry or low-resolution elements
- [ ] No stretched or distorted images

BRAND CONSISTENCY:
- [ ] Uses brand color palette (not random colors)
- [ ] Font matches brand guidelines
- [ ] Style consistent with other products in catalog
- [ ] Logo or brand mark present (where applicable)

COMMERCIAL EFFECTIVENESS:
- [ ] Makes product category immediately obvious
- [ ] Headline visible at 200px width (Gumroad grid view)
- [ ] Not too busy or cluttered
- [ ] Would you click this? (honest gut check)
```

---

## 5. NAMING CONVENTIONS

### File Naming Standards
```
Digital Products:
  [Product-Name-Titlecase]-v[major].[minor].pdf
  Examples:
    FamliClaw-v1.0.pdf            ✅
    Legacy-Letters-v2.1.pdf       ✅
    famiclaw final FINAL.pdf      ❌ (lowercase, spaces, "FINAL" in name)
    Legacy Letters v3.pdf         ❌ (space before version)

Cover Images:
  [Product-Name]-cover-v[version].[ext]
  Examples:
    FamliClaw-cover-v1.0.jpg      ✅
    legacy-letters-cover-v2.png   ✅

Assets/Supporting Files:
  [Product-Name]-[asset-type]-v[version].[ext]
  Examples:
    FamliClaw-workbook-pages-v1.0.pdf   ✅
    Legacy-Letters-bonus-guide-v1.0.pdf ✅
```

### Auto-Reject File Names (Fails QA Automatically)
```
Any file matching these patterns → REJECT:
  *DRAFT*         (still a draft)
  *draft*         (still a draft)
  *WIP*           (work in progress)
  *FINAL FINAL*   (version confusion)
  *backup*        (shouldn't be the published file)
  *copy*          (likely a duplicate)
  *test*          (test file)
  * (1).*         (Windows duplicate indicator)
  *temp*          (temporary file)
```

---

## 6. VERSION MANAGEMENT

### Version Numbering
```
Use semantic versioning: MAJOR.MINOR

MAJOR version bump when:
  - Content substantially revised (25%+ of content changed)
  - Format/layout completely redone
  - Product name changed

MINOR version bump when:
  - Typos corrected
  - Minor content additions
  - Format improvements that don't change content

Examples:
  v1.0 → Initial release
  v1.1 → Fixed 3 typos, added 2 missing exercises
  v1.2 → Updated pricing references
  v2.0 → Complete redesign with new chapters
```

### Version Record Keeping
```
For every product, maintain a version log:
Product: FamliClaw
Current version: v1.2
File: FamliClaw-v1.2.pdf
Hash: [md5 hash]
Published: 2024-01-15
Changes from v1.1:
  - Fixed typo on page 12
  - Updated copyright year to 2024
  - Improved cover image quality

Previous versions archived at: [path/location]
```

---

## 7. DOWNLOAD FLOW TESTING

### Complete Purchase Flow Test
```
STEP 1: Initiate Test Purchase
- [ ] Navigate to product listing as a stranger (use incognito browser)
- [ ] Product description loads without errors
- [ ] Cover image displays correctly
- [ ] Price shows correctly
- [ ] "Buy" or "I want this" button works

STEP 2: Complete Purchase
- [ ] Checkout page loads (Gumroad/platform checkout)
- [ ] Use test card (Stripe: 4242 4242 4242 4242, any future date, any CVV)
- [ ] Purchase completes without error
- [ ] Confirmation page displays

STEP 3: Verify Post-Purchase
- [ ] Confirmation/receipt email received within 2 minutes
- [ ] Email contains download link
- [ ] Email has correct product name and amount
- [ ] Download link works
- [ ] Downloaded file is the correct file (check name + version)
- [ ] Downloaded file opens without errors
- [ ] File content is correct (not an old version)

STEP 4: Clean Up
- [ ] Refund the test transaction (if using live payment)
- [ ] Or: delete the test order from platform
```

---

## 8. PRODUCT METADATA QUALITY

### Gumroad Metadata Checklist
```
TITLE:
- [ ] Specific and benefit-focused (not generic)
- [ ] Contains primary keyword naturally
- [ ] Under 100 characters (shows fully in listings)
- [ ] No punctuation except dash/colon for subtitle

DESCRIPTION:
- [ ] 200+ words minimum
- [ ] Opens with problem/pain (not "This is a guide to...")
- [ ] Clearly states who it's for
- [ ] Lists specific outcomes/benefits
- [ ] Includes what's physically in the product (page count, sections)
- [ ] Has a clear CTA
- [ ] Priced fairly for the stated value

TAGS:
- [ ] 3-10 tags set
- [ ] Mix of broad and specific
- [ ] Matches what buyers would search for
- [ ] No tag stuffing (irrelevant tags)

CATEGORY:
- [ ] Correctly categorized
- [ ] Most specific applicable category selected
```

---

## 9. PRICING VERIFICATION

### Pricing Sanity Check
```
Before publishing any product price:
- [ ] Price matches our pricing strategy document
- [ ] Price is not accidentally $0.00 (free) or $0.01
- [ ] Price looks right for the product category and page count
- [ ] Currency is set correctly (USD by default)
- [ ] "Pay what you want" minimum is set (if using that model)

Price Reference Points (Ten Life Creatives):
  Cards/short guides (< 30 pages):    $4.99 – $7.99
  Workbooks (30-100 pages):           $9.99 – $17.00
  Comprehensive guides (100+ pages):  $27.00 – $47.00
  Premium systems:                    $47.00 – $97.00

If proposed price is outside these ranges → flag for founder review
```

---

## 10. QUALITY TIERS BY PRODUCT TYPE

### New Product Launch
**Scrutiny level: Maximum**
Run all checklists: product-qa + pre-publish-review + brand-consistency + launch-gates

### Product Update (Existing Product)
**Scrutiny level: Standard**
Run: product-qa (file checks only) + verify purchase flow still works

### Cover Update Only
**Scrutiny level: Light**
Run: cover image standards checklist + display check on listing

### Price Update Only
**Scrutiny level: Minimal**
Run: pricing verification + confirm update saved correctly on platform
