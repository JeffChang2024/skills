from __future__ import annotations

from typing import TYPE_CHECKING

from openforge.context import assemble_context

if TYPE_CHECKING:
    from pathlib import Path

    from openforge.schemas.prd import ForgePRD, Phase, RoutingConfig, Task
    from openforge.schemas.results import TaskContextEntry


def build_reflexion_suffix(
    failure_class: str,
    failure_details: str,
    validator_output: str = "",
) -> str:
    """Reflexion hint appended on escalation retries. Per §9.5."""
    validator_section = f"\nValidator output:\n{validator_output}\n" if validator_output else ""
    return (
        "\n\nReflexion retry guidance:\n"
        f"- Failure class: {failure_class}\n"
        f"- Failure details: {failure_details}\n"
        f"{validator_section}"
        "Change strategy. Do not repeat the previous failed approach."
    )


def select_prompt_tier(executor_alias: str, routing: RoutingConfig) -> str:
    """Determine prompt tier from executor alias. Returns 'local'|'cloud'|'review'|'cheap'."""
    alias = routing.aliases.get(executor_alias)
    haystack = executor_alias.lower()
    if alias is not None:
        haystack = f"{haystack} {alias.agent.lower()}"
    if "local" in haystack:
        return "local"
    if "review" in haystack:
        return "review"
    if "cheap" in haystack:
        return "cheap"
    return "cloud"


def build_prompt(
    task: Task,
    phase: Phase,
    prd: ForgePRD,
    cwd: Path,
    run_dir: Path,
    tier: str,
    prior_context: list[TaskContextEntry] | None = None,
    reflexion: str = "",
) -> str:
    return assemble_context(
        task=task,
        phase=phase,
        prd=prd,
        cwd=cwd,
        run_dir=run_dir,
        tier=tier,
        prior_context=prior_context,
        reflexion=reflexion,
    )
