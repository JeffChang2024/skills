# Nexus Agent API Reference — Exact Schema

> This file contains the real column names from the production database.
> Always use these exact names when querying PostgREST or writing filters.

---

## Authentication flow

Use this flow exactly:

1. Human admin creates an agent API key with `agent-api-key-create`
2. Agent exchanges the key for a short-lived JWT with `agent-auth`
3. Agent uses the JWT for MCP or direct API calls

### Create agent API key

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

### Exchange API key for agent JWT

```bash
POST https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/agent-auth
Content-Type: application/json

{
  "api_key": "nxs_ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Response:

```json
{
  "access_token": "eyJ...",
  "organization_id": "uuid",
  "expires_in": 3600
}
```

### Hosted MCP endpoint

```bash
POST https://lgwvoomgrwpsgpxwyaec.supabase.co/functions/v1/mcp-server
Authorization: Bearer <agent-jwt>
```

### Scope model

| Scope | Access |
|-------|--------|
| `read` | Read-only |
| `write` | Read + create + update |
| `admin` | Full access |

### Important rules

- API key format is `nxs_ak_` + 48 random characters
- raw API keys are returned once only
- Nexus stores only a bcrypt hash
- `agent-auth` is rate limited to `10` attempts per minute per IP
- agent JWTs expire after `3600` seconds

---

## MCP tools and resources

### Tools

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

### Resources

- `nexus://organization/info`
- `nexus://schema/contacts`
- `nexus://schema/orders`
- `nexus://schema/inventory`

---

## Table: `customers`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations — **required** |
| first_name | text | |
| last_name | text | |
| email | text | |
| phone_number | text | E.164 e.g. `+201234567890` |
| address | jsonb | `{line1, line2, city, country}` |
| shopify_customer_id | text | nullable |
| customer_label | text | free text label |
| journey_stage_id | uuid | FK → customer_journey_stages |
| lead_source_id | uuid | FK → lead_sources |
| assigned_to | text | user id (text) |
| customer_score | integer | default 0 |
| tags | text[] | array of strings |
| last_contact | timestamptz | |
| next_follow_up | timestamptz | |
| notes | text | |
| created_at | timestamptz | |
| updated_at | timestamptz | |

```bash
# List contacts
GET /rest/v1/customers?organization_id=eq.<org_id>&order=created_at.desc&limit=25

# Search by phone
GET /rest/v1/customers?phone_number=eq.%2B201234567890&organization_id=eq.<org_id>

# Create contact
POST /rest/v1/customers
{"organization_id":"<org_id>","first_name":"Ahmed","last_name":"Hassan","phone_number":"+201234567890"}
```

---

## Table: `orders`

> ⚠️ The status column is named **`order_status`**, NOT `status`.

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations — **required** |
| customer_id | uuid | FK → customers |
| shopify_order_id | text | nullable |
| order_number | text | auto-generated or set manually |
| order_status | order_status enum | `pending` `confirmed` `fulfilling` `shipped` `delivered` `cancelled` |
| total_amount | numeric(10,2) | |
| currency | text | default `USD` |
| items | jsonb | embedded items array (legacy) |
| airtable_record_id | text | nullable |
| awb_number | text | nullable — filled when shipped |
| refund_amount | numeric(10,2) | default 0 |
| created_at | timestamptz | |
| updated_at | timestamptz | |

```bash
# List orders — use order_status not status
GET /rest/v1/orders?organization_id=eq.<org_id>&order_status=eq.pending&order=created_at.desc

# Filter by multiple statuses
GET /rest/v1/orders?organization_id=eq.<org_id>&order_status=in.(pending,confirmed)

# Create order
POST /rest/v1/orders
{"organization_id":"<org_id>","customer_id":"<uuid>","order_status":"pending","total_amount":450,"currency":"EGP"}

# Update order status
PATCH /rest/v1/orders?id=eq.<uuid>
{"order_status":"confirmed"}
```

---

## Table: `order_items`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| order_id | uuid | FK → orders — **required** |
| item_id | uuid | FK → items (nullable) |
| sku | text | |
| name | text | product name |
| barcode | text | |
| qty | integer | **required** |
| unit_price | numeric(12,2) | |
| created_at | timestamptz | |

```bash
POST /rest/v1/order_items
[
  {"order_id":"<uuid>","name":"T-Shirt","sku":"TSH-M","qty":2,"unit_price":150},
  {"order_id":"<uuid>","name":"Cap","sku":"CAP-BLK","qty":1,"unit_price":100}
]
```

---

## Table: `chats` (conversations)

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| platform | text | `whatsapp` `facebook` `instagram` |
| platform_chat_id | text | external chat ID |
| contact_name | text | |
| contact_phone | text | |
| contact_platform_id | text | |
| last_message | text | |
| last_message_time | timestamptz | |
| unread_count | integer | |
| is_archived | boolean | default false |
| assigned_to | text | user id |

```bash
# Open conversations
GET /rest/v1/chats?organization_id=eq.<org_id>&is_archived=eq.false&order=last_message_time.desc

# Filter by platform
GET /rest/v1/chats?organization_id=eq.<org_id>&platform=eq.whatsapp&is_archived=eq.false
```

---

## Table: `messages`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| chat_id | uuid | FK → chats |
| content | text | message text body |
| message_type | message_type enum | `text` `image` `video` `document` `audio` `template` `reaction` `sticker` `location` |
| direction | text | `inbound` `outbound` |
| status | text | `sent` `delivered` `read` `failed` |
| platform_message_id | text | external ID |
| media_url | text | |
| timestamp | timestamptz | message send time |
| created_at | timestamptz | |

```bash
# Messages in a conversation
GET /rest/v1/messages?chat_id=eq.<chat_id>&order=timestamp.asc
```

---

## Table: `items` (inventory/products)

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| name | text | **required** |
| description | text | |
| sku | text | |
| barcode | text | |
| category | text | |
| unit | text | e.g. `pcs` `kg` |
| cost_price | numeric(10,2) | |
| selling_price | numeric(10,2) | |
| min_stock_level | integer | default 0 |
| is_active | boolean | default true |

```bash
# List active items
GET /rest/v1/items?organization_id=eq.<org_id>&is_active=eq.true&order=name.asc

# Search by SKU
GET /rest/v1/items?organization_id=eq.<org_id>&sku=eq.TSH-M-BLK
```

---

## Table: `stock_balances`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| item_id | uuid | FK → items |
| warehouse_id | uuid | FK → warehouses |
| quantity | integer | total on hand |
| reserved_quantity | integer | reserved for orders |
| available_quantity | integer | **computed**: quantity − reserved_quantity |
| last_updated | timestamptz | |

```bash
# Low stock items (available < 10)
GET /rest/v1/stock_balances?organization_id=eq.<org_id>&available_quantity=lt.10

# Stock for a specific item
GET /rest/v1/stock_balances?item_id=eq.<item_id>
```

---

## Table: `awbs` (shipments)

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| awb_number | text | unique tracking number |
| order_id | uuid | FK → orders |
| courier_name | text | e.g. `bosta` |
| courier_tracking_number | text | |
| status | text | `created` `picked_up` `in_transit` `delivered` `returned` `failed` |
| pickup_date | timestamptz | |
| delivery_date | timestamptz | |
| shipping_cost | numeric(10,2) | |

```bash
# List shipments
GET /rest/v1/awbs?organization_id=eq.<org_id>&order=created_at.desc

# Track by AWB number
GET /rest/v1/awbs?awb_number=eq.AWB12345678&organization_id=eq.<org_id>

# Status log
GET /rest/v1/awb_status_logs?awb_id=eq.<awb_id>&order=timestamp.desc
```

---

## Table: `call_logs`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| customer_id | uuid | FK → customers (nullable) |
| unique_id | text | PBX call ID |
| call_date | timestamptz | **required** |
| caller_number | text | **required** |
| called_number | text | **required** |
| extension | text | |
| direction | call_direction enum | `inbound` `outbound` `internal` |
| status | call_status enum | `answered` `missed` `busy` `failed` `voicemail` |
| duration_seconds | integer | |
| agent_notes | text | |

```bash
# Calls for a contact
GET /rest/v1/call_logs?customer_id=eq.<uuid>&order=call_date.desc

# Missed calls today
GET /rest/v1/call_logs?organization_id=eq.<org_id>&status=eq.missed&call_date=gte.2026-03-05
```

---

## Table: `warehouses`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| organization_id | uuid | FK → organizations |
| name | text | **required** |
| location | text | |
| is_active | boolean | |

```bash
GET /rest/v1/warehouses?organization_id=eq.<org_id>&is_active=eq.true
```

---

## Common mistakes to avoid

| Wrong | Correct |
|-------|---------|
| `orders?status=eq.pending` | `orders?order_status=eq.pending` |
| `orders?status=eq.processing` | `orders?order_status=eq.fulfilling` (enum value is `fulfilling`) |
| `items` for inventory stock | `stock_balances` joined with `items` |
| `messages?direction=eq.in` | `messages?direction=eq.inbound` |
| `chats?status=eq.open` | `chats?is_archived=eq.false` (no status column — use is_archived) |

---

## Full order-to-ship workflow

```
1. POST /rest/v1/orders          → order_status: pending
2. PATCH /rest/v1/orders?id=eq.X → {"order_status": "confirmed"}
3. POST /functions/v1/start-picking {"order_id": "<id>"}
4. POST /functions/v1/complete-pick {"pick_list_id": "<id>"}
5. PATCH /rest/v1/orders?id=eq.X → {"order_status": "fulfilling"}
6. POST /functions/v1/create-awb-bosta {"order_id": "<id>"}
7. AWB created → order_status auto-updated to "shipped"
```
