---
name: sulcus-memory
description: "Thermodynamic memory backend for AI agents via Sulcus. Use when: (1) storing memories with heat-based decay and spaced repetition, (2) searching/recalling context across sessions, (3) configuring memory triggers that fire on events, (4) managing memory lifecycle (pin, boost, deprecate, reclassify), (5) setting up the OpenClaw memory plugin, (6) tuning thermodynamic parameters (half-lives, decay classes, resonance). Replaces flat-file memory with persistent, heat-governed recall. Works with OpenClaw plugin, MCP (Claude Desktop, local), Python SDK, Node.js SDK, or REST API."
author: "Digital Forge"
version: "1.0.0"
---

# Sulcus Memory

Sulcus is a thermodynamic virtual Memory Management Unit (vMMU). Memories have **heat** that decays over time — frequently accessed memories stay hot, neglected ones cool and page out. This mirrors how human memory works.

## Key Concepts

- **Heat**: 0.0–1.0 score. Recall boosts heat, time decays it. Hot memories enter context, cold ones don't.
- **Decay**: Governed by half-life per memory type. Episodic memories fade in hours, preferences persist for months.
- **Stability**: Spaced repetition multiplier. Each recall increases stability, stretching effective half-life.
- **Pinning**: Pinned memories never decay (heat floor = 1.0).
- **Resonance**: Related memories get heat spillover when neighbors are recalled.
- **Triggers**: Programmable rules that fire on memory events (create, recall, decay threshold, boost).

## Memory Types

| Type | Half-life | Use for |
|---|---|---|
| `episodic` | 24h | What happened — conversations, events, tasks |
| `semantic` | 30d | What you know — facts, knowledge, context |
| `preference` | 90d | What you like — user preferences, settings |
| `procedural` | 180d | How to do things — workflows, processes |
| `fact` | 30d | Verified truths — dates, names, specs |
| `moment` | 12h | Fleeting context — current mood, temp state |

## Decay Classes

| Class | Effect |
|---|---|
| `volatile` | 2× faster decay |
| `normal` | Standard half-life |
| `persistent` | 2× slower decay |
| `permanent` | No decay (heat stays at initial value) |

## Tools Available

When the Sulcus plugin is active, these tools are provided:

### memory_store
Store a new memory. Auto-detects type from content.
```
memory_store(text="User prefers dark mode in all applications", memoryType="preference")
```

### memory_search
Semantic search across all memories. Returns matches with heat scores.
```
memory_search(query="database preferences", maxResults=5, minScore=0.3)
```

### memory_get
Retrieve a specific memory by UUID. Auto-boosts heat on recall.
```
memory_get(path="019d021b-8911-7eb3-b290-da264fa673d3")
```

### memory_forget
Delete a memory permanently.
```
memory_forget(memoryId="019d021b-8911-7eb3-b290-da264fa673d3")
```

## Auto-Recall & Auto-Capture

With the OpenClaw plugin configured:

- **Auto-recall**: Before each agent turn, searches for memories relevant to the user's message and injects them into context. No manual `memory_search` needed for basic recall.
- **Auto-capture**: After each turn, detects important information (preferences, facts, decisions) and stores automatically.

Manual `memory_search` is still useful for deep/specific queries beyond what auto-recall surfaces.

## When to Store Memories

Store when you encounter:
- User preferences or settings ("I prefer TypeScript over JavaScript")
- Important decisions ("We chose PostgreSQL for the database")
- Facts worth remembering ("The server IP is 10.0.0.5")
- Procedures ("To deploy: run build, then push to main")
- Contact info ("Sarah's email is sarah@example.com")
- Project context ("The API uses REST, not GraphQL")

Do NOT store: transient chat, greetings, acknowledgments, or information already in workspace files.

## Triggers

Triggers fire automatically on memory events. See [references/triggers.md](references/triggers.md) for the full trigger API.

Common triggers:
- **Cold Memory Alert**: Notify when fact memories decay below threshold
- **Recall Boost**: Auto-boost procedural memories on recall
- **Auto-tag**: Tag high-heat memories for priority retrieval
- **New Preference**: Notify when a new preference is stored

## Security & Privacy

Sulcus is an external memory backend. When configured:
- **Auto-recall** sends the user's message text to the Sulcus API for semantic search
- **Auto-capture** sends detected preferences/facts to the Sulcus API for storage
- **All data** is stored under your tenant, isolated from other users
- **API key** is required — no anonymous access
- **Self-hosted option**: Run `sulcus-local` for fully local, offline memory with no cloud dependency
- **Open source**: Server, client, and SDKs are MIT-licensed at [github.com/digitalforgeca/sulcus](https://github.com/digitalforgeca/sulcus)

Auto-capture and auto-recall can be disabled independently in the plugin config.

## Setup

### OpenClaw Plugin (recommended)

See [references/openclaw-setup.md](references/openclaw-setup.md) for complete installation and configuration.

Quick version:
1. Copy plugin to `~/.openclaw/extensions/memory-sulcus/`
2. `cd ~/.openclaw/extensions/memory-sulcus && npm install`
3. Add to `openclaw.json`: `plugins.slots.memory = "memory-sulcus"` with config
4. `openclaw restart`

### MCP (Claude Desktop, local)

See [references/mcp-setup.md](references/mcp-setup.md) for MCP configuration.

### Python SDK

```bash
pip install sulcus
```
```python
from sulcus import Sulcus
client = Sulcus(api_key="sk-...")
client.store("User prefers dark mode", memory_type="preference")
results = client.search("dark mode")
```

### Node.js SDK

```bash
npm install sulcus
```
```typescript
import { Sulcus } from "sulcus";
const client = new Sulcus({ apiKey: "sk-..." });
await client.store("User prefers dark mode", { memoryType: "preference" });
const results = await client.search("dark mode");
```

## Thermodynamic Configuration

For tuning decay rates, resonance, tick modes, and per-type overrides, see [references/thermodynamics.md](references/thermodynamics.md).

## API Reference

For the full REST API endpoint list, see [references/api.md](references/api.md).
