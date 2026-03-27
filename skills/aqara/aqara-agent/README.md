# aqara-agent

This folder is the **aqara-agent** skill. The parent library overview is at the repo root: [`../../README.md`](../../README.md) (full **Aqara Agent Skills** README).

Official AI skill for agent-driven Aqara smart-home workflows via the Open API.

## Purpose

Consistent runtime for account setup, home selection, device query/control, and scenes—assistants must use real script/API output only, never guessed data.

## Who it is for

- Developers wiring smart-home into AI assistants
- Agent hosts and integrators (e.g. OpenClaw-style platforms)
- Operators running scripted home/device checks

## Capabilities

| Area | What it covers |
|------|----------------|
| Account / session | Login guidance, save `aqara_api_key`, re-auth on failure |
| Home / space | List homes, select or switch default home, list rooms |
| Device inquiry | Home device list, live status where supported |
| Device control | Supported attributes/actions per `references/devices-control.md` |
| Scenes | List scenes, execute by matched scene |
| Safety | Outcomes and counts must come from real API/script output only |

## Layout (this skill)

```text
aqara-agent/
├── README.md                 # This file
├── SKILL.md                  # Skill entry: workflow, errors, notes
├── assets/
│   ├── login_reply_prompt.json   # Locales, default_login_url
│   ├── login_qr.png              # Optional; same URL as default_login_url (regen if URL changes)
│   ├── user_account.example.json # Template for local user_account.json
│   └── user_account.json         # Local only (gitignored); credentials + home
├── references/               # Step-by-step flows (account, home, devices, scenes)
└── scripts/
    ├── aqara_open_api.py     # CLI: homes, rooms, home_devices, device_control, …
    ├── save_user_account.py  # Persist api key / home selection
    ├── runtime_utils.py
    └── requirements.txt
```

## Quick start

From **this directory** (`skills/aqara-agent`):

```bash
python3 -m pip install -r scripts/requirements.txt
```

Optional environment:

```bash
export AQARA_OPEN_HOST=agent.aqara.com
# Optional: full REST base URL instead of host-derived default
# export AQARA_OPEN_API_URL=https://agent.aqara.com/open/api
```

Then follow **`SKILL.md`** and **`references/`**:

- Sign in and save `aqara_api_key` (`references/aqara-account-manage.md`).
- After saving the key, run **`aqara_open_api.py homes` in a separate shell invocation** (do not chain with `save_user_account.py` using `&&` on one line). Set `home_id` / `home_name` per `references/home-space-manage.md`.
- Run inquiry, control, or scene flows as documented.

## Script CLI (summary)

`python3 scripts/aqara_open_api.py <tool> [json_body]`

Common tools: `homes`, `rooms`, `home_devices`, `device_status`, `device_control`, `home_scenes`, `execute_scenes`.

Details and JSON shapes: **`SKILL.md`** and **`references/*.md`**.

## Packaging

From the parent `skills/` directory:

```bash
cd ..
tar -czf aqara-agent.tar.gz aqara-agent
```

## Notes

- Default Open Platform host is **`agent.aqara.com`**; override with **`AQARA_OPEN_HOST`** (or **`AQARA_OPEN_API_URL`**).
- Do not present homes, devices, scenes, or states without a successful script/API run.
- Treat **`assets/user_account.json`** as secret.

## Git

- **Do not commit** `assets/user_account.json`. Copy from `user_account.example.json` after clone; complete login and home selection per `references/aqara-account-manage.md` and `references/home-space-manage.md`.
- Repo-wide git notes: see [`../../README.md`](../../README.md) → **Git and GitHub**.
