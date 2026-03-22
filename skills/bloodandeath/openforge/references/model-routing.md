# Model Routing Guide

## Executor Tiers

| Tier | Best For | Prompt Style | Cost |
|------|----------|-------------|------|
| **local** | Simple code tasks, boilerplate, single-file changes | Surgical, 8K context, code-only | Free |
| **cloud** | Multi-file coordination, architectural work, complex logic | Full context, self-critique, reflexion | $$ |
| **review** | Code review, security audit, quality assessment | Evaluative, structured JSON output | $$$ |
| **cheap** | File extraction, parsing, inventory tasks | Ultra-constrained, output-only | $ |

## Tier Selection Heuristic

OpenForge selects the prompt tier based on agent name:
- Agent name contains `local` → local tier
- Agent name contains `review` → review tier  
- Agent name contains `cheap` → cheap tier
- Everything else → cloud tier

## Fallback Chain Design

Fallbacks activate when the primary agent fails or stalls. Define them in the routing table:

```yaml
aliases:
  local:
    agent: openforge-local          # Try local first (free)
    fallback: openforge-cloud       # Escalate to cloud if local fails
  cloud:
    agent: openforge-cloud          # Primary cloud
    fallback: openforge-cloud-fallback  # Different provider as backup
  review:
    agent: openforge-review
    fallback: openforge-cloud-fallback  # Review fallback to strong coder
```

**Rules:**
- If no fallback defined, escalation attempts 3-4 are skipped (max 3 attempts).
- Fallback agents don't need their own alias — just reference a valid agent ID.
- Chain depth is 1 (primary → fallback). No cascading fallbacks.

## Context Window Considerations

Local models with limited VRAM need explicit context limits:

```yaml
local:
  agent: openforge-local
  context: 8192    # Prompt will be truncated to fit
```

Cloud models typically don't need this — their context windows are large enough.

## Cost Optimization Strategies

1. **Route simple tasks local.** Boilerplate scaffolding, single-file implementations, standard CRUD — these rarely need GPT-5.4.
2. **Reserve cloud for multi-file work.** OAuth flows, real-time systems, complex business logic.
3. **Use review tier sparingly.** One review phase at the end, not per-task.
4. **Use `--max-escalation 3` for cost control.** Prevents local tasks from burning cloud tokens on persistent failures.

## Example: Web API Project

```yaml
aliases:
  local:
    agent: openforge-local
    fallback: openforge-cloud
    context: 8192
  cloud:
    agent: openforge-cloud
    fallback: openforge-cloud-fallback
  review:
    agent: openforge-review
```

Phases:
- Stage 1 (scaffold): `cloud` — project setup needs multi-file coordination
- Stage 2 (models, routes): `local` — straightforward single-file tasks
- Stage 2 (auth, websockets): `cloud` — complex cross-cutting concerns
- Stage 3 (review): `review` — security and quality assessment

## Example: Simple Script

For small projects, a single executor is fine:

```yaml
aliases:
  cloud:
    agent: openforge-cloud
```

All phases use `executor: cloud`. No fallback needed for simple work.
