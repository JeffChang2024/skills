"""Structured result schemas for task completion and run context."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TaskResult(BaseModel):
    """Structured result envelope written by the agent after task completion.

    Agents are instructed to write this to .openforge/results/{task_id}.json.
    OpenForge uses it for authoritative completion detection and learning accumulation.
    """

    task_id: str
    status: str = "completed"  # completed | blocked | failed | noop
    summary: str = ""
    decisions: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)
    notes: str = ""


class TaskContextEntry(BaseModel):
    """One entry in the run context log (accumulated learnings)."""

    task_id: str
    phase_id: str
    agent_id: str
    summary: str = ""
    decisions: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    checks_passed: bool = True
    unresolved: list[str] = Field(default_factory=list)
