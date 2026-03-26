#!/usr/bin/env python3
"""Scan local OpenClaw sessions, filter, convert to Anthropic trajectory format.

Merged scan + convert pipeline (V2). Outputs trajectory files and a candidates
list for agent semantic quality review.

Usage:
    python scan_and_convert.py [--sessions-dir PATH] [--output-dir PATH]
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from lib.session_index import find_openclaw_sessions_dirs, get_qualifying_sessions
from lib.dag import parse_jsonl, extract_conversation_chain, count_turns, get_model_from_nodes
from lib.converter import convert_to_trajectory
from lib.metadata_stripper import strip_metadata_prefix, is_system_startup_message
from lib.system_prompt_builder import extract_session_metadata
from lib.cache_trace import get_cache_trace_path, build_session_system_prompt_index
from lib.quality_checker import check_quality, extract_user_messages_for_review

MIN_TURNS = 5
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
MANIFEST_FILENAME = "manifest.json"


def _load_manifest(output_dir: str) -> dict:
    """Load manifest to check already-submitted and rejected sessions."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"submitted": {}, "rejected": {}}


def _get_skip_session_ids(output_dir: str) -> set[str]:
    """Get set of session IDs to skip (already submitted or rejected)."""
    manifest = _load_manifest(output_dir)
    submitted = manifest.get("submitted", {})
    rejected = manifest.get("rejected", {})
    # submitted keys are like "session_id.trajectory.json"
    ids = {k.replace(".trajectory.json", "") for k in submitted}
    # rejected keys are session_id directly
    ids.update(rejected.keys())
    return ids


def _extract_user_texts_and_tools(messages: list[dict]) -> tuple[list[str], list[str]]:
    """Extract user message texts and tool names from conversation chain."""
    user_texts = []
    tool_names = []

    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        role = msg.get("role")
        content = msg.get("content", [])

        if role == "user":
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    if not is_system_startup_message(text):
                        user_texts.append(strip_metadata_prefix(text))

        elif role == "assistant":
            for block in content:
                if isinstance(block, dict) and block.get("type") == "toolCall":
                    tool_names.append(block.get("name", ""))

    return user_texts, tool_names


def _extract_session_stats(nodes: list[dict], messages: list[dict]) -> dict:
    """Extract session-level stats from source data for upload alongside trajectory.

    These stats are NOT part of the trajectory training data — they are
    operational metrics sent as a separate field during upload.
    """
    # Timestamps: first and last node
    started_at = nodes[0].get("timestamp") if nodes else None
    ended_at = nodes[-1].get("timestamp") if nodes else None

    # Accumulate usage and tool stats from the conversation chain
    token_input = 0
    token_output = 0
    cache_read = 0
    cache_write = 0
    tool_use_count = 0
    tool_name_set: set[str] = set()

    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        role = msg.get("role")

        if role == "assistant":
            usage = msg.get("usage", {})
            token_input += usage.get("input", 0)
            token_output += usage.get("output", 0)
            cache_read += usage.get("cacheRead", 0)
            cache_write += usage.get("cacheWrite", 0)
            for block in msg.get("content", []):
                if isinstance(block, dict) and block.get("type") == "toolCall":
                    tool_use_count += 1
                    name = block.get("name", "")
                    if name:
                        tool_name_set.add(name)

    return {
        "started_at": started_at,
        "ended_at": ended_at,
        "token_input": token_input,
        "token_output": token_output,
        "cache_read": cache_read,
        "cache_write": cache_write,
        "tool_use_count": tool_use_count,
        "tool_names": sorted(tool_name_set),
    }


def _compute_prefix_hash(messages: list[dict], n: int = 5) -> str:
    """Compute hash of first N user messages for prefix deduplication.

    Strips metadata prefixes before hashing so that the same message
    sent via different channels (TUI vs Telegram) produces the same hash.
    """
    user_texts = []
    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        if msg.get("role") == "user":
            content = msg.get("content", [])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    raw = block.get("text", "")
                    if not is_system_startup_message(raw):
                        user_texts.append(strip_metadata_prefix(raw))
                    break
        if len(user_texts) >= n:
            break

    combined = "\n---\n".join(user_texts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]


def _get_session_created_time(session_info: dict) -> float:
    """Get session creation time for sorting. Uses file mtime as fallback."""
    file_path = session_info.get("file_path", "")
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0.0


def _find_latest_session_ids(all_sessions: list[dict]) -> set[str]:
    """Find the latest session ID per agent to skip.

    Each agent may have an active session, so we skip the most recent
    session from each agent rather than only one globally.
    """
    if not all_sessions:
        return set()

    # Group by agent_id
    by_agent: dict[str, list[dict]] = {}
    for s in all_sessions:
        agent = s.get("agent_id", "unknown")
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(s)

    latest_ids = set()
    for agent, sessions in by_agent.items():
        # Only consider non-reset sessions as potentially active
        active_sessions = [s for s in sessions if ".reset." not in s.get("file_path", "")]
        if not active_sessions:
            continue
        latest = max(active_sessions, key=_get_session_created_time)
        sid = latest.get("session_id")
        if sid:
            latest_ids.add(sid)

    return latest_ids


def scan_and_convert(
    sessions_dirs: list[str],
    output_dir: str,
) -> list[dict]:
    """Scan sessions, filter, convert, and output trajectory files.

    Returns list of candidate dicts for agent semantic review, each containing:
        - session_id, turns, domain, output_path
        - user_messages: list of cleaned user message texts (for semantic review)
    """
    # Collect all qualifying sessions across all agents
    all_qualifying = []
    for sessions_dir in sessions_dirs:
        qualifying = get_qualifying_sessions(sessions_dir)
        all_qualifying.extend(qualifying)

    if not all_qualifying:
        print("No qualifying sessions found (model filter).", file=sys.stderr)
        return []

    # Skip the latest session per agent (might still be active)
    latest_sids = _find_latest_session_ids(all_qualifying)
    if latest_sids:
        before = len(all_qualifying)
        all_qualifying = [s for s in all_qualifying if s["session_id"] not in latest_sids]
        skipped = before - len(all_qualifying)
        if skipped:
            print(f"Skipped {skipped} latest session(s) (may still be active): {', '.join(latest_sids)}", file=sys.stderr)

    # Skip already-submitted and rejected sessions
    skip_ids = _get_skip_session_ids(output_dir)
    if skip_ids:
        before = len(all_qualifying)
        all_qualifying = [s for s in all_qualifying if s["session_id"] not in skip_ids]
        skipped = before - len(all_qualifying)
        if skipped:
            print(f"Skipped {skipped} already-processed session(s) (submitted or rejected).", file=sys.stderr)

    if not all_qualifying:
        print("No new sessions to process.", file=sys.stderr)
        return []

    # Build cache-trace system prompt index
    cache_trace_path = get_cache_trace_path()
    system_prompt_index = build_session_system_prompt_index(cache_trace_path)
    if system_prompt_index:
        print(f"Loaded system prompts for {len(system_prompt_index)} session(s) from cache-trace.", file=sys.stderr)

    # Process each session
    candidates = []
    prefix_groups: dict[str, list[dict]] = {}

    for session_info in all_qualifying:
        file_path = session_info["file_path"]
        session_id = session_info["session_id"]

        try:
            nodes = parse_jsonl(file_path)
            messages = extract_conversation_chain(nodes)

            if not messages:
                continue

            # Turn count filter
            turns = count_turns(messages)
            if turns <= MIN_TURNS:
                continue

            # Extract user texts for review (domain will be classified in agent review step)
            user_texts, tool_names = _extract_user_texts_and_tools(messages)

            # Numeric quality check
            quality_ok, quality_reason = check_quality(messages)
            if not quality_ok:
                print(f"  Quality skip ({quality_reason}): {session_id}", file=sys.stderr)
                continue

            # Require real system prompt from cache-trace
            real_system_prompt = system_prompt_index.get(session_id)
            if not real_system_prompt:
                print(f"  Skipped (no cache-trace system prompt): {session_id}", file=sys.stderr)
                continue
            session_meta = extract_session_metadata(nodes)

            # Convert to trajectory
            trajectory = convert_to_trajectory(
                messages,
                session_meta=session_meta,
                real_system_prompt=real_system_prompt,
            )

            if trajectory.get("_discarded"):
                print(f"  Skipped ({trajectory['_discarded']}): {session_id}", file=sys.stderr)
                continue

            if not trajectory["messages"]:
                print(f"  Skipped (empty after conversion): {session_id}", file=sys.stderr)
                continue

            # Add metadata
            model = get_model_from_nodes(nodes) or session_info.get("model", "unknown")
            trajectory["metadata"] = {
                "source_session_id": session_id,
                "source_agent_id": session_info.get("agent_id", ""),
                "model": model,
                "domain": "pending",
                "turns": turns,
                "converted_at": datetime.now(timezone.utc).isoformat(),
                "system_prompt_source": "cache_trace",
                "system_prompt_complete": True,
            }

            # Extract session stats (separate from trajectory)
            stats = _extract_session_stats(nodes, messages)

            # Write trajectory file
            output_filename = f"{session_id}.trajectory.json"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(trajectory, f, ensure_ascii=False, indent=2)

            # Write stats file alongside trajectory
            stats_filename = f"{session_id}.stats.json"
            stats_path = os.path.join(output_dir, stats_filename)
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

            # Extract user messages for semantic review

            # Prefix hash for dedup
            prefix_hash = _compute_prefix_hash(messages)

            candidate = {
                "session_id": session_id,
                "turns": turns,
                "domain": "pending",
                "model": model,
                "output_path": output_path,
                "message_count": len(trajectory["messages"]),
                "tool_count": len(trajectory["tools"]),
                "user_messages": review_messages,
                "_prefix_hash": prefix_hash,
            }

            # Group by prefix hash for dedup
            if prefix_hash not in prefix_groups:
                prefix_groups[prefix_hash] = []
            prefix_groups[prefix_hash].append(candidate)

        except Exception as e:
            print(f"  Error processing {file_path}: {e}", file=sys.stderr)
            continue

    # Prefix dedup: keep longest per group
    for prefix_hash, group in prefix_groups.items():
        best = max(group, key=lambda x: x["turns"])
        candidates.append(best)

        if len(group) > 1:
            dropped = len(group) - 1
            print(f"  Prefix dedup: kept {best['session_id']} ({best['turns']} turns), dropped {dropped}", file=sys.stderr)

            # Clean up trajectory files of dropped candidates
            for c in group:
                if c["session_id"] != best["session_id"]:
                    try:
                        os.remove(c["output_path"])
                    except OSError:
                        pass

    # Remove internal fields from output
    for c in candidates:
        c.pop("_prefix_hash", None)

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Scan and convert OpenClaw sessions to trajectories")
    parser.add_argument("--sessions-dir", help="Override sessions directory path")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    # Create output dir
    os.makedirs(args.output_dir, exist_ok=True)

    if args.sessions_dir:
        sessions_dirs = [args.sessions_dir]
    else:
        sessions_dirs = find_openclaw_sessions_dirs()

    if not sessions_dirs:
        print("No OpenClaw sessions directories found.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(sessions_dirs)} agent(s)...", file=sys.stderr)
    candidates = scan_and_convert(sessions_dirs, args.output_dir)
    print(f"\nGenerated {len(candidates)} candidate trajectory(ies).", file=sys.stderr)

    if candidates:
        print(f"\nDomain classification pending (will be done in agent review step).", file=sys.stderr)

    # Write full candidates (with user_messages) to file for agent review
    output_path = os.path.join(args.output_dir, "candidates.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"\nCandidates written to {output_path}", file=sys.stderr)

    # Print summary to stdout (without user_messages to avoid flooding context)
    summary = []
    for c in candidates:
        summary.append({
            "session_id": c["session_id"],
            "turns": c["turns"],
            "domain": c["domain"],
            "model": c["model"],
            "message_count": c["message_count"],
            "tool_count": c["tool_count"],
        })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
