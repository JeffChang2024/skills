#!/usr/bin/env python3
"""
heartbeat-cron.py — Push email notifications for iCloud (OpenClaw skill).

Checks iCloud for new unread emails via himalaya. If new emails are found,
sends a triage prompt to the agent and forwards important notifications
to Telegram.

Designed to run every 5 minutes via cron. Zero cost when no new emails exist.

Usage:
    python3 heartbeat-cron.py             # Normal run
    python3 heartbeat-cron.py --dry-run   # Show what would happen, no agent call
"""

import fcntl
import json
import logging
import subprocess
import sys
import os
import tempfile
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler

# --- Path resolution ---
# All paths are relative to the skill directory (parent of scripts/).
# This makes the script work both in dev (repo checkout) and deployed
# (scp'd into ~/.openclaw/workspace/skills/icloud-toolkit/).

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# --- Config ---
# Read himalaya_config from the skill's config.json so we use the same
# config as icloud.py — no hardcoded paths that diverge across machines.

def load_skill_config() -> dict:
    """Load the skill's config.json for himalaya_config path."""
    config_path = os.path.join(SKILL_DIR, "config", "config.json")
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fall back gracefully — himalaya will use its default config
        return {}

_skill_config = load_skill_config()

# --- Constants ---

HIMALAYA = _skill_config.get("himalaya_bin", "/home/linuxbrew/.linuxbrew/bin/himalaya")
OPENCLAW = _skill_config.get("openclaw_bin", "openclaw")
TELEGRAM_USER = _skill_config.get("telegram_user", "")

# Config-driven: use the same himalaya config as icloud.py.
# If himalaya_config isn't set in config.json, himalaya falls back to
# its default (~/.config/himalaya/config.toml).
HIMALAYA_CONFIG = _skill_config.get("himalaya_config")
ACCOUNT_LABEL = "icloud"

# Skill-local state — each skill owns its own state directory so there's
# no coupling between icloud-toolkit and protonmail.
STATE_DIR = os.path.join(SKILL_DIR, "state")
STATE_FILE = os.path.join(STATE_DIR, "heartbeat-state.json")
LOCK_FILE = os.path.join(STATE_DIR, "heartbeat-cron.lock")

LOG_DIR = os.path.expanduser("~/.openclaw/logs")
LOG_FILE = os.path.join(LOG_DIR, "heartbeat-icloud.log")

EMAIL_CHECK_TIMEOUT = 30   # seconds
AGENT_CALL_TIMEOUT = 120   # seconds
MAX_STATE_IDS = 500        # cap to prevent unbounded growth
RECENCY_HOURS = 24         # fallback max age if no last_fetch timestamp exists

# --- Logging ---

def setup_logging():
    """Rotating log: 1MB max, 3 backups."""
    os.makedirs(LOG_DIR, exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger = logging.getLogger("heartbeat-icloud")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

log = setup_logging()

# --- Locking ---
# Prevents overlapping cron runs from racing on the state file.

def acquire_lock():
    """Acquire an exclusive lock file. Returns the file handle, or None if locked."""
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        lock_fh = open(LOCK_FILE, "w")
        fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_fh
    except OSError:
        return None

# --- State ---

def load_state() -> dict:
    """Load heartbeat state, returning fresh state if file is missing or corrupt."""
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        if not isinstance(state.get("notified_ids"), list):
            raise ValueError("missing notified_ids")
        return state
    except FileNotFoundError:
        log.info("No state file found, starting fresh")
    except (json.JSONDecodeError, ValueError) as e:
        log.warning("Corrupt state file (%s), starting fresh", e)
    return {
        "notified_ids": [],
        "last_fetch": None,
        "last_run": None,
    }


def save_state(state: dict):
    """Save state atomically via temp file + rename."""
    if len(state["notified_ids"]) > MAX_STATE_IDS:
        state["notified_ids"] = state["notified_ids"][-MAX_STATE_IDS:]
    state["last_run"] = datetime.now(timezone.utc).isoformat()

    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.rename(tmp_path, STATE_FILE)
    except OSError as e:
        log.error("Failed to save state: %s", e)

# --- Email Checking ---

def fetch_envelopes() -> list[dict] | None:
    """
    Fetch envelope list from himalaya as JSON.
    Returns list of envelope dicts, or None on failure.
    """
    cmd = [HIMALAYA]
    if HIMALAYA_CONFIG:
        cmd += ["--config", HIMALAYA_CONFIG]
    cmd += ["envelope", "list", "--output", "json", "order", "by", "date", "desc"]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=EMAIL_CHECK_TIMEOUT
        )
        if result.returncode != 0:
            log.error("%s himalaya failed: %s", ACCOUNT_LABEL, result.stderr.strip())
            return None
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        log.error("%s himalaya timed out after %ds", ACCOUNT_LABEL, EMAIL_CHECK_TIMEOUT)
        return None
    except json.JSONDecodeError as e:
        log.error("%s himalaya returned invalid JSON: %s", ACCOUNT_LABEL, e)
        return None
    except OSError as e:
        log.error("%s himalaya could not be executed: %s", ACCOUNT_LABEL, e)
        return None


def get_unread(envelopes: list[dict]) -> list[dict]:
    """Filter to unread emails (those without 'Seen' flag)."""
    return [e for e in envelopes if "Seen" not in e.get("flags", [])]


def is_recent(email: dict, last_fetch: str | None) -> bool:
    """Check if an email's date is within the recency window.

    Uses last_fetch timestamp when available so emails that arrived during
    downtime aren't silently dropped. Falls back to RECENCY_HOURS on first run.
    """
    date_str = email.get("date", "")
    if not date_str:
        return False
    try:
        dt = datetime.fromisoformat(date_str.replace(" ", "T"))
        if last_fetch:
            cutoff = datetime.fromisoformat(last_fetch)
        else:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENCY_HOURS)
        return dt >= cutoff
    except ValueError:
        log.warning("Could not parse date: %s", date_str)
        return True  # If we can't parse, err on the side of notifying


def find_new_emails(
    envelopes: list[dict] | None, notified_ids: list[str], last_fetch: str | None
) -> list[dict]:
    """
    Return envelopes that are unread, not already notified, and recent.
    """
    if envelopes is None:
        return []
    unread = get_unread(envelopes)
    notified_set = set(notified_ids)
    new = []
    for e in unread:
        eid = e.get("id")
        if not eid:
            log.warning("Skipping envelope with no ID: %s", e)
            continue
        if eid not in notified_set and is_recent(e, last_fetch):
            new.append(e)
    return new

# --- Prompt Building ---

def _group_emails(emails: list[dict]) -> list[tuple[int, str, str]]:
    """Group emails by sender address and return (count, sender, subject) tuples.

    Groups by sender address — bulk senders collapse to one row while
    unique senders stay visible as their own row.
    """
    groups: dict[str, list] = {}
    order: list[str] = []
    for e in emails:
        addr = e.get("from", {}).get("addr", "unknown")
        if addr not in groups:
            groups[addr] = []
            order.append(addr)
        groups[addr].append(e)

    result = []
    for addr in order:
        group = groups[addr]
        count = len(group)
        sender = (
            group[0].get("from", {}).get("name")
            or group[0].get("from", {}).get("addr", "Unknown")
        )
        subject = group[0].get("subject", "(no subject)")[:80]
        result.append((count, sender, subject))
    return result


def build_prompt(new_emails: list[dict]) -> str:
    """Build a compact triage prompt grouped by sender."""
    total = len(new_emails)
    lines = [
        "[HEARTBEAT] New unread iCloud emails detected. Review and triage.",
        "",
        "Rules:",
        '- If NONE need attention: respond with exactly "NO_ACTION"',
        "- If ANY are important: describe them concisely",
        "- Important = personal messages, action items, time-sensitive",
        "- Ignore newsletters, marketing, automated notifications, receipts",
        "",
        f"Total new unread: {total}",
        "",
        "iCloud:",
    ]
    for count, sender, subject in _group_emails(new_emails):
        prefix = f"{count}x " if count > 1 else ""
        lines.append(f"  {prefix}{sender} | {subject}")

    return "\n".join(lines)

# --- Agent Integration ---

def send_to_claw(prompt: str) -> str | None:
    """
    Send triage prompt via openclaw agent --json (no --deliver).
    Returns the agent's text response, or None on failure.
    """
    cmd = [
        OPENCLAW, "agent",
        "--channel", "telegram",
        "--to", TELEGRAM_USER,
        "--message", prompt,
        "--json",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=AGENT_CALL_TIMEOUT
        )
        if result.returncode != 0:
            log.error("openclaw agent failed: %s", result.stderr.strip())
            return None

        data = json.loads(result.stdout)
        payloads = data.get("result", {}).get("payloads", [])
        texts = [p["text"] for p in payloads if p.get("text")]
        return "\n".join(texts).strip() if texts else None
    except subprocess.TimeoutExpired:
        log.error("openclaw agent timed out after %ds", AGENT_CALL_TIMEOUT)
        return None
    except (json.JSONDecodeError, KeyError) as e:
        log.error("Failed to parse agent response: %s", e)
        return result.stdout.strip() if result.stdout else None
    except OSError as e:
        log.error("openclaw agent could not be executed: %s", e)
        return None


def forward_to_telegram(message: str) -> bool:
    """Send a notification message to Telegram via openclaw message send."""
    cmd = [
        OPENCLAW, "message", "send",
        "--channel", "telegram",
        "--target", TELEGRAM_USER,
        "--message", message,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            log.error("Telegram send failed: %s", result.stderr.strip())
            return False
        log.info("Notification sent to Telegram")
        return True
    except subprocess.TimeoutExpired:
        log.error("Telegram send timed out")
        return False
    except OSError as e:
        log.error("Telegram send could not be executed: %s", e)
        return False

# --- Main ---

def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        log.addHandler(logging.StreamHandler(sys.stdout))

    lock_fh = acquire_lock()
    if lock_fh is None:
        log.warning("Another heartbeat-icloud instance is running, skipping this cycle")
        return

    log.info("--- Heartbeat iCloud run started (dry_run=%s) ---", dry_run)

    state = load_state()

    envelopes = fetch_envelopes()
    new_emails = find_new_emails(
        envelopes, state["notified_ids"], state.get("last_fetch"),
    )

    now_iso = datetime.now(timezone.utc).isoformat()
    if envelopes is not None:
        state["last_fetch"] = now_iso

    log.info("Found %d new unread iCloud emails", len(new_emails))

    if not new_emails:
        log.info("No new emails, exiting")
        save_state(state)
        return

    prompt = build_prompt(new_emails)

    if dry_run:
        print("\n=== DRY RUN: Would send this prompt to Claw ===")
        print(prompt)
        print("=== END PROMPT ===\n")
        print(f"New IDs: {[e.get('id') for e in new_emails]}")
        state["notified_ids"] += [e["id"] for e in new_emails if e.get("id")]
        save_state(state)
        return

    log.info("Sending %d new emails to Claw for triage", len(new_emails))
    response = send_to_claw(prompt)

    if not response:
        log.error("No/empty response from Claw, will retry next cycle")
        save_state(state)
        return

    log.info("Claw response: %s", response[:200])

    if response.strip().upper() == "NO_ACTION":
        log.info("Claw says nothing important, staying silent")
    else:
        log.info("Claw flagged important emails, forwarding to Telegram")
        delivered = forward_to_telegram(response)

        if not delivered:
            log.warning("Telegram delivery failed, will retry these emails next cycle")
            save_state(state)
            return

    state["notified_ids"] += [e["id"] for e in new_emails if e.get("id")]
    save_state(state)

    log.info("--- Heartbeat iCloud run completed ---")


if __name__ == "__main__":
    main()
