# Packaging Review — Reference Guide

File naming, folder structure, bundle completeness, version consistency, and delivery packaging.
The physical and organizational integrity of everything we ship.

---

## 1. FILE NAMING STANDARDS

### Mandatory Naming Rules
```
PRODUCTS:
  [ProductName-TitleCase]-v[major].[minor].[ext]
  FamliClaw-v1.0.pdf                    ✅
  Legacy-Letters-Companion-v1.2.pdf     ✅
  famiclaw.pdf                          ❌ (no version, no title case)
  Final Version NEW (1).pdf             ❌ (auto-reject)

COVER IMAGES:
  [ProductName]-cover-v[version].[ext]
  FamliClaw-cover-v1.0.jpg             ✅

BONUS/SUPPORTING FILES:
  [ProductName]-[descriptor]-v[version].[ext]
  FamliClaw-bonus-templates-v1.0.pdf   ✅
```

### Auto-Reject Filename Patterns
Any filename containing: DRAFT, draft, WIP, wip, FINAL FINAL, final_FINAL, backup, temp, Temp, (1), (2), - Copy, OLD, old → REJECT, rename before proceeding.

---

## 2. FOLDER STRUCTURE STANDARDS

### Digital Product Bundle Structure
```
FamliClaw-v1.0/
├── README.txt                    # What's in this bundle, how to use
├── FamliClaw-v1.0.pdf           # Main product file
├── FamliClaw-Quick-Start.pdf    # Optional: quick start guide
└── bonuses/
    ├── FamliClaw-Bonus-Templates-v1.0.pdf
    └── FamliClaw-Planner-Pages-v1.0.pdf
```

### Bundle Completeness Check
```
For every bundle:
- [ ] Main file is present and named correctly
- [ ] README.txt or equivalent describes contents
- [ ] All advertised bonus files present
- [ ] No extraneous files included (no source files, no backup files)
- [ ] Folder name matches product name and version
- [ ] ZIP archive (if applicable) opens without errors
```

---

## 3. VERSION CONSISTENCY

### Cross-Asset Version Check
```
Before shipping any product update:
- [ ] Version number in filename matches version in product
- [ ] Version number on cover page matches filename
- [ ] Description on platform says "v[X]" (if we display versions)
- [ ] Previous version archived (not overwritten)
- [ ] CHANGELOG updated (if maintained)

Inconsistency Example (FAIL):
  Filename: FamliClaw-v1.2.pdf
  Cover page: "Version 1.1"
  → Version mismatch → STOP, fix before publishing
```

---

## 4. PLATFORM UPLOAD VERIFICATION

### Post-Upload Check
```
After uploading to Gumroad/KDP:
- [ ] Uploaded file size matches local file size
  (Discrepancy → upload may be corrupt → re-upload)
- [ ] Uploaded file opens correctly from the platform
- [ ] Cover image displays correctly in listing
- [ ] File type shows correctly in listing
- [ ] Download count resets correctly (new upload registered)
```

---

## 5. PACKAGING REVIEW VERDICT FORMAT

```
PACKAGING REVIEW: [Product Name]

FILE NAMING:
  Main file: [filename] — PASS / FAIL
  Cover image: [filename] — PASS / FAIL
  Supporting files: [list] — PASS / FAIL

FOLDER STRUCTURE:
  Structure: PASS / FAIL
  All advertised files present: PASS / FAIL
  No extraneous files: PASS / FAIL

VERSION CONSISTENCY:
  Filename version: v[X]
  Cover page version: v[X]
  Match: PASS / FAIL

UPLOAD VERIFICATION:
  Upload complete: PASS / FAIL
  File accessible from platform: PASS / FAIL

OVERALL: ✅ PACKAGING APPROVED / ❌ PACKAGING FAILED — [issues list]
```
