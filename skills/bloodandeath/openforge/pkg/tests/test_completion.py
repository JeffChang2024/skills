from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from openforge.completion import cleanup_result_envelope, detect_completion

if TYPE_CHECKING:
    from pathlib import Path


def test_detect_completion_prefers_result_envelope(tmp_path: Path) -> None:
    result_dir = tmp_path / ".openforge" / "results"
    result_dir.mkdir(parents=True)
    (result_dir / "task-1.json").write_text(
        '{"task_id":"task-1","status":"completed","summary":"done","files_modified":["src/app.py"]}',
        encoding="utf-8",
    )

    status = detect_completion(tmp_path, "task-1", "abc123", ["src/"])

    assert status.kind == "completed"
    assert status.result is not None
    assert status.files_changed == ["src/app.py"]


def test_detect_completion_falls_back_to_git_changes(tmp_path: Path) -> None:
    with (
        patch("openforge.completion.git_rev_parse_head", return_value="def456"),
        patch(
            "openforge.completion.git_diff_name_only_from",
            return_value=["src/app.py", "README.md"],
        ),
    ):
        status = detect_completion(tmp_path, "task-1", "abc123", ["src/"])

    assert status.kind == "completed"
    assert status.files_changed == ["src/app.py"]


def test_detect_completion_returns_ambiguous_without_changes(tmp_path: Path) -> None:
    with (
        patch("openforge.completion.git_rev_parse_head", return_value="abc123"),
        patch("openforge.completion.git_diff_name_only_from", return_value=[]),
    ):
        status = detect_completion(tmp_path, "task-1", "abc123", ["src/"])

    assert status.kind == "ambiguous"
    assert status.files_changed == []


def test_cleanup_result_envelope_removes_file(tmp_path: Path) -> None:
    result_path = tmp_path / ".openforge" / "results"
    result_path.mkdir(parents=True)
    envelope = result_path / "task-1.json"
    envelope.write_text("{}", encoding="utf-8")

    cleanup_result_envelope(tmp_path, "task-1")

    assert not envelope.exists()
