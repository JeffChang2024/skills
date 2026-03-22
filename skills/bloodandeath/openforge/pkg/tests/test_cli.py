from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from openforge.cli import (
    _exit_code_for_run_state,
    _filter_prd_phases,
    _next_action,
    _run_phase_validator,
    _run_stage_validator,
    _run_task,
    app,
)
from openforge.completion import CompletionStatus
from openforge.git_ops import GitError
from openforge.parser import parse_prd
from openforge.schemas.prd import (
    ForgePRD,
    Phase,
    PhaseConfig,
    RoutingAlias,
    RoutingConfig,
    Task,
    TaskCheck,
    TaskConfig,
)
from openforge.schemas.results import TaskResult
from openforge.schemas.state import AttemptRecord, RunConfig
from openforge.state import init_run_state, update_task_state

_FIXTURES = Path(__file__).parent / "fixtures"


def test_validate_with_valid_prd_exits_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["validate", str(_FIXTURES / "valid-simple.md")])
    assert result.exit_code == 0
    assert "Valid PRD" in result.stdout


def test_validate_with_invalid_prd_exits_one(tmp_path: Path) -> None:
    runner = CliRunner()
    invalid_prd = tmp_path / "invalid.md"
    invalid_prd.write_text(
        "# PRD: Broken\n\n## Objective\nMissing required sections.\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["validate", str(invalid_prd)])
    assert result.exit_code == 1
    assert "Parse error" in result.stdout


def test_plan_with_valid_prd_shows_table() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["plan", str(_FIXTURES / "valid-simple.md")])
    assert result.exit_code == 0
    assert "Execution plan" in result.stdout
    assert "setup" in result.stdout


def test_plan_json_returns_parseable_json() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["plan", str(_FIXTURES / "valid-simple.md"), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["title"] == "Simple Test"
    assert payload["phases"][0]["id"] == "setup"


def test_next_action_redispatches_interrupted_dispatched_task() -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    state = init_run_state(
        "run-123", str(_FIXTURES / "valid-simple.md"), "abc123", ".", RunConfig(), prd
    )
    update_task_state(state, "first-task", "dispatched")
    action = _next_action(state, prd)
    assert action.kind == "dispatch"
    assert action.task is not None
    assert action.task.id == "first-task"


def test_run_task_ambiguous_completion_marks_validation_failed(tmp_path: Path) -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    phase = prd.phases[0]
    task = phase.tasks[0]
    state = init_run_state(
        "run-123", str(_FIXTURES / "valid-simple.md"), "abc123", ".", RunConfig(), prd
    )

    with (
        patch("openforge.cli.load_run_context", return_value=[]),
        patch("openforge.cli.git_rev_parse_head", return_value="abc123"),
        patch("openforge.cli.dispatch_task") as dispatch_mock,
        patch("openforge.cli.git_diff_name_only_from", return_value=[]),
        patch(
            "openforge.cli.detect_completion", return_value=CompletionStatus("ambiguous", None, [])
        ),
        patch("openforge.cli.save_state"),
        patch("openforge.cli._save_task_artifacts"),
    ):
        dispatch_mock.return_value.exit_code = 0
        dispatch_mock.return_value.stdout = "ok"
        dispatch_mock.return_value.stderr = ""
        dispatch_mock.return_value.timed_out = False
        _run_task(state, prd, phase, task, tmp_path, tmp_path, None)

    assert state.tasks[task.id].state == "validation_failed"
    assert state.tasks[task.id].attempts[-1].failure_class == "ambiguous"


def test_filter_prd_phases_keeps_stage_numbers_and_prunes_inactive_validators() -> None:
    prd = parse_prd(_FIXTURES / "valid-multi-stage.md")
    filtered = _filter_prd_phases(prd, include_phase="implement")
    assert [phase.id for phase in filtered.phases] == ["implement"]
    assert filtered.phases[0].config.stage == 2
    assert filtered.stage_validators == {2: "npm test"}


def test_filter_prd_phases_rejects_unknown_phase() -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    with pytest.raises(Exception, match="phase 'missing' not found"):
        _filter_prd_phases(prd, include_phase="missing")


def test_run_task_halts_manually_when_git_head_lookup_fails(tmp_path: Path) -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    phase = prd.phases[0]
    task = phase.tasks[0]
    state = init_run_state(
        "run-123", str(_FIXTURES / "valid-simple.md"), "abc123", ".", RunConfig(), prd
    )

    with (
        patch("openforge.cli.load_run_context", return_value=[]),
        patch(
            "openforge.cli.git_rev_parse_head", side_effect=GitError("git rev-parse HEAD failed")
        ),
        patch("openforge.cli.save_state"),
        patch("openforge.cli._save_task_artifacts"),
        patch("openforge.cli.emit_event"),
    ):
        _run_task(state, prd, phase, task, tmp_path, tmp_path, None)

    assert state.tasks[task.id].state == "halted_manual"
    assert state.tasks[task.id].attempts[-1].failure_class == "git_error"


def test_run_task_failed_check_marks_validation_failed(tmp_path: Path) -> None:
    task = Task(
        id="task-a",
        text="Do work",
        config=TaskConfig(id="task-a", produces=["src/a.py"], checks=[TaskCheck(run="pytest -q")]),
        phase_id="phase-a",
    )
    phase = Phase(id="phase-a", config=PhaseConfig(stage=1, executor="cloud"), tasks=[task])
    prd = ForgePRD(
        title="check test",
        objective="verify checks",
        in_scope=["src/"],
        routing=RoutingConfig(aliases={"cloud": RoutingAlias(agent="openforge-cloud")}),
        phases=[phase],
    )
    state = init_run_state("run-123", "prd.md", "abc123", ".", RunConfig(), prd)

    with (
        patch("openforge.cli.load_run_context", return_value=[]),
        patch("openforge.cli.git_rev_parse_head", side_effect=["abc123", "abc123"]),
        patch("openforge.cli.git_diff_name_only_from", return_value=["src/a.py"]),
        patch("openforge.cli.verify_scope", return_value=(True, [])),
        patch("openforge.cli.dispatch_task") as dispatch_mock,
        patch("openforge.cli.run_validator") as validator_mock,
        patch("openforge.cli.save_state"),
        patch("openforge.cli._save_task_artifacts"),
    ):
        dispatch_mock.return_value.exit_code = 0
        dispatch_mock.return_value.stdout = "ok"
        dispatch_mock.return_value.stderr = ""
        dispatch_mock.return_value.timed_out = False
        validator_mock.return_value.exit_code = 1
        validator_mock.return_value.stdout = "bad"
        validator_mock.return_value.stderr = ""
        validator_mock.return_value.timed_out = False
        _run_task(state, prd, phase, task, tmp_path, tmp_path, None)

    assert state.tasks[task.id].state == "validation_failed"
    assert state.tasks[task.id].attempts[-1].failure_class == "validation_failed"


def test_run_task_complete_appends_context_and_commits(tmp_path: Path) -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    phase = prd.phases[0]
    task = phase.tasks[0]
    state = init_run_state(
        "run-123", str(_FIXTURES / "valid-simple.md"), "abc123", ".", RunConfig(), prd
    )
    completion = CompletionStatus(
        "completed",
        TaskResult(
            task_id=task.id,
            status="completed",
            summary="Implemented task",
            files_modified=["src/file.py"],
        ),
        ["src/file.py"],
    )

    with (
        patch("openforge.cli.load_run_context", return_value=[]),
        patch("openforge.cli.git_rev_parse_head", side_effect=["abc123", "abc123"]),
        patch("openforge.cli.git_diff_name_only_from", return_value=["src/file.py"]),
        patch("openforge.cli.verify_scope", return_value=(True, [])),
        patch("openforge.cli.dispatch_task") as dispatch_mock,
        patch("openforge.cli.detect_completion", return_value=completion),
        patch("openforge.cli.append_task_context") as append_mock,
        patch("openforge.cli.cleanup_result_envelope") as cleanup_mock,
        patch("openforge.cli.git_add_and_commit", return_value="def456") as commit_mock,
        patch("openforge.cli.save_state"),
        patch("openforge.cli._save_task_artifacts"),
        patch("openforge.cli.emit_event"),
        patch("openforge.cli._subprocess.run") as subproc_mock,
    ):
        dispatch_mock.return_value.exit_code = 0
        dispatch_mock.return_value.stdout = "ok"
        dispatch_mock.return_value.stderr = ""
        dispatch_mock.return_value.timed_out = False
        subproc_mock.return_value.stdout = "diff"
        _run_task(state, prd, phase, task, tmp_path, tmp_path, None)

    assert state.tasks[task.id].state == "complete"
    append_mock.assert_called_once()
    cleanup_mock.assert_called_once_with(tmp_path, task.id)
    commit_mock.assert_called_once()


def test_run_phase_validator_failure_with_no_tasks_halts_without_index_error(
    tmp_path: Path,
) -> None:
    prd = ForgePRD(
        title="empty phase",
        objective="exercise validator edge case",
        in_scope=["src/"],
        routing=RoutingConfig(aliases={"cloud": RoutingAlias(agent="openforge-cloud")}),
        phases=[
            Phase(
                id="empty",
                config=PhaseConfig(stage=1, executor="cloud", validator="exit 1"),
                tasks=[],
            )
        ],
    )
    state = init_run_state("run-123", "prd.md", "abc123", ".", RunConfig(), prd)

    with (
        patch("openforge.cli.run_validator") as run_validator_mock,
        patch("openforge.cli.save_state"),
        patch("openforge.cli.emit_event"),
    ):
        run_validator_mock.return_value.exit_code = 1
        run_validator_mock.return_value.stdout = "failed"
        run_validator_mock.return_value.stderr = ""
        run_validator_mock.return_value.timed_out = False
        passed = _run_phase_validator(state, prd.phases[0], tmp_path, tmp_path)

    assert passed is False
    assert state.status == "halted"
    assert state.phases["empty"].status == "failed"


def test_run_stage_validator_attributes_failure_to_latest_completed_task(tmp_path: Path) -> None:
    task_a = Task(
        id="task-a",
        text="First",
        config=TaskConfig(id="task-a", reads=["src/"], produces=["src/a.py"]),
        phase_id="phase-a",
    )
    task_b = Task(
        id="task-b",
        text="Second",
        config=TaskConfig(id="task-b", reads=["src/"], produces=["src/b.py"]),
        phase_id="phase-b",
    )
    prd = ForgePRD(
        title="stage validator test",
        objective="verify attribution",
        in_scope=["src/"],
        routing=RoutingConfig(aliases={"cloud": RoutingAlias(agent="openforge-cloud")}),
        phases=[
            Phase(id="phase-a", config=PhaseConfig(stage=1, executor="cloud"), tasks=[task_a]),
            Phase(id="phase-b", config=PhaseConfig(stage=1, executor="cloud"), tasks=[task_b]),
        ],
        stage_validators={1: "exit 1"},
    )
    state = init_run_state("run-123", "prd.md", "abc123", ".", RunConfig(), prd)

    for task_id in ("task-a", "task-b"):
        update_task_state(state, task_id, "dispatched")
        update_task_state(state, task_id, "agent_succeeded")
        update_task_state(state, task_id, "scope_verified")
        update_task_state(state, task_id, "validation_passed")
        update_task_state(state, task_id, "complete")
        state.tasks[task_id].attempts.append(AttemptRecord(number=1, agent="cloud"))
    for phase in prd.phases:
        state.phases[phase.id].status = "validated"

    with (
        patch("openforge.cli.run_validator") as run_validator_mock,
        patch("openforge.cli.save_state"),
    ):
        run_validator_mock.return_value.exit_code = 1
        run_validator_mock.return_value.stdout = "failed"
        run_validator_mock.return_value.stderr = ""
        run_validator_mock.return_value.timed_out = False
        passed = _run_stage_validator(state, prd, 1, tmp_path, tmp_path)

    assert passed is False
    assert state.tasks["task-b"].state == "validation_failed"
    assert state.tasks["task-a"].state == "complete"
    assert state.tasks["task-b"].attempts[-1].failure_class == "validator_failure"


def test_exit_code_for_completed_run_is_zero() -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    state = init_run_state("run-123", "prd.md", "abc123", ".", RunConfig(), prd)
    state.status = "completed"
    assert _exit_code_for_run_state(state) == 0


def test_exit_code_for_halted_security_run_is_six() -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    state = init_run_state("run-123", "prd.md", "abc123", ".", RunConfig(), prd)
    state.status = "halted"
    state.tasks["first-task"].state = "halted_security"
    assert _exit_code_for_run_state(state) == 6


def test_exit_code_for_non_security_halt_is_three() -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")
    state = init_run_state("run-123", "prd.md", "abc123", ".", RunConfig(), prd)
    state.status = "halted"
    state.tasks["first-task"].state = "halted_manual"
    assert _exit_code_for_run_state(state) == 3


def test_run_command_returns_security_exit_code_when_scheduler_halts_for_scope_violation(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    prd_path = _FIXTURES / "valid-simple.md"
    final_state = init_run_state(
        "run-123", str(prd_path), "abc123", str(tmp_path), RunConfig(), parse_prd(prd_path)
    )
    final_state.status = "halted"
    final_state.tasks["first-task"].state = "halted_security"

    with (
        patch("openforge.cli._preflight"),
        patch("openforge.cli.parse_prd", return_value=parse_prd(prd_path)),
        patch("openforge.cli.validate_overlap", return_value=[]),
        patch("openforge.cli.validate_fallback_tiers", return_value=[]),
        patch("openforge.cli._health_check", return_value={"cloud": (True, "ok")}),
        patch("openforge.cli._print_health_table"),
        patch("openforge.cli.capture_baseline", return_value=("hash", "base", [])),
        patch("openforge.cli.compute_prd_hash", return_value="abc123"),
        patch("openforge.cli.init_run_state", return_value=final_state),
        patch("openforge.cli.save_state"),
        patch("openforge.cli.emit_event"),
        patch("openforge.cli.shutil.copy2"),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.write_text"),
        patch("openforge.cli._scheduler_loop", return_value=final_state),
        patch("openforge.cli._print_run_summary"),
    ):
        result = runner.invoke(app, ["run", str(prd_path), "--cwd", str(tmp_path)])

    assert result.exit_code == 6
