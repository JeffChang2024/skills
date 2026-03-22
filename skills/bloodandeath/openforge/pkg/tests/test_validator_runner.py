from __future__ import annotations

from typing import TYPE_CHECKING

from openforge.validator_runner import run_validator

if TYPE_CHECKING:
    from pathlib import Path


def test_run_validator_success(tmp_path: Path) -> None:
    result = run_validator("echo ok", tmp_path)

    assert result.exit_code == 0
    assert result.timed_out is False
    assert "ok" in result.stdout


def test_run_validator_failure(tmp_path: Path) -> None:
    result = run_validator("exit 1", tmp_path)

    assert result.exit_code == 1
    assert result.timed_out is False


def test_run_validator_timeout(tmp_path: Path) -> None:
    result = run_validator("sleep 10", tmp_path, timeout=1)

    assert result.exit_code == 124
    assert result.timed_out is True
