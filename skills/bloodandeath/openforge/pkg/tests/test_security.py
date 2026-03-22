from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from openforge.security import (
    is_secret_file,
    redact_secrets,
    sanitized_env,
    scan_for_secrets,
    verify_scope,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_is_secret_file_matches_expected_sensitive_names() -> None:
    assert is_secret_file(".env")
    assert is_secret_file(".env.local")
    assert is_secret_file("key.pem")
    assert is_secret_file("my_credentials.json")


def test_is_secret_file_ignores_normal_project_files() -> None:
    assert not is_secret_file("package.json")
    assert not is_secret_file("src/index.ts")


def test_scan_for_secrets_detects_common_secret_patterns() -> None:
    content = """
    api_key = sk-abcdefghijklmnopqrstuvwxyz1234
    Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload
    aws = AKIA1234567890ABCDEF
    -----BEGIN RSA PRIVATE KEY-----
    """

    findings = scan_for_secrets(content)

    assert len(findings) >= 4


def test_scan_for_secrets_returns_empty_for_clean_content() -> None:
    content = "const greeting = 'hello';\nexport function add(a, b) { return a + b; }"

    assert scan_for_secrets(content) == []


def test_redact_secrets_replaces_matches() -> None:
    content = "token=supersecret\napi_key=sk-abcdefghijklmnopqrstuvwxyz1234"

    redacted = redact_secrets(content)

    assert "[REDACTED]" in redacted
    assert "supersecret" not in redacted
    assert "sk-abcdefghijklmnopqrstuvwxyz1234" not in redacted


def test_verify_scope_passes_for_paths_inside_claims(tmp_path: Path) -> None:
    passed, violations = verify_scope(
        modified_paths=["src/feature.ts", "tests/feature.test.ts"],
        declared_produces=["src/", "tests/feature.test.ts"],
        cwd=tmp_path,
    )

    assert passed is True
    assert violations == []


def test_verify_scope_fails_for_paths_outside_claims(tmp_path: Path) -> None:
    passed, violations = verify_scope(
        modified_paths=["src/feature.ts", "docs/notes.md"],
        declared_produces=["src/"],
        cwd=tmp_path,
    )

    assert passed is False
    assert violations == ["docs/notes.md"]


def test_is_secret_file_returns_true_for_secret_patterns() -> None:
    assert is_secret_file(".env")
    assert is_secret_file(".env.production")
    assert is_secret_file("server.pem")
    assert is_secret_file("id_rsa.key")
    assert is_secret_file("my_credentials.json")
    assert is_secret_file("app_secret.txt")


def test_is_secret_file_returns_false_for_normal_files() -> None:
    assert not is_secret_file("README.md")
    assert not is_secret_file("src/app.py")
    assert not is_secret_file("package.json")
    assert not is_secret_file("config.yaml")


def test_redact_secrets_replaces_api_key_patterns() -> None:
    content = "OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz1234"
    redacted = redact_secrets(content)
    assert "[REDACTED]" in redacted
    assert "sk-abcdefghijklmnopqrstuvwxyz1234" not in redacted


def test_redact_secrets_replaces_bearer_tokens() -> None:
    content = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"
    redacted = redact_secrets(content)
    assert "[REDACTED]" in redacted
    assert "eyJhbGciOiJIUzI1NiJ9" not in redacted


def test_redact_secrets_replaces_aws_keys() -> None:
    content = "aws_access_key_id = AKIA1234567890ABCDEF"
    redacted = redact_secrets(content)
    assert "[REDACTED]" in redacted
    assert "AKIA1234567890ABCDEF" not in redacted


def test_redact_secrets_leaves_clean_content_unchanged() -> None:
    content = "x = 42\ndef hello(): return 'world'"
    assert redact_secrets(content) == content


def test_sanitized_env_uses_allowlist() -> None:
    """sanitized_env uses an allowlist — only explicitly permitted vars pass through."""
    fake_env = {
        "PATH": "/usr/bin",
        "HOME": "/home/test",
        "LANG": "en_US.UTF-8",
        "TMPDIR": "/tmp",
        "OPENAI_API_KEY": "secret",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "NORMAL_VAR": "should-be-stripped",
        "DATABASE_URL": "should-be-stripped",
    }

    with patch.dict("openforge.security.os.environ", fake_env, clear=True):
        env = sanitized_env()

    # Allowlisted vars pass through
    assert env["PATH"] == "/usr/bin"
    assert env["HOME"] == "/home/test"
    assert env["LANG"] == "en_US.UTF-8"
    assert env["TMPDIR"] == "/tmp"
    # Everything else is stripped — allowlist, not denylist
    assert "OPENAI_API_KEY" not in env
    assert "AWS_SECRET_ACCESS_KEY" not in env
    assert "NORMAL_VAR" not in env
    assert "DATABASE_URL" not in env
