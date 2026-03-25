#!/bin/bash
# OpenClaw Doctor - 24/7 健康看门狗 v2
# macOS Gateway watchdog with L1-L4 health checks
# Requires: macOS, OpenClaw Gateway installed
set -euo pipefail

LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/doctor.log"
GATEWAY_URL="${OPENCLAW_DOCTOR_GATEWAY_URL:-http://127.0.0.1:18789}"
SERVICE_NAME="${OPENCLAW_DOCTOR_SERVICE_NAME:-ai.openclaw.gateway}"
NODE_SERVICE_NAME="${OPENCLAW_DOCTOR_NODE_SERVICE:-ai.openclaw.node}"
MAX_LOG_SIZE=5242880  # 5MB

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

rotate_log() {
    if [ -f "$LOG_FILE" ] && [ "$(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0)" -gt "$MAX_LOG_SIZE" ]; then
        tail -1000 "$LOG_FILE" > "$LOG_FILE.tmp"
        mv "$LOG_FILE.tmp" "$LOG_FILE"
        log "LOG_ROTATED"
    fi
}

# L1: Process alive check
check_process() {
    pgrep -f "openclaw.*gateway" > /dev/null 2>&1 && return 0
    launchctl list "$SERVICE_NAME" 2>/dev/null | grep -q '"PID"' && return 0
    return 1
}

# L2: HTTP port responding
check_http() {
    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$GATEWAY_URL/" 2>/dev/null || echo "000")
    [ "$status" != "000" ]
}

# L3: WebSocket communication health (log-based)
check_ws_health() {
    local log_file="/tmp/openclaw/openclaw-$(date '+%Y-%m-%d').log"
    [ ! -f "$log_file" ] && return 0
    local recent_errors
    recent_errors=$(tail -200 "$log_file" 2>/dev/null | grep -c "gateway closed (1006)" || echo "0")
    [ "$recent_errors" -le 3 ]
}

# L4: Prevent macOS sleep
ensure_awake() {
    if ! pgrep -f "caffeinate" > /dev/null 2>&1; then
        nohup caffeinate -dis -t 3600 > /dev/null 2>&1 &
        log "INFO - Started caffeinate to prevent sleep (1h)"
    fi
}

restart_gateway() {
    log "ACTION - Restarting gateway"
    launchctl kickstart -k "gui/$(id -u)/$SERVICE_NAME" 2>&1 && return 0
    launchctl bootout "gui/$(id -u)/$SERVICE_NAME" 2>/dev/null || true
    sleep 2
    launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist" 2>&1 && return 0
    openclaw gateway start 2>&1 || true
}

restart_node() {
    log "ACTION - Restarting node"
    launchctl kickstart -k "gui/$(id -u)/$NODE_SERVICE_NAME" 2>&1 && return 0
    return 1
}

# === Main logic ===
rotate_log
ensure_awake

HEALTHY=true
ISSUES=""

if ! check_process; then
    HEALTHY=false; ISSUES="PROCESS_DOWN"
    log "ALERT - Gateway process not found"
fi

if ! check_http; then
    HEALTHY=false; ISSUES="${ISSUES:+$ISSUES+}HTTP_UNREACHABLE"
    log "ALERT - Gateway HTTP probe failed"
fi

if [ "$HEALTHY" = true ] && ! check_ws_health; then
    HEALTHY=false; ISSUES="WS_FREQUENT_DISCONNECT"
    log "ALERT - Frequent WS disconnections detected"
fi

if [ "$HEALTHY" = false ]; then
    log "DIAGNOSIS - $ISSUES"
    case "$ISSUES" in
        *WS_FREQUENT_DISCONNECT*)
            restart_node; sleep 5
            if ! check_ws_health; then
                restart_gateway; sleep 3; restart_node; sleep 5
            fi
            check_http && log "RESOLVED - WS fix applied" || log "CRITICAL - Still unhealthy!"
            ;;
        *)
            openclaw doctor --repair --non-interactive --yes 2>&1 | tail -5 >> "$LOG_FILE" || true
            sleep 3
            if ! check_http; then
                restart_gateway; sleep 5
                check_http && log "RESOLVED - Gateway recovered" || log "CRITICAL - Gateway still down!"
            else
                log "RESOLVED - Doctor repair succeeded"
            fi
            ;;
    esac
else
    MINUTE=$(date '+%M')
    [ "$MINUTE" -lt 5 ] && log "HEARTBEAT - All checks passed ✓ (v2)"
fi
exit 0
