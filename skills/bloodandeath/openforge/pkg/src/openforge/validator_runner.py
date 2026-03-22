from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from openforge.security import sanitized_env

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(slots=True)
class ValidatorResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool


def run_validator(
    command: str,
    cwd: Path,
    timeout: int = 300,
    env: dict[str, str] | None = None,
) -> ValidatorResult:
    """Run validator subprocess with output capture and timeout."""
    merged_env = sanitized_env()
    if env is not None:
        merged_env.update(env)

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            env=merged_env,
        )
    except subprocess.TimeoutExpired as exc:
        return ValidatorResult(
            exit_code=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            timed_out=True,
        )

    return ValidatorResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        timed_out=False,
    )
