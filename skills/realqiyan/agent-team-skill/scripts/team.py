#!/usr/bin/env python3
"""Team Division Management Tool

Manages team member information including skills, roles, and work assignments.
Data is stored in ~/.agent-team/team.json by default, or a custom path via --data-file.
"""

import argparse
import json
import sys
from pathlib import Path

# Global variable to store custom data file path
_data_file_path: Path | None = None


def set_data_file(path: str | None) -> None:
    """Set a custom data file path."""
    global _data_file_path
    if path:
        _data_file_path = Path(path)


def get_data_file() -> Path:
    """Get the path to the team data file."""
    if _data_file_path:
        data_file = _data_file_path
        data_file.parent.mkdir(parents=True, exist_ok=True)
        return data_file
    data_dir = Path.home() / ".agent-team"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "team.json"


def load_data() -> dict:
    """Load team data from JSON file."""
    data_file = get_data_file()
    if not data_file.exists():
        return {"team": {}}

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "team" not in data:
                return {"team": {}}
            return data
    except (json.JSONDecodeError, IOError):
        return {"team": {}}


def save_data(data: dict) -> None:
    """Save team data to JSON file."""
    data_file = get_data_file()
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def reset_data() -> None:
    """Reset all team data to empty state."""
    save_data({"team": {}})
    print("Team data has been reset to empty.")


def list_members() -> None:
    """List all team members in table format."""
    data = load_data()
    team = data.get("team", {})

    if not team:
        print("No team members found.")
        return

    headers = ["Agent ID", "Name", "Role", "Enabled", "Tags", "Expertise", "Not Good At"]
    col_widths = [12, 10, 15, 8, 20, 20, 20]

    # Print header
    def print_separator():
        parts = ["+" + "-" * (w + 2) for w in col_widths]
        print("".join(parts) + "+")

    def print_row(values):
        parts = []
        for i, val in enumerate(values):
            truncated = str(val)[:col_widths[i]]
            parts.append(f"| {truncated:<{col_widths[i]}}")
        print("".join(parts) + "|")

    print_separator()
    print_row(headers)
    print_separator()

    for member_id, member in team.items():
        tags = ", ".join(member.get("tags", []))
        expertise = ", ".join(member.get("expertise", []))
        not_good_at = ", ".join(member.get("not_good_at", []))

        row = [
            member.get("agent_id", "")[:col_widths[0]],
            member.get("name", "")[:col_widths[1]],
            member.get("role", "")[:col_widths[2]],
            str(member.get("enabled", ""))[:col_widths[3]],
            tags[:col_widths[4]],
            expertise[:col_widths[5]],
            not_good_at[:col_widths[6]],
        ]
        print_row(row)

    print_separator()
    print(f"Total: {len(team)} member(s)")


def update_member(
    agent_id: str,
    name: str,
    role: str,
    enabled: bool,
    tags: str,
    expertise: str,
    not_good_at: str,
) -> None:
    """Add or update a team member."""
    data = load_data()
    is_new = agent_id not in data["team"]

    member = {
        "agent_id": agent_id,
        "name": name,
        "role": role,
        "enabled": enabled,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "expertise": [e.strip() for e in expertise.split(",") if e.strip()],
        "not_good_at": [n.strip() for n in not_good_at.split(",") if n.strip()],
    }

    data["team"][agent_id] = member
    save_data(data)

    action = "Added" if is_new else "Updated"
    print(f"{action} member: {name} ({agent_id})")


def main():
    parser = argparse.ArgumentParser(
        description="Team Division Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data-file",
        help="Path to data file (default: ~/.agent-team/team.json)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    subparsers.add_parser("list", help="List all team members")

    # reset command
    subparsers.add_parser("reset", help="Reset all team data to empty")

    # update command
    update_parser = subparsers.add_parser("update", help="Add or update a team member")
    update_parser.add_argument("--agent-id", required=True, help="Member unique ID")
    update_parser.add_argument("--name", required=True, help="Member name")
    update_parser.add_argument("--role", required=True, help="Member role")
    update_parser.add_argument(
        "--enabled", required=True, choices=["true", "false"], help="Is member enabled"
    )
    update_parser.add_argument("--tags", required=True, help="Tags (comma separated)")
    update_parser.add_argument(
        "--expertise", required=True, help="Expertise skills (comma separated)"
    )
    update_parser.add_argument(
        "--not-good-at", required=True, help="Weak areas (comma separated)"
    )

    args = parser.parse_args()

    # Set custom data file if provided
    set_data_file(args.data_file)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list":
        list_members()
    elif args.command == "reset":
        reset_data()
    elif args.command == "update":
        update_member(
            agent_id=args.agent_id,
            name=args.name,
            role=args.role,
            enabled=args.enabled == "true",
            tags=args.tags,
            expertise=args.expertise,
            not_good_at=args.not_good_at,
        )


if __name__ == "__main__":
    main()