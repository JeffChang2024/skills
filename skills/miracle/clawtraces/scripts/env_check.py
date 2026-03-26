#!/usr/bin/env python3
"""Check and auto-fix OpenClaw environment for ClawTraces.

Ensures diagnostics.cacheTrace is enabled with includeSystem=true
in openclaw.json. Modifies the config automatically if needed.

Usage:
    python env_check.py
"""

import json
import os
import sys


def get_openclaw_config_path() -> str:
    """Get openclaw.json path."""
    state_dir = os.environ.get("OPENCLAW_STATE_DIR", os.path.expanduser("~/.openclaw"))
    return os.path.join(state_dir, "openclaw.json")


def load_config(config_path: str) -> dict:
    """Load openclaw.json, returning empty dict if not found."""
    if not os.path.isfile(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Failed to parse {config_path}: {e}", file=sys.stderr)
        return {}


def save_config(config_path: str, config: dict):
    """Save config back to openclaw.json."""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")


def check_and_fix(config_path: str | None = None) -> dict:
    """Check cache-trace config and auto-fix if needed.

    Returns dict with:
        - ok: bool — whether config is now correct
        - changed: bool — whether config was modified
        - needs_restart: bool — whether OpenClaw needs restart
        - message: str — human-readable status
    """
    if config_path is None:
        config_path = get_openclaw_config_path()

    config = load_config(config_path)
    changed = False

    # Ensure diagnostics.cacheTrace exists
    if "diagnostics" not in config:
        config["diagnostics"] = {}
    if "cacheTrace" not in config["diagnostics"]:
        config["diagnostics"]["cacheTrace"] = {}

    cache_trace = config["diagnostics"]["cacheTrace"]

    # Check and fix enabled
    if cache_trace.get("enabled") is not True:
        cache_trace["enabled"] = True
        changed = True

    # Check and fix includeSystem
    if cache_trace.get("includeSystem") is not True:
        cache_trace["includeSystem"] = True
        changed = True

    if changed:
        save_config(config_path, config)
        return {
            "ok": True,
            "changed": True,
            "needs_restart": True,
            "message": (
                f"已自动更新 {config_path}，开启了 cache-trace 诊断。\n"
                "需要重启 OpenClaw 使配置生效。"
            ),
        }

    return {
        "ok": True,
        "changed": False,
        "needs_restart": False,
        "message": "cache-trace 配置正常。",
    }


def main():
    result = check_and_fix()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["changed"]:
        print(f"\n{result['message']}", file=sys.stderr)


if __name__ == "__main__":
    main()
