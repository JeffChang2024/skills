from __future__ import annotations

import hashlib
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from openforge.schemas.state import RunState


class GitError(RuntimeError):
    """Raised when a git subprocess fails."""


class ResumeError(RuntimeError):
    """Raised when a saved run cannot be safely resumed."""


def _run_git(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "git command failed"
        msg = f"git {' '.join(args)} failed: {stderr}"
        raise GitError(msg)
    return result


def _split_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.strip()]


def _dirty_patch_hash(cwd: Path) -> str:
    diff = _run_git(["diff", "HEAD", "--", "."], cwd).stdout
    return hashlib.sha256(diff.encode("utf-8")).hexdigest()


def git_rev_parse_head(cwd: Path) -> str:
    return _run_git(["rev-parse", "HEAD"], cwd).stdout.strip()


def git_diff_names(cwd: Path) -> list[str]:
    """Unstaged modified file names."""
    return _split_lines(_run_git(["diff", "--name-only"], cwd).stdout)


def git_diff_staged_names(cwd: Path) -> list[str]:
    return _split_lines(_run_git(["diff", "--cached", "--name-only"], cwd).stdout)


def git_ls_untracked(cwd: Path) -> list[str]:
    """Untracked files not in .gitignore."""
    return _split_lines(_run_git(["ls-files", "--others", "--exclude-standard"], cwd).stdout)


def git_status_porcelain(cwd: Path) -> str:
    return _run_git(["status", "--porcelain"], cwd).stdout


def git_is_ancestor(ancestor: str, descendant: str, cwd: Path) -> bool:
    result = _run_git(["merge-base", "--is-ancestor", ancestor, descendant], cwd, check=False)
    if result.returncode in {0, 1}:
        return result.returncode == 0
    stderr = result.stderr.strip() or result.stdout.strip() or "git merge-base failed"
    raise GitError(stderr)


def git_diff_name_only_from(sha: str, cwd: Path) -> list[str]:
    """Files changed since sha (committed + staged + unstaged)."""
    committed = _split_lines(_run_git(["diff", "--name-only", f"{sha}..HEAD"], cwd).stdout)
    staged = git_diff_staged_names(cwd)
    unstaged = git_diff_names(cwd)
    untracked = git_ls_untracked(cwd)
    return sorted(set(committed + staged + unstaged + untracked))


def capture_baseline(cwd: Path) -> tuple[str, str, list[str]]:
    """Returns (baseline_hash, base_commit, untracked_files) per §13.2."""
    return (_dirty_patch_hash(cwd), git_rev_parse_head(cwd), git_ls_untracked(cwd))


def verify_baseline(state: RunState, cwd: Path) -> None:
    """Raises ResumeError if baseline doesn't match. Per §13.2."""
    current_head = git_rev_parse_head(cwd)
    expected_head = state.base_commit
    if expected_head is not None and current_head != expected_head and not git_is_ancestor(
        expected_head, current_head, cwd
    ):
        msg = (
            f"base commit mismatch: expected descendant of {expected_head}, found {current_head}"
        )
        raise ResumeError(msg)

    if state.baseline_dirty_patch_hash is not None:
        current_dirty_hash = _dirty_patch_hash(cwd)
        if current_dirty_hash != state.baseline_dirty_patch_hash:
            msg = "working tree baseline patch hash changed since run started"
            raise ResumeError(msg)

    current_untracked = git_ls_untracked(cwd)
    if sorted(current_untracked) != sorted(state.baseline_untracked_files):
        msg = "untracked file set changed since run started"
        raise ResumeError(msg)


def git_add_and_commit(cwd: Path, message: str) -> str | None:
    """Stage all changes and commit. Returns commit SHA or None if nothing to commit."""
    _run_git(["add", "-A"], cwd)
    status = git_status_porcelain(cwd).strip()
    if not status:
        return None
    result = _run_git(["commit", "-m", message], cwd, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        if "nothing to commit" in stderr.lower():
            return None
        msg = stderr or "git commit failed"
        raise GitError(msg)
    return git_rev_parse_head(cwd)
