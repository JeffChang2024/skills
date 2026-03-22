from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from openforge.git_ops import git_diff_name_only_from, git_rev_parse_head
from openforge.schemas.results import TaskResult

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(slots=True)
class CompletionStatus:
    kind: str
    result: TaskResult | None
    files_changed: list[str]


def _result_path(cwd: Path, task_id: str) -> Path:
    return cwd / ".openforge" / "results" / f"{task_id}.json"


def _matches_scope(path: str, produces: list[str]) -> bool:
    for item in produces:
        prefix = item.rstrip("/")
        if path == prefix or path.startswith(f"{prefix}/"):
            return True
    return False


def detect_completion(
    cwd: Path,
    task_id: str,
    sha_before: str,
    produces: list[str],
) -> CompletionStatus:
    """Detect task completion using structured results first, then git evidence."""
    result_path = _result_path(cwd, task_id)
    if result_path.exists():
        result = TaskResult.model_validate_json(result_path.read_text(encoding="utf-8"))
        return CompletionStatus(
            kind=result.status,
            result=result,
            files_changed=result.files_modified,
        )

    sha_after = git_rev_parse_head(cwd)
    files_changed = git_diff_name_only_from(sha_before, cwd)
    if sha_after != sha_before or files_changed:
        if produces:
            relevant = [path for path in files_changed if _matches_scope(path, produces)]
            if relevant:
                return CompletionStatus(kind="completed", result=None, files_changed=relevant)
        return CompletionStatus(kind="completed", result=None, files_changed=files_changed)

    return CompletionStatus(kind="ambiguous", result=None, files_changed=[])


def cleanup_result_envelope(cwd: Path, task_id: str) -> None:
    """Remove the result envelope file after processing."""
    path = _result_path(cwd, task_id)
    if path.exists():
        path.unlink()
