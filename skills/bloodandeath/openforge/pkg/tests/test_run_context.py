from __future__ import annotations

from typing import TYPE_CHECKING

from openforge.run_context import (
    append_task_context,
    build_context_from_result,
    load_run_context,
    render_context_summary,
)
from openforge.schemas.results import TaskContextEntry, TaskResult

if TYPE_CHECKING:
    from pathlib import Path


def test_append_and_load_run_context_roundtrip(tmp_path: Path) -> None:
    entry = TaskContextEntry(
        task_id="task-1",
        phase_id="phase-a",
        agent_id="cloud",
        summary="Did the work",
        decisions=["Use helper"],
        files_modified=["src/app.py"],
    )

    append_task_context(tmp_path, entry)
    loaded = load_run_context(tmp_path)

    assert loaded == [entry]


def test_build_context_from_result_uses_structured_payload() -> None:
    result = TaskResult(
        task_id="task-1",
        status="completed",
        summary="Implemented feature",
        decisions=["Added validator"],
        files_modified=["src/app.py"],
        artifacts=["report.txt"],
        unresolved=["edge case"],
    )

    entry = build_context_from_result("task-1", "phase-a", "cloud", result, ["fallback.py"])

    assert entry.summary == "Implemented feature"
    assert entry.decisions == ["Added validator"]
    assert entry.files_modified == ["src/app.py"]
    assert entry.unresolved == ["edge case"]


def test_build_context_from_result_without_result_uses_heuristic() -> None:
    entry = build_context_from_result("task-1", "phase-a", "cloud", None, ["src/app.py"])

    assert "without a structured result envelope" in entry.summary
    assert entry.files_modified == ["src/app.py"]


def test_render_context_summary_respects_budget() -> None:
    entries = [
        TaskContextEntry(task_id=f"task-{i}", phase_id="phase", agent_id="cloud", summary="x" * 40)
        for i in range(6)
    ]

    summary = render_context_summary(entries, max_chars=180)

    assert "task-5" in summary
    assert len(summary) <= 180
