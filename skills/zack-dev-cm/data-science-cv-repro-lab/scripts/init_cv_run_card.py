#!/usr/bin/env python3
"""Create a machine-readable run card skeleton for a CV candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Path to the output JSON file.")
    parser.add_argument("--candidate-id", required=True, help="Stable candidate identifier.")
    parser.add_argument("--task-id", default="", help="Optional task or investigation identifier.")
    parser.add_argument("--baseline-id", default="", help="Optional current trusted baseline identifier.")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": args.task_id,
        "candidate_id": args.candidate_id,
        "baseline_id": args.baseline_id,
        "problem": {
            "summary": "",
            "primary_metric": "",
            "non_regression_surfaces": [],
        },
        "source_control": {
            "benchmark_repo": {"name": "", "commit": ""},
            "trainer_repo": {"name": "", "commit": ""},
            "deploy_repo": {"name": "", "commit": ""},
        },
        "data": {
            "dataset_id": "",
            "dataset_version": "",
            "manifest_path": "",
            "manifest_sha256": "",
        },
        "training": {
            "lane": "",
            "runtime": "",
            "gpu_type": "",
            "command": [],
            "run_root": "",
            "checkpoint_path": "",
            "export_path": "",
            "config_summary": {},
        },
        "browser_lane": {
            "used": False,
            "tool": "",
            "browser_alias": "",
            "session_alias": "",
            "target_url": "",
            "target_host": "",
            "target_kind": "",
            "target_label": "",
            "url_redacted": False,
            "runtime_type": "",
            "requested_mode": "",
            "actual_mode": "",
            "attach_status": "",
            "timeout_seconds": 0,
            "screenshots": [],
            "artifact_manifest_path": "",
            "browser_run_card_path": "",
            "validation_scorecard_path": "",
            "local_pull_status": "",
            "status": "",
        },
        "evaluation": {
            "benchmark_set": "",
            "semantic_summary_path": "",
            "runtime_summary_path": "",
            "ui_gate_summary_path": "",
            "product_surface_summary_path": "",
            "promotion_bundle_path": "",
            "metrics": {},
            "per_case": [],
        },
        "decision": {
            "status": "hold",
            "reason": "",
            "rollback_target": "",
        },
    }

    out_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
