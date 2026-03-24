#!/usr/bin/env python3
"""Summarize flagged ride rows into a repair worklist.

Reads rides_flagged.jsonl from validate_extracted_rides.py and prints one JSON line per
flagged gmail_message_id with the current ride file path, email file path, and issues.
This is a helper for the Gateway-backed one-email-at-a-time repair phase.
"""

import argparse
import json
from pathlib import Path

IMPORTANT_FIELDS = [
    "amount",
    "currency",
    "pickup",
    "dropoff",
    "payment_method",
    "distance_text",
    "duration_text",
    "start_time_text",
    "end_time_text",
]

ISSUE_FIELD_HINTS = {
    "bad_currency_code": ["currency"],
    "amount_not_numeric": ["amount"],
    "start_time_looks_like_duration": ["start_time_text", "duration_text"],
    "end_time_looks_like_duration": ["end_time_text", "duration_text"],
    "duration_equals_time_field": ["duration_text", "start_time_text", "end_time_text"],
    "distance_text_unusual": ["distance_text"],
    "one_sided_route": ["pickup", "dropoff"],
    "bolt_missing_total_cluster": ["amount", "currency"],
    "bolt_duration_shifted_into_start_time": ["start_time_text", "duration_text", "end_time_text"],
    "yandex_missing_total_cluster": ["amount", "currency"],
    "yandex_total_mentions_byn_but_currency_null": ["currency", "amount"],
    "yandex_symbol_total_but_currency_null": ["currency", "amount"],
    "uber_cancellation_should_not_have_route_fields": ["pickup", "dropoff", "distance_text", "duration_text", "start_time_text", "end_time_text"],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def missing_important_fields(ride_obj: dict) -> list[str]:
    ride = (ride_obj or {}).get("ride") or {}
    return [field for field in IMPORTANT_FIELDS if ride.get(field) is None]


def field_hints(issues: list[str]) -> list[str]:
    out = []
    for issue in issues:
        out.extend(ISSUE_FIELD_HINTS.get(issue, []))
    return sorted(set(out))


def iter_flagged(flagged_path: Path):
    with flagged_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flagged", required=True)
    ap.add_argument("--emails-dir", required=True)
    ap.add_argument("--rides-dir", required=True)
    args = ap.parse_args()

    flagged_path = Path(args.flagged)
    emails_dir = Path(args.emails_dir)
    rides_dir = Path(args.rides_dir)

    count = 0
    for item in iter_flagged(flagged_path):
        row = item.get("row") or {}
        source = row.get("source") or {}
        gmail_message_id = source.get("gmail_message_id")
        if not gmail_message_id:
            continue

        ride_path = rides_dir / f"{gmail_message_id}.json"
        email_path = emails_dir / f"{gmail_message_id}.json"

        current = load_json(ride_path) if ride_path.exists() else row
        issues = item.get("issues") or []
        missing = missing_important_fields(current)
        hinted = field_hints(issues)

        work_item = {
            "gmail_message_id": gmail_message_id,
            "provider": current.get("provider"),
            "email_file": str(email_path),
            "ride_file": str(ride_path),
            "issues": issues,
            "missing_important_fields": missing,
            "suggested_focus_fields": sorted(set(missing + hinted)),
        }
        print(json.dumps(work_item, ensure_ascii=False))
        count += 1

    print(json.dumps({"flagged_rows": count}, ensure_ascii=False))


if __name__ == "__main__":
    main()
