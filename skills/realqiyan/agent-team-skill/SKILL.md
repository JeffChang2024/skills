---
name: agent-team
description: Manage team member information including skills, roles, and work assignments. Use when: (1) listing team members, (2) adding or updating member profiles, (3) checking member expertise for task assignment, (4) managing team division and collaboration.
---

# Agent Team Management

Manage team member information including skills, roles, and work assignments.

## Commands

All commands are executed via the `team.py` script:

```bash
python3 scripts/team.py <command> [options]
```

### List Members

List all team members in table format:

```bash
python3 scripts/team.py list
```

Output example:
```
+-------------+--------+------------+---------+------------------+------------------+------------------+
| Agent ID    | Name   | Role       | Enabled | Tags             | Expertise        | Not Good At      |
+-------------+--------+------------+---------+------------------+------------------+------------------+
| agent-001   | Alice  | Developer  | true    | backend, api     | python, go       | frontend         |
| agent-002   | Bob    | Designer   | true    | ui, ux           | figma, css       | backend          |
+-------------+--------+------------+---------+------------------+------------------+------------------+
```

### Add/Update Member

Add a new member or update an existing one:

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --enabled true \
  --tags "backend,api,database" \
  --expertise "python,go,postgresql" \
  --not-good-at "frontend,design"
```

Parameters:

| Parameter | Description | Required |
|-----------|-------------|----------|
| --agent-id | Member unique identifier | Yes |
| --name | Member name | Yes |
| --role | Role/position | Yes |
| --enabled | Enable status (true/false) | Yes |
| --tags | Tags (comma-separated) | Yes |
| --expertise | Skills (comma-separated) | Yes |
| --not-good-at | Weak areas (comma-separated) | Yes |

### Reset Data

Clear all team data and reset to empty state:

```bash
python3 scripts/team.py reset
```

This resets the team data to `{"team": {}}`.

## Data Storage

Team data is stored at `~/.agent-team/team.json`. The directory is created automatically if it doesn't exist.

## Use Cases

- **Team Building**: Record all team members and their skill information
- **Task Assignment**: Assign tasks based on member expertise and tags
- **Capability Assessment**: Understand each member's strengths and weaknesses
- **Team Collaboration**: Quickly find members with specific skills