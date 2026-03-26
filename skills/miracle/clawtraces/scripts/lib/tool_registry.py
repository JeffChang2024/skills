"""Built-in OpenClaw tool schema definitions and schema inference for unknown tools."""

# Built-in tool schemas (Anthropic format with input_schema)
BUILTIN_TOOLS: dict[str, dict] = {
    "exec": {
        "name": "exec",
        "description": "Run shell commands",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
                "timeout": {"type": "number", "description": "Timeout in milliseconds"},
                "cwd": {"type": "string", "description": "Working directory"},
            },
            "required": ["command"],
        },
    },
    "read": {
        "name": "read",
        "description": "Read file contents",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to file to read"},
                "offset": {"type": "number", "description": "Line offset to start reading from"},
                "limit": {"type": "number", "description": "Number of lines to read"},
            },
            "required": ["file_path"],
        },
    },
    "write": {
        "name": "write",
        "description": "Create or overwrite files",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to file to write"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["file_path", "content"],
        },
    },
    "edit": {
        "name": "edit",
        "description": "Make precise edits to files",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to file to edit"},
                "old_string": {"type": "string", "description": "Text to replace"},
                "new_string": {"type": "string", "description": "Replacement text"},
            },
            "required": ["file_path", "old_string", "new_string"],
        },
    },
    "web_search": {
        "name": "web_search",
        "description": "Search the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "count": {"type": "number", "description": "Number of results"},
            },
            "required": ["query"],
        },
    },
    "web_fetch": {
        "name": "web_fetch",
        "description": "Fetch and extract readable content from a URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
            },
            "required": ["url"],
        },
    },
    "browser": {
        "name": "browser",
        "description": "Control web browser for navigation and interaction",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Browser action to perform"},
                "url": {"type": "string", "description": "URL to navigate to"},
                "selector": {"type": "string", "description": "CSS selector for element"},
                "text": {"type": "string", "description": "Text input"},
                "coordinate": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Click coordinates [x, y]",
                },
            },
            "required": ["action"],
        },
    },
    "process": {
        "name": "process",
        "description": "Manage background exec sessions",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: poll, log, kill, list",
                },
                "pid": {"type": "string", "description": "Process ID"},
            },
            "required": ["action"],
        },
    },
    "apply_patch": {
        "name": "apply_patch",
        "description": "Apply a patch to files",
        "input_schema": {
            "type": "object",
            "properties": {
                "patch": {"type": "string", "description": "Unified diff patch content"},
            },
            "required": ["patch"],
        },
    },
}


def _infer_json_type(value) -> str:
    """Infer JSON Schema type from a Python value."""
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "number"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _infer_schema_from_calls(calls: list[dict]) -> dict:
    """Infer a JSON Schema input_schema by merging arguments from all calls to the same tool.

    Collects all observed property names and their types across invocations.
    Properties that appear in every call are marked as required.
    """
    properties: dict[str, dict] = {}
    call_count = len(calls)
    property_counts: dict[str, int] = {}

    for call in calls:
        args = call.get("arguments", {})
        # arguments may be a JSON string in some OpenClaw versions
        if isinstance(args, str):
            try:
                import json
                args = json.loads(args)
            except (json.JSONDecodeError, ValueError):
                continue
        if not isinstance(args, dict):
            continue
        for key, value in args.items():
            property_counts[key] = property_counts.get(key, 0) + 1
            if key not in properties:
                properties[key] = {"type": _infer_json_type(value)}

    # Properties present in every call are considered required
    required = sorted(k for k, count in property_counts.items() if count == call_count)

    schema: dict = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required

    return schema


def get_tool_schemas(tool_calls: list[dict]) -> list[dict]:
    """Build tool schema list from observed tool calls.

    For built-in tools, uses predefined schemas from BUILTIN_TOOLS.
    For non-built-in tools (plugins, MCP), reverse-engineers the schema
    from observed call arguments across all invocations.

    Every tool_use in messages will have a corresponding schema in the
    tools array (1:1 correspondence required by Anthropic format).

    Args:
        tool_calls: List of toolCall blocks from the conversation
    """
    schemas = []
    builtin_added: set[str] = set()
    # Group non-builtin calls by name for schema inference
    non_builtin_calls: dict[str, list[dict]] = {}

    for call in tool_calls:
        name = call.get("name", "")
        if not name:
            continue

        if name in BUILTIN_TOOLS:
            if name not in builtin_added:
                builtin_added.add(name)
                schemas.append(BUILTIN_TOOLS[name])
        else:
            if name not in non_builtin_calls:
                non_builtin_calls[name] = []
            non_builtin_calls[name].append(call)

    # Add inferred schemas for non-builtin tools
    for name, calls in non_builtin_calls.items():
        inferred_schema = _infer_schema_from_calls(calls)
        schemas.append({
            "name": name,
            "description": "",
            "input_schema": inferred_schema,
        })

    return schemas
