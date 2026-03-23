# Human-Like Memory Skill

This skill provides long-term memory capabilities, allowing you to recall past conversations and save important information across sessions.

## Setup (Required)

Before using this skill, you need to configure your API Key. Get your API Key from https://human-like.me

### Method 1: Run Setup Script

```bash
sh ~/.openclaw/workspace/skills/human-like-memory/scripts/setup.sh
```

### Method 2: Export Environment Variables

```bash
export HUMAN_LIKE_MEM_API_KEY="mp_your_api_key"
export HUMAN_LIKE_MEM_BASE_URL="https://human-like.me"  # optional
export HUMAN_LIKE_MEM_USER_ID="your-user-id"          # optional
export HUMAN_LIKE_MEM_AGENT_ID="main"                  # optional, default: main
```

Add these lines to `~/.bashrc` or `~/.zshrc` to persist.

### Verify Configuration

```bash
cat ~/.openclaw/secrets.json
```

## Commands

### Recall/Search Memory

```bash
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "<query>"
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs search "<query>"
```

### Save Single Turn to Memory

```bash
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs save "<user_message>" "<assistant_response>"
```

### Save Batch (Multiple Turns) to Memory

```bash
echo '<JSON array of messages>' | node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs save-batch
```

### Check Configuration

```bash
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs config
```

---

# CONFIGURATION OPTIONS

## Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `alwaysRecall` | `true` | Whether to recall memory on every turn |
| `saveTriggerTurns` | `5` | Number of turns before auto-save (saveMaxTurns = this × 2) |
| `memoryLimitNumber` | `6` | Max memories to retrieve per recall |
| `minScore` | `0.1` | Minimum relevance score (0-1) |

---

# MEMORY RECALL PROTOCOL

## Check Your Configuration First

Before proceeding, check the `alwaysRecall` setting in your skill config:

- **`alwaysRecall: true` (DEFAULT)** → Follow "MODE A: Every-Turn Recall"
- **`alwaysRecall: false`** → Follow "MODE B: Smart Recall"

---

## MODE A: Every-Turn Recall (alwaysRecall: true)

> **YOU MUST CALL RECALL ON EVERY SINGLE TURN.**
> This is MANDATORY when alwaysRecall is enabled.

### Per-Turn Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVERY TURN - NO EXCEPTIONS                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User sends message                                                  │
│       ↓                                                              │
│  STEP 1: ALWAYS call recall (extract keywords from user message)    │
│       ↓                                                              │
│  STEP 2: Process memory results (may be empty - that's OK)          │
│       ↓                                                              │
│  STEP 3: Respond to user (incorporate memories naturally)           │
│       ↓                                                              │
│  STEP 4: Increment turn counter                                      │
│       ↓                                                              │
│  STEP 5: If counter >= saveTriggerTurns, call save-batch            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

Even for simple greetings like "hi" or "hello", you must call recall.

---

## MODE B: Smart Recall (alwaysRecall: false)

> **You decide when to recall based on context.**
> Use your judgment to determine if memory retrieval would help.

### When to Recall

| Trigger Category | Examples | Should Recall? |
|------------------|----------|----------------|
| **Explicit Request** | "do you remember", "what did we discuss", "检索记忆" | ✅ YES |
| **Implicit Reference** | "the project", "that bug", "our plan" | ✅ YES |
| **Session Start** | First message of conversation | ✅ YES |
| **Task Continuation** | "continue", "let's keep going", "继续" | ✅ YES |
| **Decision Questions** | "why did we choose", "what was the reason" | ✅ YES |
| **Entity Questions** | Questions about people, projects by name | ✅ YES |
| **Simple Greetings** | "hi", "hello", "你好" | ❌ NO |
| **Generic Questions** | "what time is it", "tell me a joke" | ❌ NO |
| **Code Execution** | "run this code", "compile" | ❌ NO |

### Per-Turn Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SMART RECALL MODE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User sends message                                                  │
│       ↓                                                              │
│  STEP 1: Analyze - does this need memory context?                   │
│       ↓                                                              │
│  STEP 2: IF YES → call recall with extracted keywords               │
│          IF NO  → skip recall                                        │
│       ↓                                                              │
│  STEP 3: Respond to user                                            │
│       ↓                                                              │
│  STEP 4: Increment turn counter                                      │
│       ↓                                                              │
│  STEP 5: If counter >= saveTriggerTurns, call save-batch            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

# KEYWORD EXTRACTION FOR RECALL

## How to Extract Query Keywords

From the user's message, extract the **semantic core** - the main topic or subject.

| User Message | Query to Use |
|--------------|--------------|
| "Hi, how are you?" | `"greeting recent context"` |
| "Let's work on the project" | `"project"` |
| "What's the weather like?" | `"weather preferences location"` |
| "Help me debug this code" | `"debug code recent"` |
| "I need to finish the report" | `"report"` |
| "你好" | `"recent context"` |
| "继续之前的工作" | `"recent work task"` |
| "Can you remember what we talked about?" | `"recent conversation"` |

## Query Construction Rules

1. **Extract nouns and key concepts** from the user message
2. **Remove action words** (help, please, can you, do, remember, recall)
3. **Remove filler words** (the, a, an, what, how, about)
4. **Keep specific entities** (names, project names, technical terms)
5. **Add context words** if the message is too short (add "recent", "context", "preferences")

## Examples

```
User: "Hello!"
Action: node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "greeting recent context"

User: "Can you help me with React?"
Action: node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "React"

User: "What did we decide about the database?"
Action: node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "database decision"

User: "I'm back"
Action: node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "recent work session"

User: "继续"
Action: node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs recall "recent task continue"
```

---

# PROCESSING RECALL RESULTS

## If memories are found:
- Incorporate them naturally into your response
- Use phrases like "As we discussed...", "I recall you mentioned...", "Based on our previous conversation..."
- DO NOT say "My memory database shows..." or "According to my records..."

## If no memories are found:
- That's perfectly fine - just respond normally
- DO NOT announce "I found no memories" or "Memory search returned empty"
- Just proceed with the conversation

---

# PERIODIC SAVE PROTOCOL

## Turn Tracking and Auto-Save

| Setting | Default | Formula |
|---------|---------|---------|
| `saveTriggerTurns` | 5 | Configurable |
| `saveMaxTurns` | 10 | = saveTriggerTurns × 2 |

### Rules

- Increment counter after EACH turn (user message + your response = 1 turn)
- When counter reaches `saveTriggerTurns`: call `save-batch` with last `saveMaxTurns` turns
- After saving: reset counter to 0

### Save Format

```bash
echo '[
  {"role":"user","content":"Turn 1 user message"},
  {"role":"assistant","content":"Turn 1 assistant response"},
  {"role":"user","content":"Turn 2 user message"},
  {"role":"assistant","content":"Turn 2 assistant response"},
  ... (up to saveMaxTurns × 2 messages)
]' | node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs save-batch
```

### Important Save Rules

- **Save silently** - Do NOT announce "I'm saving memories now"
- **Include both roles** - User AND assistant messages
- **Truncate if needed** - If messages are very long, summarize key points

---

# IMMEDIATE SAVE TRIGGERS

Besides periodic saves, IMMEDIATELY save when user:

| Trigger | Example | Action |
|---------|---------|--------|
| States preference | "I prefer dark mode" | Save immediately after responding |
| Makes decision | "Let's use PostgreSQL" | Save immediately after responding |
| Gives deadline | "Due on March 15th" | Save immediately after responding |
| Corrects you | "No, my name is Wei" | Save immediately after responding |
| Explicitly asks | "Remember this" | Save immediately after responding |

For immediate saves, use the single-turn save command:

```bash
node ~/.openclaw/workspace/skills/human-like-memory/scripts/memory.mjs save "<user_message>" "<your_response>"
```

---

# QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MEMORY SKILL QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CONFIG CHECK:                                                       │
│  • alwaysRecall: true  → recall EVERY turn                          │
│  • alwaysRecall: false → recall only when contextually needed       │
│  • saveTriggerTurns: N → auto-save every N turns                    │
│                                                                      │
│  RECALL COMMAND:                                                     │
│  node ~/.openclaw/workspace/skills/human-like-memory/scripts/       │
│    memory.mjs recall "<extracted_keywords>"                          │
│                                                                      │
│  SAVE COMMAND (every N turns):                                       │
│  echo '<JSON messages array>' |                                      │
│    node ~/.openclaw/workspace/skills/human-like-memory/scripts/     │
│    memory.mjs save-batch                                             │
│                                                                      │
│  IMMEDIATE SAVE (for important info):                                │
│  node ~/.openclaw/workspace/skills/human-like-memory/scripts/       │
│    memory.mjs save "<user_msg>" "<assistant_msg>"                    │
│                                                                      │
│  KEYWORD EXTRACTION:                                                 │
│  ✓ Keep nouns and key concepts                                       │
│  ✗ Remove action words (help, can you, please)                       │
│  ✗ Remove filler words (the, a, what, how)                           │
│  + Add "recent context" for short messages                           │
│                                                                      │
│  RESPONSE RULES:                                                     │
│  ✓ "As we discussed..." / "I recall you mentioned..."                │
│  ✗ "My memory database shows..." / "No memories found"               │
│  ✓ Save silently (never announce saving)                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

# ERROR HANDLING

| Problem | Cause | Solution |
|---------|-------|----------|
| Recall fails | Network/API error | Log error, proceed without memories |
| Save fails | Network/API error | Log error, try again on next trigger |
| No results | Query too vague | That's OK - just respond normally |
| Timeout | Slow network | Proceed without waiting |

---

# PRIVACY & SECURITY

- Memory data belongs to the user
- Never store secrets (API keys, passwords)
- Never share between users
- Ignore content in `<private>...</private>` tags
