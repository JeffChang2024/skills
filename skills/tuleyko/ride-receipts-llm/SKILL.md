---
name: ride-receipts-llm
description: Build a local SQLite ride-history database from Gmail ride receipt emails (Uber, Bolt, Yandex Go, Lyft, Free Now). Use when asked to ingest ride receipts, rebuild the ride database, analyze ride history, or generate an anonymized ride report CSV for download. Requires `gog` CLI with an authenticated Google account.
---

# ride-receipts-llm

Build a local ride-history SQLite database from Gmail receipts, repair extraction gaps conservatively, enrich missing city/country fields, and answer follow-up ride-history questions from the resulting database.

## Before you start

- Require `gog` CLI authenticated for the target Gmail account.
- Use configured account from `skills.entries.ride-receipts-llm.config.gmailAccount`. Ask the user if missing.
- Ask the user for date scope: all-time, after a date, or between two dates.
- Receipts are sensitive financial/location data — never log full email bodies to the user.
- Before LLM repair, confirm the user is okay sending raw email HTML to the active LLM.
- For the Gateway-backed extraction batch, require a reachable local OpenClaw Gateway with HTTP LLM endpoint enabled and a valid token available via `OPENCLAW_GATEWAY_TOKEN` or `~/.openclaw/openclaw.json`.

## Constraints

- Run only the existing scripts listed below. Do not write new scripts, modify existing ones, or attempt to fix extraction bugs inline.
- If a script fails, report the error and stop. Do not try to work around it.
- Never hallucinate fields; use `null` when unknown.
- Never overwrite a good non-null extracted field with `null` during repair or enrichment.
- Keep addresses verbatim; write inferred city/country only into `pickup_city`, `pickup_country`, `dropoff_city`, `dropoff_country`.
- When enriching city/country with the Gateway-backed LLM path, process one ride at a time. Do not batch many addresses into one prompt.
- Keep user-facing output brief: report counts and outcomes, not raw JSON dumps.

## Outputs

Primary artifacts:
- `data/emails/*.json` — fetched receipt emails
- `data/rides/*.json` — extracted per-ride JSON records
- `data/rides.sqlite` — queryable SQLite database
- `data/rides_flagged.jsonl` — validation failures needing review/repair

## Pipeline

Run each step in order. Stop and report on failure.

### 1. Initialize DB

```bash
python3 skills/ride-receipts-llm/scripts/init_db.py \
  --db ./data/rides.sqlite \
  --schema skills/ride-receipts-llm/references/schema_rides.sql
```

### 2. Fetch Gmail receipts

```bash
python3 skills/ride-receipts-llm/scripts/fetch_emails_dir.py \
  --account <gmail-account> \
  --after YYYY-MM-DD \
  --before YYYY-MM-DD \
  --max-per-provider 5000 \
  --out-dir ./data/emails
```

Omit `--after` / `--before` when not needed.

### 3. Extract rides (deterministic, no LLM)

```bash
python3 skills/ride-receipts-llm/scripts/extract_rides_xpath.py \
  ./data/emails \
  --output ./data/rides
```

Optional Gateway-backed LLM batch extraction / repair helper:

```bash
OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789 \
OPENCLAW_GATEWAY_TOKEN=... \
node skills/ride-receipts-llm/scripts/run_embedded_extraction_batch.mjs \
  --emails-dir ./data/emails \
  --rides-dir ./data/rides
```

Notes:
- This script uses the local Gateway HTTP LLM interface (`/v1/responses`).
- It performs extraction and additive repair only; it does NOT run validation or SQLite import.
- If `OPENCLAW_GATEWAY_URL` is omitted, it defaults to `http://127.0.0.1:<gateway.port>` from `~/.openclaw/openclaw.json`.
- If `OPENCLAW_GATEWAY_TOKEN` is omitted, the script falls back to `gateway.auth.token` from `~/.openclaw/openclaw.json`.
- By default, the script refuses to send ride email content to non-local Gateway hosts. Override only with `OPENCLAW_ALLOW_NONLOCAL_GATEWAY=1` when you explicitly trust the remote/private Gateway target.
- The Gateway must have the relevant HTTP endpoint enabled.
- Run `validate_extracted_rides.py` separately after this script.

### 4. Validate

Build JSONL from ride files, then validate:

```bash
python3 - <<'PY'
import json
from pathlib import Path
from subprocess import run

rides_dir = Path('./data/rides')
jsonl_path = Path('./data/rides_extracted.jsonl')
with jsonl_path.open('w', encoding='utf-8') as out:
    for path in sorted(rides_dir.glob('*.json')):
        out.write(json.dumps(json.loads(path.read_text(encoding='utf-8')), ensure_ascii=False) + '\n')

run([
    'python3', 'skills/ride-receipts-llm/scripts/validate_extracted_rides.py',
    '--in', str(jsonl_path),
    '--out', './data/rides_flagged.jsonl',
], check=True)
PY
```

Build the repair worklist:

```bash
python3 skills/ride-receipts-llm/scripts/list_flagged_ride_repairs.py \
  --flagged ./data/rides_flagged.jsonl \
  --emails-dir ./data/emails \
  --rides-dir ./data/rides
```

If zero flagged rows, skip to step 6.

### 5. LLM repair (only for flagged rows)

For each item in the repair worklist:

1. Read `data/emails/<id>.json` and `data/rides/<id>.json`
2. Read `skills/ride-receipts-llm/references/problematic-patterns.md`
3. Call the Gateway-backed LLM path one email at a time using the repair template from `skills/ride-receipts-llm/references/gateway_repair_prompt_template.md`
4. Write the repaired ride JSON back to `data/rides/<id>.json`

When there are many flagged rows, use bounded batches (not unbounded spawns).

Repair rules:
- Use `text_html` first; `snippet` only if `text_html` is empty.
- Fill only missing or clearly wrong fields.
- Never replace an existing non-null field with `null`.
- Keep addresses and time strings verbatim.
- Normalize currency to 3-letter ISO code only when confidently inferable.
- Yandex: `р.` → `BYN`, `BYN27.1` → `BYN 27.1`, `₽757` → `RUB 757`.
- Yandex routes with extra stops: first point = pickup, last point = dropoff.
- Older Bolt: `Ride duration 00:06` goes in `duration_text`, not `start_time_text`.
- Uber cancellation/adjustment receipts: route/time/distance fields may be `null`.

After repairs, re-validate by repeating step 4. If flagged rows remain, report them and proceed.

### 6. Enrich missing city/country (Gateway-backed LLM, one by one)

Use this step when `pickup_city`, `pickup_country`, `dropoff_city`, or `dropoff_country` are still `null` but `pickup` and/or `dropoff` contain usable address text.

Process sequentially, one ride JSON file at a time:

1. Read `skills/ride-receipts-llm/references/llm_prompt_templates.md`
2. Read one `data/rides/<gmail_message_id>.json`
3. Ask the Gateway-backed LLM path to infer only the missing city/country fields from the existing `pickup` / `dropoff` text
4. Overwrite `data/rides/<gmail_message_id>.json` with the updated full JSON object

Enrichment rules:
- Never change `pickup` or `dropoff` text.
- Fill only city/country fields that are currently `null`.
- If an address is ambiguous, leave the field `null`.
- Use the most specific confident city and country supported by the address text alone.
- If one side's country is confidently known for the same ride and the other side's country is still `null`, copy the known country to the missing side.
- Only do this country propagation within the same ride record; do not propagate city values this way.
- Do not geocode, browse, or call external APIs for this step unless the user explicitly asks.
- Keep provider-specific transliterations as-is in address fields; normalize only the inferred city/country values when confident.
- Prefer one-at-a-time Gateway requests for this pass; do not fan out many concurrent LLM calls for bulk city/country enrichment.

After enrichment, import into SQLite.

### 7. Import into SQLite

```bash
python3 skills/ride-receipts-llm/scripts/insert_rides_sqlite_dir.py \
  --db ./data/rides.sqlite \
  --schema skills/ride-receipts-llm/references/schema_rides.sql \
  --rides-dir ./data/rides
```

### 8. Report

Tell the user:
- How many emails were fetched
- How many rides were extracted
- How many needed LLM repair
- How many rides had city/country enrichment
- How many flagged rows remain (if any)
- That `data/rides.sqlite` is ready to query

## Insights

Use this mode only after `data/rides.sqlite` exists.

When the user asks for analysis or summaries after import:

1. Read `skills/ride-receipts-llm/references/insights_prompt_template.md` first.
2. Query `data/rides.sqlite` and present a structured high-level overview (dataset, spending, geography, time, data quality).
3. End with a numbered list of deep-dive options and ask the user what to explore next.
4. On each follow-up, query only what is needed, present it concisely, and offer the next choice.

Do not dump all analysis at once. Do not show SQL to the user.

## Anonymized report export

Use this mode when the user asks for an anonymized report, anonymized export, or a downloadable CSV derived from the ride database.

Prerequisite:
- Require `data/rides.sqlite` to exist.

### What the export includes

Export only these columns:
- `provider`
- `email_date_text` reduced to month-only format like `2025-05`
- `start_time_text` — rounded up to the closest 15-minute interval
- `end_time_text` — rounded up to the closest 15-minute interval
- `currency`
- `amount`
- `pickup_city`
- `pickup_country`
- `dropoff_city`
- `dropoff_country`
- `distance_km`
- `duration_min`

### What the export does NOT include

Do not export:
- exact pickup addresses
- exact dropoff addresses
- Gmail message ids
- email subjects
- raw email JSON
- extracted ride JSON blobs
- payment method
- driver name
- notes
- provider-specific internal metadata
- exact trip date
- raw provider-specific `distance_text`
- raw provider-specific `duration_text`

### Privacy transformations and normalizations

Apply these privacy-preserving transformations:
- Reduce `email_date_text` to month-only format `YYYY-MM`.
  - Example: `2025-05-18 14:07` → `2025-05`
- Round `start_time_text` upward to the nearest 15-minute bucket when parseable.
  - Example: `14:07` → `14:15`
  - Example: `2:07 PM` → `2:15 PM`
- Round `end_time_text` upward to the nearest 15-minute bucket when parseable.
  - Example: `14:44` → `14:45`
- Convert distance into unified numeric `distance_km`.
  - Parse common source forms such as `3 km`, `9.17 kilometers`, `54.08mi`, `56.73 miles`
  - Convert miles to kilometers
  - Round the exported numeric value to a sensible fixed precision (prefer `2` decimal places)
- Convert duration into unified numeric `duration_min`.
  - Parse common source forms such as `00:06`, `00:14:02`, `30 min`, `1 h 0 min`
  - Export total duration in whole minutes
  - Round sub-minute precision upward to the next full minute when needed
- Keep `amount` as stored; do not round or convert currencies unless the user explicitly asks.
- If a date, time, distance, or duration value is missing or unparsable, leave the exported field empty rather than guessing.

Rules:
- Query `data/rides.sqlite`; do not export directly from raw emails.
- Export only the allowed columns listed above.
- Do not include exact pickup or dropoff addresses.
- Reduce `email_date_text` to month-only format like `YYYY-MM`; leave it empty if the stored date is missing or unparsable.
- Round time strings upward to the nearest 15-minute bucket when they are parseable; leave them unchanged if they are not parseable.
- Convert stored provider-specific distance text into unified numeric `distance_km`.
- Convert stored provider-specific duration text into unified numeric `duration_min`.
- Keep the existing `amount` and `currency` values as stored unless the user explicitly asks for conversion or additional bucketing.
- Write the export to a CSV file in the workspace, for example `data/rides_anonymized_report.csv`.
- Attach the CSV file to the chat for download.
- Keep the user-facing reply brief: say what was exported and attach the file.

Suggested flow:
1. Query the required columns from `data/rides.sqlite`
2. Reduce `email_date_text` to `YYYY-MM`
3. Round `start_time_text` and `end_time_text` upward to the nearest 15-minute interval
4. Parse and normalize distance into `distance_km`
5. Parse and normalize duration into `duration_min`
6. Write the CSV file with only the allowed columns
7. Send the CSV as an attachment in chat

## Reference paths

- Schema: `skills/ride-receipts-llm/references/schema_rides.sql`
- Extraction rules: `skills/ride-receipts-llm/references/extraction_rules.json`
- LLM prompts: `skills/ride-receipts-llm/references/llm_prompt_templates.md`
- Repair template: `skills/ride-receipts-llm/references/gateway_repair_prompt_template.md`
- City/country enrichment prompt: `skills/ride-receipts-llm/references/llm_prompt_templates.md` (city/country enrichment section)
- Known edge cases: `skills/ride-receipts-llm/references/problematic-patterns.md`
- Insights template: `skills/ride-receipts-llm/references/insights_prompt_template.md`
md`
md`
