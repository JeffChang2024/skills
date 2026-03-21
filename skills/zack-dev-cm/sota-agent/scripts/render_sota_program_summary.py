#!/usr/bin/env python3
"""Render a concise markdown summary from structured SOTA program artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from sota_public_safety import sanitize_ref


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"expected JSON object in {path}")
    return payload


def add_field(lines: list[str], label: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str):
        value = sanitize_ref(value)
        if not value:
            return
    if isinstance(value, list) and not value:
        return
    lines.append(f"- {label}: `{value}`")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", required=True, help="Program JSON file.")
    parser.add_argument("--out", required=True, help="Output markdown file.")
    parser.add_argument("--candidate", help="Optional candidate JSON file.")
    parser.add_argument("--scoreboard", help="Optional scoreboard JSON file.")
    parser.add_argument("--review-packet", help="Optional review packet JSON file.")
    args = parser.parse_args()

    program = load_json(Path(args.program).expanduser().resolve())
    candidate = load_json(Path(args.candidate).expanduser().resolve()) if args.candidate else {}
    scoreboard = load_json(Path(args.scoreboard).expanduser().resolve()) if args.scoreboard else {}
    review_packet = load_json(Path(args.review_packet).expanduser().resolve()) if args.review_packet else {}

    lines = [f"# SOTA Program Summary: {program.get('program_id', 'unnamed-program')}", ""]

    add_field(lines, "problem", program.get("problem"))
    benchmark = program.get("benchmark") or {}
    add_field(lines, "primary_metric", benchmark.get("primary_metric"))
    add_field(lines, "goal_direction", benchmark.get("goal_direction"))
    surfaces = benchmark.get("non_regression_surfaces") or []
    for surface in surfaces:
        add_field(lines, "non_regression_surface", surface)
    lines.append("")

    baselines = program.get("baselines") or []
    if baselines:
        lines.append("## Baselines")
        for baseline in baselines:
            lines.append(f"- `{baseline.get('name')}`: `{baseline.get('score')}`")
        lines.append("")

    if candidate:
        lines.append("## Candidate")
        add_field(lines, "candidate_id", candidate.get("candidate_id"))
        add_field(lines, "hypothesis", candidate.get("hypothesis"))
        add_field(lines, "expected_win", candidate.get("expected_win"))
        for change in candidate.get("change_set") or []:
            add_field(lines, "change", change)
        lines.append("")

    entries = scoreboard.get("entries") or []
    if entries:
        lines.append("## Scoreboard")
        add_field(lines, "metric_name", scoreboard.get("metric_name"))
        add_field(lines, "best_candidate", scoreboard.get("best_candidate"))
        for item in entries[:10]:
            lines.append(
                f"- rank `{item.get('rank')}`: `{item.get('candidate_id')}` score `{item.get('score')}` stage `{item.get('stage')}`"
            )
        lines.append("")

    if review_packet:
        lines.append("## Decision")
        decision = review_packet.get("decision") or {}
        add_field(lines, "status", decision.get("status"))
        add_field(lines, "reason", decision.get("reason"))
        lines.append("")

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
