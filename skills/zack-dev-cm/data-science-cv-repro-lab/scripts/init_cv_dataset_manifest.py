#!/usr/bin/env python3
"""Create a machine-readable dataset manifest skeleton for CV work."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from cv_public_safety import sanitize_path


def parse_key_value(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid key=value item: {item!r}")
        key, value = item.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Path to the output JSON file.")
    parser.add_argument("--dataset-id", required=True, help="Stable dataset identifier.")
    parser.add_argument("--version", default="", help="Optional dataset version string.")
    parser.add_argument("--source-root", action="append", default=[], help="Repeatable source root path.")
    parser.add_argument("--split", action="append", default=[], help="Repeatable split=value pair.")
    parser.add_argument("--label-note", action="append", default=[], help="Repeatable label policy note.")
    parser.add_argument("--sample-count", type=int, default=0, help="Optional total sample count.")
    parser.add_argument("--fingerprint", default="", help="Optional hash or fingerprint value.")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": args.dataset_id,
        "version": args.version,
        "sources": {
            "source_roots": [sanitize_path(path, allow_absolute_paths=False) for path in args.source_root],
            "download_url": "",
            "local_cache_root": "",
        },
        "identity": {
            "sample_count": args.sample_count,
            "fingerprint": args.fingerprint,
            "splits": parse_key_value(args.split),
        },
        "labels": {
            "policy_summary": "",
            "notes": args.label_note,
        },
        "preparation": {
            "post_download_steps": [],
            "conversion_steps": [],
        },
        "artifacts": {
            "preview_paths": [],
            "manifest_owner": "",
            "public_safe": True,
        },
        "notes": [],
    }

    out_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
