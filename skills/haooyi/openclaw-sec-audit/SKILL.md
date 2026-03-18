# OpenClaw Security Audit

## Purpose

Run a local security audit against the current OpenClaw installation and runtime environment, then return high-signal risks, impacted locations, and prioritized remediation steps.

## When To Trigger

- The user asks whether the current OpenClaw environment is secure
- The user suspects API key leaks, log leaks, overly broad permissions, or public exposure
- The user wants a locally executable security report

## How To Execute

Use local shell execution to run `resources/run_audit.sh`. The wrapper locates the project root and invokes the local `openclaw-sec audit` CLI.

## Output Requirements

- Never print raw secrets
- Summarize risks, impacted files, priority, and remediation only
- Order remediation steps as `critical -> high -> medium -> low`
- If a host check is unsupported or permission-limited, say `skipped` or `unsupported` explicitly

## Suggested Invocation

```bash
./skills/openclaw-sec-audit/resources/run_audit.sh --format all
```
