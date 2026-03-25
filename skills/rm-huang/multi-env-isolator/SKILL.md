---
name: multi-env-isolator
description: |
  Generate isolated dev/test/prod environments for uvicorn/FastAPI Python web projects. Creates separate config files, startup scripts, data directories, and documentation with one command. Use when:
  (1) Setting up a new FastAPI/uvicorn project that needs dev/test/prod separation
  (2) An existing project has only one environment and needs isolation for parallel work
  (3) A multi-agent team needs developers and testers working simultaneously without conflicts
  (4) Someone asks "how to separate development and production" or "set up environment isolation"
  (5) A project suffers from dev changes breaking production, or testers interfering with developers
  NOT for: Node.js, Go, Docker-based, or non-Python projects (startup scripts are uvicorn-specific).
---

# Multi-Environment Isolator

Generate isolated dev/test/prod environments for uvicorn/FastAPI projects with one command.

## What This Skill Does

This skill solves a common problem in multi-agent AI teams: **developers, testers, and production users stepping on each other's toes.** It generates a complete environment isolation setup so that:

- A **developer** can freely break things on port 8020 without affecting anyone
- A **tester** can validate releases on port 8010 with isolated test data
- **Production** stays stable on port 8000, untouched by dev/test activity

Each environment gets its own config file, startup script, database, and media storage — completely isolated from the others.

## What Gets Generated

Running the setup script creates this structure inside the target project:

```
your-project/
├── .env.dev              # Dev config: DEBUG=True, hot reload, no rate limit
├── .env.test             # Test config: rate limiting enabled, QA settings
├── .env.prod             # Prod config: DEBUG=False, secure CORS, multi-worker
├── scripts/
│   ├── start-dev.sh      # Starts dev server on port 8020 with --reload
│   ├── start-test.sh     # Starts test server on port 8010
│   └── start-prod.sh     # Starts prod server on port 8000 with auto workers
├── data/
│   ├── dev/              # Dev database + media uploads (safe to delete)
│   │   └── media/
│   ├── test/             # Test database + media uploads
│   │   └── media/
│   └── prod/             # Prod database + media uploads (back this up!)
│       └── media/
├── docs/
│   └── MULTI_ENV_SETUP.md  # Auto-generated setup guide for the team
└── .gitignore            # Updated to exclude .env.* and data/
```

## How to Use

### Step 1: Run the setup script

```bash
python3 scripts/setup_envs.py /path/to/your-project \
  --name "Your Project Name" \
  --dev-port 8020 \
  --test-port 8010 \
  --prod-port 8000 \
  --dev-user "Alice" \
  --test-user "Bob" \
  --app-module "server.main:app"
```

All flags except `--name` are optional and have sensible defaults.

### Step 2: Customize configs

Edit the generated `.env.dev`, `.env.test`, `.env.prod` files to add project-specific settings like API keys, external service URLs, etc.

### Step 3: Start an environment

```bash
# For development (hot reload enabled)
./scripts/start-dev.sh

# For testing
./scripts/start-test.sh

# For production
./scripts/start-prod.sh
```

Each script loads its own `.env.*` file, uses its own port, and writes to its own `data/` subdirectory.

## Command Reference

```
python3 scripts/setup_envs.py <project_dir> --name <name> [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `project_dir` | (required) | Path to the target project |
| `--name` | (required) | Project name, used in configs and docs |
| `--dev-port` | 8020 | Development server port |
| `--test-port` | 8010 | Testing server port |
| `--prod-port` | 8000 | Production server port |
| `--dev-user` | (none) | Developer name, shown in dev startup message |
| `--test-user` | (none) | Tester name, shown in test startup message |
| `--db-type` | sqlite | `sqlite` or `postgres` |
| `--app-module` | server.main:app | Uvicorn application module path |
| `--dev-db` | (auto) | Override dev database URL |
| `--test-db` | (auto) | Override test database URL |
| `--prod-db` | (auto) | Override prod database URL |

## Environment Differences at a Glance

| Setting | Dev | Test | Prod |
|---------|-----|------|------|
| `DEBUG` | True | True | **False** |
| Hot Reload | **Yes** | No | No |
| CORS | Allow All | Allow All | **Restricted** |
| Rate Limiting | **Off** | On | On |
| Workers | 1 (reload) | 1 | **Auto (CPU cores)** |
| Log Level | DEBUG | INFO | **WARNING** |
| Database | `data/dev/` | `data/test/` | `data/prod/` |
| Media | `data/dev/media/` | `data/test/media/` | `data/prod/media/` |

## Recommended Git Branch Strategy

For teams using this setup:

```
main ──────────── Production (start-prod.sh)
  ├── release/* ── Testing (start-test.sh)
  └── feature/* ── Development (start-dev.sh)
```

1. Developer works on `feature/*`, deploys to dev environment
2. Merge to `release/*`, tester validates on test environment
3. Tester approves, merge to `main`, deploy to production

## Important Notes

- **Existing files are not overwritten.** If `.env.dev` already exists, the script skips it and prints a warning. Safe to re-run.
- **Startup scripts are uvicorn-specific.** The generated `start-*.sh` scripts use `uvicorn` commands. For other frameworks, modify the scripts after generation.
- **Production JWT secret must be changed.** The generated `.env.prod` has a placeholder `JWT_SECRET`. Replace it with a strong random value before going live.
- **Back up production data.** The `data/prod/` directory contains the production database. Set up regular backups.

## Detailed Config Reference

For all environment variables and troubleshooting: read `references/config-options.md`
