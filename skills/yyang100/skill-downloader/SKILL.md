---
name: skill-downloader
description: Search and install OpenClaw skills from trusted sources including skills.sh, ClawHub, and GitHub. Handles both "find X skill" search queries and "install X skill" download requests. Always use this skill when the user requests to download, install, or add third-party skills.
triggers:
  - "search"
  - "find"
  - "look for"
  - "查找"
  - "搜索"
  - "is there a skill"
  - "有没有.*技能"
  - "download skill"
  - "install skill"
  - "添加技能"
  - "下载技能"
compatibility: requires git, curl, Node.js/npm
---

# skill-downloader

Download and install OpenClaw skills from trusted sources with proper security checks and directory handling.

## Trusted download sources

Default trusted sources (ordered by priority):
1. `https://skills.sh/` - Open agent skills ecosystem registry (via npx skills CLI)
2. `https://clawhub.ai/` - Official ClawHub skill repository
3. `https://github.com/anthropics/skills` - Anthropic example skills repository

Users can add additional sources later by updating this list in SKILL.md.

## Core rules

1. **Always confirm before downloading**: Do not download any skill without explicit instruction from the user. If the user just asks about skills or where to find them, recommend sources but wait for a clear download command.
2. **Security**: Before installation, automatically read the content of the new skill to check for sensitive content:
   - Check the main code and documentation for malicious behavior: unauthorized data exfiltration, secret stealing, automatic destructive operations, malicious code obfuscation
   - If suspicious sensitive content is detected, abort installation and inform the user of the specific risk found
3. **Search order**: Search for the skill in the default trusted sources in priority order. If not found, ask the user if they can provide an alternative download URL.
4. **Recommend when uncertain**: If unsure where to find the skill, list the available trusted sources and ask the user which one to use.
5. **Multiple results handling**: If multiple matching skills are found:
   - Collect skill name, description, popularity/install count (if available), source repository, and skills.sh page URL
   - Organize into a clear list/table for the user
   - For each skill, add a short recommendation note explaining its best use case
   - After listing all skills, give a summary recommendation of which one to choose overall, prioritizing skills that are secure, actively maintained, and have high functional matching

## Installation directory rules

Follow these rules strictly for where to install the skill:

### Global installation
- When the user explicitly mentions "global", "system-wide", or similar words indicating global installation:
  - **macOS/Linux**: `~/.openclaw/skills/`
  - **Windows**: `%USERPROFILE%\.openclaw\skills\`
  - **Other platforms**: Follow the XDG base directory spec if defined, otherwise use `~/.openclaw/skills/`

### Local installation (default)
- When the user does NOT mention "global" or similar words:
  - Install to: `{current_workspace}/skills/`
  - If no workspace is detected, default to `~/.openclaw/workspace/skills/`

## Workflow

### Mode A: Search Only (no installation)

When user only asks to "search", "find", or "look for" a skill (no download/install intent):

1. **Detect search intent** — User asks "find X skill", "search for Y", "is there a skill that can..."
2. **Use npx skills find** — Run `npx skills find <query>` to search skills.sh
3. **Present results** — Show results in table format with:
   - Skill name and owner/repo
   - Install count (popularity)
   - Skills.sh URL
   - Brief recommendation
4. **Wait for user** — Ask if they want to install any of the results
5. **If yes** → Continue to Mode B (Installation)
6. **Done** — End here if user just wants to browse

### Mode B: Installation (download + install)

1. **Capture request**
   - Extract the skill name to download
   - Check if user requested global installation
   - Confirm this is an explicit download request (if not, ask for confirmation)
   - **Check existing installation**:
     - For global installation: check if skill already exists at `~/.openclaw/skills/<skill-name>/`
     - For local installation: check if skill already exists at `{current_workspace}/skills/<skill-name>/`
     - If skill already exists: inform the user the skill is already installed, ask whether they want to **update** it to the latest version, then proceed accordingly

2. **Find the skill**
   - For `skills.sh` source: use the `npx skills find <query>` CLI to search the open ecosystem
   - For other sources: search manually in the configured trusted repositories
   - Search in priority order (skills.sh first)
   - If multiple matching skills found: organize information (name, description, popularity, source) and recommend → wait for user selection
   - If found: obtain the repository URL, clone to `/tmp/skill-downloader/` temporary directory
   - If not found: inform user, suggest alternative sources, wait for user-provided URL

3. **Internal sensitive content check**
   - For skills.sh packages: download to temporary location, don't use `npx skills add` symlink installation
   - After downloading to a temporary location, automatically read all text files to check for sensitive/malicious content:
     - Look for patterns: unauthorized private data collection, secret/credential exfiltration, destructive system commands (rm -rf /, etc.), obfuscated malicious code, crypto-mining scripts
   - If suspicious sensitive/malicious content is detected: delete the download, inform user of the specific issues, stop
   - If no suspicious content is found: proceed to installation
   - If user explicitly requests additional third-party security scan, run:
     ```
     skill-scanner scan the downloaded files
     skill-vetting evaluate the skill
     ```

4. **Install / Update**
   - Create the target directory if it doesn't exist
   - If updating existing skill:
     - Backup old version to target directory with `.bak` suffix (e.g. `skill-name.bak.<timestamp>`)
     - **Preserve skill-generated data**:
       - Keep all non-source files that are not part of the original download (e.g. cached data, user configuration, generated outputs)
       - Only delete/overwrite files that exist in the new downloaded version
       - Do not delete empty directories or directories that contain user data
   - Copy the full source files from temp to target directory (**do NOT use symlinks**)
   - Overwrite only existing source files, leave untouched any additional user/data files
   - Verify the skill structure (ensures SKILL.md exists)
   - If updated: inform user that the update is complete, mention the backup location and that existing user data has been preserved
   - If installed: inform user of successful new installation:
     - Where it was installed
     - How to use it
     - Any additional setup required

5. **Cleanup**
   - Remove temporary download files

6. **Post-installation prompt**
   - After successful installation/update and cleanup, ask the user: "Would you like me to explain the functions and usage of this new skill for you?"
   - If user agrees, read the skill's SKILL.md and summarize the core functions, usage flow and key notes to the user

7. **Done**

## Adding new sources

Users can add new trusted sources by appending to the *Trusted download sources* list above. Maintain the numbered order.

## Examples

**Example 1: Global install**
> User: Download the weather skill globally
- Skill name: `weather`
- Install path: `~/.openclaw/skills/weather`
- Run security checks → install

**Example 2: Local install**
> User: Can you install skill-creator in this workspace
- Skill name: `skill-creator`
- Install path: `./skills/skill-creator`
- Run security checks → install

**Example 3: Not found**
> User: Download my-custom-skill
- Not found in default sources → "I couldn't find 'my-custom-skill' in the default trusted sources. Can you provide a download URL?"

**Example 4: Uncertain request**
> User: Where can I find a good markdown processing skill?
- "You can find skills on https://skills.sh/, https://clawhub.ai/, or https://github.com/anthropics/skills. Would you like me to search for and download a markdown processing skill?"
