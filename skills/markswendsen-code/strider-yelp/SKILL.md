---
name: strider-yelp
description: Search businesses via Yelp using Strider Labs MCP connector. Find restaurants, services, read reviews, get hours and contact info. Complete autonomous local discovery for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "discovery"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Yelp Connector

MCP connector for searching local businesses on Yelp — find restaurants, services, read reviews, check hours, and get contact information. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-yelp
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "yelp": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-yelp"]
    }
  }
}
```

## Available Tools

### yelp.search_businesses
Search for businesses by type, location, and filters.

**Input Schema:**
```json
{
  "term": "string (business type or name)",
  "location": "string (city, address, or zip)",
  "categories": ["string (optional: restaurants, plumbers, etc.)"],
  "price": ["string (optional: 1, 2, 3, 4 for $ to $$$$)"],
  "open_now": "boolean (optional)",
  "sort_by": "string (optional: rating, review_count, distance)"
}
```

**Output:**
```json
{
  "businesses": [{
    "id": "string",
    "name": "string",
    "rating": "number",
    "review_count": "number",
    "price": "string ($ to $$$$)",
    "categories": ["string"],
    "address": "string",
    "phone": "string",
    "distance_miles": "number",
    "is_open": "boolean"
  }]
}
```

### yelp.get_business_details
Get full details including hours, photos, and popular dishes.

**Output:**
```json
{
  "id": "string",
  "name": "string",
  "rating": "number",
  "hours": [{
    "day": "string",
    "open": "string",
    "close": "string"
  }],
  "photos": ["string"],
  "popular_dishes": ["string"],
  "highlights": ["string (Good for Groups, Outdoor Seating, etc.)"]
}
```

### yelp.get_reviews
Get recent reviews for a business.

**Output:**
```json
{
  "reviews": [{
    "rating": "number",
    "text": "string",
    "user": "string",
    "date": "string"
  }]
}
```

### yelp.search_events
Search for local events.

### yelp.get_categories
Get business categories for filtering.

## Authentication

Yelp connector uses public data. No user authentication required.

## Usage Examples

**Find restaurants:**
```
Search Yelp for the best Italian restaurants in San Francisco
```

**Open now:**
```
Find a highly-rated coffee shop open now near me
```

**Read reviews:**
```
What do people say about this restaurant on Yelp?
```

**Service search:**
```
Find a well-reviewed plumber in my area on Yelp
```

**Filter by price:**
```
Search for cheap but good tacos ($ or $$) in Austin
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| NO_RESULTS | No businesses found | Broaden search |
| LOCATION_INVALID | Can't find location | Try different format |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Restaurant discovery: find where to eat
- Service providers: plumbers, mechanics, doctors
- Event planning: find venues for gatherings
- Travel research: explore new cities

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-yelp
- Strider Labs: https://striderlabs.ai
