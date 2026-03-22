from __future__ import annotations

import json
import os
import shutil
import subprocess as _subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from openforge.completion import cleanup_result_envelope, detect_completion
from openforge.events import emit_event, make_event
from openforge.executor import (
    check_agent_health,
    dispatch_task,
    resolve_agent_for_attempt,
    validate_fallback_tiers,
)
from openforge.git_ops import (
    GitError,
    ResumeError,
    capture_baseline,
    git_add_and_commit,
    git_diff_name_only_from,
    git_rev_parse_head,
    git_status_porcelain,
    verify_baseline,
)
from openforge.overlap import validate_overlap
from openforge.parser import ParseError, parse_prd
from openforge.prompts import build_prompt, build_reflexion_suffix, select_prompt_tier
from openforge.run_context import (
    append_task_context,
    build_context_from_result,
    load_run_context,
    render_context_summary,
)
from openforge.schemas.prd import ForgePRD, Phase, Task
from openforge.schemas.state import AttemptRecord, RunConfig, RunState
from openforge.security import redact_secrets, verify_scope
from openforge.state import (
    compute_prd_hash,
    init_run_state,
    load_state,
    mark_task_validation_failed,
    save_state,
    update_task_state,
)
from openforge.validator_runner import run_validator

app = typer.Typer(name="openforge", help="Multi-model PRD execution for OpenClaw")
console = Console()


@dataclass(slots=True)
class SchedulerAction:
    kind: str
    phase: Phase | None = None
    task: Task | None = None


def _run_root(run_root: str | None) -> Path:
    default_root = os.environ.get("OPENFORGE_RUN_ROOT") or os.path.join(
        os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")),
        "openforge",
        "runs",
    )
    return Path(run_root or default_root)


def _json_print(data: object) -> None:
    console.print_json(json.dumps(data, default=str))


def _phase_lookup(prd: ForgePRD) -> dict[str, Phase]:
    return {phase.id: phase for phase in prd.phases}


def _find_task(prd: ForgePRD, task_id: str) -> tuple[Phase, Task]:
    for phase in prd.phases:
        for task in phase.tasks:
            if task.id == task_id:
                return (phase, task)
    msg = f"task '{task_id}' not found"
    raise KeyError(msg)


def _filter_prd_phases(
    prd: ForgePRD,
    *,
    include_phase: str | None = None,
    exclude_phase: str | None = None,
) -> ForgePRD:
    phases = prd.phases
    if include_phase is not None:
        phases = [selected for selected in phases if selected.id == include_phase]
        if not phases:
            raise typer.BadParameter(f"phase '{include_phase}' not found")
    if exclude_phase is not None:
        phases = [selected for selected in phases if selected.id != exclude_phase]
        if len(phases) == len(prd.phases):
            raise typer.BadParameter(f"skip-phase '{exclude_phase}' not found")
    if not phases:
        raise typer.BadParameter("phase filtering removed all phases")

    active_stages = {phase.config.stage for phase in phases}
    return ForgePRD(
        **{
            **prd.model_dump(mode="python"),
            "phases": phases,
            "stage_validators": {
                stage: command
                for stage, command in prd.stage_validators.items()
                if stage in active_stages
            },
        }
    )


def _build_prompt(
    task: Task,
    phase: Phase,
    prd: ForgePRD,
    cwd: Path,
    run_dir: Path,
    executor_alias: str,
    reflexion: str = "",
) -> str:
    tier = select_prompt_tier(executor_alias, prd.routing)
    prior_context = load_run_context(run_dir)
    prompt = build_prompt(
        task=task,
        phase=phase,
        prd=prd,
        cwd=cwd,
        run_dir=run_dir,
        tier=tier,
        prior_context=prior_context,
        reflexion=reflexion,
    )
    progress_summary = render_context_summary(prior_context)
    if progress_summary and tier == "cloud":
        return f"{prompt}\n## Run progress summary\n{progress_summary}\n"
    return prompt


def _next_action(state: RunState, prd: ForgePRD) -> SchedulerAction:
    """Deterministic scheduler per §5.7. Same state always produces same action."""
    for phase in prd.phases:
        for task in phase.tasks:
            ts = state.tasks[task.id].state
            if ts == "halted_security":
                return SchedulerAction(kind="halt", phase=phase, task=task)
            if ts in {"halted_manual", "halted_escalation"}:
                return SchedulerAction(kind="halt", phase=phase, task=task)

    stage_numbers = sorted({p.config.stage for p in prd.phases})
    for stage_num in stage_numbers:
        stage_key = str(stage_num)
        if state.stages.get(stage_key) and state.stages[stage_key].status == "validated":
            continue

        stage_phases = [p for p in prd.phases if p.config.stage == stage_num]
        for phase in stage_phases:
            if state.phases[phase.id].status == "validated":
                continue

            all_complete = all(state.tasks[t.id].state == "complete" for t in phase.tasks)
            if all_complete:
                return SchedulerAction(kind="validate_phase", phase=phase)

            for task in phase.tasks:
                ts = state.tasks[task.id].state
                if ts == "complete":
                    continue
                if ts in {"queued", "dispatched", "agent_failed", "validation_failed"}:
                    return SchedulerAction(kind="dispatch", phase=phase, task=task)
                return SchedulerAction(kind="wait", phase=phase)

        if all(state.phases[p.id].status == "validated" for p in stage_phases):
            return SchedulerAction(kind="validate_stage", phase=stage_phases[0])

        return SchedulerAction(kind="wait", phase=stage_phases[0])

    return SchedulerAction(kind="done")


def _preflight(prd_path: Path, cwd: Path, allow_dirty: bool) -> None:
    if not prd_path.exists():
        raise typer.BadParameter(f"PRD does not exist: {prd_path}")
    if not cwd.exists():
        raise typer.BadParameter(f"cwd does not exist: {cwd}")
    if not allow_dirty and git_status_porcelain(cwd).strip():
        raise RuntimeError("working tree is dirty; re-run with --allow-dirty to override")


def _health_check(prd: ForgePRD) -> dict[str, tuple[bool, str]]:
    results: dict[str, tuple[bool, str]] = {}
    for alias_name, alias in prd.routing.aliases.items():
        results[alias_name] = check_agent_health(alias.agent)
    return results


def _print_health_table(results: dict[str, tuple[bool, str]]) -> None:
    table = Table(title="Agent health")
    table.add_column("Alias")
    table.add_column("Healthy")
    table.add_column("Message")
    for alias, (healthy, message) in sorted(results.items()):
        table.add_row(alias, "yes" if healthy else "no", message)
    console.print(table)


def _save_task_artifacts(
    run_dir: Path,
    task_id: str,
    attempt_num: int,
    prompt: str,
    response: str,
    diff_output: str,
    scope_check: dict[str, object],
    meta: dict[str, object],
) -> None:
    task_dir = run_dir / "tasks" / task_id / f"attempt-{attempt_num}"
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "prompt.md").write_text(redact_secrets(prompt), encoding="utf-8")
    (task_dir / "response.md").write_text(redact_secrets(response), encoding="utf-8")
    (task_dir / "diff.patch").write_text(redact_secrets(diff_output), encoding="utf-8")
    (task_dir / "scope-check.json").write_text(
        json.dumps(scope_check, indent=2), encoding="utf-8",
    )
    (task_dir / "meta.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")


def _halt_task_for_internal_error(
    state: RunState,
    task: Task,
    run_dir: Path,
    attempt_number: int,
    prompt: str,
    agent_id: str,
    message: str,
) -> None:
    state.tasks[task.id].attempts[-1].failure_class = "git_error"
    update_task_state(state, task.id, "halted_manual")
    save_state(state, run_dir)
    _save_task_artifacts(
        run_dir,
        task.id,
        attempt_number,
        prompt,
        message,
        "",
        {"declared": task.config.produces, "actual": [], "passed": False},
        {"agent": agent_id, "exit_code": None, "failure_class": "git_error"},
    )
    emit_event(
        make_event(
            "openforge.task.halted",
            state.run_id,
            task_id=task.id,
            reason="git_error",
            message=message,
        ),
        run_dir,
    )


def _run_task(
    state: RunState,
    prd: ForgePRD,
    phase: Phase,
    task: Task,
    cwd: Path,
    run_dir: Path,
    force_executor: str | None,
) -> None:
    current_state = state.tasks[task.id].state
    if current_state in {"queued", "agent_failed", "validation_failed"}:
        update_task_state(state, task.id, "dispatched")
    elif current_state != "dispatched":
        msg = f"task '{task.id}' is not dispatchable from state '{current_state}'"
        raise RuntimeError(msg)

    executor_alias = force_executor or phase.config.executor
    alias = prd.routing.aliases[executor_alias]
    prior_attempts = len(state.tasks[task.id].attempts)
    if prior_attempts >= state.config.max_escalation:
        update_task_state(state, task.id, "halted_escalation")
        save_state(state, run_dir)
        return
    attempt_number = prior_attempts + 1
    agent_id = resolve_agent_for_attempt(alias, prd.routing, attempt_number)

    reflexion = ""
    if prior_attempts > 0:
        previous = state.tasks[task.id].attempts[-1]
        reflexion = build_reflexion_suffix(
            previous.failure_class or "retry",
            f"retry attempt {attempt_number}",
        )

    prompt = _build_prompt(task, phase, prd, cwd, run_dir, executor_alias, reflexion=reflexion)

    try:
        sha_before = git_rev_parse_head(cwd)
    except GitError as exc:
        attempt = AttemptRecord(number=attempt_number, agent=agent_id)
        state.tasks[task.id].attempts.append(attempt)
        save_state(state, run_dir)
        _halt_task_for_internal_error(
            state, task, run_dir, attempt_number, prompt, agent_id, str(exc)
        )
        return

    attempt = AttemptRecord(number=attempt_number, agent=agent_id, sha_before=sha_before)
    state.tasks[task.id].attempts.append(attempt)
    save_state(state, run_dir)

    console.print(f"    Agent: [cyan]{agent_id}[/cyan] (attempt {attempt_number})")

    dispatch_result = dispatch_task(agent_id, prompt, cwd, timeout=state.config.task_timeout)
    attempt.exit_code = dispatch_result.exit_code

    if dispatch_result.exit_code != 0 or dispatch_result.timed_out:
        attempt.failure_class = "timeout" if dispatch_result.timed_out else "transport_error"
        update_task_state(state, task.id, "agent_failed")
        if len(state.tasks[task.id].attempts) >= state.config.max_escalation:
            update_task_state(state, task.id, "halted_escalation")
        save_state(state, run_dir)
        _save_task_artifacts(
            run_dir,
            task.id,
            attempt_number,
            prompt,
            dispatch_result.stdout + dispatch_result.stderr,
            "",
            {"declared": task.config.produces, "actual": [], "passed": False},
            {
                "agent": agent_id,
                "exit_code": dispatch_result.exit_code,
                "failure_class": attempt.failure_class,
                "timed_out": dispatch_result.timed_out,
            },
        )
        emit_event(
            make_event(
                "openforge.task.failed",
                state.run_id,
                task_id=task.id,
                failure_class=attempt.failure_class,
            ),
            run_dir,
        )
        return

    try:
        sha_after = git_rev_parse_head(cwd)
        attempt.sha_after = sha_after
        changed_paths = git_diff_name_only_from(sha_before, cwd)
        attempt.modified_paths = changed_paths
    except GitError as exc:
        _halt_task_for_internal_error(
            state, task, run_dir, attempt_number, prompt, agent_id, str(exc)
        )
        return

    update_task_state(state, task.id, "agent_succeeded")
    scope_ok, violations = verify_scope(changed_paths, task.config.produces, cwd)
    attempt.scope_verified = scope_ok
    if not scope_ok:
        attempt.failure_class = f"scope_violation: {', '.join(violations)}"
        update_task_state(state, task.id, "scope_failed")
        update_task_state(state, task.id, "halted_security")
        save_state(state, run_dir)
        _save_task_artifacts(
            run_dir,
            task.id,
            attempt_number,
            prompt,
            dispatch_result.stdout + dispatch_result.stderr,
            "",
            {
                "declared": task.config.produces,
                "actual": changed_paths,
                "passed": False,
                "violations": violations,
            },
            {"agent": agent_id, "exit_code": 0, "failure_class": "scope_violation"},
        )
        emit_event(
            make_event(
                "openforge.task.halted",
                state.run_id,
                task_id=task.id,
                reason="scope_violation",
                violations=violations,
            ),
            run_dir,
        )
        return

    update_task_state(state, task.id, "scope_verified")

    check_logs: list[dict[str, object]] = []
    for check in task.config.checks:
        check_cwd = (cwd / check.working_dir).resolve()
        check_result = run_validator(check.run, check_cwd, timeout=check.timeout_seconds)
        check_logs.append(
            {
                "run": check.run,
                "working_dir": check.working_dir,
                "exit_code": check_result.exit_code,
                "stdout": check_result.stdout,
                "stderr": check_result.stderr,
                "timed_out": check_result.timed_out,
            }
        )
        if check_result.exit_code != 0 or check_result.timed_out:
            attempt.failure_class = "validation_failed"
            update_task_state(state, task.id, "validation_failed")
            if len(state.tasks[task.id].attempts) >= state.config.max_escalation:
                update_task_state(state, task.id, "halted_escalation")
            save_state(state, run_dir)
            _save_task_artifacts(
                run_dir,
                task.id,
                attempt_number,
                prompt,
                dispatch_result.stdout + dispatch_result.stderr,
                "",
                {"declared": task.config.produces, "actual": changed_paths, "passed": True},
                {
                    "agent": agent_id,
                    "exit_code": 0,
                    "failure_class": "validation_failed",
                    "checks": check_logs,
                },
            )
            return

    try:
        completion = detect_completion(cwd, task.id, sha_before, task.config.produces)
    except (GitError, ValueError) as exc:
        _halt_task_for_internal_error(
            state, task, run_dir, attempt_number, prompt, agent_id, str(exc)
        )
        return

    if completion.kind in {"ambiguous", "noop", "blocked", "failed"}:
        attempt.failure_class = completion.kind
        update_task_state(state, task.id, "validation_failed")
        if len(state.tasks[task.id].attempts) >= state.config.max_escalation:
            update_task_state(state, task.id, "halted_escalation")
        save_state(state, run_dir)
        _save_task_artifacts(
            run_dir,
            task.id,
            attempt_number,
            prompt,
            dispatch_result.stdout + dispatch_result.stderr,
            "",
            {"declared": task.config.produces, "actual": changed_paths, "passed": False},
            {
                "agent": agent_id,
                "exit_code": 0,
                "failure_class": completion.kind,
                "result": completion.result.model_dump(mode="json") if completion.result else None,
            },
        )
        return

    update_task_state(state, task.id, "validation_passed")
    update_task_state(state, task.id, "complete")

    context_entry = build_context_from_result(
        task_id=task.id,
        phase_id=phase.id,
        agent_id=agent_id,
        result=completion.result,
        files_modified=completion.files_changed or changed_paths,
    )
    append_task_context(run_dir, context_entry)
    cleanup_result_envelope(cwd, task.id)

    summary = (context_entry.summary or task.text).strip().splitlines()[0][:72]
    commit_sha = git_add_and_commit(cwd, f"openforge({phase.id}): {summary}")
    if commit_sha is not None:
        attempt.sha_after = commit_sha

    save_state(state, run_dir)

    diff_end = attempt.sha_after or sha_before
    diff_result = _subprocess.run(
        ["git", "diff", f"{sha_before}..{diff_end}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    _save_task_artifacts(
        run_dir,
        task.id,
        attempt_number,
        prompt,
        dispatch_result.stdout + dispatch_result.stderr,
        diff_result.stdout,
        {"declared": task.config.produces, "actual": changed_paths, "passed": True},
        {
            "agent": agent_id,
            "exit_code": 0,
            "failure_class": None,
            "sha_before": sha_before,
            "sha_after": attempt.sha_after,
            "checks": check_logs,
        },
    )
    emit_event(make_event("openforge.task.completed", state.run_id, task_id=task.id), run_dir)


def _run_phase_validator(
    state: RunState, phase: Phase, cwd: Path, run_dir: Path,
) -> bool:
    """Run phase validator. Returns True if passed (or no validator defined)."""
    if not phase.config.validator:
        state.phases[phase.id].status = "validated"
        save_state(state, run_dir)
        return True

    console.print(f"  [dim]Running phase validator for '{phase.id}'...[/dim]")
    result = run_validator(phase.config.validator, cwd, timeout=phase.config.validator_timeout)
    validators_dir = run_dir / "validators"
    validators_dir.mkdir(parents=True, exist_ok=True)
    (validators_dir / f"phase-{phase.id}.log").write_text(
        result.stdout + "\n" + result.stderr, encoding="utf-8",
    )

    if result.exit_code == 0 and not result.timed_out:
        state.phases[phase.id].status = "validated"
        save_state(state, run_dir)
        emit_event(make_event("openforge.phase.validated", state.run_id, phase=phase.id), run_dir)
        return True

    console.print(f"  [red]Phase validator failed for '{phase.id}'[/red]")
    state.phases[phase.id].status = "failed"
    if not phase.tasks:
        state.status = "halted"
        save_state(state, run_dir)
        emit_event(
            make_event(
                "openforge.validator.failed",
                state.run_id,
                phase=phase.id,
                reason="phase_has_no_tasks",
            ),
            run_dir,
        )
        return False

    last_task = phase.tasks[-1]
    for task in reversed(phase.tasks):
        if state.tasks[task.id].state == "complete":
            last_task = task
            break
    mark_task_validation_failed(state, last_task.id)
    if state.tasks[last_task.id].attempts:
        state.tasks[last_task.id].attempts[-1].failure_class = "validator_failure"
    if len(state.tasks[last_task.id].attempts) >= state.config.max_escalation:
        update_task_state(state, last_task.id, "halted_escalation")
    save_state(state, run_dir)
    emit_event(
        make_event("openforge.validator.failed", state.run_id, phase=phase.id), run_dir,
    )
    return False


def _run_stage_validator(
    state: RunState, prd: ForgePRD, stage_num: int, cwd: Path, run_dir: Path,
) -> bool:
    """Run stage validator. Returns True if passed (or no validator defined)."""
    validator_cmd = prd.stage_validators.get(stage_num)
    stage_key = str(stage_num)
    if not validator_cmd:
        state.stages[stage_key].status = "validated"
        save_state(state, run_dir)
        return True

    console.print(f"  [dim]Running stage {stage_num} validator...[/dim]")
    result = run_validator(validator_cmd, cwd)
    validators_dir = run_dir / "validators"
    validators_dir.mkdir(parents=True, exist_ok=True)
    (validators_dir / f"stage-{stage_num}.log").write_text(
        result.stdout + "\n" + result.stderr, encoding="utf-8",
    )
    state.stages[stage_key].validator_exit_code = result.exit_code

    if result.exit_code == 0 and not result.timed_out:
        state.stages[stage_key].status = "validated"
        save_state(state, run_dir)
        emit_event(
            make_event("openforge.stage.validated", state.run_id, stage=stage_num), run_dir,
        )
        return True

    console.print(f"  [red]Stage {stage_num} validator failed[/red]")
    state.stages[stage_key].status = "failed"
    stage_phases = [p for p in prd.phases if p.config.stage == stage_num]
    stage_tasks = [task for phase in stage_phases for task in phase.tasks]
    if not stage_tasks:
        state.status = "halted"
        save_state(state, run_dir)
        emit_event(
            make_event(
                "openforge.validator.failed",
                state.run_id,
                stage=stage_num,
                reason="stage_has_no_tasks",
            ),
            run_dir,
        )
        return False

    last_task = stage_tasks[-1]
    found_last_complete = False
    for phase in reversed(stage_phases):
        for task in reversed(phase.tasks):
            if state.tasks[task.id].state == "complete":
                last_task = task
                found_last_complete = True
                break
        if found_last_complete:
            break
    mark_task_validation_failed(state, last_task.id)
    if state.tasks[last_task.id].attempts:
        state.tasks[last_task.id].attempts[-1].failure_class = "validator_failure"
    if len(state.tasks[last_task.id].attempts) >= state.config.max_escalation:
        update_task_state(state, last_task.id, "halted_escalation")
    phase_for_task = next(p for p in stage_phases if any(t.id == last_task.id for t in p.tasks))
    state.phases[phase_for_task.id].status = "running"
    save_state(state, run_dir)
    return False


def _scheduler_loop(
    state: RunState,
    prd: ForgePRD,
    cwd: Path,
    run_dir: Path,
    force_executor: str | None,
) -> RunState:
    while True:
        action = _next_action(state, prd)
        save_state(state, run_dir)

        if action.kind == "done":
            state.status = "completed"
            save_state(state, run_dir)
            emit_event(make_event("openforge.run.end", state.run_id, status="completed"), run_dir)
            return state

        if action.kind == "halt":
            state.status = "halted"
            save_state(state, run_dir)
            task_id = action.task.id if action.task else "unknown"
            emit_event(
                make_event("openforge.run.end", state.run_id, status="halted", task=task_id),
                run_dir,
            )
            return state

        if action.kind == "validate_phase":
            assert action.phase is not None
            _run_phase_validator(state, action.phase, cwd, run_dir)
            continue

        if action.kind == "validate_stage":
            assert action.phase is not None
            stage_num = action.phase.config.stage
            _run_stage_validator(state, prd, stage_num, cwd, run_dir)
            continue

        if action.kind == "wait":
            state.status = "waiting"
            save_state(state, run_dir)
            return state

        assert action.phase is not None
        assert action.task is not None
        console.print(
            f"  [bold]Dispatching:[/bold] {action.task.id} "
            f"({action.phase.id}, stage {action.phase.config.stage})"
        )
        _run_task(state, prd, action.phase, action.task, cwd, run_dir, force_executor)


def _print_run_summary(state: RunState) -> None:
    table = Table(title=f"Run {state.run_id}")
    table.add_column("Task")
    table.add_column("Phase")
    table.add_column("State")
    table.add_column("Attempts")
    for task_id, task_state in sorted(state.tasks.items()):
        table.add_row(task_id, task_state.phase, task_state.state, str(len(task_state.attempts)))
    console.print(table)
    console.print(Panel.fit(f"Run status: {state.status}"))


def _exit_code_for_run_state(state: RunState) -> int:
    if state.status == "completed":
        return 0

    if any(task.state == "halted_security" for task in state.tasks.values()):
        return 6

    if state.status in {"halted", "waiting"}:
        return 3

    return 0


@app.command()
def validate(
    prd: str,
    lenient: bool = False,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    try:
        parsed = parse_prd(Path(prd), lenient=lenient)
        overlaps = validate_overlap(parsed)
    except ParseError as exc:
        console.print(f"Parse error: {exc}")
        raise typer.Exit(code=1) from exc
    if json_output:
        _json_print({"ok": True, "title": parsed.title, "overlaps": overlaps})
        return
    console.print(f"Valid PRD: {parsed.title}")
    if overlaps:
        console.print("Overlap warnings:")
        for item in overlaps:
            console.print(f"- {item}")


@app.command()
def plan(
    prd: str,
    cwd: str = ".",
    lenient: bool = False,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    parsed = parse_prd(Path(prd), lenient=lenient)
    data = {
        "title": parsed.title,
        "cwd": str(Path(cwd).resolve()),
        "phases": [
            {
                "id": phase.id,
                "stage": phase.config.stage,
                "executor": phase.config.executor,
                "validator": phase.config.validator,
                "tasks": [task.model_dump(mode="json") for task in phase.tasks],
            }
            for phase in parsed.phases
        ],
    }
    if json_output:
        _json_print(data)
        return
    table = Table(title=f"Execution plan: {parsed.title}")
    table.add_column("Phase")
    table.add_column("Stage")
    table.add_column("Executor")
    table.add_column("Tasks")
    for phase in parsed.phases:
        table.add_row(
            phase.id, str(phase.config.stage), phase.config.executor, str(len(phase.tasks))
        )
    console.print(table)


@app.command()
def run(
    prd: str,
    cwd: str = ".",
    phase: str | None = None,
    skip_phase: str | None = None,
    force_executor: str | None = None,
    max_escalation: int = 5,
    task_timeout: int = 600,
    allow_dirty: bool = False,
    allow_network_validators: bool = False,
    run_root: str | None = None,
    lenient: bool = False,
) -> None:
    prd_path = Path(prd).resolve()
    cwd_path = Path(cwd).resolve()
    _preflight(prd_path, cwd_path, allow_dirty)
    parsed = parse_prd(prd_path, lenient=lenient)
    overlaps = validate_overlap(parsed)
    if overlaps and not lenient:
        raise typer.Exit(code=1)

    if phase is not None or skip_phase is not None:
        parsed = _filter_prd_phases(parsed, include_phase=phase, exclude_phase=skip_phase)

    tier_warnings = validate_fallback_tiers(parsed.routing)
    for warning in tier_warnings:
        console.print(f"[bold red]⚠ ROUTING WARNING:[/bold red] {warning}")
    if tier_warnings:
        console.print(
            "[yellow]Review tier fallbacks should use review or cloud-capable models.[/yellow]"
        )

    health = _health_check(parsed)
    _print_health_table(health)
    unhealthy = {alias: message for alias, (ok, message) in health.items() if not ok}
    if unhealthy:
        raise RuntimeError(f"unhealthy agents: {unhealthy}")

    baseline_hash, base_commit, untracked = capture_baseline(cwd_path)
    run_id = uuid.uuid4().hex[:12]
    config = RunConfig(
        max_escalation=max_escalation,
        allow_dirty=allow_dirty,
        allow_network_validators=allow_network_validators,
        task_timeout=task_timeout,
    )
    state = init_run_state(
        run_id,
        str(prd_path),
        compute_prd_hash(prd_path),
        str(cwd_path),
        config,
        parsed,
    )
    state.base_commit = base_commit
    state.baseline_dirty_patch_hash = baseline_hash
    state.baseline_untracked_files = untracked

    root = _run_root(run_root)
    run_dir = root / run_id

    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(prd_path, run_dir / "prd.snapshot.md")
    plan_data = {
        "title": parsed.title,
        "phases": [
            {"id": p.id, "stage": p.config.stage, "executor": p.config.executor,
             "tasks": [t.id for t in p.tasks]}
            for p in parsed.phases
        ],
        "stage_validators": {str(k): v for k, v in parsed.stage_validators.items()},
    }
    (run_dir / "plan.json").write_text(json.dumps(plan_data, indent=2), encoding="utf-8")
    (run_dir / "config.json").write_text(
        json.dumps(config.model_dump(), indent=2), encoding="utf-8",
    )

    save_state(state, run_dir)
    emit_event(
        make_event("openforge.run.start", state.run_id, cwd=str(cwd_path), prd=str(prd_path)),
        run_dir,
    )
    final_state = _scheduler_loop(state, parsed, cwd_path, run_dir, force_executor)
    _print_run_summary(final_state)
    raise typer.Exit(code=_exit_code_for_run_state(final_state))


@app.command()
def resume(run_id: str, force: bool = False, run_root: str | None = None) -> None:
    root = _run_root(run_root)
    run_dir = root / run_id
    state = load_state(run_dir)
    prd_path = Path(state.prd_path)
    cwd = Path(state.cwd)
    if compute_prd_hash(prd_path) != state.prd_hash:
        raise ResumeError("PRD hash mismatch; file changed since run started")
    if not force:
        verify_baseline(state, cwd)
    prd = parse_prd(prd_path)
    state.status = "running"
    save_state(state, run_dir)
    final_state = _scheduler_loop(state, prd, cwd, run_dir, None)
    _print_run_summary(final_state)
    raise typer.Exit(code=_exit_code_for_run_state(final_state))


@app.command()
def status(
    run_id: str,
    run_root: str | None = None,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    state = load_state(_run_root(run_root) / run_id)
    if json_output:
        _json_print(state.model_dump(mode="json"))
        return
    _print_run_summary(state)


@app.command(name="list")
def list_runs(
    run_root: str | None = None,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    root = _run_root(run_root)
    items: list[dict[str, object]] = []
    if root.exists():
        for child in sorted(root.iterdir()):
            if not child.is_dir() or not (child / "state.json").exists():
                continue
            state = load_state(child)
            items.append({
                "run_id": state.run_id,
                "status": state.status,
                "started_at": state.started_at,
                "cwd": state.cwd,
            })
    if json_output:
        _json_print(items)
        return
    table = Table(title="OpenForge runs")
    table.add_column("Run ID")
    table.add_column("Status")
    table.add_column("Started")
    table.add_column("CWD")
    for item in items:
        table.add_row(
            str(item["run_id"]),
            str(item["status"]),
            str(item["started_at"]),
            str(item["cwd"]),
        )
    console.print(table)


if __name__ == "__main__":
    app()
