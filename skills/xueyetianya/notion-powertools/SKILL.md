# Notion Powertools

> Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

A comprehensive Notion API toolkit for managing pages, databases, blocks, and content directly from the command line. Create and update pages, query databases with filters, manage block content, search across your workspace, and export structured data — all using the official Notion API with your own integration token.

## Description

Notion Powertools provides full programmatic access to your Notion workspace. Whether you need to automate content creation, query databases for reporting, manage page properties, or bulk-update blocks, this skill handles it all through a clean CLI interface. Supports formatted output in table, JSON, or markdown formats.

## Requirements

- `NOTION_API_KEY` — Your Notion integration token (starts with `ntn_` or `secret_`)
- Create an integration at https://www.notion.so/my-integrations
- Share target pages/databases with your integration

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search pages and databases across your workspace |
| `page get <page_id>` | Get page properties and metadata |
| `page create <parent_id> <title> [properties_json]` | Create a new page |
| `page update <page_id> <properties_json>` | Update page properties |
| `page archive <page_id>` | Archive (soft-delete) a page |
| `db query <database_id> [filter_json] [sort_json]` | Query a database with optional filters and sorts |
| `db list <database_id>` | List all entries in a database |
| `block children <block_id>` | List child blocks of a page or block |
| `block append <block_id> <content> [type]` | Append a block to a page (paragraph, heading, todo, etc.) |
| `block delete <block_id>` | Delete a block |
| `user list` | List all users in the workspace |
| `user get <user_id>` | Get user details |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NOTION_API_KEY` | Yes | Notion integration token |
| `NOTION_OUTPUT_FORMAT` | No | Output format: `table` (default), `json`, `markdown` |

## Examples

```bash
# Search for pages
NOTION_API_KEY=ntn_xxx notion-powertools search "Meeting Notes"

# Query a database with filter
NOTION_API_KEY=ntn_xxx notion-powertools db query abc123 '{"property":"Status","select":{"equals":"In Progress"}}'

# Create a new page
NOTION_API_KEY=ntn_xxx notion-powertools page create parent123 "New Task" '{"Status":{"select":{"name":"Todo"}}}'

# Append content to a page
NOTION_API_KEY=ntn_xxx notion-powertools block append page123 "Hello world" paragraph

# List workspace users
NOTION_API_KEY=ntn_xxx notion-powertools user list
```

## Output Formats

- **table** — Human-readable formatted table (default)
- **json** — Raw JSON response from API
- **markdown** — Markdown-formatted output for docs/notes
