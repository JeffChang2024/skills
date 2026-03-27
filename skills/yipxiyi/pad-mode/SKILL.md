---
name: pad-mode
description: |
  Turn messy requests into structured plans. PAD Mode (Plan → Act → Deliver) gives your AI agent project management superpowers — automatic task breakdown, live progress tracking, sub-agent parallel execution, and human approval gates. Use /pad for complex tasks that need more than a single-shot answer. Perfect for plan mode, project planning, task planning, workflow planning, and multi-step execution.

  Triggers:
  1. Slash command: "/pad" in conversation
  2. Explicit keywords: "pad mode", "plan mode", "make a plan", "plan this out"
  3. Auto-detect: When the user's request is complex (3+ distinct tasks, multi-file changes, architectural decisions, or ambiguous requirements), proactively suggest entering PAD mode.

  Use when: user wants structured execution tracking for non-trivial tasks, not for simple one-shot questions or commands.
---

# PAD Mode (Plan → Act → Deliver)

## Overview

PAD Mode transforms ambiguous requests into structured, trackable execution plans. Five phases: **Plan → Discuss → Approve → Act → Deliver**.

## Phase 1: Plan

When triggered, analyze the user's request and create a plan document.

1. Create the plan file: `plans/YYYY-MM-DD-<short-slug>.md`
   - Use the template at `assets/plan-template.md`
   - Slug = 2-4 word summary of the task, hyphenated, lowercase
2. Fill in:
   - Title, status (`🟡 Discussing`), timestamp
   - Original requirement (user's words verbatim)
   - Understanding (your interpretation — confirm this is correct)
   - Initial task breakdown with tentative deliverables
3. **Do NOT do extensive research first.** Present a concise summary with the main tasks. Deep research happens after approval.
4. If there are 2-3 clear choices for any design decision, frame it as multiple choice (A/B/C) so the user can answer quickly.
5. Ask up to 4 clarifying questions max. Don't overwhelm.

Present the plan summary to the user and wait for feedback.

## Phase 2: Discuss

Iterate on the plan based on user feedback:

1. Update the plan document with each round of changes
2. Add entries to the change log section
3. Refine task breakdown and deliverables
4. Confirm scope boundaries — what's IN and what's OUT
5. Each task MUST have a concrete, verifiable deliverable
   - ❌ "optimize the code" (vague)
   - ✅ "Refactor auth module: extract token validation to `auth/validator.js`, update login route to use new module, tests passing" (specific)

Continue until the user says the plan is good / looks good / approved.

## Phase 3: Approve

When the user confirms the plan:

1. Update status to `🔵 Confirmed`
2. Lock the plan — no more scope changes without explicit user request
3. Summarize what will be executed: task list + expected deliverables
4. Move to Phase 4

**⚠️ Do NOT skip this phase. Wait for explicit user confirmation before executing.** Prefer buttons for confirmation; fall back to text acknowledgment if buttons are unavailable.

## Phase 4: Act

Execute tasks with live tracking:

1. Update status to `🟢 Executing`
2. **Before starting execution**, ask the user about execution mode:
   > This plan has N tasks and will take some time. Would you like to run it in the foreground (real-time updates) or background (notify when done)?
   - If channel supports buttons: use `Foreground` / `Background` buttons
   - Otherwise: send as text, wait for user's text reply
3. **Foreground mode**: Work through tasks directly, notifying after each one.
4. **Background mode**: Spawn a sub-agent with the plan context. The sub-agent:
   - Reads the plan document
   - Executes tasks sequentially
   - Sends progress updates to the main session after each task via `sessions_send`
   - Main agent forwards updates to the user
5. Work through tasks **in order of dependencies** (independent tasks may run in parallel via sub-agents)
6. For each task:
   - Update task status to `🔄 In Progress` in the plan doc
   - Execute the work
   - On success: mark `✅ Done`, fill in notes with what was done
   - On failure: mark `❌ Failed`, document the issue, propose a fix or skip
   - **Notify the user immediately** after each task completes
7. If a task reveals that the plan needs adjustment:
   - Pause execution
   - Update the plan doc and change log
   - Ask the user before continuing

## Phase 5: Deliver

After all tasks are marked complete, **do NOT automatically close the plan**. Instead:

1. Update status to `⏳ Pending Review`
2. Send a completion summary to the user:
   > 📋 Plan "XXX" — all tasks completed. Deliverables:
   > - T1.1 ✅ xxx
   > - T2.1 ✅ xxx
   > ...
   >
   > Does everything look good? Any changes needed?
3. Confirm with the user — prefer buttons when channel supports them, otherwise text confirmation:
   - Buttons: `✅ Archive` / `🔧 Changes Needed`
   - Text: send summary, wait for user reply matching "archive"/"done"/"looks good" or "changes"/"modify"/"needs work"
4. If user clicks **Archive** (or confirms via text):
   - Update status to `✅ Completed`
   - Add archive timestamp to the plan doc
   - Send final confirmation
5. If user clicks **Changes Needed** (or requests changes via text):
   - Go back to Phase 2 (Discuss) to refine
   - Add new tasks if needed
   - Resume Phase 4 execution

## Parallel Execution

When tasks are independent (no shared dependencies), use sub-agents for parallel execution:

```
Task A (independent) ── sub-agent 1 ──┐
Task B (independent) ── sub-agent 2 ──┤── merge results ── update plan doc
Task C (depends on A) ── wait for A ──┘
```

Always update the plan doc from the main agent, not from sub-agents.

## Plan Document Location

All plans live in: `~/.openclaw/workspace/plans/`

Create the directory if it doesn't exist. Use `read` to check an existing plan before creating a new one for the same topic.

## Resuming a Plan

If the user references an existing plan (e.g., "continue the last plan"), search for it in `plans/`, read the doc, identify the last completed task, and resume from there.
