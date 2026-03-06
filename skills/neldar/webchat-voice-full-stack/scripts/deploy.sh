#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILLS_DIR="${SKILLS_DIR:-$WORKSPACE/skills}"

BACKEND="$SKILLS_DIR/faster-whisper-local-service/scripts/deploy.sh"
PROXY="$SKILLS_DIR/webchat-https-proxy/scripts/deploy.sh"
GUI="$SKILLS_DIR/webchat-voice-gui/scripts/deploy.sh"

if [[ ! -f "$BACKEND" ]]; then
  echo "ERROR: faster-whisper-local-service not found at: $SKILLS_DIR/faster-whisper-local-service" >&2
  echo "Install it first: npx clawhub install faster-whisper-local-service" >&2
  exit 2
fi

if [[ ! -f "$PROXY" ]]; then
  echo "ERROR: webchat-https-proxy not found at: $SKILLS_DIR/webchat-https-proxy" >&2
  echo "Install it first: npx clawhub install webchat-https-proxy" >&2
  exit 2
fi

if [[ ! -f "$GUI" ]]; then
  echo "ERROR: webchat-voice-gui not found at: $SKILLS_DIR/webchat-voice-gui" >&2
  echo "Install it first: npx clawhub install webchat-voice-gui" >&2
  exit 2
fi

echo "=== [full-stack] Step 1/3: Deploy backend (faster-whisper-local-service) ==="
bash "$BACKEND"

echo ""
echo "=== [full-stack] Step 2/3: Deploy HTTPS proxy (webchat-https-proxy) ==="
bash "$PROXY"

echo ""
echo "=== [full-stack] Step 3/3: Deploy voice GUI (webchat-voice-gui) ==="
bash "$GUI"

echo ""
echo "=== [full-stack] Deploy complete ==="
echo ""
echo "Next steps:"
echo "  1. Open https://<your-host>:${VOICE_HTTPS_PORT:-8443}/chat?session=main"
echo "  2. Accept the self-signed certificate"
echo "  3. Approve the pending device if prompted (openclaw devices approve ...)"
echo "  4. Click the mic button and speak"
