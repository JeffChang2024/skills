from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from openforge.security import is_secret_file, redact_secrets

if TYPE_CHECKING:
    from pathlib import Path

    from openforge.schemas.prd import ForgePRD, Phase, Task
    from openforge.schemas.results import TaskContextEntry

_BUDGETS = {"local": 6000, "cloud": 50000, "review": 30000, "cheap": 3000}
_CONVENTION_FILES = ("AGENTS.md", "CLAUDE.md", ".openforge/conventions.md")


def _format_list(items: list[str], empty: str = "- None declared") -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def _read_text_if_exists(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _task_contract(task: Task, phase: Phase, prd: ForgePRD) -> str:
    checks = [check.run for check in task.config.checks]
    checks_block = _format_list(checks, empty="- None declared")
    requirement = f"Your changes must pass: {', '.join(checks)}\n" if checks else ""
    return (
        "## Task contract\n"
        f"PRD: {prd.title}\n"
        f"Phase: {phase.id} (stage {phase.config.stage})\n"
        f"Task: {task.id}\n"
        f"Instruction: {task.text}\n\n"
        "Reads:\n"
        f"{_format_list(task.config.reads)}\n\n"
        "Produces:\n"
        f"{_format_list(task.config.produces)}\n\n"
        "Checks:\n"
        f"{checks_block}\n"
        f"{requirement}"
    )


def _scope_rules(task: Task, prd: ForgePRD) -> str:
    out_of_scope = _format_list(prd.out_of_scope, empty="- None declared")
    produces = _format_list(task.config.produces)
    return (
        "## Scope rules\n"
        "- Edit files directly in the working tree.\n"
        "- Do NOT create commits, branches, or PRs.\n"
        "- Stay strictly inside declared produces unless a read-only check requires otherwise.\n"
        f"- Do not modify out-of-scope areas: {out_of_scope}\n"
        f"- Do not modify files outside: {produces}\n"
        "- Keep changes minimal and relevant to this task only.\n"
    )


def _result_envelope(task: Task) -> str:
    return (
        "## Result envelope\n"
        f"After completing your work, write a result file to `.openforge/results/{task.id}.json`.\n"
        "Schema:\n"
        '{"task_id":"string","status":"completed|blocked|failed|noop","summary":"string",'
        '"decisions":["string"],"files_modified":["string"],"artifacts":["string"],'
        '"unresolved":["string"],"notes":"string"}\n'
    )


def _conventions(cwd: Path) -> str:
    snippets: list[str] = []
    for relative in _CONVENTION_FILES:
        path = cwd / relative
        content = _read_text_if_exists(path)
        if content:
            content = redact_secrets(content)
            snippets.append(f"### {relative}\n{content.strip()}")
    if not snippets:
        return ""
    return "## Conventions\n" + "\n\n".join(snippets) + "\n"


def _prior_context(entries: list[TaskContextEntry] | None, max_chars: int) -> str:
    if not entries:
        return ""
    lines = ["## Prior task context"]
    used = len(lines[0]) + 1
    for entry in reversed(entries):
        summary = entry.summary or "No summary"
        block = (
            f"- {entry.phase_id}/{entry.task_id} via {entry.agent_id}: {summary}\n"
            f"  Decisions: {', '.join(entry.decisions) or 'None'}\n"
            f"  Files: {', '.join(entry.files_modified) or 'None'}\n"
            f"  Unresolved: {', '.join(entry.unresolved) or 'None'}\n"
        )
        if used + len(block) > max_chars:
            break
        lines.append(block.rstrip())
        used += len(block)
    return "\n".join(lines) + "\n"


def _file_context(task: Task, cwd: Path, tier: str) -> str:
    if not task.config.reads:
        return ""

    parts = ["## Referenced file context"]
    for read_target in task.config.reads:
        path = cwd / read_target
        if not path.exists():
            parts.append(f"### {read_target}\n[MISSING]")
            continue
        if path.is_dir():
            listed = [
                str(item.relative_to(cwd))
                for item in path.rglob("*")
                if item.is_file() and not is_secret_file(str(item.relative_to(cwd)))
            ]
            preview = sorted(listed)[:50]
            body = "\n".join(f"- {item}" for item in preview)
            suffix = "\n... truncated ..." if len(listed) > len(preview) else ""
            parts.append(f"### {read_target}\nDirectory contents:\n{body}{suffix}")
            continue

        if is_secret_file(read_target):
            parts.append(f"### {read_target}\n[REDACTED: matches secret file pattern]")
            continue

        content = _read_text_if_exists(path)
        if content is None:
            parts.append(f"### {read_target}\n[Binary or unreadable file]")
            continue
        content = redact_secrets(content)
        if tier == "local" or len(content) <= 2000:
            parts.append(f"### {read_target}\n```\n{content.strip()}\n```")
        else:
            truncated = content[:2000]
            parts.append(
                f"### {read_target}\n"
                f"Large file ({len(content)} chars), showing first 2000 chars:\n```\n{truncated.strip()}\n```\n[truncated]"
            )
    return "\n\n".join(parts) + "\n"


def _git_context(cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return ""
    if result.returncode != 0 or not result.stdout.strip():
        return ""
    return f"## Git context\n{redact_secrets(result.stdout.strip())}\n"


def _reflexion(reflexion: str) -> str:
    if not reflexion.strip():
        return ""
    return f"## Retry hint\n{reflexion.strip()}\n"


def assemble_context(
    task: Task,
    phase: Phase,
    prd: ForgePRD,
    cwd: Path,
    run_dir: Path,
    tier: str,
    prior_context: list[TaskContextEntry] | None = None,
    reflexion: str = "",
) -> str:
    """Build a complete prompt with tier-appropriate context."""
    budget = _BUDGETS.get(tier, _BUDGETS["cloud"])
    del run_dir

    sections = [
        _task_contract(task, phase, prd),
        _scope_rules(task, prd),
        _result_envelope(task),
        _conventions(cwd),
        _prior_context(prior_context, max_chars=max(500, budget // 4)),
        _file_context(task, cwd, tier),
        _git_context(cwd),
        _reflexion(reflexion),
    ]

    included: list[str] = []
    used = 0
    for section in sections:
        if not section:
            continue
        chunk = section.rstrip() + "\n\n"
        if used + len(chunk) > budget:
            break
        included.append(chunk)
        used += len(chunk)

    return redact_secrets("".join(included).rstrip() + "\n")
