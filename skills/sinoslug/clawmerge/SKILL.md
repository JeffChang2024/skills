---
name: clawmerge
version: 2.2
description: |
  OpenClaw workspace backup, restore, and merge tool with disaster recovery.
  Use when user wants to:
  (1) Create versioned backups with security exclusions
  (2) Restore workspace with merge mode (no overwrite)
  (3) Preview backups with --dry-run
  (4) List available backups
  (5) Transfer workspace between computers
  (6) Disaster recovery with automatic pre-restore backup
  (7) Backup/restore cron tasks (integrated in archive)
  (8) Backup/restore session records (conversation history)
  
Unique features: Merge-mode restore + Integrated cron backup + Session records backup

improvements:
  - Security: Excludes sensitive files (credentials, openclaw.json, .env)
  - Disaster Recovery: Auto-backup before restore
  - Dry-run Mode: Preview what would be backed up/restored
  - List Mode: Show available backups
  - Cron Tasks Backup: Integrated in main archive (NEW in v2.2)
  - Session Records: Optional conversation history backup (NEW in v2.2)
  - Better conflict handling
---

# Workspace Backup/Restore/Merge v2.2

## What's New in v2.2

### ✅ Fixed: Cron tasks integrated in archive
- Cron export files are now **included in the main .tar.gz**
- No more separate files to manage
- Automatically cleaned up after backup

### ✅ Fixed: Session records backup (optional)
- Add `--with-sessions` to backup conversation history
- Includes all session JSONL files from `~/.openclaw/agents/main/sessions/`
- Restore with `--with-sessions` flag
- **Note:** Sessions include full conversation history across all channels

### 📋 Updated Commands

**Backup with sessions:**
```bash
./one-click-backup.sh --with-sessions
```

**Restore with sessions:**
```bash
./one-click-restore.sh ~/backups/clawmerge-*.tar.gz --with-sessions
```

---

## Data Locations

- **Workspace**: `~/.openclaw/workspace/`
- **Backups**: `~/.openclaw/backups/`
- **Disaster Recovery**: `~/.openclaw/.local-backup/`
- **Sessions**: `~/.openclaw/agents/main/sessions/` (optional backup)
- **Key files**: MEMORY.md, memory/, USER.md, IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md, HEARTBEAT.md, skills/

---

## Quick Start (One-Click)

### 📦 Backup

**Basic backup:**
```bash
~/.openclaw/workspace/skills/clawmerge/scripts/one-click-backup.sh
```

**With options:**
```bash
# Include session records (conversation history)
./one-click-backup.sh --with-sessions

# Dry-run: Preview what would be backed up
./one-click-backup.sh --dry-run

# List: Show available backups
./one-click-backup.sh --list

# Custom output directory
./one-click-backup.sh /mnt/external-drive/backups

# Combine options
./one-click-backup.sh /mnt/external-drive --with-sessions --dry-run
```

**Output:** `~/backups/clawmerge-YYYYMMDD-HHMMSS.tar.gz`

**What gets backed up:**
- ✓ MEMORY.md, memory/
- ✓ USER.md, IDENTITY.md, SOUL.md, AGENTS.md, TOOLS.md, HEARTBEAT.md
- ✓ skills/
- ✓ Cron tasks export (integrated in archive)
- ✓ System crontab (integrated in archive)
- ✓ Session records (with `--with-sessions`)

**Security exclusions:**
- ✗ `*.tar.gz` - Old backups
- ✗ `.git/` - Git history
- ✗ `.clawhub/` - ClawHub metadata
- ✗ `.openclaw/` - Internal configs
- ✗ `config.yaml` - User config
- ✗ `*.log` - Log files
- ✗ `node_modules/` - NPM dependencies

---

### ♻️ Restore (Merge Mode)

**Basic restore:**
```bash
~/.openclaw/workspace/skills/clawmerge/scripts/one-click-restore.sh ~/backups/clawmerge-YYYYMMDD-HHMMSS.tar.gz
```

**With options:**
```bash
# Restore with session records
./one-click-restore.sh ~/backups/clawmerge-*.tar.gz --with-sessions

# Dry-run: Preview
./one-click-restore.sh ~/backups/clawmerge-*.tar.gz --dry-run

# Force: Skip confirmation
./one-click-restore.sh ~/backups/clawmerge-*.tar.gz --force
```

---

## Version History

### v2.2 (2026-03-21)
- ✅ **FIXED**: Cron tasks integrated in main archive
- ✅ **FIXED**: Session records backup (optional with `--with-sessions`)
- ✅ Cleanup temp files after backup
- ✅ Better restore preview
- ✅ Updated documentation

### v2.1 (2026-03-21)
- ✅ Cron tasks backup/export for migration
- ✅ System crontab backup
- ✅ Cron restore guidance script

### v2.0 (2026-03-19)
- ✅ Security: Exclude sensitive files
- ✅ Disaster Recovery: Auto-backup before restore
- ✅ Dry-run mode
- ✅ List mode

### v1.0 (2026-03-18)
- Initial release with merge-mode restore

---

[Rest of the original SKILL.md content remains the same...]
