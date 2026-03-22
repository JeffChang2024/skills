from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import patch

from openforge.executor import DispatchResult, _agent_workspace, detect_no_op, resolve_agent_for_attempt
from openforge.schemas.prd import RoutingAlias, RoutingConfig

if TYPE_CHECKING:
    from pathlib import Path


def test_detect_no_op_returns_true_when_no_changes(tmp_path: Path) -> None:
    """No commits, no staged, no unstaged, no untracked → no-op."""
    with (
        patch("openforge.executor.git_rev_parse_head", return_value="abc123"),
        patch("openforge.executor.git_diff_staged_names", return_value=[]),
        patch("openforge.executor.git_diff_names", return_value=[]),
        patch("openforge.executor.git_ls_untracked", return_value=[]),
    ):
        assert detect_no_op(tmp_path, "abc123", ["src/"]) is True


def test_detect_no_op_returns_false_when_new_commit(tmp_path: Path) -> None:
    """New commit after task → not a no-op."""
    with (
        patch("openforge.executor.git_rev_parse_head", return_value="def456"),
        patch("openforge.executor.git_diff_staged_names", return_value=[]),
        patch("openforge.executor.git_diff_names", return_value=[]),
        patch("openforge.executor.git_ls_untracked", return_value=[]),
    ):
        assert detect_no_op(tmp_path, "abc123", ["src/"]) is False


def test_detect_no_op_returns_false_when_unstaged_in_scope(tmp_path: Path) -> None:
    """Unstaged changes within produces scope → not a no-op."""
    with (
        patch("openforge.executor.git_rev_parse_head", return_value="abc123"),
        patch("openforge.executor.git_diff_staged_names", return_value=[]),
        patch("openforge.executor.git_diff_names", return_value=["src/feature.ts"]),
        patch("openforge.executor.git_ls_untracked", return_value=[]),
    ):
        assert detect_no_op(tmp_path, "abc123", ["src/"]) is False


def test_detect_no_op_returns_true_when_changes_outside_scope(tmp_path: Path) -> None:
    """Changes exist but outside produces scope → still a no-op for this task."""
    with (
        patch("openforge.executor.git_rev_parse_head", return_value="abc123"),
        patch("openforge.executor.git_diff_staged_names", return_value=[]),
        patch("openforge.executor.git_diff_names", return_value=["docs/readme.md"]),
        patch("openforge.executor.git_ls_untracked", return_value=[]),
    ):
        assert detect_no_op(tmp_path, "abc123", ["src/"]) is True


def test_detect_no_op_no_produces_with_changes(tmp_path: Path) -> None:
    """No produces declared but files changed → not a no-op."""
    with (
        patch("openforge.executor.git_rev_parse_head", return_value="abc123"),
        patch("openforge.executor.git_diff_staged_names", return_value=[]),
        patch("openforge.executor.git_diff_names", return_value=["something.txt"]),
        patch("openforge.executor.git_ls_untracked", return_value=[]),
    ):
        assert detect_no_op(tmp_path, "abc123", []) is False


def test_resolve_agent_for_late_attempts_keeps_using_fallback() -> None:
    routing = RoutingConfig(
        aliases={
            "primary": RoutingAlias(agent="openforge-cloud", fallback="backup"),
            "backup": RoutingAlias(agent="openforge-review"),
        }
    )

    assert resolve_agent_for_attempt(routing.aliases["primary"], routing, 1) == "openforge-cloud"
    assert resolve_agent_for_attempt(routing.aliases["primary"], routing, 2) == "openforge-cloud"
    assert resolve_agent_for_attempt(routing.aliases["primary"], routing, 3) == "openforge-review"
    assert resolve_agent_for_attempt(routing.aliases["primary"], routing, 5) == "openforge-review"


def _make_openclaw_config(home_dir: Path, agent_id: str, workspace: str | None = None) -> Path:
    """Helper to create a fake openclaw.json at home_dir/.openclaw/openclaw.json."""
    openclaw_dir = home_dir / ".openclaw"
    openclaw_dir.mkdir(exist_ok=True)
    agent: dict = {"id": agent_id}
    if workspace is not None:
        agent["workspace"] = workspace
    config = {"agents": {"list": [agent]}}
    config_path = openclaw_dir / "openclaw.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config_path


def test_agent_workspace_restores_original_after_dispatch(tmp_path: Path) -> None:
    """Workspace should be restored to original value after context manager exits."""
    config_path = _make_openclaw_config(tmp_path, "openforge-cloud", workspace="/original/path")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    with patch("openforge.executor.Path.home", return_value=tmp_path):
        with _agent_workspace("openforge-cloud", project_dir):
            # Inside: workspace should be updated
            config = json.loads(config_path.read_text())
            assert config["agents"]["list"][0]["workspace"] == str(project_dir)

        # After: workspace should be restored
        config = json.loads(config_path.read_text())
        assert config["agents"]["list"][0]["workspace"] == "/original/path"


def test_agent_workspace_restores_even_if_dispatch_fails(tmp_path: Path) -> None:
    """Workspace must be restored even if body raises an exception."""
    config_path = _make_openclaw_config(tmp_path, "openforge-cloud", workspace="/original/path")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    with patch("openforge.executor.Path.home", return_value=tmp_path):
        try:
            with _agent_workspace("openforge-cloud", project_dir):
                raise RuntimeError("simulated dispatch failure")
        except RuntimeError:
            pass

        config = json.loads(config_path.read_text())
        assert config["agents"]["list"][0]["workspace"] == "/original/path"


def test_agent_workspace_removes_key_when_none_originally(tmp_path: Path) -> None:
    """If agent had no workspace key, it should be removed (not set to None) on restore."""
    config_path = _make_openclaw_config(tmp_path, "openforge-cloud", workspace=None)
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    with patch("openforge.executor.Path.home", return_value=tmp_path):
        with _agent_workspace("openforge-cloud", project_dir):
            config = json.loads(config_path.read_text())
            assert "workspace" in config["agents"]["list"][0]

        config = json.loads(config_path.read_text())
        assert "workspace" not in config["agents"]["list"][0]


def test_agent_workspace_noop_when_agent_not_in_config(tmp_path: Path) -> None:
    """When agent is not found in config, context manager should do nothing."""
    config_path = _make_openclaw_config(tmp_path, "other-agent", workspace="/some/path")
    original_text = config_path.read_text()
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    with patch("openforge.executor.Path.home", return_value=tmp_path):
        with _agent_workspace("openforge-cloud", project_dir):
            pass  # Should not modify config

    assert config_path.read_text() == original_text


def test_agent_workspace_restores_using_fresh_reload(tmp_path: Path) -> None:
    """Restore should reload config from disk (not stale in-memory copy) before writing."""
    config_path = _make_openclaw_config(tmp_path, "openforge-cloud", workspace="/original/path")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    with patch("openforge.executor.Path.home", return_value=tmp_path):
        with _agent_workspace("openforge-cloud", project_dir):
            # Simulate an external write to config during execution
            config = json.loads(config_path.read_text())
            config["agents"]["list"][0]["extra_field"] = "added_externally"
            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        # After: workspace restored, extra_field preserved (fresh reload was used)
        config = json.loads(config_path.read_text())
        assert config["agents"]["list"][0]["workspace"] == "/original/path"
        assert config["agents"]["list"][0].get("extra_field") == "added_externally"


def test_agent_workspace_handles_corrupted_config_on_restore(tmp_path: Path) -> None:
    """If config is corrupted before restore, the context manager should not raise."""
    config_path = _make_openclaw_config(tmp_path, "openforge-cloud", workspace="/original/path")
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    with patch("openforge.executor.Path.home", return_value=tmp_path):
        with _agent_workspace("openforge-cloud", project_dir):
            # Corrupt the config file during execution
            config_path.write_text("{ invalid json }", encoding="utf-8")
        # Should not raise; restore silently skips


def test_dispatch_result_dataclass_construction() -> None:
    result = DispatchResult(exit_code=0, stdout="ok", stderr="", timed_out=False)

    assert result.exit_code == 0
    assert result.stdout == "ok"
    assert result.stderr == ""
    assert result.timed_out is False
