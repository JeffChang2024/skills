from __future__ import annotations

from typing import TYPE_CHECKING

from openforge.schemas.results import TaskContextEntry, TaskResult

if TYPE_CHECKING:
    from pathlib import Path

_CONTEXT_FILE = "task_context.jsonl"


def load_run_context(run_dir: Path) -> list[TaskContextEntry]:
    """Load accumulated task context from run directory."""
    path = run_dir / _CONTEXT_FILE
    if not path.exists():
        return []
    entries: list[TaskContextEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(TaskContextEntry.model_validate_json(line))
    return entries


def append_task_context(run_dir: Path, entry: TaskContextEntry) -> None:
    """Append a completed task's context to the run log."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / _CONTEXT_FILE
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry.model_dump_json())
        handle.write("\n")


def build_context_from_result(
    task_id: str,
    phase_id: str,
    agent_id: str,
    result: TaskResult | None,
    files_modified: list[str],
) -> TaskContextEntry:
    """Build a context entry from a task result (or heuristic if no result)."""
    if result is None:
        return TaskContextEntry(
            task_id=task_id,
            phase_id=phase_id,
            agent_id=agent_id,
            summary=f"Task {task_id} completed without a structured result envelope.",
            files_modified=files_modified,
            checks_passed=True,
        )

    return TaskContextEntry(
        task_id=task_id,
        phase_id=phase_id,
        agent_id=agent_id,
        summary=result.summary or f"Task {task_id} finished with status {result.status}.",
        decisions=result.decisions,
        files_modified=result.files_modified or files_modified,
        artifacts=result.artifacts,
        checks_passed=result.status not in {"blocked", "failed"},
        unresolved=result.unresolved,
    )


def render_context_summary(entries: list[TaskContextEntry], max_chars: int = 5000) -> str:
    """Render accumulated context as a prompt-friendly string."""
    if not entries:
        return ""

    rendered: list[str] = []
    used = 0
    for entry in reversed(entries):
        block = (
            f"- [{entry.phase_id}/{entry.task_id}] {entry.summary or 'No summary'}\n"
            f"  agent={entry.agent_id}; files={', '.join(entry.files_modified) or 'None'}; "
            f"checks_passed={'yes' if entry.checks_passed else 'no'}\n"
            f"  decisions={', '.join(entry.decisions) or 'None'}\n"
            f"  unresolved={', '.join(entry.unresolved) or 'None'}\n"
        )
        if used + len(block) > max_chars:
            break
        rendered.append(block.rstrip())
        used += len(block)
    return "\n".join(rendered)
