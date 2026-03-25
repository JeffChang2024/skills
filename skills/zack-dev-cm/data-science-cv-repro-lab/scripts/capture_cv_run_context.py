#!/usr/bin/env python3
"""Capture a compact, reproducible snapshot of a CV experiment context."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from cv_public_safety import sanitize_path


DEFAULT_MODULES = [
    "torch",
    "torchvision",
    "numpy",
    "albumentations",
    "cv2",
    "onnx",
    "onnxruntime",
    "ultralytics",
    "mmseg",
    "mmcv",
    "timm",
    "segmentation_models_pytorch",
    "wandb",
    "mlflow",
]

def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def parse_key_value(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid --param value: {item!r}, expected key=value")
        key, value = item.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def git_info(
    repo_root: Path,
    *,
    alias_roots: list[tuple[Path | None, str]],
    allow_absolute_paths: bool,
) -> dict[str, Any]:
    info: dict[str, Any] = {"is_git_repo": False}
    code, _, _ = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
    if code != 0:
        return info
    info["is_git_repo"] = True
    info["repo_root"] = sanitize_path(
        repo_root,
        alias_roots=alias_roots,
        allow_absolute_paths=allow_absolute_paths,
    )
    for key, cmd in {
        "head": ["git", "rev-parse", "HEAD"],
        "short_head": ["git", "rev-parse", "--short", "HEAD"],
        "branch": ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        "describe": ["git", "describe", "--always", "--dirty", "--tags"],
    }.items():
        _, out, _ = run(cmd, cwd=repo_root)
        info[key] = out or None
    _, status_out, _ = run(["git", "status", "--short"], cwd=repo_root)
    status_lines = [line for line in status_out.splitlines() if line.strip()]
    info["dirty"] = bool(status_lines)
    info["status_short"] = status_lines[:200]
    info["modified_count"] = sum(1 for line in status_lines if not line.startswith("??"))
    info["untracked_count"] = sum(1 for line in status_lines if line.startswith("??"))
    return info


def module_versions(names: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    package_index = importlib_metadata.packages_distributions()
    for name in names:
        distributions = package_index.get(name) or [name]
        installed = False
        record: dict[str, Any] = {"installed": False}
        for dist_name in distributions:
            try:
                version = importlib_metadata.version(dist_name)
            except importlib_metadata.PackageNotFoundError:
                continue
            installed = True
            record = {
                "installed": True,
                "version": version,
                "distribution": dist_name,
            }
            break
        if not installed:
            record["distribution_candidates"] = distributions
        data[name] = record
    return data


def gpu_snapshot() -> dict[str, Any]:
    code, out, err = run(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ]
    )
    if code != 0:
        return {"available": False, "error": err or "nvidia-smi unavailable"}
    rows = []
    for line in out.splitlines():
        parts = [chunk.strip() for chunk in line.split(",")]
        if len(parts) != 5:
            continue
        rows.append(
            {
                "name": parts[0],
                "driver_version": parts[1],
                "memory_total_mib": int(parts[2]),
                "memory_used_mib": int(parts[3]),
                "utilization_gpu_pct": int(parts[4]),
            }
        )
    return {"available": True, "gpus": rows}


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# CV Run Context: {payload.get('label') or 'unnamed'}",
        "",
        f"- captured_utc: `{payload['captured_utc']}`",
        f"- cwd: `{payload['cwd']}`",
        f"- python: `{payload['python']['version']}`",
        f"- platform: `{payload['platform']['platform']}`",
    ]
    git = payload.get("git") or {}
    if git.get("is_git_repo"):
        lines.extend(
            [
                f"- git branch: `{git.get('branch')}`",
                f"- git head: `{git.get('short_head')}`",
                f"- git dirty: `{git.get('dirty')}`",
            ]
        )
    gpu = payload.get("gpu") or {}
    if gpu.get("available") and gpu.get("gpus"):
        first = gpu["gpus"][0]
        lines.append(
            f"- gpu0: `{first['name']}`, util `{first['utilization_gpu_pct']}%`, "
            f"mem `{first['memory_used_mib']}/{first['memory_total_mib']} MiB`"
        )
    if payload.get("params"):
        lines.append("")
        lines.append("## Params")
        for key, value in sorted(payload["params"].items()):
            lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown-out")
    parser.add_argument("--label")
    parser.add_argument("--param", action="append", default=[])
    parser.add_argument("--module", action="append", default=[])
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()
    md_path = Path(args.markdown_out).expanduser().resolve() if args.markdown_out else None
    alias_roots = [(repo_root, "$REPO_ROOT")]

    payload: dict[str, Any] = {
        "label": args.label,
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "cwd": sanitize_path(
            Path.cwd(),
            alias_roots=alias_roots,
            allow_absolute_paths=False,
        ),
        "python": {
            "executable": sanitize_path(
                sys.executable,
                alias_roots=alias_roots,
                allow_absolute_paths=False,
            ),
            "version": sys.version.replace("\n", " "),
        },
        "platform": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "git": git_info(
            repo_root,
            alias_roots=alias_roots,
            allow_absolute_paths=False,
        ),
        "params": parse_key_value(args.param),
        "modules": module_versions(args.module or DEFAULT_MODULES),
        "gpu": gpu_snapshot(),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if md_path:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
