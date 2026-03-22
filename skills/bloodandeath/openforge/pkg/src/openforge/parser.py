from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import ValidationError

from openforge.overlap import validate_overlap as validate_path_overlap
from openforge.schemas.prd import (
    ForgePRD,
    Phase,
    PhaseConfig,
    RoutingConfig,
    Task,
    TaskCheck,
    TaskConfig,
)

if TYPE_CHECKING:
    from pathlib import Path

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*\S)\s*$")
_CHECKLIST_RE = re.compile(r"^\s*- \[(?: |x|X)\] (.+\S)\s*$")
_BULLET_RE = re.compile(r"^\s*- (.+\S)\s*$")
_FENCE_OPEN_RE = re.compile(r"^\s*```yaml\s+([a-z-]+(?::[a-z0-9][a-z0-9_-]*)?)\s*$")
_FENCE_CLOSE_RE = re.compile(r"^\s*```\s*$")
_PHASE_HEADING_RE = re.compile(r"^Phase:\s*([a-z0-9][a-z0-9_-]*)\s*$")
_ALLOWED_BLOCK_TYPES = {"routing", "phase", "task", "stage-validators"}
_ALLOWED_ROUTING_KEYS = {"aliases"}
_ALLOWED_PHASE_KEYS = {"stage", "executor", "validator", "validator_timeout"}
_ALLOWED_TASK_KEYS = {"id", "reads", "produces", "checks", "check"}
_REQUIRED_SECTIONS = {"title", "objective", "scope", "routing", "phases"}


class ParseError(Exception):
    def __init__(self, line: int, message: str) -> None:
        self.line = line
        self.message = message
        super().__init__(f"line {line}: {message}")


class _TaskDraft:
    def __init__(self, text: str, line: int) -> None:
        self.text = text
        self.line = line


def _parse_yaml_block(lines: list[str], line_number: int) -> Any:  # noqa: ANN401
    try:
        data = yaml.safe_load("\n".join(lines))
    except yaml.YAMLError as exc:  # pragma: no cover - PyYAML formatting detail
        raise ParseError(line_number, f"invalid YAML: {exc}") from exc
    return {} if data is None else data


def _expect_mapping(data: Any, label: str, line_number: int) -> dict[str, Any]:  # noqa: ANN401
    if not isinstance(data, dict):
        msg = f"yaml block '{label}' must parse to a mapping"
        raise ParseError(line_number, msg)
    return data


def _check_unknown_keys(
    data: dict[str, Any],
    allowed_keys: set[str],
    label: str,
    line_number: int,
    *,
    lenient: bool,
) -> None:
    unknown = sorted(set(data) - allowed_keys)
    if unknown and not lenient:
        msg = f"unknown keys in {label}: {', '.join(unknown)}"
        raise ParseError(line_number, msg)


def _normalize_claim_path(path: str, line_number: int) -> str:
    candidate = path.strip().replace("\\", "/")
    if not candidate:
        raise ParseError(line_number, "path entries must not be empty")
    if candidate.startswith("/"):
        raise ParseError(line_number, f"absolute paths are not allowed: {path}")

    normalized_parts: list[str] = []
    trailing_slash = candidate.endswith("/")
    for segment in candidate.split("/"):
        if segment in {"", "."}:
            continue
        if segment == "..":
            raise ParseError(line_number, f"parent path traversal is not allowed: {path}")
        normalized_parts.append(segment)

    normalized = "/".join(normalized_parts)
    if trailing_slash and normalized:
        normalized = f"{normalized}/"
    if not normalized:
        raise ParseError(line_number, f"path resolves to logical root and is not allowed: {path}")
    return normalized


def parse_prd(path: Path, *, lenient: bool = False) -> ForgePRD:
    """Parse a PRD file into a validated ForgePRD model."""
    lines = path.read_text(encoding="utf-8").splitlines()

    title: str | None = None
    objective_lines: list[str] = []
    problem_lines: list[str] = []
    in_scope: list[str] = []
    out_of_scope: list[str] = []
    acceptance_criteria: list[str] = []
    routing_data: dict[str, Any] | None = None
    stage_validators_data: dict[int, str | None] = {}

    current_h2: str | None = None
    current_h3: str | None = None
    current_phase_id: str | None = None
    pending_task: _TaskDraft | None = None

    phase_order: list[str] = []
    phase_configs: dict[str, dict[str, Any]] = {}
    phase_lines: dict[str, int] = {}
    phase_tasks: dict[str, list[Task]] = {}
    seen_blocks: set[tuple[str, str | None]] = set()

    index = 0
    while index < len(lines):
        line_number = index + 1
        line = lines[index]
        stripped = line.strip()

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            depth = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if depth == 1:
                if not heading_text.startswith("PRD:"):
                    raise ParseError(line_number, "expected H1 heading in format '# PRD: <title>'")
                parsed_title = heading_text[4:].strip()
                if not parsed_title:
                    raise ParseError(line_number, "PRD title must not be empty")
                title = parsed_title
                current_h2 = None
                current_h3 = None
                current_phase_id = None
            elif depth == 2:
                current_h2 = heading_text
                current_h3 = None
                phase_match = _PHASE_HEADING_RE.match(heading_text)
                current_phase_id = phase_match.group(1) if phase_match else None
            else:
                current_h3 = heading_text
            index += 1
            continue

        fence_match = _FENCE_OPEN_RE.match(line)
        if fence_match:
            label = fence_match.group(1)
            block_type, _, block_id = label.partition(":")
            if block_type not in _ALLOWED_BLOCK_TYPES:
                raise ParseError(line_number, f"unsupported yaml block type '{block_type}'")
            block_key = (block_type, block_id or None)
            if block_key in seen_blocks:
                raise ParseError(line_number, f"duplicate yaml block '{label}'")
            seen_blocks.add(block_key)

            block_lines: list[str] = []
            index += 1
            while index < len(lines) and not _FENCE_CLOSE_RE.match(lines[index]):
                block_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                raise ParseError(line_number, f"unclosed yaml fence for '{label}'")

            data = _expect_mapping(_parse_yaml_block(block_lines, line_number), label, line_number)

            if block_type == "routing":
                if block_id:
                    raise ParseError(line_number, "routing block must not include an id")
                _check_unknown_keys(
                    data,
                    _ALLOWED_ROUTING_KEYS,
                    label,
                    line_number,
                    lenient=lenient,
                )
                routing_data = data
            elif block_type == "phase":
                if not block_id:
                    raise ParseError(line_number, "phase block must include an id")
                if current_phase_id is None:
                    raise ParseError(
                        line_number,
                        "phase yaml block must appear under a matching phase heading",
                    )
                if current_phase_id != block_id:
                    raise ParseError(
                        line_number,
                        (
                            f"phase heading id '{current_phase_id}' does not match "
                            f"yaml block id '{block_id}'"
                        ),
                    )
                _check_unknown_keys(
                    data,
                    _ALLOWED_PHASE_KEYS,
                    label,
                    line_number,
                    lenient=lenient,
                )
                phase_order.append(block_id)
                phase_configs[block_id] = data
                phase_lines[block_id] = line_number
                phase_tasks[block_id] = []
            elif block_type == "task":
                if not block_id:
                    raise ParseError(line_number, "task block must include an id")
                if current_phase_id is None:
                    raise ParseError(
                        line_number,
                        "task yaml block must appear inside a phase section",
                    )
                if pending_task is None:
                    raise ParseError(line_number, "task yaml block must follow a checklist item")
                _check_unknown_keys(
                    data,
                    _ALLOWED_TASK_KEYS,
                    label,
                    line_number,
                    lenient=lenient,
                )
                if "id" not in data:
                    raise ParseError(
                        line_number,
                        f"task yaml block '{label}' is missing required key 'id'",
                    )
                if data["id"] != block_id:
                    raise ParseError(
                        line_number,
                        f"task yaml id '{data['id']}' does not match block id '{block_id}'",
                    )

                reads = data.get("reads", [])
                produces = data.get("produces", [])
                if not isinstance(reads, list):
                    raise ParseError(line_number, "task 'reads' must be a list")
                if not isinstance(produces, list):
                    raise ParseError(line_number, "task 'produces' must be a list")

                normalized_reads = [
                    _normalize_claim_path(str(item), line_number) for item in reads
                ]
                normalized_produces = [
                    _normalize_claim_path(str(item), line_number) for item in produces
                ]

                # Parse checks: support string shorthand or list of objects
                raw_checks = data.get("checks", data.get("check"))
                parsed_checks: list[TaskCheck] = []
                if isinstance(raw_checks, str):
                    parsed_checks = [TaskCheck(run=raw_checks)]
                elif isinstance(raw_checks, list):
                    for chk in raw_checks:
                        if isinstance(chk, str):
                            parsed_checks.append(TaskCheck(run=chk))
                        elif isinstance(chk, dict):
                            parsed_checks.append(TaskCheck(**chk))
                elif isinstance(raw_checks, dict):
                    parsed_checks = [TaskCheck(**raw_checks)]

                task_config = TaskConfig(
                    id=str(data["id"]),
                    reads=normalized_reads,
                    produces=normalized_produces,
                    checks=parsed_checks,
                )
                task = Task(
                    id=task_config.id,
                    text=pending_task.text,
                    config=task_config,
                    phase_id=current_phase_id,
                )
                phase_tasks[current_phase_id].append(task)
                pending_task = None
            else:
                if block_id:
                    raise ParseError(line_number, "stage-validators block must not include an id")
                validators: dict[int, str | None] = {}
                for raw_key, raw_value in data.items():
                    if not isinstance(raw_key, int):
                        raise ParseError(line_number, "stage validator keys must be integers")
                    validators[int(raw_key)] = None if raw_value is None else str(raw_value)
                stage_validators_data = validators

            index += 1
            continue

        checklist_match = _CHECKLIST_RE.match(line)
        if checklist_match:
            item_text = checklist_match.group(1).strip()
            if current_phase_id is not None:
                pending_task = _TaskDraft(item_text, line_number)
            elif current_h2 == "Acceptance Criteria":
                acceptance_criteria.append(item_text)
            index += 1
            continue

        bullet_match = _BULLET_RE.match(line)
        if bullet_match and not _CHECKLIST_RE.match(line):
            item_text = bullet_match.group(1).strip()
            if current_h2 == "Scope" and current_h3 == "In Scope":
                in_scope.append(item_text)
            elif current_h2 == "Scope" and current_h3 == "Out of Scope":
                out_of_scope.append(item_text)
            elif current_h2 == "Acceptance Criteria":
                acceptance_criteria.append(item_text)
            index += 1
            continue

        if stripped:
            if current_h2 == "Objective":
                objective_lines.append(stripped)
            elif current_h2 == "Problem":
                problem_lines.append(stripped)
        index += 1

    if pending_task is not None:
        raise ParseError(pending_task.line, "checklist item is missing a following task yaml block")

    missing_sections: list[str] = []
    if title is None:
        missing_sections.append("title")
    if not objective_lines:
        missing_sections.append("objective")
    if not in_scope and not out_of_scope:
        missing_sections.append("scope")
    if routing_data is None:
        missing_sections.append("routing")
    if not phase_order:
        missing_sections.append("phases")
    if missing_sections:
        missing = ", ".join(
            section for section in _REQUIRED_SECTIONS if section in missing_sections
        )
        raise ParseError(1, f"missing required sections: {missing}")

    try:
        routing = RoutingConfig.model_validate(routing_data)
    except ValidationError as exc:
        raise ParseError(1, str(exc)) from exc

    phases: list[Phase] = []
    stage_counts: dict[int, int] = {}
    for phase_id in phase_order:
        raw_config = phase_configs[phase_id]
        try:
            config = PhaseConfig.model_validate(raw_config)
        except ValidationError as exc:
            raise ParseError(phase_lines[phase_id], str(exc)) from exc
        stage_counts[config.stage] = stage_counts.get(config.stage, 0) + 1
        phases.append(Phase(id=phase_id, config=config, tasks=phase_tasks[phase_id]))

    for phase in phases:
        if stage_counts[phase.config.stage] > 1:
            for task in phase.tasks:
                if not task.config.produces:
                    raise ParseError(
                        phase_lines[phase.id],
                        (
                            f"task '{task.id}' must declare produces because "
                            f"stage {phase.config.stage} has multiple phases"
                        ),
                    )

    try:
        prd = ForgePRD(
            title=title,
            objective="\n".join(objective_lines).strip(),
            problem="\n".join(problem_lines).strip() or None,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            routing=routing,
            phases=phases,
            stage_validators=stage_validators_data,
            acceptance_criteria=acceptance_criteria,
        )
    except ValidationError as exc:
        message = exc.errors()[0]["msg"] if exc.errors() else str(exc)
        raise ParseError(1, message) from exc

    overlap_errors = validate_path_overlap(prd)
    if overlap_errors and not lenient:
        raise ParseError(1, overlap_errors[0])

    return prd


def validate_overlap(prd: ForgePRD) -> list[str]:
    """Check for path claim overlaps between phases in the same stage.

    Returns list of error messages. Empty = no overlaps.
    """
    return validate_path_overlap(prd)
