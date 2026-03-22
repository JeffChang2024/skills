from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from openforge.parser import parse_prd
from openforge.schemas.state import RunConfig
from openforge.state import (
    compute_prd_hash,
    init_run_state,
    load_state,
    mark_task_validation_failed,
    save_state,
    update_task_state,
)

_FIXTURES = Path(__file__).parent / "fixtures"


def _build_state() -> tuple[object, object]:
    prd = parse_prd(_FIXTURES / "valid-multi-stage.md")
    state = init_run_state(
        run_id="run-123",
        prd_path=str(_FIXTURES / "valid-multi-stage.md"),
        prd_hash="abc123",
        cwd=".",
        config=RunConfig(),
        prd=prd,
    )
    return prd, state


def test_init_run_state_queues_all_tasks() -> None:
    prd, state = _build_state()

    assert state.run_id == "run-123"
    assert state.prd_hash == "abc123"
    assert set(state.tasks) == {"setup-project", "build-feature"}
    assert all(task_state.state == "queued" for task_state in state.tasks.values())
    assert state.tasks["setup-project"].phase == "scaffold"
    assert state.tasks["build-feature"].phase == "implement"
    assert set(state.phases) == {phase.id for phase in prd.phases}
    assert set(state.stages) == {"1", "2"}


def test_save_and_load_state_roundtrip(tmp_path: Path) -> None:
    _, state = _build_state()
    state.base_commit = "deadbeef"

    save_state(state, tmp_path)
    loaded = load_state(tmp_path)

    assert loaded == state


def test_update_task_state_allows_legal_transitions() -> None:
    _, state = _build_state()

    update_task_state(state, "setup-project", "dispatched")
    update_task_state(state, "setup-project", "agent_succeeded")
    update_task_state(state, "setup-project", "scope_verified")
    update_task_state(state, "setup-project", "validation_passed")
    update_task_state(state, "setup-project", "complete")

    assert state.tasks["setup-project"].state == "complete"


def test_update_task_state_rejects_illegal_transitions() -> None:
    _, state = _build_state()

    with pytest.raises(ValueError, match="queued -> complete"):
        update_task_state(state, "setup-project", "complete")

    update_task_state(state, "setup-project", "dispatched")
    update_task_state(state, "setup-project", "agent_succeeded")
    update_task_state(state, "setup-project", "scope_verified")
    update_task_state(state, "setup-project", "validation_passed")
    update_task_state(state, "setup-project", "complete")

    with pytest.raises(ValueError, match="complete -> dispatched"):
        update_task_state(state, "setup-project", "dispatched")


def test_mark_task_validation_failed_allows_only_special_case_from_complete() -> None:
    _, state = _build_state()

    update_task_state(state, "setup-project", "dispatched")
    update_task_state(state, "setup-project", "agent_succeeded")
    update_task_state(state, "setup-project", "scope_verified")
    update_task_state(state, "setup-project", "validation_passed")
    update_task_state(state, "setup-project", "complete")

    mark_task_validation_failed(state, "setup-project")

    assert state.tasks["setup-project"].state == "validation_failed"

    with pytest.raises(ValueError, match="queued -> validation_failed"):
        mark_task_validation_failed(state, "build-feature")


def test_compute_prd_hash_is_consistent(tmp_path: Path) -> None:
    prd_path = tmp_path / "prd.md"
    prd_path.write_text("# PRD: Hash Test\n", encoding="utf-8")

    first = compute_prd_hash(prd_path)
    second = compute_prd_hash(prd_path)

    assert first == second
    assert len(first) == 64


def test_save_state_atomic_write_exposes_valid_json_mid_write(tmp_path: Path) -> None:
    _, state = _build_state()
    observed: dict[str, object] = {}
    original_rename = os.rename

    def _inspect_then_rename(src: str | Path, dst: str | Path) -> None:
        content = Path(src).read_text(encoding="utf-8")
        observed["parsed"] = json.loads(content)
        original_rename(src, dst)

    with patch("openforge.state.os.rename", side_effect=_inspect_then_rename):
        save_state(state, tmp_path)

    parsed = observed["parsed"]
    assert isinstance(parsed, dict)
    assert parsed["run_id"] == state.run_id
    assert load_state(tmp_path).run_id == state.run_id
