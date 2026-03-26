"""Extract session metadata from OpenClaw JSONL logs."""

from __future__ import annotations


def extract_session_metadata(nodes: list[dict]) -> dict:
    """Extract metadata from JSONL nodes for trajectory metadata.

    Returns dict with keys: cwd, model, thinking_level, timestamp, tool_names.
    """
    meta: dict = {
        "cwd": "",
        "model": "",
        "thinking_level": "off",
        "timestamp": "",
        "tool_names": [],
    }

    for node in nodes:
        node_type = node.get("type")

        if node_type == "session":
            meta["cwd"] = node.get("cwd", "")
            meta["timestamp"] = node.get("timestamp", "")

        elif node_type == "model_change":
            meta["model"] = node.get("modelId", "")

        elif node_type == "thinking_level_change":
            meta["thinking_level"] = node.get("thinkingLevel", "off")

        elif node_type == "message":
            msg = node.get("message", {})
            if msg.get("role") == "assistant":
                for block in msg.get("content", []):
                    if isinstance(block, dict) and block.get("type") == "toolCall":
                        name = block.get("name", "")
                        if name:
                            meta["tool_names"].append(name)

            if not meta["model"] and msg.get("model"):
                meta["model"] = msg["model"]

    # Deduplicate tool names preserving order
    seen = set()
    unique = []
    for name in meta["tool_names"]:
        if name not in seen:
            seen.add(name)
            unique.append(name)
    meta["tool_names"] = unique

    return meta
