from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from openforge.schemas.state import PhaseStatus, RunConfig, RunState, StageStatus, TaskState

if TYPE_CHECKING:
    from pathlib import Path

    from openforge.schemas.prd import ForgePRD

_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"dispatched"},
    "dispatched": {"agent_succeeded", "agent_failed", "halted_security", "halted_manual"},
    "agent_succeeded": {"scope_verified", "scope_failed", "halted_manual"},
    "agent_failed": {"dispatched", "halted_escalation"},
    "scope_verified": {"validation_passed", "validation_failed", "halted_manual"},
    "scope_failed": {"halted_security"},
    "validation_passed": {"complete"},
    "validation_failed": {"dispatched", "halted_escalation"},
    "complete": set(),
    "halted_escalation": set(),
    "halted_security": set(),
    "halted_manual": set(),
}

_SPECIAL_TRANSITIONS: dict[str, set[str]] = {
    "complete": {"validation_failed"},
}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def init_run_state(
    run_id: str,
    prd_path: str,
    prd_hash: str,
    cwd: str,
    config: RunConfig,
    prd: ForgePRD,
) -> RunState:
    """Create initial run state from parsed PRD."""
    timestamp = _now_iso()
    tasks = {
        task.id: TaskState(phase=phase.id)
        for phase in prd.phases
        for task in phase.tasks
    }
    phases = {phase.id: PhaseStatus() for phase in prd.phases}
    stage_numbers = {phase.config.stage for phase in prd.phases}
    stages = {str(stage): StageStatus() for stage in sorted(stage_numbers)}
    return RunState(
        run_id=run_id,
        prd_path=os.path.abspath(prd_path),
        prd_hash=prd_hash,
        cwd=os.path.abspath(cwd),
        started_at=timestamp,
        updated_at=timestamp,
        config=config,
        tasks=tasks,
        phases=phases,
        stages=stages,
    )


def save_state(state: RunState, run_dir: Path) -> None:
    """Atomic write: write to .tmp then rename."""
    run_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = run_dir / ".state.json.tmp"
    final_path = run_dir / "state.json"
    tmp_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    os.rename(tmp_path, final_path)


def load_state(run_dir: Path) -> RunState:
    """Load state.json from run directory."""
    return RunState.model_validate_json((run_dir / "state.json").read_text(encoding="utf-8"))


def update_task_state(state: RunState, task_id: str, new_state: str) -> None:
    """Transition a task to a new state. Validates the transition is legal per §5.3."""
    if task_id not in state.tasks:
        msg = f"unknown task id '{task_id}'"
        raise KeyError(msg)

    task_state = state.tasks[task_id]
    current_state = task_state.state
    allowed = _ALLOWED_TRANSITIONS.get(current_state)
    if allowed is None:
        msg = f"unknown current task state '{current_state}'"
        raise ValueError(msg)
    if new_state not in allowed:
        msg = f"illegal task transition for '{task_id}': {current_state} -> {new_state}"
        raise ValueError(msg)

    task_state.state = new_state
    state.updated_at = _now_iso()


def mark_task_validation_failed(state: RunState, task_id: str) -> None:
    """Mark a completed task as validation_failed through an explicit special-case rule.

    Phase/stage validators run after task completion, so validator failures must be able to
    attribute back to the completed task without bypassing transition checks.
    """
    if task_id not in state.tasks:
        msg = f"unknown task id '{task_id}'"
        raise KeyError(msg)

    task_state = state.tasks[task_id]
    current_state = task_state.state
    allowed = _SPECIAL_TRANSITIONS.get(current_state, set())
    if "validation_failed" not in allowed:
        msg = f"illegal task transition for '{task_id}': {current_state} -> validation_failed"
        raise ValueError(msg)

    task_state.state = "validation_failed"
    state.updated_at = _now_iso()


def compute_prd_hash(prd_path: Path) -> str:
    """SHA-256 hash of PRD file contents."""
    return hashlib.sha256(prd_path.read_bytes()).hexdigest()
