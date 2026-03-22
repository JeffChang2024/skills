from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator, model_validator

_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class RoutingAlias(BaseModel):
    agent: str
    fallback: str | None = None
    context: int | None = None


class RoutingConfig(BaseModel):
    aliases: dict[str, RoutingAlias]

    @field_validator("aliases")
    @classmethod
    def validate_aliases(cls, value: dict[str, RoutingAlias]) -> dict[str, RoutingAlias]:
        if not value:
            msg = "routing aliases must contain at least one alias"
            raise ValueError(msg)
        return value


class PhaseConfig(BaseModel):
    stage: int
    executor: str
    validator: str | None = None
    validator_timeout: int = 300

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, value: int) -> int:
        if value < 1:
            msg = "stage must be >= 1"
            raise ValueError(msg)
        return value


class TaskCheck(BaseModel):
    """Per-task quality check. Runs after agent completes, before marking done."""

    run: str  # shell command
    timeout_seconds: int = 300
    working_dir: str = "."


class TaskConfig(BaseModel):
    id: str
    reads: list[str] = Field(default_factory=list)
    produces: list[str] = Field(default_factory=list)
    checks: list[TaskCheck] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not _ID_PATTERN.fullmatch(value):
            msg = f"task id must match {_ID_PATTERN.pattern}"
            raise ValueError(msg)
        return value


class Task(BaseModel):
    id: str
    text: str
    config: TaskConfig
    phase_id: str


class Phase(BaseModel):
    id: str
    config: PhaseConfig
    tasks: list[Task]


class ForgePRD(BaseModel):
    title: str
    objective: str
    problem: str | None = None
    in_scope: list[str]
    out_of_scope: list[str] = Field(default_factory=list)
    routing: RoutingConfig
    phases: list[Phase]
    stage_validators: dict[int, str | None] = Field(default_factory=dict)
    acceptance_criteria: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_integrity(self) -> ForgePRD:
        aliases = self.routing.aliases
        seen_task_ids: set[str] = set()

        for phase in self.phases:
            if phase.config.executor not in aliases:
                msg = (
                    f"phase '{phase.id}' references unknown executor alias "
                    f"'{phase.config.executor}'"
                )
                raise ValueError(msg)

            for task in phase.tasks:
                if task.id in seen_task_ids:
                    msg = f"duplicate task id '{task.id}'"
                    raise ValueError(msg)
                seen_task_ids.add(task.id)

        return self
