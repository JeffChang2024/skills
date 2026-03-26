"""Content quality checks for trajectory candidates (numeric heuristics).

These are fast, offline checks run before the agent's semantic quality judgment.
"""

from .metadata_stripper import strip_metadata_prefix, is_system_startup_message

# Thresholds
MIN_AVG_USER_MSG_LENGTH = 30  # characters
MIN_TOOL_CALLS = 1
MIN_LONG_USER_MESSAGES = 2  # messages > 100 chars
LONG_MESSAGE_THRESHOLD = 100  # characters


def check_quality(message_nodes: list[dict]) -> tuple[bool, str]:
    """Run numeric quality checks on a conversation's message nodes.

    Args:
        message_nodes: Chronologically ordered list of message nodes
                      (output of dag.extract_conversation_chain)

    Returns:
        (passed, reason) — if passed is False, reason explains why.
    """
    user_texts: list[str] = []
    tool_call_count = 0

    for node in message_nodes:
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
                    tool_call_count += 1

    if not user_texts:
        return False, "no user messages"

    # Check 1: average user message length
    avg_length = sum(len(t) for t in user_texts) / len(user_texts)
    if avg_length < MIN_AVG_USER_MSG_LENGTH:
        return False, f"avg user message length {avg_length:.0f} < {MIN_AVG_USER_MSG_LENGTH}"

    # Check 2: at least 1 tool call
    if tool_call_count < MIN_TOOL_CALLS:
        return False, f"tool calls {tool_call_count} < {MIN_TOOL_CALLS}"

    # Check 3: at least 2 user messages > 100 chars
    long_msgs = sum(1 for t in user_texts if len(t) > LONG_MESSAGE_THRESHOLD)
    if long_msgs < MIN_LONG_USER_MESSAGES:
        return False, f"long user messages ({long_msgs}) < {MIN_LONG_USER_MESSAGES}"

    return True, "passed"


def extract_user_messages_for_review(message_nodes: list[dict]) -> list[str]:
    """Extract cleaned user message texts for agent semantic review.

    Returns list of user message strings (metadata stripped, startup excluded).
    """
    texts: list[str] = []

    for node in message_nodes:
        if node.get("type") == "compaction":
            continue

        msg = node.get("message", {})
        if msg.get("role") != "user":
            continue

        content = msg.get("content", [])
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if not is_system_startup_message(text):
                    cleaned = strip_metadata_prefix(text)
                    if cleaned.strip():
                        texts.append(cleaned)

    return texts
