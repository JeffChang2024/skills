# OpenClaw Plugin Setup

## Prerequisites

- OpenClaw 2026.3.2 or later
- A Sulcus account with API key ([sulcus.ca](https://sulcus.ca))

## Install

```bash
# Create plugin directory
mkdir -p ~/.openclaw/extensions/memory-sulcus

# Option A: From Sulcus repo
git clone https://github.com/digitalforgeca/sulcus.git /tmp/sulcus
cp /tmp/sulcus/packages/openclaw-sulcus/* ~/.openclaw/extensions/memory-sulcus/

# Option B: From npm (when published)
# openclaw plugins install @digitalforgestudios/openclaw-sulcus

# Install dependencies
cd ~/.openclaw/extensions/memory-sulcus && npm install

# Verify discovery
openclaw plugins list
# → Memory (Sulcus) | memory-sulcus | disabled
```

## Configure

Add to `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "slots": {
      "memory": "memory-sulcus"
    },
    "entries": {
      "memory-sulcus": {
        "enabled": true,
        "config": {
          "serverUrl": "https://api.sulcus.ca",
          "apiKey": "YOUR_SULCUS_API_KEY",
          "agentId": "my-agent",
          "namespace": "my-agent",
          "autoRecall": true,
          "autoCapture": true,
          "maxRecallResults": 5,
          "minRecallScore": 0.3
        }
      }
    }
  }
}
```

Then restart: `openclaw restart`

## Config Options

| Option | Type | Default | Description |
|---|---|---|---|
| `serverUrl` | string | `https://api.sulcus.ca` | Sulcus server URL |
| `apiKey` | string | (required) | Sulcus API key |
| `agentId` | string | — | Agent identifier for namespacing |
| `namespace` | string | value of `agentId` | Memory namespace |
| `autoRecall` | boolean | `true` | Inject relevant memories before each turn |
| `autoCapture` | boolean | `true` | Auto-store important info from conversations |
| `maxRecallResults` | number | `5` | Max memories injected per turn |
| `minRecallScore` | number | `0.3` | Min relevance score for auto-recall |

## Multi-Agent Setup

Each agent gets its own namespace. All agents under the same tenant can query each other's memories.

```json
{
  "plugins": {
    "entries": {
      "memory-sulcus": {
        "config": {
          "agentId": "daedalus",
          "namespace": "daedalus"
        }
      }
    }
  }
}
```

## Verifying

After restart:

```bash
# Check plugin loaded
openclaw plugins list
# → Memory (Sulcus) | memory-sulcus | loaded

# Check tools available
openclaw plugins info memory-sulcus
# → Tools: memory_search, memory_get, memory_store, memory_forget
```

## Troubleshooting

- **Plugin not discovered**: Ensure `~/.openclaw/extensions/memory-sulcus/` contains `index.ts`, `package.json`, and `openclaw.plugin.json`
- **Search returns 404**: Verify `serverUrl` points to `https://api.sulcus.ca` (not `sulcus.ca`)
- **Auth failures**: Verify API key is correct and tenant exists
- **Empty results**: Agent may have no stored memories yet — store some first
