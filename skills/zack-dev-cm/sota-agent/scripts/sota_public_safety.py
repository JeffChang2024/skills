#!/usr/bin/env python3
"""Helpers for public-safe SOTA-agent artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


SENSITIVE_KEY_HINTS = (
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "COOKIE",
    "CREDENTIAL",
    "AUTH",
)


def is_sensitive_key(key: str) -> bool:
    normalized = key.upper().replace("-", "_")
    return any(hint in normalized for hint in SENSITIVE_KEY_HINTS)


def looks_like_credential_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return bool(parsed.scheme and (parsed.username or parsed.password))


def is_absolute_like(value: str) -> bool:
    return value.startswith("/") or value.startswith("~/")


def classify_target(host: str, path: str) -> str:
    host = host.lower()
    path = path.lower()
    if "colab" in host:
        return "colab"
    if "kaggle" in host:
        return "kaggle"
    if "github" in host:
        return "github"
    if "chatgpt" in host:
        return "chatgpt"
    if "gemini" in host:
        return "gemini"
    if "notebook" in host or "notebook" in path:
        return "notebook"
    if host:
        return "browser"
    return ""


def sanitize_url(raw_url: str, allow_raw: bool = False) -> dict[str, Any]:
    raw_url = raw_url.strip()
    if not raw_url:
        return {
            "url": "",
            "target_host": "",
            "target_kind": "",
            "target_label": "",
            "url_redacted": False,
        }
    try:
        parsed = urlsplit(raw_url)
    except ValueError:
        parsed = urlsplit("")
    host = parsed.hostname or parsed.netloc.split("@")[-1]
    kind = classify_target(host, parsed.path)
    label = host or kind or "browser-target"
    return {
        "url": raw_url if allow_raw else "",
        "target_host": host,
        "target_kind": kind,
        "target_label": label,
        "url_redacted": not allow_raw,
    }


def sanitize_url_for_display(raw_url: str, allow_raw: bool = False) -> str:
    info = sanitize_url(raw_url, allow_raw=allow_raw)
    if allow_raw:
        return info["url"]
    parts = [part for part in (info["target_label"], info["target_kind"]) if part]
    return " ".join(parts) if parts else "<redacted-url>"


def sanitize_path(
    path: str | Path,
    *,
    alias_roots: Iterable[tuple[Path | None, str]] = (),
    allow_absolute_paths: bool = False,
) -> str:
    resolved = Path(path).expanduser().resolve()
    if allow_absolute_paths:
        return str(resolved)
    for root, alias in alias_roots:
        if root is None:
            continue
        try:
            relative = resolved.relative_to(root.expanduser().resolve())
        except ValueError:
            continue
        rel_text = relative.as_posix()
        return alias if not rel_text or rel_text == "." else f"{alias}/{rel_text}"
    return f"<external>/{resolved.name or 'path'}"


def sanitize_env_value(key: str, value: str, allow_raw: bool = False) -> str:
    if allow_raw:
        return value
    if is_sensitive_key(key):
        return "<redacted:sensitive-key>"
    if looks_like_credential_url(value):
        return "<redacted:credential-url>"
    return value


def sanitize_env_map(items: dict[str, str], allow_raw: bool = False) -> dict[str, str]:
    return {key: sanitize_env_value(key, value, allow_raw=allow_raw) for key, value in items.items()}


def sanitize_command_tokens(
    tokens: list[str],
    *,
    alias_roots: Iterable[tuple[Path | None, str]] = (),
    allow_absolute_paths: bool = False,
    allow_raw: bool = False,
) -> list[str]:
    if allow_raw:
        return list(tokens)

    sanitized: list[str] = []
    redact_next = False
    for token in tokens:
        if redact_next:
            sanitized.append("<redacted:sensitive-flag-value>")
            redact_next = False
            continue

        if token.startswith("--"):
            if "=" in token:
                flag, value = token.split("=", 1)
                flag_name = flag.lstrip("-")
                if is_sensitive_key(flag_name):
                    sanitized.append(f"{flag}=<redacted:sensitive-flag-value>")
                elif looks_like_credential_url(value):
                    sanitized.append(f"{flag}=<redacted:credential-url>")
                elif is_absolute_like(value):
                    sanitized.append(
                        f"{flag}={sanitize_path(value, alias_roots=alias_roots, allow_absolute_paths=allow_absolute_paths)}"
                    )
                else:
                    sanitized.append(token)
            else:
                sanitized.append(token)
                if is_sensitive_key(token.lstrip("-")):
                    redact_next = True
            continue

        if "=" in token:
            key, value = token.split("=", 1)
            if is_sensitive_key(key):
                sanitized.append(f"{key}=<redacted:sensitive-env>")
                continue
            if looks_like_credential_url(value):
                sanitized.append(f"{key}=<redacted:credential-url>")
                continue
            if is_absolute_like(value):
                sanitized.append(
                    f"{key}={sanitize_path(value, alias_roots=alias_roots, allow_absolute_paths=allow_absolute_paths)}"
                )
                continue

        if looks_like_credential_url(token):
            sanitized.append("<redacted:credential-url>")
        elif is_absolute_like(token):
            sanitized.append(sanitize_path(token, alias_roots=alias_roots, allow_absolute_paths=allow_absolute_paths))
        else:
            sanitized.append(token)
    return sanitized


def sanitize_ref(value: str, allow_raw: bool = False) -> str:
    value = value.strip()
    if not value:
        return ""
    if "://" in value:
        return sanitize_url_for_display(value, allow_raw=allow_raw)
    if is_absolute_like(value):
        return sanitize_path(value, allow_absolute_paths=allow_raw)
    return value
