from __future__ import annotations

from typing import TYPE_CHECKING

from openforge.context import assemble_context
from openforge.prompts import build_prompt, build_reflexion_suffix, select_prompt_tier
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
from openforge.schemas.results import TaskContextEntry

if TYPE_CHECKING:
    from pathlib import Path


def _sample_prd() -> tuple[ForgePRD, Phase, Task]:
    task = Task(
        id="build-feature",
        text="Add capability safely",
        config=TaskConfig(
            id="build-feature",
            reads=["src/example.txt"],
            produces=["src/feature.ts"],
            checks=[TaskCheck(run="pytest -q")],
        ),
        phase_id="implement",
    )
    phase = Phase(
        id="implement",
        config=PhaseConfig(stage=2, executor="cloud"),
        tasks=[task],
    )
    prd = ForgePRD(
        title="Prompt Test",
        objective="Ship a feature safely.",
        problem="The feature is missing.",
        in_scope=["src/", "tests/"],
        routing=RoutingConfig(
            aliases={
                "local": RoutingAlias(agent="openforge-local"),
                "cloud": RoutingAlias(agent="openforge-cloud"),
                "review": RoutingAlias(agent="openforge-review"),
                "cheap": RoutingAlias(agent="openforge-cheap"),
            }
        ),
        phases=[phase],
        acceptance_criteria=["Tests pass"],
    )
    return prd, phase, task


def test_assemble_context_contains_contract_scope_result_and_checks(tmp_path: Path) -> None:
    prd, phase, task = _sample_prd()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "example.txt").write_text("hello from read file", encoding="utf-8")
    (tmp_path / ".openforge").mkdir()
    (tmp_path / ".openforge" / "conventions.md").write_text(
        "Follow conventions.",
        encoding="utf-8",
    )
    prior = [
        TaskContextEntry(
            task_id="earlier",
            phase_id="setup",
            agent_id="cloud-agent",
            summary="Established test harness.",
            files_modified=["tests/test_app.py"],
        )
    ]

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cloud", prior_context=prior)

    assert "## Task contract" in prompt
    assert "Edit files directly in the working tree" in prompt
    assert "Do NOT create commits, branches, or PRs" in prompt
    assert ".openforge/results/build-feature.json" in prompt
    assert "Your changes must pass: pytest -q" in prompt
    assert "hello from read file" in prompt
    assert "Established test harness." in prompt
    assert "Follow conventions." in prompt


def test_build_prompt_delegates_to_context_assembly(tmp_path: Path) -> None:
    prd, phase, task = _sample_prd()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "example.txt").write_text("hello", encoding="utf-8")

    prompt = build_prompt(task, phase, prd, tmp_path, tmp_path, "local")

    assert "Add capability safely" in prompt
    assert "src/feature.ts" in prompt


def test_build_reflexion_suffix_contains_failure_details() -> None:
    prompt = build_reflexion_suffix("validator_failure", "tests failed", validator_output="trace")

    assert "validator_failure" in prompt
    assert "tests failed" in prompt
    assert "trace" in prompt


def test_select_prompt_tier_returns_expected_tiers() -> None:
    prd, _, _ = _sample_prd()
    routing = prd.routing

    assert select_prompt_tier("local", routing) == "local"
    assert select_prompt_tier("review", routing) == "review"
    assert select_prompt_tier("cheap", routing) == "cheap"
    assert select_prompt_tier("cloud", routing) == "cloud"
