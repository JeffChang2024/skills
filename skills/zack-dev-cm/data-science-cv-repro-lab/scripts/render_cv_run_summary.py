#!/usr/bin/env python3
"""Render a concise markdown summary from a CV run card."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cv_public_safety import is_absolute_like, sanitize_path, sanitize_url_for_display


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object in {path}")
    return data


def display_value(value: Any, *, allow_private_details: bool) -> Any:
    if allow_private_details or not isinstance(value, str):
        return value
    if "://" in value:
        return sanitize_url_for_display(value, allow_raw=False)
    if is_absolute_like(value):
        return sanitize_path(value, allow_absolute_paths=False)
    return value


def add_field(lines: list[str], label: str, value: Any, *, allow_private_details: bool) -> None:
    if value is None:
        return
    if isinstance(value, str) and not value.strip():
        return
    if isinstance(value, list) and not value:
        return
    lines.append(f"- {label}: `{display_value(value, allow_private_details=allow_private_details)}`")


def render_repo_lines(lines: list[str], repos: dict[str, Any]) -> None:
    lines.append("## Source Control")
    for key, label in (
        ("benchmark_repo", "benchmark"),
        ("trainer_repo", "trainer"),
        ("deploy_repo", "deploy"),
    ):
        repo = repos.get(key) or {}
        if not isinstance(repo, dict):
            continue
        name = str(repo.get("name") or "").strip()
        commit = str(repo.get("commit") or "").strip()
        if name or commit:
            joined = " @ ".join(part for part in (name, commit) if part)
            lines.append(f"- {label}: `{joined}`")
    lines.append("")


def render_metrics(lines: list[str], metrics: dict[str, Any]) -> None:
    if not metrics:
        return
    lines.append("### Metrics")
    for key in sorted(metrics):
        lines.append(f"- `{key}`: `{metrics[key]}`")
    lines.append("")


def render_browser(lines: list[str], browser_lane: dict[str, Any], *, allow_private_details: bool) -> None:
    if not browser_lane.get("used"):
        return
    lines.append("## Browser Lane")
    for key in (
        "tool",
        "browser_alias",
        "session_alias",
        "target_url",
        "target_host",
        "target_kind",
        "target_label",
        "url_redacted",
        "runtime_type",
        "requested_mode",
        "actual_mode",
        "attach_status",
        "timeout_seconds",
        "artifact_manifest_path",
        "browser_run_card_path",
        "validation_scorecard_path",
        "local_pull_status",
        "status",
    ):
        add_field(lines, key, browser_lane.get(key), allow_private_details=allow_private_details)
    screenshots = browser_lane.get("screenshots") or []
    if screenshots:
        lines.append(f"- screenshots: `{len(screenshots)}`")
        for path in screenshots[:10]:
            lines.append(
                f"- screenshot_path: `{display_value(path, allow_private_details=allow_private_details)}`"
            )
    lines.append("")


def render_training(lines: list[str], training: dict[str, Any], *, allow_private_details: bool) -> None:
    lines.append("## Training")
    for key in (
        "lane",
        "runtime",
        "gpu_type",
        "run_root",
        "checkpoint_path",
        "export_path",
    ):
        add_field(lines, key, training.get(key), allow_private_details=allow_private_details)
    command = training.get("command") or []
    if command:
        rendered = " ".join(str(display_value(part, allow_private_details=allow_private_details)) for part in command)
        lines.append(f"- command: `{rendered}`")
    config_summary = training.get("config_summary") or {}
    if config_summary:
        lines.append("- config_summary:")
        for key in sorted(config_summary):
            value = display_value(config_summary[key], allow_private_details=allow_private_details)
            lines.append(f"  - `{key}`: `{value}`")
    lines.append("")


def render_evaluation(lines: list[str], evaluation: dict[str, Any], *, allow_private_details: bool) -> None:
    lines.append("## Evaluation")
    for key in (
        "benchmark_set",
        "semantic_summary_path",
        "runtime_summary_path",
        "ui_gate_summary_path",
        "product_surface_summary_path",
        "promotion_bundle_path",
    ):
        add_field(lines, key, evaluation.get(key), allow_private_details=allow_private_details)
    render_metrics(lines, evaluation.get("metrics") or {})
    per_case = evaluation.get("per_case") or []
    if per_case:
        lines.append(f"- per_case_records: `{len(per_case)}`")
    lines.append("")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-card", required=True, help="Path to the input run card JSON file.")
    parser.add_argument("--out", required=True, help="Path to the output markdown file.")
    parser.add_argument("--title", default="", help="Optional explicit title override.")
    args = parser.parse_args()

    run_card_path = Path(args.run_card).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()
    payload = load_json(run_card_path)

    candidate_id = str(payload.get("candidate_id") or "unnamed-candidate")
    title = args.title.strip() or f"CV Run Summary: {candidate_id}"

    lines = [f"# {title}", ""]

    add_field(lines, "candidate_id", payload.get("candidate_id"), allow_private_details=False)
    add_field(lines, "task_id", payload.get("task_id"), allow_private_details=False)
    add_field(lines, "baseline_id", payload.get("baseline_id"), allow_private_details=False)
    add_field(lines, "created_utc", payload.get("created_utc"), allow_private_details=False)
    lines.append("")

    problem = payload.get("problem") or {}
    lines.append("## Problem")
    add_field(lines, "summary", problem.get("summary"), allow_private_details=False)
    add_field(lines, "primary_metric", problem.get("primary_metric"), allow_private_details=False)
    surfaces = problem.get("non_regression_surfaces") or []
    if surfaces:
        for surface in surfaces:
            lines.append(f"- non_regression_surface: `{surface}`")
    lines.append("")

    render_repo_lines(lines, payload.get("source_control") or {})

    data = payload.get("data") or {}
    lines.append("## Data")
    for key in ("dataset_id", "dataset_version", "manifest_path", "manifest_sha256"):
        add_field(lines, key, data.get(key), allow_private_details=False)
    lines.append("")

    render_training(lines, payload.get("training") or {}, allow_private_details=False)
    render_browser(lines, payload.get("browser_lane") or {}, allow_private_details=False)
    render_evaluation(lines, payload.get("evaluation") or {}, allow_private_details=False)

    decision = payload.get("decision") or {}
    lines.append("## Decision")
    for key in ("status", "reason", "rollback_target"):
        add_field(lines, key, decision.get(key), allow_private_details=False)
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
