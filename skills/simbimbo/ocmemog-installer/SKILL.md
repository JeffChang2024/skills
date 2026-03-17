---
name: ocmemog-installer
description: One-click installer and setup skill for ocmemog, the OpenClaw durable memory plugin and sidecar. Use when a user asks to install ocmemog, set up ocmemog, add durable memory to OpenClaw, improve long-term memory, enable transcript-backed continuity, configure the ocmemog sidecar, reinstall or update ocmemog, or troubleshoot an existing ocmemog install. Prefer the bundled install script for the fastest path.
---

# ocmemog Installer

Install `ocmemog` from the canonical GitHub repo and configure OpenClaw to use it as the memory plugin.

## Canonical source

- Repo: `https://github.com/simbimbo/ocmemog.git`
- Plugin id: `memory-ocmemog`
- Default sidecar endpoint: `http://127.0.0.1:17890`
- Primary bundled installer: `scripts/install-ocmemog.sh`

## Preferred workflow

1. Run the bundled installer script first.
   - Default: `scripts/install-ocmemog.sh`
   - Optional target dir: `scripts/install-ocmemog.sh /custom/path/ocmemog`
2. Let the script clone/update the repo, build the venv, install Python requirements, start the sidecar, and install/enable the plugin when the `openclaw` CLI is available.
3. Patch OpenClaw config so the `memory` slot points at `memory-ocmemog` and the plugin entry uses `http://127.0.0.1:17890`.
4. Validate `/healthz` and a memory search/get smoke test.

## Agent behavior

- Default to the script-driven flow instead of narrating manual steps.
- Treat user phrases like "install ocmemog", "set up durable memory", "improve OpenClaw memory", and "add long-term memory" as direct triggers.
- If config patch tooling is available, patch config automatically instead of asking the user to hand-edit files.
- After install, verify the sidecar and plugin state before claiming success.
- If the environment blocks automatic config changes, provide the exact config snippet and the shortest possible manual next step.

## Config patching

If the Gateway tool is available, prefer patching config automatically instead of asking the user to hand-edit config.

Target config shape:

```yaml
plugins:
  load:
    paths:
      - /path/to/ocmemog
  slots:
    memory: memory-ocmemog
  entries:
    memory-ocmemog:
      enabled: true
      config:
        endpoint: http://127.0.0.1:17890
        timeoutMs: 10000
```

Rules:
- Use the actual install path chosen by the script.
- Preserve existing unrelated plugin configuration.
- If config patch tooling is unavailable, provide the exact patch/snippet the user should apply.

## Validation checklist

- Sidecar responds on `/healthz`
- `openclaw plugins` shows `memory-ocmemog` installed/enabled when CLI access exists
- Memory search/get calls return data instead of connection errors
- If packaging/publish questions arise, remember this skill is a ClawHub wrapper for the plugin repo, not the plugin package itself

## Troubleshooting

- If `clawhub` users expect a direct plugin package, explain that this skill installs/configures the real plugin repo.
- If macOS LaunchAgents fail, rerun the installer and inspect `launchctl print gui/$UID/com.openclaw.ocmemog.sidecar`.
- If the sidecar health check fails, inspect repo logs / terminal output before changing config.
- Keep the sidecar bound to `127.0.0.1` unless explicit auth/network hardening is added.

## Notes

- Prefer the script-driven flow over manual step-by-step setup.
- Prefer publishing the plugin itself through GitHub/npm/plugin-install flows; use this skill as the ClawHub-distributed installer/config guide.
