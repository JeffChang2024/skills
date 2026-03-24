# Gateway repair prompt template

Use this template when sending one targeted Gateway-backed LLM request for one flagged ride email.

## Goal

Repair only the flagged or missing fields for a single ride JSON file using the matching email JSON.

## Inputs

- Email JSON file: `data/emails/<gmail_message_id>.json`
- Current ride JSON file: `data/rides/<gmail_message_id>.json`
- Validation issues from `data/rides_flagged.jsonl`
- Suggested focus fields from `data/rides_repair_worklist.jsonl`

## Required behavior

- Read the email JSON and current ride JSON.
- Use `text_html` as primary source. Use `snippet` only if `text_html` is empty.
- Fill only missing or clearly wrong fields.
- Never replace a good non-null field with `null`.
- Keep addresses and time strings verbatim.
- Return the full ride JSON object with the same schema.
- Write the repaired object back to `data/rides/<gmail_message_id>.json`.

## Mailbox-specific rules

- Yandex: `р.` means `BYN`; `BYN27.1` means `currency=BYN`, `amount=27.1`; `₽757` means `currency=RUB`, `amount=757`.
- Yandex routes with extra stops or `Destination changed`: use first point/time as pickup/start and final point/time as dropoff/end.
- Older Bolt receipts: keep `Ride duration 00:06` in `duration_text`; start/end must come from route timestamps.
- Uber cancellation or fare-adjustment receipts may legitimately keep route/time/distance fields as `null`.

## Suggested request message shape

```text
Repair one flagged ride receipt.

Read:
- data/emails/<gmail_message_id>.json
- data/rides/<gmail_message_id>.json
- skills/ride-receipts-llm/references/problematic-patterns.md

Context:
- issues: <issues>
- suggested_focus_fields: <fields>

Task:
Repair only the missing or suspicious fields supported by the email, preserve existing good values, and overwrite data/rides/<gmail_message_id>.json with the repaired full JSON object.
```
object.
```
