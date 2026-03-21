---
name: strider-hertz
description: Rent cars from Hertz via Strider Labs MCP connector. Search available vehicles, compare rates, make reservations, and manage Gold Plus Rewards membership.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Hertz Connector

MCP connector for Hertz car rental. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-hertz
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "hertz": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-hertz"]
    }
  }
}
```

## Available Tools

### hertz.search_vehicles
Search available rental cars.

**Input Schema:**
```json
{
  "pickup_location": "string (airport code or address)",
  "pickup_date": "string (YYYY-MM-DD)",
  "pickup_time": "string (HH:MM)",
  "return_date": "string",
  "return_time": "string",
  "vehicle_class": "economy | compact | midsize | suv | luxury (optional)"
}
```

**Output:**
```json
{
  "vehicles": [{
    "class": "midsize",
    "make_model": "Toyota Camry or similar",
    "daily_rate": 45.99,
    "total_price": 183.96,
    "features": ["Bluetooth", "Backup Camera"],
    "seats": 5,
    "bags": 3
  }]
}
```

### hertz.make_reservation
Book a rental car.

**Input Schema:**
```json
{
  "vehicle_id": "string",
  "pickup_location": "string",
  "pickup_date": "string",
  "return_date": "string",
  "add_insurance": "boolean (optional)",
  "add_gps": "boolean (optional)"
}
```

### hertz.get_reservations
List upcoming reservations.

### hertz.modify_reservation
Change an existing reservation.

### hertz.cancel_reservation
Cancel a rental booking.

### hertz.get_gold_status
Check Gold Plus Rewards status and points.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Hertz login
2. Gold Plus Rewards linked automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Search rentals:**
```
Find a midsize car at LAX for next weekend
```

**Book a car:**
```
Book the cheapest SUV at Denver airport March 20-23
```

**Check reservations:**
```
What Hertz reservations do I have?
```

**Modify booking:**
```
Change my Hertz reservation to return a day later
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_AVAILABILITY | No cars available | Try different dates/location |
| RESERVATION_NOT_FOUND | Invalid confirmation | Check number |
| RATE_LIMITED | Too many requests | Retry after delay |

## Use Cases

- Business travel: book rental cars for work trips
- Airport pickups: reserve vehicles at airports
- Weekend trips: rent cars for short getaways
- Rewards tracking: monitor Gold Plus points
- Fleet comparison: compare prices across vehicle classes

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-hertz
- Strider Labs: https://striderlabs.ai
