# OpenForge

Multi-model PRD execution orchestrator for OpenClaw.

OpenForge turns PRD documents into staged, multi-model execution plans. Each phase routes to the right AI model — local models for simple coding, cloud models for complex work, premium models for review — with automatic escalation and validation gates.

## Quick Start

```bash
# Install
bash scripts/install.sh

# Validate a PRD
scripts/openforge validate --prd path/to/prd.md

# Execute a PRD
scripts/openforge run --prd path/to/prd.md --cwd /path/to/project
```

## Documentation

See `references/` for detailed docs on PRD format, model routing, escalation, and security.
