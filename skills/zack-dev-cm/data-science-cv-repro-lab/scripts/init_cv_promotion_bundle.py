#!/usr/bin/env python3
"""Create a machine-readable promotion bundle entry point for a CV candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from cv_public_safety import is_absolute_like, sanitize_path


def sanitize_ref(
    value: str,
    *,
    alias_roots: list[tuple[Path | None, str]],
    allow_absolute_paths: bool,
) -> str:
    value = value.strip()
    if not value:
        return ""
    if is_absolute_like(value):
        return sanitize_path(
            value,
            alias_roots=alias_roots,
            allow_absolute_paths=allow_absolute_paths,
        )
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Path to the output JSON file.")
    parser.add_argument("--candidate-id", required=True, help="Stable candidate identifier.")
    parser.add_argument("--decision", default="hold", help="promote, hold, or rollback.")
    parser.add_argument("--reason", default="", help="Short benchmark-backed reason.")
    parser.add_argument("--rollback-target", default="", help="Optional rollback target or baseline id.")
    parser.add_argument("--dataset-manifest", default="", help="Dataset manifest path or id.")
    parser.add_argument("--run-card", default="", help="Candidate run card path.")
    parser.add_argument("--browser-run-card", default="", help="Browser run card path.")
    parser.add_argument("--validation-scorecard", default="", help="Validation scorecard path.")
    parser.add_argument("--artifact-manifest", default="", help="Artifact manifest path.")
    parser.add_argument("--semantic-summary", default="", help="Semantic benchmark summary path.")
    parser.add_argument("--runtime-summary", default="", help="Runtime or service summary path.")
    parser.add_argument("--product-surface-summary", default="", help="Product-surface summary path.")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_root = out_path.parent
    alias_roots = [(bundle_root, "$PROMOTION_BUNDLE_DIR")]

    payload = {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_id": args.candidate_id,
        "decision": {
            "status": args.decision,
            "reason": args.reason,
            "rollback_target": args.rollback_target,
        },
        "artifacts": {
            "dataset_manifest": sanitize_ref(
                args.dataset_manifest,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "run_card": sanitize_ref(
                args.run_card,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "browser_run_card": sanitize_ref(
                args.browser_run_card,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "validation_scorecard": sanitize_ref(
                args.validation_scorecard,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "artifact_manifest": sanitize_ref(
                args.artifact_manifest,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "semantic_summary": sanitize_ref(
                args.semantic_summary,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "runtime_summary": sanitize_ref(
                args.runtime_summary,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "product_surface_summary": sanitize_ref(
                args.product_surface_summary,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
        },
        "notes": [],
    }

    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
