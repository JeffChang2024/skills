---
name: nexus-agent
description: Operate the Nexus multi-tenant Ops OS as an AI agent. Covers agent authentication via API keys, CRM (contacts, segments), omnichannel messaging (WhatsApp, Messenger, Instagram), order management (create, fulfill, ship, track), inventory management, warehouse operations, shipping (AWB), VoIP call initiation, CS analytics, and automation workflows. Use when the user or task requires reading, creating, or updating Nexus data programmatically.
---

# Nexus Agent Skill

Nexus is a multi-tenant Ops OS. This skill covers how to authenticate as an AI agent, how to use the hosted MCP server, and how to fall back to direct API access when MCP is not enough.

## Authentication

AI agents do **not** use human user JWTs directly.

The correct flow is:

1. A human org admin creates an agent API key with `agent-api-key-create`
2. The agent exchanges that key for a short-lived JWT with `agent-auth`
3. The agent uses the short-lived JWT for MCP or direct API calls

### Step 1: create an API key

This is a **human admin** operation.

```bash
POST https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/agent-api-key-create
Authorization: Bearer <human-admin-jwt>
Content-Type: application/json

{
  "name": "Bahig - Karim assistant",
  "scopes": ["read", "write"],
  "expires_at": "2026-12-31T23:59:59Z"
}
```

Response:

```json
{
  "api_key": "nxs_ak_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12",
  "key_prefix": "nxs_ak_ab12CD34",
  "organization_id": "uuid",
  "name": "Bahig - Karim assistant",
  "scopes": ["read", "write"],
  "expires_at": "2026-12-31T23:59:59.000Z",
  "message": "Store this API key now. It is only returned once."
}
```

Important:

- The raw key is returned **once only**
- Nexus stores only a **bcrypt hash**
- Keys can be revoked

### Step 2: exchange API key for an agent JWT

```bash
POST https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/agent-auth
Content-Type: application/json

{"api_key": "nxs_ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
```

Response:
```json
{
  "access_token": "eyJ...",
  "organization_id": "uuid",
  "expires_in": 3600
}
```

Use the `access_token` as `Authorization: Bearer <token>` on all subsequent requests.

### API key format

`nxs_ak_` prefix + 48 random alphanumeric chars. Keep it secret — treat it like a password.

### Scopes

Nexus agent scopes are:

- `read`
- `write`
- `admin`

Access model:

- `read` = read-only operations
- `write` = read + create + update
- `admin` = full access

### MCP authentication

The hosted MCP endpoint accepts the **agent JWT**, not the raw API key:

```bash
POST https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/mcp-server
Authorization: Bearer <agent-jwt>
```

---

## Base URLs

| Service | URL |
|---------|-----|
| Edge Functions | `https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/<function-name>` |
| PostgREST (DB) | `https://lgwvoomgrwpsgpxwyaec.supabase.co/rest/v1/<table>` |
| MCP | `https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/mcp-server` |

For PostgREST, also include: `apikey: <anon-key>` header.  
Anon key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnd3Zvb21ncndwc2dweHd5YWVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2MTcxNjAsImV4cCI6MjA2ODE5MzE2MH0.MeFgUnUaUTD1lsSVVGtwjWNuUJfJbdY-UB6X5YRuqNM`

---

## Preferred integration path: MCP first

Prefer the hosted MCP server when possible. It exposes stable, documented tools and resources for the most common agent workflows.

### MCP tools

- `nexus_list_contacts`
- `nexus_get_contact`
- `nexus_create_contact`
- `nexus_update_contact`
- `nexus_list_orders`
- `nexus_get_order`
- `nexus_create_order`
- `nexus_update_order_status`
- `nexus_list_inventory`
- `nexus_check_stock`
- `nexus_list_conversations`
- `nexus_send_message`
- `nexus_search`

### MCP resources

- `nexus://organization/info`
- `nexus://schema/contacts`
- `nexus://schema/orders`
- `nexus://schema/inventory`

### When to use MCP vs direct API

Use MCP when:

- the client supports MCP
- you want a compact tool surface
- you want resource discovery and schema resources

Use direct API when:

- the client does not support MCP
- you need raw PostgREST querying
- you are debugging a low-level integration

---

## Core Operations

### Contacts (CRM)

> Journey stage is stored as `journey_stage_id` (uuid FK → `customer_journey_stages`), not a text field.

```bash
# List contacts
GET /rest/v1/customers?organization_id=eq.<org_id>&order=created_at.desc&limit=25
Authorization: Bearer <token>

# Search by phone (URL-encode + as %2B)
GET /rest/v1/customers?phone_number=eq.%2B201234567890&organization_id=eq.<org_id>

# Create contact
POST /rest/v1/customers
{"first_name":"Ahmed","last_name":"Hassan","phone_number":"+201234567890","organization_id":"<org_id>"}

# Update tags
PATCH /rest/v1/customers?id=eq.<uuid>
{"tags":["vip","repeat-buyer"]}
```

### Messages (Omnichannel Inbox)

> `chats` has no `status` column — use `is_archived`. `messages` orders by `timestamp` not `created_at`.

```bash
# List open conversations (not archived)
GET /rest/v1/chats?organization_id=eq.<org_id>&is_archived=eq.false&order=last_message_time.desc

# Get messages in a conversation
GET /rest/v1/messages?chat_id=eq.<chat_id>&order=timestamp.asc

# Send WhatsApp message
POST /functions/v1/whatsapp-send-message
{"chatId":"<chat_id>","message":"Hello from Nexus AI agent","organizationId":"<org_id>"}

# Send template message
POST /functions/v1/whatsapp-send-template
{"phone_number":"+201234567890","template_name":"order_shipped","language":"ar","components":[]}
```

### Orders

> ⚠️ The status column is **`order_status`** (not `status`). Enum values: `pending` `confirmed` `fulfilling` `shipped` `delivered` `cancelled`

```bash
# List orders
GET /rest/v1/orders?organization_id=eq.<org_id>&order=created_at.desc&limit=50

# Filter by status — use order_status
GET /rest/v1/orders?organization_id=eq.<org_id>&order_status=eq.pending

# Create order
POST /rest/v1/orders
{"customer_id":"<uuid>","organization_id":"<org_id>","order_status":"pending","total_amount":450,"currency":"EGP"}

# Update order status
PATCH /rest/v1/orders?id=eq.<uuid>
{"order_status":"confirmed"}

# Get order items (qty column, not quantity)
GET /rest/v1/order_items?order_id=eq.<order_id>
```

### Inventory

> Table is `items` (products) + `stock_balances` (quantities per warehouse). There is no `inventory_items` table.

```bash
# List products
GET /rest/v1/items?organization_id=eq.<org_id>&is_active=eq.true&order=name.asc

# Search by SKU
GET /rest/v1/items?organization_id=eq.<org_id>&sku=eq.TSHIRT-M-BLK

# Check stock — available_quantity is a computed column
GET /rest/v1/stock_balances?organization_id=eq.<org_id>&available_quantity=lt.10

# Stock for one item across all warehouses
GET /rest/v1/stock_balances?item_id=eq.<uuid>
```

### Shipping

```bash
# Create AWB (Bosta courier)
POST /functions/v1/create-awb-bosta
{"order_id":"<uuid>","pickup_date":"2025-06-17"}

# List shipments
GET /rest/v1/awbs?order=created_at.desc

# Get tracking history
GET /rest/v1/awb_status_logs?awb_id=eq.<awb_id>&order=created_at.desc
```

### VoIP

```bash
# Initiate call
POST /functions/v1/call-initiate
{"phone_number":"+201234567890"}

# Get call logs for a contact
GET /rest/v1/call_logs?customer_id=eq.<uuid>&order=created_at.desc
```

### AI Analytics

```bash
# Get CS annotations for a conversation
GET /rest/v1/cs_annotations?chat_id=eq.<chat_id>

# Trigger annotation on a conversation
POST /functions/v1/ai-cs-annotator
{"chat_id":"<uuid>"}

# Get business analysis
POST /functions/v1/ai-business-analysis
{"org_id":"<uuid>","period_days":30}
```

---

## Pagination

Use `Range` header or query params:

```bash
GET /rest/v1/customers
Range: 0-24          # first 25 records
# or
GET /rest/v1/customers?offset=0&limit=25
```

Response includes `Content-Range: 0-24/1523`.

---

## Filtering

PostgREST operators: `eq`, `neq`, `gt`, `gte`, `lt`, `like`, `in`, `is`

```bash
# Multiple filters
GET /rest/v1/orders?status=eq.shipped&created_at=gte.2025-01-01

# Null check
GET /rest/v1/orders?shopify_order_id=is.null
```

---

## Error handling

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Invalid/expired token | Re-authenticate via `agent-auth` |
| 403 | Scope not allowed | Check API key scopes |
| 404 | Record not found | Verify the UUID |
| 429 | Rate limited | Retry after `Retry-After` seconds |

---

## Scopes reference

| Scope | Access |
|-------|--------|
| `read` | Read-only access |
| `write` | Read + create + update |
| `admin` | Full access |

---

## Deployed endpoints for agents

### Agent bootstrap

- `POST /functions/v1/agent-api-key-create`
- `POST /functions/v1/agent-auth`
- `POST /functions/v1/mcp-server`

### Outbound messaging used by MCP

- `POST /functions/v1/whatsapp-send-message`
- `POST /functions/v1/facebook-send-message`
- `POST /functions/v1/instagram-send-message`

### Notes

- `agent-auth` is rate-limited to **10 attempts per minute per IP**
- agent JWTs expire after **1 hour**
- use the raw API key only with `agent-auth`

---

## Support

If you encounter an error, an undocumented behaviour, or need access to a scope not covered here, send an email to:

- **To:** info@aiforstartups.io
- **CC:** karim.sherif@aiforstartups.io

Include your `agent_id`, the endpoint you were calling, the error message, and a short description of what you were trying to do.

## Additional resources

- Full API reference: [api-reference.md](api-reference.md)
- Hosted MCP docs: `https://nexus-docs.aiforstartups.io/api/ai-agents-mcp`
- OpenAPI spec: `https://nexus-docs.aiforstartups.io/openapi.yaml`
- Docs: `https://nexus-docs.aiforstartups.io`
