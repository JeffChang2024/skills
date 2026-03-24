#!/usr/bin/env python3
"""Validate extracted ride JSONL and flag rows that likely need repair before SQLite import.

This does not try to re-extract anything. It only catches suspicious outputs so the
agent can run a targeted repair pass on bad rows.
"""

import argparse
import json
import re
from pathlib import Path

TIME_RE = re.compile(r"\b\d{1,2}:\d{2}\b")
DURATION_RE = re.compile(r"^(?:\d{1,2}:\d{2}|\d+\s*(?:min|mins|minutes|hour|hours|h))$", re.I)
DISTANCE_RE = re.compile(r"\b(?:\d+(?:[.,]\d+)?)\s*(?:km|kilometers?|mi|miles?)\b", re.I)
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


def check_row(obj):
    issues = []
    provider = obj.get("provider")
    ride = obj.get("ride") or {}
    source = obj.get("source") or {}

    if provider not in {"Uber", "Bolt", "Yandex", "Lyft", "FreeNow"}:
        issues.append("bad_provider")

    if not source.get("gmail_message_id"):
        issues.append("missing_gmail_message_id")

    currency = ride.get("currency")
    if currency is not None and not CURRENCY_RE.match(str(currency)):
        issues.append("bad_currency_code")

    amount = ride.get("amount")
    if amount is not None and not isinstance(amount, (int, float)):
        issues.append("amount_not_numeric")

    st = ride.get("start_time_text")
    et = ride.get("end_time_text")
    dur = ride.get("duration_text")
    dist = ride.get("distance_text")
    total = ride.get("total_text")
    pickup = ride.get("pickup")
    dropoff = ride.get("dropoff")
    notes = (ride.get("notes") or "").lower()
    subj = (source.get("subject") or "").lower()

    if st and DURATION_RE.match(str(st)) and not TIME_RE.search(str(st)):
        issues.append("start_time_looks_like_duration")
    if et and DURATION_RE.match(str(et)) and not TIME_RE.search(str(et)):
        issues.append("end_time_looks_like_duration")
    if dur and TIME_RE.search(str(dur)) and (st == dur or et == dur):
        issues.append("duration_equals_time_field")
    if dist and not DISTANCE_RE.search(str(dist)):
        issues.append("distance_text_unusual")

    if (pickup is None) != (dropoff is None):
        issues.append("one_sided_route")

    if provider == "Bolt":
        if total is None and amount is None and currency is None:
            issues.append("bolt_missing_total_cluster")
        if pickup is None and dur and TIME_RE.search(str(st or "")) and st == dur:
            issues.append("bolt_duration_shifted_into_start_time")

    if provider == "Yandex":
        if total is None and amount is None and currency is None:
            issues.append("yandex_missing_total_cluster")
        if total and "BYN" in total and currency is None:
            issues.append("yandex_total_mentions_byn_but_currency_null")
        if total and ("р." in total or "₽" in total) and currency is None:
            issues.append("yandex_symbol_total_but_currency_null")

    if provider == "Uber":
        cancellation_like = "cancellation fee" in notes or "canceled trip" in subj or (amount in {0, 5, 5.0} and pickup is None and dropoff is None)
        if cancellation_like and any([pickup, dropoff, st, et, dist, dur]):
            issues.append("uber_cancellation_should_not_have_route_fields")

    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = 0
    flagged = 0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with Path(args.infile).open("r", encoding="utf-8") as inf, out_path.open("w", encoding="utf-8") as outf:
        for line in inf:
            line = line.strip()
            if not line:
                continue
            rows += 1
            obj = json.loads(line)
            issues = check_row(obj)
            if issues:
                flagged += 1
                outf.write(json.dumps({"issues": issues, "row": obj}, ensure_ascii=False) + "\n")

    print(json.dumps({"rows": rows, "flagged": flagged, "out": str(out_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
