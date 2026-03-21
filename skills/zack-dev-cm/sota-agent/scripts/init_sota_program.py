#!/usr/bin/env python3
"""Create a machine-readable program record for a DS/CV SOTA effort."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sota_public_safety import sanitize_ref


def parse_baseline(items: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid --baseline value: {item!r}, expected name=score")
        name, raw_score = item.split("=", 1)
        rows.append({"name": name.strip(), "score": float(raw_score.strip())})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Output JSON file.")
    parser.add_argument("--program-id", required=True, help="Stable program identifier.")
    parser.add_argument("--problem", required=True, help="One-sentence program goal.")
    parser.add_argument("--primary-metric", required=True, help="Primary benchmark metric.")
    parser.add_argument("--surface", action="append", default=[], help="Repeatable non-regression surface.")
    parser.add_argument("--baseline", action="append", default=[], help="Repeatable name=score baseline entry.")
    parser.add_argument("--paper", action="append", default=[], help="Repeatable frontier paper title or public URL.")
    parser.add_argument("--minimize", action="store_true", default=False, help="Treat lower metric values as better.")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "program_id": args.program_id,
        "problem": args.problem,
        "benchmark": {
            "primary_metric": args.primary_metric,
            "goal_direction": "minimize" if args.minimize else "maximize",
            "non_regression_surfaces": args.surface,
        },
        "baselines": parse_baseline(args.baseline),
        "frontier_sources": [sanitize_ref(item) for item in args.paper],
        "queues": {
            "research_backlog": [],
            "prove_it": [],
            "promotion": [],
        },
        "artifacts": {
            "scoreboard_path": "",
            "review_packet_path": "",
        },
        "decision": {
            "status": "research",
            "reason": "",
        },
    }

    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
