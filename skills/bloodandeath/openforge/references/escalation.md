# Escalation & Failure Recovery

## Failure Classes

| Class | Detection | Recovery |
|-------|-----------|----------|
| **Timeout** | Agent exceeds `--task-timeout` (default 600s) | Retryable → escalation |
| **Transport Error** | `openclaw agent` exits non-zero | Retryable → escalation |
| **No-Op** | Agent exits 0 but no files changed in `produces:` scope | Retryable with reflexion hint |
| **Scope Violation** | Modified files outside declared `produces:` | **Terminal** → `halted_security` |
| **Validator Failure** | Phase validator exits non-zero after task | Retryable → escalation |
| **Secret Detected** | Secret pattern in prompt content or artifacts | **Terminal** → `halted_security` |
| **Partial Write** | Agent crashed mid-execution (detected on resume) | Inspects worktree, doesn't blindly re-run |

## The Escalation Cascade

Each task gets up to 5 attempts (configurable via `--max-escalation`):

```
Attempt 1: primary agent
Attempt 2: primary agent + reflexion hint
Attempt 3: fallback agent (if defined)
Attempt 4: fallback agent + reflexion hint
Attempt 5: HALT → halted_escalation
```

If no fallback is defined in the routing table, attempts 3-4 are skipped — max 3 effective attempts.

The cascade **resets per task**. Task A exhausting its cascade doesn't affect Task B.

## Reflexion Hints

On retry attempts (2 and 4), a reflexion suffix is appended to the prompt:

```
IMPORTANT — PRIOR ATTEMPT FAILED:
Failure type: no_op
Details: retry attempt 2
Validator output: npm test exited with code 1

You MUST try a fundamentally different approach. Do not repeat what failed.
```

This forces the model to try a different strategy instead of repeating the same mistake.

## Terminal States

These states have **no outbound transitions**. The run halts.

| State | Cause | Resolution |
|-------|-------|-----------|
| `halted_escalation` | All attempts exhausted | Review task, simplify, or change executor |
| `halted_security` | Scope violation or secret detected | Investigate violation, fix PRD claims |
| `halted_manual` | Requires human intervention | Manual fix, then `openforge resume --force` |

## Tuning Escalation

**For cost control:**
```bash
openforge run --prd prd.md --max-escalation 3 --cwd .
```
Prevents local tasks from burning cloud tokens.

**For reliability:**
```bash
openforge run --prd prd.md --max-escalation 7 --cwd .
```
More attempts before giving up. Useful for flaky environments.

**Force a single executor (debugging):**
```bash
openforge run --prd prd.md --force-executor cloud --cwd .
```
Bypasses routing table. All tasks go to one executor.

## Validator Failure Propagation

Phase validators run **after all tasks in a phase complete** (not per-task).

When a phase validator fails:
1. Phase status → "failed"
2. Last completed task in the phase → `validation_failed`
3. That task enters the escalation cascade (re-dispatched with validator error context)
4. After re-completion, the phase validator runs again
5. If all attempts exhausted → `halted_escalation`

Stage validators work similarly, but attribute failure to the last completed task across all phases in the stage.
