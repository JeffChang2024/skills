#!/bin/bash
#
# One-Click Backup for OpenClaw Workspace v2.2
# Usage: ./one-click-backup.sh [output_dir] [--dry-run] [--list] [--with-sessions]
#
# Improvements in v2.2:
# - Session records backup (optional)
# - Cron tasks integrated into main archive
# - Better security exclusions
#

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
OPENCLAW_DIR="$HOME/.openclaw"
DEFAULT_OUTPUT_DIR="$HOME/.openclaw/backups"
OUTPUT_DIR=""
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse arguments
DRY_RUN=false
LIST_MODE=false
WITH_SESSIONS=false
OUTPUT_DIR_SET=false

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --list)
            LIST_MODE=true
            ;;
        --with-sessions)
            WITH_SESSIONS=true
            ;;
        *)
            if [ "$OUTPUT_DIR_SET" = false ]; then
                OUTPUT_DIR="$arg"
                OUTPUT_DIR_SET=true
            fi
            ;;
    esac
done

if [ "$OUTPUT_DIR_SET" = false ]; then
    OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
fi

BACKUP_FILE="$OUTPUT_DIR/clawmerge-$TIMESTAMP.tar.gz"

# List mode
if [ "$LIST_MODE" = true ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Available Backups${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    if [ -d "$OUTPUT_DIR" ]; then
        BACKUP_COUNT=$(ls -1 "$OUTPUT_DIR"/clawmerge-*.tar.gz 2>/dev/null | wc -l)
        if [ "$BACKUP_COUNT" -gt 0 ]; then
            echo -e "${YELLOW}Backup directory:${NC} $OUTPUT_DIR"
            echo -e "${YELLOW}Total backups:${NC} $BACKUP_COUNT"
            echo ""
            ls -lht "$OUTPUT_DIR"/clawmerge-*.tar.gz | awk '{print "  " $9 " (" $5 ") " $6 " " $7 " " $8}'
            echo ""
        else
            echo -e "${YELLOW}No backups found in $OUTPUT_DIR${NC}"
        fi
    else
        echo -e "${RED}Backup directory not found: $OUTPUT_DIR${NC}"
    fi
    exit 0
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  OpenClaw Workspace Backup v2.2${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ ! -d "$WORKSPACE_DIR" ]; then
    echo -e "${RED}Error: Workspace not found at $WORKSPACE_DIR${NC}"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# ============================================
# Step 1: Export cron tasks to temp file
# ============================================
CRON_EXPORT_DIR=$(mktemp -d)
trap "rm -rf $CRON_EXPORT_DIR" EXIT

echo -e "${YELLOW}[1/4] Exporting cron tasks...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/backup-cron-tasks.sh" ]; then
    bash "$SCRIPT_DIR/backup-cron-tasks.sh" "$CRON_EXPORT_DIR" >/dev/null 2>&1 || true
fi

# Copy cron files to workspace for inclusion in archive
cp "$CRON_EXPORT_DIR"/cron-tasks-*.json "$WORKSPACE_DIR/" 2>/dev/null && echo -e "  ${GREEN}✓ Cron tasks exported${NC}" || echo -e "  ${BLUE}○ No cron tasks${NC}"
cp "$CRON_EXPORT_DIR"/system-crontab-*.txt "$WORKSPACE_DIR/" 2>/dev/null && echo -e "  ${GREEN}✓ System crontab exported${NC}" || true
echo ""

# ============================================
# Step 2: Export session records (optional)
# ============================================
SESSIONS_EXPORT_DIR=""
if [ "$WITH_SESSIONS" = true ]; then
    SESSIONS_EXPORT_DIR=$(mktemp -d)
    trap "rm -rf $SESSIONS_EXPORT_DIR" EXIT
    
    echo -e "${YELLOW}[2/4] Exporting session records...${NC}"
    SESSIONS_DIR="$OPENCLAW_DIR/agents/main/sessions"
    
    if [ -d "$SESSIONS_DIR" ]; then
        # Copy session files
        cp -r "$SESSIONS_DIR" "$SESSIONS_EXPORT_DIR/" 2>/dev/null || true
        
        # Copy to workspace for inclusion
        if [ -d "$SESSIONS_EXPORT_DIR/sessions" ]; then
            cp -r "$SESSIONS_EXPORT_DIR/sessions" "$WORKSPACE_DIR/.backup-sessions" 2>/dev/null || true
            echo -e "  ${GREEN}✓ Session records exported${NC}"
            echo -e "  ${CYAN}  Note: Sessions include conversation history${NC}"
        fi
    else
        echo -e "  ${BLUE}○ No session records found${NC}"
    fi
    echo ""
fi

# ============================================
# Step 3: Create backup archive
# ============================================
echo -e "${YELLOW}[3/4] Creating backup archive...${NC}"

BACKUP_ITEMS=(
    "MEMORY.md"
    "memory/"
    "USER.md"
    "IDENTITY.md"
    "SOUL.md"
    "AGENTS.md"
    "TOOLS.md"
    "HEARTBEAT.md"
    "skills/"
)

# Add cron files if they exist
for f in "$WORKSPACE_DIR"/cron-tasks-*.json; do
    [ -f "$f" ] && BACKUP_ITEMS+=("$(basename "$f")")
done
for f in "$WORKSPACE_DIR"/system-crontab-*.txt; do
    [ -f "$f" ] && BACKUP_ITEMS+=("$(basename "$f")")
done

# Add sessions if requested
if [ "$WITH_SESSIONS" = true ] && [ -d "$WORKSPACE_DIR/.backup-sessions" ]; then
    BACKUP_ITEMS+=(".backup-sessions/")
fi

EXCLUDE_ITEMS=(
    "*.tar.gz"
    ".git"
    ".clawhub"
    ".openclaw"
    "config.yaml"
    "*.log"
    ".DS_Store"
    "__pycache__"
    "node_modules"
    ".backup-sessions"
)

cd "$WORKSPACE_DIR"

TAR_EXCLUDES=""
for exc in "${EXCLUDE_ITEMS[@]}"; do
    TAR_EXCLUDES="$TAR_EXCLUDES --exclude=$exc"
done

if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  DRY RUN - Simulating backup${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    echo -e "${YELLOW}Files that would be backed up:${NC}"
    tar -cvf /dev/null $TAR_EXCLUDES "${BACKUP_ITEMS[@]}" 2>&1 | tail -20
    
    echo ""
    echo -e "${BLUE}Output would be:${NC} $BACKUP_FILE"
    echo ""
    echo -e "${GREEN}Done! (no files modified)${NC}"
    
    # Cleanup temp files
    rm -f "$WORKSPACE_DIR"/cron-tasks-*.json "$WORKSPACE_DIR"/system-crontab-*.txt 2>/dev/null || true
    rm -rf "$WORKSPACE_DIR/.backup-sessions" 2>/dev/null || true
    exit 0
fi

# Create archive
tar -czvf "$BACKUP_FILE" $TAR_EXCLUDES "${BACKUP_ITEMS[@]}" 2>&1 | tail -5

# Verify archive contains cron files
if tar -tzf "$BACKUP_FILE" | grep -q "cron-tasks-"; then
    echo -e "  ${GREEN}✓ Cron tasks included in archive${NC}"
else
    echo -e "  ${YELLOW}⚠ Cron tasks may not be in archive${NC}"
fi

echo ""

# Cleanup temp files from workspace AFTER backup is complete
rm -f "$WORKSPACE_DIR"/cron-tasks-*.json "$WORKSPACE_DIR"/system-crontab-*.txt 2>/dev/null || true
rm -rf "$WORKSPACE_DIR/.backup-sessions" 2>/dev/null || true

# ============================================
# Step 4: Verify and summary
# ============================================
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    CHECKSUM=$(md5sum "$BACKUP_FILE" | awk '{print $1}')
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Backup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "File: ${YELLOW}$BACKUP_FILE${NC}"
    echo -e "Size: ${YELLOW}$SIZE${NC}"
    echo -e "MD5:  ${YELLOW}$CHECKSUM${NC}"
    echo ""
    
    # Show what was included
    echo -e "${CYAN}Backup contents:${NC}"
    tar -tzf "$BACKUP_FILE" | head -20
    if [ $(tar -tzf "$BACKUP_FILE" | wc -l) -gt 20 ]; then
        echo "  ... (and more)"
    fi
    echo ""
    
    # Rotation
    cd "$OUTPUT_DIR"
    BACKUP_COUNT=$(ls -1 clawmerge-*.tar.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        echo -e "${YELLOW}Cleaning up old backups (keeping last 10)...${NC}"
        ls -1t clawmerge-*.tar.gz | tail -n +11 | xargs -r rm -f
    fi
    
    echo -e "${BLUE}Tip:${NC} Run with --list to see all backups"
    echo -e "${BLUE}Tip:${NC} Add --with-sessions to include session records"
else
    echo -e "${RED}Error: Backup failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Done!${NC}"
