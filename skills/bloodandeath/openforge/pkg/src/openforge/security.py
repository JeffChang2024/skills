from __future__ import annotations

import fnmatch
import os
import re
from typing import TYPE_CHECKING

from openforge.overlap import normalize_path, paths_overlap

if TYPE_CHECKING:
    from pathlib import Path

SECRET_FILE_PATTERNS = [
    ".env*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.keystore",
    "*credential*",
    "*secret*",
    "id_rsa*",
    "id_ed25519*",
    "id_ecdsa*",
    "id_dsa*",
    ".npmrc",
    ".pypirc",
    ".netrc",
    ".docker/config.json",
    ".aws/credentials",
    "*.pfx",
]

SECRET_CONTENT_PATTERNS = [
    r"(?:api[_-]?key|apikey)\s*[:=]\s*\S+",
    r"(?:secret|token|password|passwd|pwd)\s*[:=]\s*\S+",
    r"-----BEGIN\s+\S+\s+PRIVATE\s+KEY-----",
    r"Bearer\s+ey[A-Za-z0-9_-]+",
    r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}",
    r"sk-[A-Za-z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
]

_COMPILED_SECRET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in SECRET_CONTENT_PATTERNS
]

_ENV_ALLOWLIST = {
    "HOME", "LANG", "LC_ALL", "LC_CTYPE", "PATH", "PWD",
    "PYTHONPATH", "TMPDIR", "VIRTUAL_ENV", "UV_PYTHON",
    "NODE_ENV", "NODE_PATH", "NPM_CONFIG_PREFIX",
    "TERM", "SHELL", "USER", "LOGNAME",
}


def is_secret_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    basename = normalized.rsplit("/", 1)[-1]
    return any(
        fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(basename, pattern)
        for pattern in SECRET_FILE_PATTERNS
    )


def scan_for_secrets(content: str) -> list[str]:
    """Returns list of detected secret descriptions. Empty = clean."""
    findings: list[str] = []
    for pattern in _COMPILED_SECRET_PATTERNS:
        match = pattern.search(content)
        if match is not None:
            findings.append(f"matched secret pattern: {pattern.pattern}")
    return findings


def redact_secrets(content: str) -> str:
    """Replace detected secrets with [REDACTED]."""
    redacted = content
    for pattern in _COMPILED_SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


# Paths created by OpenForge itself or by OpenClaw bootstrap — never scope violations
_OPENFORGE_INTERNAL_PREFIXES = (
    ".openforge/",
    ".openclaw/",
)
_OPENCLAW_BOOTSTRAP_FILES = {
    "AGENTS.md", "BOOTSTRAP.md", "HEARTBEAT.md", "IDENTITY.md",
    "MEMORY.md", "SOUL.md", "TOOLS.md", "USER.md",
}


def verify_scope(
    modified_paths: list[str], declared_produces: list[str], cwd: Path
) -> tuple[bool, list[str]]:
    """Check modified paths are within declared scope. Returns (passed, violations)."""
    del cwd
    allowed = [normalize_path(path) for path in declared_produces]
    violations: list[str] = []

    for modified in modified_paths:
        normalized_modified = normalize_path(modified)
        if not normalized_modified:
            violations.append(modified)
            continue
        # Skip OpenForge internal files and OpenClaw bootstrap files
        if any(normalized_modified.startswith(prefix) for prefix in _OPENFORGE_INTERNAL_PREFIXES):
            continue
        if normalized_modified in _OPENCLAW_BOOTSTRAP_FILES:
            continue
        if not any(paths_overlap(normalized_modified, claim) for claim in allowed):
            violations.append(modified)

    return (not violations, violations)


def sanitized_env() -> dict[str, str]:
    """Return sanitized environment for validator subprocess.

    Uses an ALLOWLIST model: only explicitly permitted variables pass through.
    Everything else is stripped.
    """
    return {key: value for key, value in os.environ.items() if key in _ENV_ALLOWLIST}
