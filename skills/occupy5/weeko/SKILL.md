---
name: weeko
description: Manage bookmarks and groups via Weeko API. Use when the user wants to save links, list/search bookmarks, create groups, or organize their Weeko collection. Triggers on phrases like "save this to weeko", "add bookmark", "my weeko bookmarks", "create a weeko group", or any mention of weeko/bookmarks in the context of saving or organizing links.
---

# Weeko

Capture freely. Digest weekly.

## Setup

**Required:** Configure API key in one of two ways:

### Option 1: openclaw.json (Recommended)

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "weeko": {
      "apiKey": "wk_your_api_key_here"
    }
  }
}
```

### Option 2: Environment Variable

```bash
export WEEKO_API_KEY="wk_your_api_key_here"
```

Get your API key from Weeko Settings → API tab. Keys start with `wk_`.

## Authentication

API key lookup order (first found wins):
1. `openclaw.json` → `skills.weeko.apiKey`
2. Environment variable `WEEKO_API_KEY`

All API requests require the Authorization header:

```
Authorization: Bearer wk_xxx
```

## Bookmarks

### List All Bookmarks

```bash
curl -s "https://weeko.blog/api/bookmarks" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

**Query Parameters:**
| Name | Type | Description |
|------|------|-------------|
| groupId | string | Filter by group ID |

### Get Single Bookmark

```bash
curl -s "https://weeko.blog/api/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

### Create Bookmark

```bash
curl -s -X POST "https://weeko.blog/api/bookmarks" \
  -H "Authorization: Bearer $WEEKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Bookmark", "url": "https://example.com", "groupId": "clx...", "description": "Optional description"}'
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Bookmark title (1-500 chars) |
| url | string | No | URL (valid URL, max 2000 chars) |
| groupId | string | Yes | Target group ID |
| description | string | No | Description (max 5000 chars) |

**Note:** URL metadata (title, description, favicon) is auto-fetched for links. If bookmark already exists in the group, it will be updated with fresh metadata.

### Update Bookmark

```bash
curl -s -X PATCH "https://weeko.blog/api/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $WEEKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "description": "New description", "url": "https://new-url.com", "groupId": "clx..."}'
```

All fields are optional. Only provided fields will be updated.

### Delete Bookmark

```bash
curl -s -X DELETE "https://weeko.blog/api/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

### Search Bookmarks

```bash
curl -s "https://weeko.blog/api/bookmarks/search?query=keyword" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

**Query Parameters:**
| Name | Type | Description |
|------|------|-------------|
| query | string | Search query (min 1 char) |
| limit | number | Max results (1-50, default: 20) |

Searches by title, URL, or description.

## Groups

### List All Groups

```bash
curl -s "https://weeko.blog/api/groups" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

### Get Single Group

```bash
curl -s "https://weeko.blog/api/groups/GROUP_ID" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

Returns group with its bookmarks.

### Create Group

```bash
curl -s -X POST "https://weeko.blog/api/groups" \
  -H "Authorization: Bearer $WEEKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Group", "color": "#3b82f6"}'
```

**Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Group name (1-100 chars) |
| color | string | No | Hex color (e.g., `#3b82f6`) |

Default color: `#3b82f6`

### Update Group

```bash
curl -s -X PATCH "https://weeko.blog/api/groups/GROUP_ID" \
  -H "Authorization: Bearer $WEEKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name", "color": "#ec4899"}'
```

All fields are optional.

### Delete Group

```bash
curl -s -X DELETE "https://weeko.blog/api/groups/GROUP_ID" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

**Warning:** Deleting a group removes all bookmarks in it. Cannot delete system groups.

## User

### Get Current User

```bash
curl -s "https://weeko.blog/api/user/me" \
  -H "Authorization: Bearer $WEEKO_API_KEY"
```

Returns authenticated user's profile (id, name, email).

## Response Format

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Bookmark Object:**
```json
{
  "id": "clx...",
  "title": "Example",
  "description": "Description text",
  "url": "https://example.com",
  "image": "https://example.com/og.png",
  "favicon": "https://example.com/favicon.ico",
  "siteName": "Example",
  "type": "link",
  "color": null,
  "isPublic": false,
  "groupId": "clx...",
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T00:00:00.000Z",
  "group": { "id": "clx...", "name": "Development", "color": "#3b82f6" }
}
```

**Group Object:**
```json
{
  "id": "clx...",
  "name": "Development",
  "color": "#3b82f6",
  "isPublic": false,
  "bookmarkCount": 42,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T00:00:00.000Z"
}
```

## Rate Limits

| Type | Limit | Methods |
|------|-------|---------|
| General | 60/min | GET |
| Write | 30/min | POST, PATCH, DELETE |
| Key Generation | 5/hour | Key Gen |

Headers in every response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid input or bad request |
| 401 | Unauthorized (invalid/missing API key) |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Workflow

**Before ANY API call:**
1. Check API key in order:
   - Read from `~/.openclaw/openclaw.json` → `skills.weeko.apiKey`
   - Fall back to environment variable `$WEEKO_API_KEY`
2. If NOT found, output this message and STOP:

   "Weeko API key not configured. Add to `~/.openclaw/openclaw.json`:

   ```json
   {
     \"skills\": {
       \"weeko\": {
         \"apiKey\": \"wk_your_key_here\"
       }
     }
   }
   ```

   Or set environment variable: `export WEEKO_API_KEY=\"wk_your_key_here\"`"

3. Only proceed with API calls after key is confirmed

**Adding a bookmark:**
1. For URLs without titles, optionally fetch page title via web fetch
2. Show confirmation with bookmark title and URL
3. Offer to assign to a group if groups exist

**Searching bookmarks:**
1. Use search endpoint with query parameter
2. Present matching results clearly

**Creating groups:**
1. Ask for group name
2. Ask for color preference (hex format: `#3b82f6`)
3. Create via API and confirm

## MCP Integration

For AI assistants supporting Model Context Protocol (Claude Desktop, Cursor, Windsurf):

```json
{
  "mcpServers": {
    "weeko": {
      "type": "http",
      "url": "https://weeko.blog/api/mcp",
      "headers": {
        "Authorization": "Bearer wk_your_api_key"
      }
    }
  }
}
```

**Available MCP Tools:** `list_bookmarks`, `get_bookmark`, `create_bookmark`, `update_bookmark`, `delete_bookmark`, `search_bookmarks`, `list_groups`, `get_group`, `create_group`, `update_group`, `delete_group`, `get_current_user`

## Best Practices

- Confirm operations with brief message
- Format list output clearly (not raw JSON)
- Default to URL's page title when adding bookmarks
- Suggest creating groups if user frequently adds unsorted bookmarks