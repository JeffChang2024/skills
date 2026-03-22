from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from openforge.context import assemble_context
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


def _sample() -> tuple[ForgePRD, Phase, Task]:
    task = Task(
        id="task-one",
        text="Implement the thing",
        config=TaskConfig(
            id="task-one",
            reads=["src/input.txt", "docs"],
            produces=["src/output.txt"],
            checks=[TaskCheck(run="pytest -q")],
        ),
        phase_id="phase-one",
    )
    phase = Phase(id="phase-one", config=PhaseConfig(stage=1, executor="cloud"), tasks=[task])
    prd = ForgePRD(
        title="Context Test",
        objective="Ship it.",
        in_scope=["src/"],
        out_of_scope=["infra/"],
        routing=RoutingConfig(aliases={"cloud": RoutingAlias(agent="openforge-cloud")}),
        phases=[phase],
    )
    return prd, phase, task


def test_assemble_context_cloud_summarizes_large_files(tmp_path: Path) -> None:
    prd, phase, task = _sample()
    (tmp_path / "src").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "readme.md").write_text("doc", encoding="utf-8")
    (tmp_path / "src" / "input.txt").write_text("x" * 3001, encoding="utf-8")

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cloud")

    assert "Large file" in prompt
    assert "docs/readme.md" in prompt


def test_assemble_context_local_inlines_small_files_and_reflexion(tmp_path: Path) -> None:
    prd, phase, task = _sample()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "input.txt").write_text("small file", encoding="utf-8")
    prior = [TaskContextEntry(task_id="t0", phase_id="p0", agent_id="a0", summary="Learned X")]

    with patch("openforge.context.subprocess.run") as run_mock:
        run_mock.return_value.returncode = 0
        run_mock.return_value.stdout = "abc123 prior commit"
        prompt = assemble_context(
            task,
            phase,
            prd,
            tmp_path,
            tmp_path,
            "local",
            prior_context=prior,
            reflexion="Try a different approach.",
        )

    assert "small file" in prompt
    assert "Learned X" in prompt
    assert "abc123 prior commit" in prompt
    assert "Try a different approach." in prompt


def test_file_context_excludes_secret_files(tmp_path: Path) -> None:
    """Secret files in reads: should show [REDACTED] not their contents."""
    prd, phase, _ = _sample()
    task = Task(
        id="task-secret",
        text="Read some files",
        config=TaskConfig(
            id="task-secret",
            reads=[".env"],
            produces=["src/output.txt"],
            checks=[],
        ),
        phase_id="phase-one",
    )
    (tmp_path / ".env").write_text("API_KEY=supersecret", encoding="utf-8")

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cloud")

    assert "[REDACTED: matches secret file pattern]" in prompt
    assert "supersecret" not in prompt


def test_file_context_redacts_secret_content_in_normal_files(tmp_path: Path) -> None:
    """Secret patterns within normal files should be redacted before prompt inclusion."""
    prd, phase, _ = _sample()
    task = Task(
        id="task-content",
        text="Read config",
        config=TaskConfig(
            id="task-content",
            reads=["src/config.txt"],
            produces=["src/output.txt"],
            checks=[],
        ),
        phase_id="phase-one",
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "config.txt").write_text(
        "base_url=https://example.com\napi_key=sk-abcdefghijklmnopqrstuvwxyz1234",
        encoding="utf-8",
    )

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cloud")

    assert "[REDACTED]" in prompt
    assert "sk-abcdefghijklmnopqrstuvwxyz1234" not in prompt


def test_large_file_shows_truncated_content_not_read_instruction(tmp_path: Path) -> None:
    """Large files (>2000 chars, cloud tier) should show truncated content, not a 'Read directly' instruction."""
    prd, phase, _ = _sample()
    task = Task(
        id="task-large",
        text="Read a large file",
        config=TaskConfig(
            id="task-large",
            reads=["src/bigfile.txt"],
            produces=["src/output.txt"],
            checks=[],
        ),
        phase_id="phase-one",
    )
    (tmp_path / "src").mkdir()
    big_content = "A" * 3000
    (tmp_path / "src" / "bigfile.txt").write_text(big_content, encoding="utf-8")

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cloud")

    assert "Read directly from working tree" not in prompt
    assert "Large file" in prompt
    assert "showing first 2000 chars" in prompt
    assert "[truncated]" in prompt
    # Should include the first 2000 chars of content
    assert "A" * 100 in prompt


def test_directory_listing_excludes_secret_files(tmp_path: Path) -> None:
    """Directory listings should not reveal secret filenames."""
    prd, phase, _ = _sample()
    task = Task(
        id="task-dir",
        text="Explore directory",
        config=TaskConfig(
            id="task-dir",
            reads=["mydir"],
            produces=["src/output.txt"],
            checks=[],
        ),
        phase_id="phase-one",
    )
    mydir = tmp_path / "mydir"
    mydir.mkdir()
    (mydir / "normal.py").write_text("print('hi')", encoding="utf-8")
    (mydir / ".env").write_text("SECRET=hunter2", encoding="utf-8")
    (mydir / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (mydir / "credentials.json").write_text('{"key": "val"}', encoding="utf-8")

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cloud")

    assert "normal.py" in prompt
    assert ".env" not in prompt
    assert "id_rsa" not in prompt
    assert "credentials.json" not in prompt


def test_assemble_context_cheap_trims_low_priority_sections(tmp_path: Path) -> None:
    prd, phase, task = _sample()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "input.txt").write_text("x" * 2500, encoding="utf-8")

    prompt = assemble_context(task, phase, prd, tmp_path, tmp_path, "cheap")

    assert "## Task contract" in prompt
    assert ".openforge/results/task-one.json" in prompt
    assert len(prompt) <= 3200
