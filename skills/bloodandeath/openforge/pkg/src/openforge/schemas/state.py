from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

_VALID_TASK_STATES = {
    "queued",
    "dispatched",
    "agent_succeeded",
    "agent_failed",
    "scope_verified",
    "scope_failed",
    "validation_passed",
    "validation_failed",
    "complete",
    "halted_escalation",
    "halted_security",
    "halted_manual",
}


class AttemptRecord(BaseModel):
    number: int
    agent: str
    failure_class: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    exit_code: int | None = None
    sha_before: str | None = None
    sha_after: str | None = None
    modified_paths: list[str] = Field(default_factory=list)
    scope_verified: bool | None = None
    reflexion: bool = False


class TaskState(BaseModel):
    phase: str
    state: str = "queued"
    attempts: list[AttemptRecord] = Field(default_factory=list)

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        if value not in _VALID_TASK_STATES:
            msg = f"invalid task state '{value}'"
            raise ValueError(msg)
        return value


class PhaseStatus(BaseModel):
    status: str = "pending"


class StageStatus(BaseModel):
    status: str = "pending"
    validator_exit_code: int | None = None


class RunConfig(BaseModel):
    max_escalation: int = 5
    trust_mode: str = "trusted"
    allow_dirty: bool = False
    allow_network_validators: bool = False
    task_timeout: int = 600


class RunState(BaseModel):
    schema_version: str = "1.0.0"
    run_id: str
    parent_run_id: str | None = None
    prd_path: str
    prd_hash: str
    cwd: str
    base_commit: str | None = None
    baseline_dirty_patch_hash: str | None = None
    baseline_untracked_files: list[str] = Field(default_factory=list)
    started_at: str
    updated_at: str
    status: str = "running"
    current_stage: int = 1
    config: RunConfig = Field(default_factory=RunConfig)
    tasks: dict[str, TaskState] = Field(default_factory=dict)
    phases: dict[str, PhaseStatus] = Field(default_factory=dict)
    stages: dict[str, StageStatus] = Field(default_factory=dict)
    fix_run_id: str | None = None
