#!/bin/bash
# healthy-backup v1.2.3 — health-gated OpenClaw backup
#
# Usage: healthy-backup.sh [--dry-run]
#   --dry-run  Run full audit + show what would be staged; write nothing.
#
# Secrets policy (enforced in code, not just docs):
#   - openclaw.json staged with sensitive fields SCRUBBED (password/token/secret/key values)
#   - shared/secrets/, credentials/, *.key/pem/env/secret NEVER copied by rsync
#   - secrets-manifest contains key NAMES only (file is read but values never written)
#   - GPG passphrase via chmod-600 temp file — never on CLI/ps
#   - All temp files removed on EXIT via trap
set -euo pipefail

VERSION="1.2.3"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

# ---- Dry-run flag ----
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# ---- Output helpers ----
R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' B='\033[0;34m' BO='\033[1m' X='\033[0m'
log()    { echo -e "${B}[hb]${X} $*"; }
ok()     { echo -e "${G}  ✓${X} $*"; }
fail()   { echo -e "${R}  ✗${X} $*"; }
warn()   { echo -e "${Y}  ⚠${X} $*"; }
header() { echo -e "\n${BO}$*${X}"; }

# ---- Cleanup trap ----
STAGING_DIR="" ARCHIVE_DIR="" PASSPHRASE_FILE=""
cleanup() {
    rm -rf "$STAGING_DIR" "$ARCHIVE_DIR"
    [ -f "$PASSPHRASE_FILE" ] && rm -f "$PASSPHRASE_FILE"
}
trap cleanup EXIT

# ---- Config ----
[ -f "$OPENCLAW_CONFIG" ] || { fail "openclaw.json not found at $OPENCLAW_CONFIG"; exit 1; }

SC=$(jq -r '.skills.entries["healthy-backup"].config // empty' "$OPENCLAW_CONFIG" 2>/dev/null)
cfg() {   # cfg <json_key> <ENV_VAR> <default>
    local v
    v=$(echo "$SC" | jq -r ".$1 // empty" 2>/dev/null)
    v="${v/#\~/$HOME}"
    echo "${v:-${!2:-$3}}"
}

OPENCLAW_DIR="$HOME/.openclaw"
WORKSPACE_DIR=$(jq -r '.agents.defaults.workspace // empty' "$OPENCLAW_CONFIG" 2>/dev/null)
WORKSPACE_DIR="${WORKSPACE_DIR:-$OPENCLAW_DIR/workspace}"
SKILLS_DIR=$(cfg skillsDir  SKILLS_DIR  "$OPENCLAW_DIR/skills")
BACKUP_ROOT=$(cfg backupRoot BACKUP_ROOT "$HOME/openclaw-backups")
REMOTE_DEST=$(cfg remoteDest REMOTE_DEST "")
UPLOAD_MODE=$(cfg uploadMode UPLOAD_MODE "local-only")
BACKUP_TIER=$(cfg backupTier BACKUP_TIER "migratable")
MAX_BACKUPS=$(cfg maxBackups MAX_BACKUPS "5")
MIN_DISK_MB=$(cfg minDiskMb  MIN_DISK_MB "500")
COLLECT_NPM=$(cfg    collectNpm     COLLECT_NPM     "false")
COLLECT_CRON=$(cfg   collectCrontab COLLECT_CRONTAB "false")
COLLECT_OLLAMA=$(cfg collectOllama  COLLECT_OLLAMA  "true")
SECRETS_FILE="$OPENCLAW_DIR/shared/secrets/openclaw-secrets.env"

# Load encryption password (key file takes lowest priority so env/config can override)
BACKUP_PASSWORD="${BACKUP_PASSWORD:-$(cfg password BACKUP_PASSWORD "")}"
KEY_FILE="$OPENCLAW_DIR/credentials/backup.key"
[ -z "$BACKUP_PASSWORD" ] && [ -f "$KEY_FILE" ] && BACKUP_PASSWORD=$(tr -d '\n' < "$KEY_FILE")

# Paths always excluded from rsync (no config override)
EXCLUDES=(
    --exclude=shared/secrets/ --exclude=credentials/
    --exclude='*.key' --exclude='*.pem' --exclude='*.env'
    --exclude='*.secret' --exclude='.env'
    --exclude='.git/' --exclude='node_modules/' --exclude='BACKUPS/'
)

# ==========================================
# HEALTH AUDIT
# ==========================================

HEALTH_FAILED=0
REPORT=()
chk_ok()   { ok   "$1"; REPORT+=("PASS: $1"); }
chk_fail() { fail "$1"; REPORT+=("FAIL: $1"); HEALTH_FAILED=1; }
chk_warn() { warn "$1"; REPORT+=("WARN: $1"); }

check_perms() {  # check_perms <file> <label>
    local p
    p=$(stat -c "%a" "$1" 2>/dev/null || stat -f "%OLp" "$1" 2>/dev/null)
    [ "$p" = "600" ] && chk_ok "$2 permissions OK (600)" \
                     || chk_fail "$2 permissions are $p — run: chmod 600 $1"
}

header "━━━ HEALTH AUDIT ━━━"

header "1. Binaries"
for cmd in tar jq gpg rsync; do
    command -v "$cmd" &>/dev/null \
        && chk_ok  "$cmd ($(command -v "$cmd"))" \
        || chk_fail "$cmd not found"
done
[ "$UPLOAD_MODE" = "rclone" ] && {
    command -v rclone &>/dev/null \
        && chk_ok  "rclone found" \
        || chk_fail "rclone not found (required for uploadMode=rclone)"
}

header "2. Config"
jq empty "$OPENCLAW_CONFIG" 2>/dev/null \
    && chk_ok  "openclaw.json valid JSON" \
    || chk_fail "openclaw.json corrupt"
agent_count=$(jq '.agents.entries | length' "$OPENCLAW_CONFIG" 2>/dev/null || echo 0)
[ "$agent_count" -gt 0 ] \
    && chk_ok   "$agent_count agent(s) defined" \
    || chk_warn "No agents in config (may be intentional)"

header "3. Directories"
[ -d "$OPENCLAW_DIR" ]  && chk_ok "openclaw dir ($OPENCLAW_DIR)"  || chk_fail "openclaw dir not found: $OPENCLAW_DIR"
[ -d "$WORKSPACE_DIR" ] && chk_ok "workspace ($WORKSPACE_DIR)"    || chk_fail "workspace not found: $WORKSPACE_DIR"
[ -d "$SKILLS_DIR" ] \
    && chk_ok  "skills dir — $(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ') skill(s)" \
    || chk_warn "Skills dir not found: $SKILLS_DIR"

header "4. Disk"
avail=$(df -m "$HOME" | awk 'NR==2{print $4}')
[ "$avail" -ge "$MIN_DISK_MB" ] \
    && chk_ok   "Disk OK — ${avail}MB free (min ${MIN_DISK_MB}MB)" \
    || chk_fail "Low disk — ${avail}MB free, need ${MIN_DISK_MB}MB"

header "5. Encryption"
[ -n "$BACKUP_PASSWORD" ] \
    && chk_ok   "Password found" \
    || chk_fail "No password — use backup.key, BACKUP_PASSWORD env, or skill config"
[ -f "$KEY_FILE" ] && check_perms "$KEY_FILE" "backup.key"

# Warn if password is stored inline in openclaw.json (will be redacted in backup, but
# the live config file on disk still contains it — recommend moving to key file)
inline_pw=$(jq -r '.skills.entries["healthy-backup"].config.password // empty' "$OPENCLAW_CONFIG" 2>/dev/null)
[ -n "$inline_pw" ] && chk_warn "Password stored inline in openclaw.json — consider moving to $KEY_FILE (chmod 600) so the live config file contains no secrets"

header "6. Secrets file"
if [ -f "$SECRETS_FILE" ]; then
    chk_ok "Secrets file found (excluded from staging by policy)"
    check_perms "$SECRETS_FILE" "Secrets file"
else
    chk_warn "Secrets file not found at $SECRETS_FILE (may be optional)"
fi

if [ "$UPLOAD_MODE" = "rclone" ]; then
    header "7. Cloud remote"
    if [ -z "$REMOTE_DEST" ]; then
        chk_fail "uploadMode=rclone but remoteDest not set"
    else
        REMOTE_NAME="${REMOTE_DEST%%:*}"
        rclone listremotes 2>/dev/null | grep -q "^${REMOTE_NAME}:" \
            && chk_ok   "rclone remote '$REMOTE_NAME' configured" \
            || chk_fail "rclone remote '$REMOTE_NAME' not found — run: rclone config"
    fi
fi

header "8. Ollama"
if command -v ollama &>/dev/null; then
    models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ' ')
    [ -n "$models" ] && chk_ok "Ollama running — $models" || chk_warn "Ollama installed, no models loaded"
else
    chk_warn "Ollama not found (skip if unused)"
fi

# ---- Audit result ----
header "━━━ AUDIT RESULT ━━━"
printf "  ${G}Pass:${X}  %s\n  ${Y}Warn:${X}  %s\n  ${R}Fail:${X}  %s\n" \
    "$(printf '%s\n' "${REPORT[@]}" | grep -c '^PASS:')" \
    "$(printf '%s\n' "${REPORT[@]}" | grep -c '^WARN:')" \
    "$(printf '%s\n' "${REPORT[@]}" | grep -c '^FAIL:')"

if [ "$HEALTH_FAILED" -eq 1 ]; then
    echo -e "\n${R}${BO}✗ Audit failed — backup aborted. Fix issues above and re-run.${X}\n"
    exit 1
fi
echo -e "\n${G}${BO}✓ Rig healthy — proceeding to backup...${X}\n"

# ---- Dry-run: show what would be staged, then exit ----
if [ "$DRY_RUN" = true ]; then
    header "━━━ DRY RUN — no files will be written ━━━"
    log "Would stage tier: ${BACKUP_TIER}"
    log "Would write to:   ${BACKUP_ROOT}/"
    log "Would encrypt:    AES256 GPG"
    log "Would retain:     last ${MAX_BACKUPS} archives"
    [ "$UPLOAD_MODE" = "rclone" ] && log "Would sync to:    ${REMOTE_DEST}"
    echo ""
    log "Files that would be included (rsync --dry-run):"

    # Show what rsync would copy for each tier, without writing anything
    dry_sync() {
        local src="$1"; shift 2  # skip dest_subdir
        rsync -a --dry-run --out-format="  %n" "${EXCLUDES[@]}" "$@" "$src/" /dev/null 2>/dev/null || true
    }

    echo "  [config] openclaw.json (sensitive values redacted)"
    [ -f "$SECRETS_FILE" ] && echo "  [config] secrets-manifest.txt (key names only)"

    if [[ "$BACKUP_TIER" == "migratable" || "$BACKUP_TIER" == "full" ]]; then
        echo "  [openclaw dir]"
        dry_sync "$OPENCLAW_DIR" openclaw --exclude='logs/' --exclude='media/' --exclude='browser/'
    fi
    if [[ "$BACKUP_TIER" == "full" ]]; then
        [ -d "$WORKSPACE_DIR" ] && { echo "  [workspace]"; dry_sync "$WORKSPACE_DIR" workspace --exclude='canvas/'; }
        [ -d "$SKILLS_DIR" ]   && { echo "  [skills]";    dry_sync "$SKILLS_DIR"   skills   --exclude='.venv/'; }
    fi

    echo ""
    echo -e "${Y}${BO}Dry run complete — nothing written.${X} Remove --dry-run to execute.\n"
    exit 0
fi

# ==========================================
# BACKUP
# ==========================================

# Secure passphrase file (never passed on CLI)
PASSPHRASE_FILE=$(mktemp); chmod 600 "$PASSPHRASE_FILE"
printf '%s' "$BACKUP_PASSWORD" > "$PASSPHRASE_FILE"
unset BACKUP_PASSWORD

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE_NAME="healthy-backup-${TIMESTAMP}-${BACKUP_TIER}.tgz"
ENCRYPTED_NAME="${ARCHIVE_NAME}.gpg"
STAGING_DIR=$(mktemp -d); ARCHIVE_DIR=$(mktemp -d)
ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_NAME"
ENCRYPTED_PATH="$ARCHIVE_DIR/$ENCRYPTED_NAME"
mkdir -p "$BACKUP_ROOT"

header "━━━ BACKUP [${BACKUP_TIER}] ━━━"
log "Staging..."

# Shared rsync helper
sync_dir() {  # sync_dir <src> <dest_subdir> [extra excludes...]
    local src="$1" dest="$STAGING_DIR/$2"; shift 2
    mkdir -p "$dest"
    rsync -a "${EXCLUDES[@]}" "$@" "$src/" "$dest/"
}

stage_minimal() {
    mkdir -p "$STAGING_DIR/config"

    # Stage openclaw.json with sensitive field VALUES scrubbed.
    # Any key whose name contains password, token, secret, or key has its value replaced.
    # Structure and all non-sensitive config is preserved.
    jq 'walk(
        if type == "object" then
            with_entries(
                if (.key | test("password|token|secret|key"; "i"))
                then .value = "<redacted>"
                else .
                end
            )
        else .
        end
    )' "$OPENCLAW_CONFIG" > "$STAGING_DIR/config/openclaw.json"
    ok "openclaw.json (sensitive field values redacted)"

    # Secrets manifest — reads the secrets file to extract variable NAMES only.
    # The file itself is never copied; only the key names are written.
    if [ -f "$SECRETS_FILE" ]; then
        grep -oE '^[A-Za-z_][A-Za-z0-9_]*' "$SECRETS_FILE" \
            > "$STAGING_DIR/config/secrets-manifest.txt" 2>/dev/null || true
        ok "secrets-manifest.txt (key names only — values never written)"
    fi
}

stage_migratable() {
    stage_minimal
    sync_dir "$OPENCLAW_DIR" openclaw --exclude='logs/' --exclude='media/' --exclude='browser/'
    ok "~/.openclaw (secrets excluded)"

    # Dependencies manifest — sensitive sections are opt-in
    {
        echo "# Dependencies Manifest — healthy-backup v${VERSION} — $(date)"
        echo; echo "## Binaries"
        for cmd in tar gpg jq rsync rclone ollama node npm python3; do
            command -v "$cmd" &>/dev/null \
                && echo "- \`$cmd\`: $($cmd --version 2>&1 | head -1)" \
                || echo "- \`$cmd\`: not installed"
        done
        echo; echo "## OS"; uname -a

        echo; echo "## npm globals"
        [ "$COLLECT_NPM" = "true" ] \
            && npm list -g --depth=0 2>/dev/null | tail -n +2 \
            || echo "(opt-in disabled — set collectNpm: true to enable)"

        echo; echo "## Ollama models"
        [ "$COLLECT_OLLAMA" = "true" ] \
            && ollama list 2>/dev/null | tail -n +2 \
            || echo "(disabled)"

        echo; echo "## Cron (VAR=values redacted)"
        [ "$COLLECT_CRON" = "true" ] \
            && crontab -l 2>/dev/null | sed 's/\([A-Za-z_][A-Za-z0-9_]*\)=[^ ]*/\1=<REDACTED>/g' \
            || echo "(opt-in disabled — set collectCrontab: true to enable)"
    } > "$STAGING_DIR/DEPENDENCIES.md"
    ok "DEPENDENCIES.md (npm=$COLLECT_NPM cron=$COLLECT_CRON ollama=$COLLECT_OLLAMA)"
}

stage_full() {
    stage_migratable
    [ -d "$WORKSPACE_DIR" ] \
        && { sync_dir "$WORKSPACE_DIR" workspace --exclude='canvas/'; ok "workspace"; } \
        || warn "Workspace not found — skipped"
    [ -d "$SKILLS_DIR" ] \
        && { sync_dir "$SKILLS_DIR" skills --exclude='.venv/'; ok "skills"; } \
        || warn "Skills dir not found — skipped"
}

case "$BACKUP_TIER" in
    minimal)    stage_minimal ;;
    migratable) stage_migratable ;;
    full)       stage_full ;;
    *) fail "Unknown tier '$BACKUP_TIER' — use: minimal | migratable | full"; exit 1 ;;
esac

# Health report inside archive
printf "healthy-backup v%s — Health Report\nTimestamp: %s\nTier: %s\nUpload: %s\n\n%s\n" \
    "$VERSION" "$(date)" "$BACKUP_TIER" "$UPLOAD_MODE" \
    "$(printf '%s\n' "${REPORT[@]}")" > "$STAGING_DIR/HEALTH_REPORT.txt"

log "Compressing..."
tar -czf "$ARCHIVE_PATH" -C "$STAGING_DIR" .
ok "$(du -sh "$ARCHIVE_PATH" | cut -f1) compressed"

log "Encrypting (AES256)..."
gpg --batch --yes --passphrase-file "$PASSPHRASE_FILE" \
    --symmetric --cipher-algo AES256 -o "$ENCRYPTED_PATH" "$ARCHIVE_PATH"
ok "$ENCRYPTED_NAME"

mv "$ENCRYPTED_PATH" "$BACKUP_ROOT/"
sha256sum "$BACKUP_ROOT/$ENCRYPTED_NAME" > "$BACKUP_ROOT/$ENCRYPTED_NAME.sha256"
ok "Saved + checksummed → $BACKUP_ROOT/"

log "Pruning (keep $MAX_BACKUPS)..."
mapfile -t ALL < <(ls -t "$BACKUP_ROOT"/healthy-backup-*.tgz.gpg 2>/dev/null)
if [ "${#ALL[@]}" -gt "$MAX_BACKUPS" ]; then
    for f in "${ALL[@]:$MAX_BACKUPS}"; do
        rm -f "$f" "$f.sha256"
        warn "Pruned: $(basename "$f")"
    done
fi
ok "${#ALL[@]} → kept max $MAX_BACKUPS"

[ "$UPLOAD_MODE" = "rclone" ] && [ -n "$REMOTE_DEST" ] && {
    header "━━━ CLOUD SYNC ━━━"
    rclone sync "$BACKUP_ROOT" "$REMOTE_DEST" --include "*.gpg" --progress
    ok "Synced → $REMOTE_DEST"
}

header "━━━ DONE ━━━"
echo -e "${G}${BO}✓ Backup complete${X}"
echo -e "  Archive:  $BACKUP_ROOT/$ENCRYPTED_NAME"
echo -e "  Tier:     $BACKUP_TIER  |  Retained: $MAX_BACKUPS"
[ "$UPLOAD_MODE" = "rclone" ] && echo -e "  Cloud:    $REMOTE_DEST"
SELF_SHA=$(sha256sum "$0" | awk '{print $1}')
echo -e "  Script:   $SELF_SHA  (sha256sum $0)"
echo ""

# END OF FILE — healthy-backup.sh v1.2.3
