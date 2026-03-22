from __future__ import annotations

import json
import os
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from openforge.git_ops import (
    git_diff_names,
    git_diff_staged_names,
    git_ls_untracked,
    git_rev_parse_head,
)
from openforge.overlap import normalize_path, paths_overlap

if TYPE_CHECKING:
    from openforge.schemas.prd import RoutingAlias, RoutingConfig


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON atomically via temp file + rename."""
    content = json.dumps(data, indent=2).encode("utf-8")
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_bytes(content)
    os.replace(str(tmp_path), str(path))


# Tiers that must not fall back to weaker tiers
_TIER_FROM_KEYWORDS: list[tuple[str, str]] = [
    ("review", "review"),
    ("local", "local"),
    ("cheap", "cheap"),
]

_REVIEW_COMPATIBLE_TIERS = {"review", "cloud"}


@dataclass(slots=True)
class DispatchResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool


def _infer_tier(agent_id: str) -> str:
    """Infer the prompt/capability tier from an agent ID."""
    lower = agent_id.lower()
    for keyword, tier in _TIER_FROM_KEYWORDS:
        if keyword in lower:
            return tier
    return "cloud"


def resolve_agent_for_attempt(
    alias: RoutingAlias,
    routing: RoutingConfig,
    attempt_number: int,
) -> str:
    """Resolve which agent ID to use for a given escalation attempt.

    Attempt 1-2 use the primary agent. Attempt 3+ stays on the fallback agent when one
    is defined so later retries do not silently bounce back to the weaker/failed primary.
    The caller is responsible for enforcing the maximum attempt count.
    """
    if attempt_number <= 2 or not alias.fallback:
        return alias.agent

    # Resolve fallback — could be an alias name or a direct agent ID
    if alias.fallback in routing.aliases:
        return routing.aliases[alias.fallback].agent
    return alias.fallback


def validate_fallback_tiers(routing: RoutingConfig) -> list[str]:
    """Validate that fallback chains don't downgrade capability tiers.

    Returns list of warnings. Critical for review tier: must not fall back to
    cheap or local models that cannot identify security issues.
    """
    warnings: list[str] = []
    for alias_name, alias in routing.aliases.items():
        if not alias.fallback:
            continue
        primary_tier = _infer_tier(alias.agent)
        # Resolve fallback agent ID
        if alias.fallback in routing.aliases:
            fallback_agent = routing.aliases[alias.fallback].agent
        else:
            fallback_agent = alias.fallback
        fallback_tier = _infer_tier(fallback_agent)

        if primary_tier == "review" and fallback_tier not in _REVIEW_COMPATIBLE_TIERS:
            warnings.append(
                f"alias '{alias_name}': review agent '{alias.agent}' falls back to "
                f"'{fallback_agent}' (tier '{fallback_tier}'). Review tasks require "
                f"review or cloud-tier models. Cheap/local models cannot reliably "
                f"identify critical issues."
            )
    return warnings


@contextmanager
def _agent_workspace(agent_id: str, cwd: Path):  # type: ignore[return]
    """Context manager that temporarily points an agent's workspace at ``cwd``.

    Saves the original workspace value (if any) and restores it in a ``finally``
    block so the config is always left in its original state, even if the
    dispatch raises an exception.
    """
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists():
        yield
        return

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        yield
        return

    agent_list = config.get("agents", {}).get("list", [])

    target_agent = None
    original_workspace = None
    for agent in agent_list:
        if agent.get("id") == agent_id:
            target_agent = agent
            original_workspace = agent.get("workspace")
            break

    if target_agent is None:
        # Agent not in config — nothing to modify or restore
        yield
        return

    target_agent["workspace"] = str(cwd)
    _atomic_write_json(config_path, config)
    try:
        yield
    finally:
        try:
            fresh_config = json.loads(config_path.read_text(encoding="utf-8"))
            fresh_agents = fresh_config.get("agents", {}).get("list", [])
            for a in fresh_agents:
                if a.get("id") == agent_id:
                    if original_workspace is None:
                        a.pop("workspace", None)
                    else:
                        a["workspace"] = original_workspace
                    break
            _atomic_write_json(config_path, fresh_config)
        except (json.JSONDecodeError, OSError):
            pass  # Config was corrupted or removed externally; skip restore


def dispatch_task(agent_id: str, prompt: str, cwd: Path, timeout: int = 600) -> DispatchResult:
    """Dispatch via: openclaw agent --agent <id> --local --message <prompt>.

    Temporarily updates the agent's workspace to cwd during dispatch, then
    restores the original value afterward (even on failure).
    """
    command = ["openclaw", "agent", "--agent", agent_id, "--local", "--message", prompt]
    with _agent_workspace(agent_id, cwd):
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            return DispatchResult(
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True,
            )
        except FileNotFoundError as exc:
            return DispatchResult(exit_code=127, stdout="", stderr=str(exc), timed_out=False)

    return DispatchResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        timed_out=False,
    )


def check_agent_health(agent_id: str) -> tuple[bool, str]:
    """Check if an agent is configured. Does NOT dispatch a real message."""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
    except FileNotFoundError:
        return (False, "openclaw CLI not found in PATH")
    except subprocess.TimeoutExpired:
        return (False, "openclaw CLI timed out")

    if result.returncode != 0:
        return (False, "openclaw CLI returned non-zero")

    # We can't cheaply verify agent config without dispatching.
    # Return healthy with a note; real validation happens on first dispatch.
    return (True, f"openclaw available; agent '{agent_id}' will be verified on first dispatch")


def detect_no_op(cwd: Path, sha_before: str, produces: list[str]) -> bool:
    """Per §5.6 no-op detection algorithm. Returns True if no meaningful changes."""
    # 1. Check committed changes
    sha_after = git_rev_parse_head(cwd)
    if sha_after != sha_before:
        return False  # New commit(s) exist

    # 2. Check staged changes
    staged = git_diff_staged_names(cwd)
    if staged:
        return False

    # 3. Check unstaged changes within produces scope
    unstaged = git_diff_names(cwd)
    if produces:
        normalized_produces = [normalize_path(p) for p in produces]
        if any(
            any(paths_overlap(normalize_path(f), claim) for claim in normalized_produces)
            for f in unstaged
        ):
            return False
    elif unstaged:
        # No produces declared but files changed — not a no-op
        return False

    # 4. Check new untracked files within produces scope
    untracked = git_ls_untracked(cwd)
    if produces:
        normalized_produces = [normalize_path(p) for p in produces]
        if any(
            any(paths_overlap(normalize_path(f), claim) for claim in normalized_produces)
            for f in untracked
        ):
            return False
    elif untracked:
        return False

    return True  # No-op confirmed
