#!/usr/bin/env python3
"""Submit converted trajectory files to the ClawTraces collection server.

Usage:
    python submit.py [--output-dir PATH] [--count-only]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, os.path.dirname(__file__))

from lib.auth import get_server_url, get_stored_key, handle_401

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
MANIFEST_FILENAME = "manifest.json"


def load_manifest(output_dir: str) -> dict:
    """Load the submission manifest."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"submitted": {}, "rejected": {}}


def save_manifest(output_dir: str, manifest: dict):
    """Save the submission manifest."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def _load_stats(trajectory_path: str) -> str | None:
    """Load the stats JSON file that corresponds to a trajectory file."""
    stats_path = trajectory_path.replace(".trajectory.json", ".stats.json")
    if os.path.isfile(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def upload_file(server_url: str, secret_key: str, file_path: str) -> dict:
    """Upload a single trajectory file to the server, with optional stats."""
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    stats_json = _load_stats(file_path)

    boundary = "----ClawTracesBoundary9876543210"
    parts = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode("utf-8") + file_data + b"\r\n"

    if stats_json:
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="stats"\r\n'
            f"Content-Type: application/json\r\n"
            f"\r\n"
            f"{stats_json}\r\n"
        ).encode("utf-8")

    body = parts + f"--{boundary}--\r\n".encode("utf-8")

    url = f"{server_url}/upload"
    req = Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Secret-Key": secret_key,
            "User-Agent": "ClawTraces/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 401:
            handle_401()
            return {"error": "unauthorized"}
        error_body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": error_body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def query_count(server_url: str, secret_key: str) -> dict:
    """Query the server for submission count."""
    url = f"{server_url}/count"
    req = Request(url, headers={"X-Secret-Key": secret_key, "User-Agent": "ClawTraces/1.0"}, method="GET")

    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 401:
            handle_401()
            return {"error": "unauthorized"}
        return {"error": str(e)}
    except URLError as e:
        return {"error": str(e)}


def submit_all(output_dir: str, server_url: str, secret_key: str) -> dict:
    """Submit all new trajectory files.

    Returns summary dict with success_count, error_count, total.
    """
    manifest = load_manifest(output_dir)
    submitted = manifest.get("submitted", {})

    all_files = [
        f for f in os.listdir(output_dir)
        if f.endswith(".trajectory.json")
    ]

    new_files = [f for f in all_files if f not in submitted]

    if not new_files:
        count_result = query_count(server_url, secret_key)
        return {
            "success_count": 0,
            "error_count": 0,
            "new_files": 0,
            "server_total": count_result.get("count", "unknown"),
        }

    success_count = 0
    error_count = 0
    auth_failed = False

    for filename in new_files:
        file_path = os.path.join(output_dir, filename)
        print(f"  Uploading: {filename}...", end=" ", flush=True)

        result = upload_file(server_url, secret_key, file_path)

        if result.get("error") == "unauthorized":
            print("FAILED (unauthorized)")
            error_count += 1
            auth_failed = True
            break
        elif result.get("error") == "duplicate":
            # Already on server — record in manifest to avoid retrying
            print("OK (already submitted)")
            success_count += 1
            submitted[filename] = {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "server_response": "duplicate",
            }
            manifest["submitted"] = submitted
            save_manifest(output_dir, manifest)
        elif "error" in result:
            print(f"FAILED ({result['error']})")
            error_count += 1
        else:
            print("OK")
            success_count += 1
            submitted[filename] = {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "server_response": result.get("status", "ok"),
            }
            manifest["submitted"] = submitted
            save_manifest(output_dir, manifest)

    # Only query server count if auth is still valid
    server_total: int | str = "unknown"
    if not auth_failed:
        count_result = query_count(server_url, secret_key)
        server_total = count_result.get("count", "unknown")

    return {
        "success_count": success_count,
        "error_count": error_count,
        "new_files": len(new_files),
        "server_total": server_total,
    }


def main():
    parser = argparse.ArgumentParser(description="Submit trajectory files to collection server")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Directory with .trajectory.json files")
    parser.add_argument("--count-only", action="store_true", help="Only query submission count")
    args = parser.parse_args()

    key = get_stored_key()
    if not key:
        print("Not authenticated. Please run /clawtraces to authenticate first.", file=sys.stderr)
        sys.exit(1)

    server_url = get_server_url()

    if args.count_only:
        result = query_count(server_url, key)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Total submitted: {result.get('count', 0)}")
        return

    result = submit_all(args.output_dir, server_url, key)
    print(f"\nDone: {result['success_count']} uploaded, {result['error_count']} failed")
    print(f"Your total submissions: {result['server_total']}")


if __name__ == "__main__":
    main()
