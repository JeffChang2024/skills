# OpenForge Installation Guide

This guide walks you through setting up OpenForge on any machine running OpenClaw.

## Prerequisites

- **OpenClaw** installed and running (`openclaw status` should show a healthy gateway)
- **Python >= 3.11** available on PATH
- **git** installed
- **uv** (astral.sh) — the install script will install this if missing

## Step 1: Install the Skill

If installed via ClawHub:
```bash
clawhub install openforge
```

If installed manually (e.g., cloned from repo):
```bash
cd /path/to/openforge
bash scripts/install.sh
```

The install script will:
1. Install `uv` if not present
2. Sync the Python environment (`uv sync`)
3. Run a smoke test (`openforge validate` on a bundled template)

## Step 2: Register OpenForge Agents

OpenForge dispatches tasks to named agents. You need to register at least one.

### Recommended Agent Setup

```bash
# Cloud coder (GPT-5.4) — primary workhorse for most tasks
openclaw agents add openforge-cloud \
  --model "openai-codex/gpt-5.4" \
  --workspace ~/.openclaw/workspaces/openforge \
  --non-interactive

# Cloud fallback (Sonnet) — used when primary fails
openclaw agents add openforge-cloud-fallback \
  --model "anthropic/claude-sonnet-4-6" \
  --workspace ~/.openclaw/workspaces/openforge \
  --non-interactive

# Review agent (Opus) — for code review and security audit phases
openclaw agents add openforge-review \
  --model "anthropic/claude-opus-4-6" \
  --workspace ~/.openclaw/workspaces/openforge \
  --non-interactive

# Cheap agent (Haiku) — for extraction and parsing tasks
openclaw agents add openforge-cheap \
  --model "anthropic/claude-haiku-4-5" \
  --workspace ~/.openclaw/workspaces/openforge \
  --non-interactive
```

### Optional: Local Model Agent

If you have Ollama running with a coding model:

```bash
# Local coder (requires Ollama with qwen2.5-coder or similar)
openclaw agents add openforge-local \
  --model "ollama/qwen2.5-coder:7b" \
  --workspace ~/.openclaw/workspaces/openforge \
  --non-interactive
```

> **Note:** Local model support depends on your OpenClaw version supporting Ollama as a provider. Check `openclaw status` for provider availability.

### Minimal Setup (Single Agent)

If you just want to get started quickly:

```bash
openclaw agents add openforge-cloud \
  --model "openai-codex/gpt-5.4" \
  --workspace ~/.openclaw/workspaces/openforge \
  --non-interactive
```

Then use a simple routing table in your PRDs:
```yaml
aliases:
  cloud:
    agent: openforge-cloud
```

## Step 3: Verify Installation

```bash
# Check agents are registered
openclaw agents list

# Validate a sample PRD
<skill_dir>/scripts/openforge validate <skill_dir>/templates/prd-simple.md

# Show execution plan
<skill_dir>/scripts/openforge plan <skill_dir>/templates/prd-simple.md
```

## Step 4: Run Your First PRD

1. Create a git repository (or use an existing one):
```bash
mkdir my-project && cd my-project
git init
echo '{}' > package.json
git add -A && git commit -m "init"
```

2. Write a PRD (or copy a template):
```bash
cp <skill_dir>/templates/prd-simple.md ./prd.md
# Edit prd.md with your tasks
git add prd.md && git commit -m "add prd"
```

3. Execute:
```bash
<skill_dir>/scripts/openforge run prd.md --cwd .
```

4. Monitor progress — OpenForge prints a status table after each task.

5. If interrupted, resume:
```bash
<skill_dir>/scripts/openforge list
<skill_dir>/scripts/openforge resume <run-id>
```

## Agent Configuration Notes

### Workspace Sharing
All OpenForge agents share `~/.openclaw/workspaces/openforge` as their workspace. This is fine — they don't store persistent state there. The actual project work happens in the `--cwd` directory you specify.

### Temporary Workspace Override During Dispatch
When OpenForge dispatches a task, it temporarily updates the agent's `workspace` field in `~/.openclaw/openclaw.json` to point at the project directory (`--cwd`). This ensures the agent's file tools operate on the correct project. The original workspace value is always restored after each task completes — even if the dispatch fails or times out.

### Model Selection
Choose models based on your budget and needs:

| Agent | Model | Cost | Best For |
|-------|-------|------|----------|
| openforge-cloud | gpt-5.4 | $$ | Most coding tasks |
| openforge-cloud-fallback | claude-sonnet-4-6 | $$ | Fallback when GPT fails |
| openforge-review | claude-opus-4-6 | $$$ | Security/quality review |
| openforge-cheap | claude-haiku-4-5 | $ | Extraction, parsing |
| openforge-local | ollama/qwen2.5-coder:7b | Free | Simple single-file tasks |

### Custom Agents
You can register agents with any model your OpenClaw instance supports. Reference them in your PRD routing table by their agent ID.

## Troubleshooting

### "openclaw CLI not found"
Ensure OpenClaw is installed and on your PATH: `which openclaw`

### "Unknown agent id"
Register the agent first: `openclaw agents add <name> --model <model-id> ...`

### "working tree is dirty"
Commit or stash your changes before running, or use `--allow-dirty`.

### Agent dispatch fails
Check `openclaw status` for provider health. Verify API keys are configured for the model provider.

### Timeouts
Increase task timeout: `--task-timeout 900` (default is 600 seconds).

## Uninstalling

```bash
# Remove agents
openclaw agents delete openforge-cloud
openclaw agents delete openforge-cloud-fallback
openclaw agents delete openforge-review
openclaw agents delete openforge-cheap

# Remove workspace
rm -rf ~/.openclaw/workspaces/openforge

# Remove run artifacts
rm -rf ~/.local/state/openforge
```
