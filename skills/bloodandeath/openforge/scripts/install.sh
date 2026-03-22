#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PKG_DIR="$SKILL_DIR/pkg"

echo "[openforge] Installing OpenForge..."

if ! command -v uv &>/dev/null; then
    echo "[openforge] Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

cd "$PKG_DIR"
uv sync
echo "[openforge] ✓ Python environment ready"

if command -v openclaw &>/dev/null; then
    echo "[openforge] OpenClaw detected. Register agents from config/agents.example.json manually."
else
    echo "[openforge] ⚠ openclaw not found — skip agent registration"
fi

if "$SCRIPT_DIR/openforge" validate "$SKILL_DIR/templates/prd-simple.md" &>/dev/null; then
    echo "[openforge] ✓ Smoke test passed"
else
    echo "[openforge] ✗ Smoke test failed"
    exit 1
fi

echo "[openforge] ✓ Installation complete"
echo "[openforge] Entrypoint: $SCRIPT_DIR/openforge"
