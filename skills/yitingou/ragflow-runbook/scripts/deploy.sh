#!/usr/bin/env bash
# RAGFlow deploy (ops-only)
#
# Goal:
# - Prefer a robust install path using `git clone`.
# - Fall back to downloading upstream docker assets if git is not available.
#
# Usage:
#   bash deploy.sh [deploy_root]
#
# Output:
# - Creates/uses a directory that contains the upstream `docker/` folder.
# - Starts RAGFlow via `docker compose up -d` from inside that `docker/` folder.

set -euo pipefail

DEPLOY_ROOT=${1:-"./ragflow"}

echo "=========================================="
echo "           RAGFlow Deploy"
echo "=========================================="
echo

echo "1) System checks"
if command -v docker >/dev/null 2>&1; then
  echo "  OK: $(docker --version)"
else
  echo "  ERROR: docker is not installed"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  echo "  OK: $(docker compose version)"
elif command -v docker-compose >/dev/null 2>&1; then
  echo "  OK: $(docker-compose --version)"
else
  echo "  ERROR: docker compose is not installed"
  exit 1
fi

echo

echo "2) Prepare deploy root: $DEPLOY_ROOT"
mkdir -p "$DEPLOY_ROOT"
cd "$DEPLOY_ROOT"

UPSTREAM_REPO_URL="https://github.com/infiniflow/ragflow.git"
UPSTREAM_DIR="$DEPLOY_ROOT/ragflow"
DOCKER_DIR="$UPSTREAM_DIR/docker"

have_git=0
if command -v git >/dev/null 2>&1; then
  have_git=1
fi

if [[ $have_git -eq 1 ]]; then
  echo "3) Fetch upstream via git clone (preferred)"

  if [[ -d "$UPSTREAM_DIR/.git" ]]; then
    echo "  - Found existing repo: $UPSTREAM_DIR"
    echo "  - Updating..."
    (cd "$UPSTREAM_DIR" && git fetch --all --prune)
  elif [[ -e "$UPSTREAM_DIR" ]]; then
    echo "  ERROR: $UPSTREAM_DIR exists but is not a git repo"
    echo "         Move it aside or choose a different deploy_root"
    exit 2
  else
    echo "  - Cloning: $UPSTREAM_REPO_URL"
    git clone "$UPSTREAM_REPO_URL" "$UPSTREAM_DIR"
  fi

  if [[ ! -d "$DOCKER_DIR" ]]; then
    echo "  ERROR: docker directory not found at: $DOCKER_DIR"
    exit 3
  fi

else
  echo "3) Git not found; falling back to downloading upstream docker assets"

  UPSTREAM_DIR="$DEPLOY_ROOT/ragflow"
  DOCKER_DIR="$UPSTREAM_DIR/docker"
  mkdir -p "$DOCKER_DIR"
  cd "$DOCKER_DIR"

  echo "  - Download docker files"
  FILES=(
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/docker-compose.yml"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/docker-compose-base.yml"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/.env"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/service_conf.yaml.template"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/entrypoint.sh"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/README.md"
  )

  dl() {
    local url="$1"
    local name
    name=$(basename "$url")
    echo "    - $name"
    wget -q "$url" || curl -fsSLO "$url"
  }

  for url in "${FILES[@]}"; do
    dl "$url"
  done

  echo "  - Download nginx configuration"
  mkdir -p nginx
  cd nginx

  NGINX_FILES=(
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/nginx/nginx.conf"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/nginx/ragflow.conf"
    "https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/nginx/proxy.conf"
  )

  for url in "${NGINX_FILES[@]}"; do
    dl "$url"
  done

  cd "$DOCKER_DIR"
fi

echo

echo "4) Enter docker directory: $DOCKER_DIR"
cd "$DOCKER_DIR"

if [[ "$(uname)" == "Linux" ]] && [[ -r /proc/sys/vm/max_map_count ]]; then
  map_count=$(cat /proc/sys/vm/max_map_count)
  if [[ "$map_count" -ge 262144 ]]; then
    echo "  OK: vm.max_map_count=$map_count"
  else
    echo "  WARN: vm.max_map_count=$map_count (some profiles require >= 262144)"
    echo "        Run: sudo sysctl -w vm.max_map_count=262144"
  fi
fi

echo

echo "5) Start services"
docker compose up -d

echo

echo "6) Status"
docker compose ps

echo

echo "=========================================="
echo "            Deploy Done"
echo "=========================================="
echo

echo "Next steps:"
echo "- Check liveness: curl -sS http://127.0.0.1:9380/openapi.json (adjust host/port if needed)"
echo "- Or use this skill's helpers: scripts/ragflow_ping.py / scripts/ragflow_smoke.py"

echo

echo "Notes:"
echo "- Edit docker/.env if you need to change exposed ports."
echo "- For production, do not keep default passwords from .env."
