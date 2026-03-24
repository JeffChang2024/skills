#!/usr/bin/env python3
"""Run the ride-receipts hybrid pipeline.

Pipeline:
1. init DB
2. optionally fetch emails into data/emails/
3. deterministic Python extraction into data/rides/
4. validate extracted rides into rides_flagged.jsonl
5. build a repair worklist for Gateway-backed LLM repair
6. optionally import into SQLite if no flagged rows remain

This script intentionally does NOT call the Gateway-backed LLM itself.
Instead it prepares the repair queue and stops before import when flagged rows remain,
so the repair step can run targeted one-email-at-a-time LLM requests and then re-run with --skip-fetch.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
DEFAULT_DB = DATA_DIR / "rides.sqlite"
DEFAULT_EMAILS_DIR = DATA_DIR / "emails"
DEFAULT_RIDES_DIR = DATA_DIR / "rides"
DEFAULT_JSONL = DATA_DIR / "rides_extracted.jsonl"
DEFAULT_FLAGGED = DATA_DIR / "rides_flagged.jsonl"
DEFAULT_WORKLIST = DATA_DIR / "rides_repair_worklist.jsonl"
DEFAULT_SCHEMA = ROOT / "skills/ride-receipts-llm/references/schema_rides.sql"


def run(cmd: list[str], *, capture=False):
    if capture:
        res = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return res.stdout
    subprocess.run(cmd, check=True)
    return None


def build_jsonl_from_rides(rides_dir: Path, jsonl_path: Path):
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("w", encoding="utf-8") as out:
        for path in sorted(rides_dir.glob("*.json")):
            out.write(json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False) + "\n")


def validate(rides_dir: Path, jsonl_path: Path, flagged_path: Path):
    build_jsonl_from_rides(rides_dir, jsonl_path)
    stdout = run([
        "python3",
        "skills/ride-receipts-llm/scripts/validate_extracted_rides.py",
        "--in", str(jsonl_path),
        "--out", str(flagged_path),
    ], capture=True)
    lines = [line for line in stdout.splitlines() if line.strip()]
    return json.loads(lines[-1]) if lines else {"rows": 0, "flagged": 0, "out": str(flagged_path)}


def write_repair_worklist(flagged_path: Path, emails_dir: Path, rides_dir: Path, worklist_path: Path):
    stdout = run([
        "python3",
        "skills/ride-receipts-llm/scripts/list_flagged_ride_repairs.py",
        "--flagged", str(flagged_path),
        "--emails-dir", str(emails_dir),
        "--rides-dir", str(rides_dir),
    ], capture=True)
    lines = [line for line in stdout.splitlines() if line.strip()]
    work_items = []
    summary = None
    for line in lines:
        item = json.loads(line)
        if "flagged_rows" in item:
            summary = item
        else:
            work_items.append(item)
    worklist_path.parent.mkdir(parents=True, exist_ok=True)
    with worklist_path.open("w", encoding="utf-8") as out:
        for item in work_items:
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
    return {"work_items": len(work_items), "summary": summary or {"flagged_rows": len(work_items)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", help="Gmail account for gog fetch step")
    ap.add_argument("--after", help="Only include emails after YYYY-MM-DD")
    ap.add_argument("--before", help="Only include emails before YYYY-MM-DD")
    ap.add_argument("--max-per-provider", type=int, default=5000)
    ap.add_argument("--providers", help="Comma-separated provider list")
    ap.add_argument("--skip-fetch", action="store_true", help="Reuse existing data/emails without refetching")
    ap.add_argument("--skip-init-db", action="store_true")
    ap.add_argument("--allow-import-with-flagged", action="store_true", help="Import into SQLite even if flagged rows remain")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    ap.add_argument("--emails-dir", default=str(DEFAULT_EMAILS_DIR))
    ap.add_argument("--rides-dir", default=str(DEFAULT_RIDES_DIR))
    ap.add_argument("--jsonl", default=str(DEFAULT_JSONL))
    ap.add_argument("--flagged", default=str(DEFAULT_FLAGGED))
    ap.add_argument("--worklist", default=str(DEFAULT_WORKLIST))
    args = ap.parse_args()

    db = Path(args.db)
    schema = Path(args.schema)
    emails_dir = Path(args.emails_dir)
    rides_dir = Path(args.rides_dir)
    jsonl_path = Path(args.jsonl)
    flagged_path = Path(args.flagged)
    worklist_path = Path(args.worklist)

    emails_dir.mkdir(parents=True, exist_ok=True)
    rides_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_init_db:
        run([
            "python3",
            "skills/ride-receipts-llm/scripts/init_db.py",
            "--db", str(db),
            "--schema", str(schema),
        ])

    if not args.skip_fetch:
        if not args.account:
            raise SystemExit("--account is required unless --skip-fetch is set")
        cmd = [
            "python3",
            "skills/ride-receipts-llm/scripts/fetch_emails_dir.py",
            "--account", args.account,
            "--max-per-provider", str(args.max_per_provider),
            "--out-dir", str(emails_dir),
        ]
        if args.after:
            cmd += ["--after", args.after]
        if args.before:
            cmd += ["--before", args.before]
        if args.providers:
            cmd += ["--providers", args.providers]
        run(cmd)

    run([
        "python3",
        "skills/ride-receipts-llm/scripts/extract_rides_xpath.py",
        str(emails_dir),
        "--output", str(rides_dir),
    ])

    validation = validate(rides_dir, jsonl_path, flagged_path)
    worklist = write_repair_worklist(flagged_path, emails_dir, rides_dir, worklist_path)

    flagged_rows = int(validation.get("flagged") or 0)

    if flagged_rows and not args.allow_import_with_flagged:
        print(json.dumps({
            "status": "repair_required",
            "db": str(db),
            "emails_dir": str(emails_dir),
            "rides_dir": str(rides_dir),
            "flagged_jsonl": str(flagged_path),
            "repair_worklist": str(worklist_path),
            "rows": validation.get("rows"),
            "flagged": flagged_rows,
            "next_step": "Run targeted Gateway-backed LLM repairs for worklist items, then re-run this script with --skip-fetch.",
        }, ensure_ascii=False))
        return

    run([
        "python3",
        "skills/ride-receipts-llm/scripts/insert_rides_sqlite_dir.py",
        "--db", str(db),
        "--schema", str(schema),
        "--rides-dir", str(rides_dir),
    ])

    print(json.dumps({
        "status": "imported",
        "db": str(db),
        "emails_dir": str(emails_dir),
        "rides_dir": str(rides_dir),
        "flagged_jsonl": str(flagged_path),
        "repair_worklist": str(worklist_path),
        "rows": validation.get("rows"),
        "flagged": flagged_rows,
        "work_items": worklist.get("work_items"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as err:
        print(err, file=sys.stderr)
        sys.exit(err.returncode or 1)
err.returncode or 1)
