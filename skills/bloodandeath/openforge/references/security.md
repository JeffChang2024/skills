# Security Model

## Threat Model

OpenForge v1 operates in a **trusted PRD author** threat model. The person writing the PRD is assumed non-malicious.

### What v1 Protects Against

- **Accidental scope creep** — agents writing files outside their declared `produces:` paths
- **Accidental secret leakage** — API keys, tokens, private keys in prompts or artifacts
- **Agent-produced output** outside intended file scope

### What v1 Does NOT Protect Against

- **Malicious PRDs** — a deliberately adversarial PRD can craft harmful validators or prompts
- **Determined prompt injection** — adversarial content in repo files that manipulates agent behavior
- **OS-level sandbox escape** — agents run with user permissions, not in containers
- **Binary/encoded secrets** — only regex-based text patterns are detected

This is stated honestly. We don't claim stronger isolation than exists.

## Path Confinement

### How It Works

1. **Parse time:** All `reads:` and `produces:` paths normalized and checked:
   - Must be relative to `--cwd`
   - No absolute paths → parse error
   - No `..` above `--cwd` → parse error
   - Overlap detection for same-stage phases

2. **Runtime:** After each task completes, `git diff --name-only` is compared against declared `produces:` claims:
   - Every modified path must fall within a declared claim
   - Undeclared modification → `halted_security`
   - Paths resolved with `os.path.realpath()` and checked against `--cwd`

3. **Symlinks:** Not followed if they resolve outside `--cwd`

4. **Git submodules:** Out of scope unless `produces:` explicitly references them

5. **`.git/` directory:** Always excluded

### What It Catches

- Agent modifying `package.json` when only `src/auth/` was declared
- Agent creating files in unrelated directories
- Path traversal attempts via symlinks

### What It Doesn't Catch

- Agent reading sensitive files not in `reads:` (reads aren't enforced, only recommended)
- Rename operations where the source isn't in scope
- Changes made via external processes spawned by the agent

## Secret Scanning

### When Scanning Happens

Secret scanning now occurs **before prompts are dispatched to agents**, not only when saving artifacts. This prevents accidental secret leakage into model context windows.

**Stage 1 — Secret file pattern check (before reading):**
If a `reads:` path matches a secret file pattern, the file is never read. The prompt includes `[REDACTED: matches secret file pattern]` instead.

**Stage 2 — Content redaction (before prompt inclusion):**
All file contents that pass the filename check are scanned with regex patterns and secrets are replaced with `[REDACTED]` before being assembled into the prompt.

**Stage 3 — Final assembled prompt scan (safety net):**
After all sections are assembled, `redact_secrets()` is applied to the complete prompt as a last-pass safety net.

**Git log redaction:**
Git log output included via `_git_context()` is also passed through `redact_secrets()` before inclusion.

### File Ignore Patterns

These file patterns are never read into prompts:

```
.env*  *.pem  *.key  *.p12  *.keystore  *credential*  *secret*
```

If a `reads:` path matches, file content is replaced with `[REDACTED: matches secret file pattern]`.

### Content Patterns

Regex scan on all file content before prompt inclusion:

- API key assignments (`api_key = ...`, `apikey: ...`)
- Token/password assignments
- Private key headers (`-----BEGIN ... PRIVATE KEY-----`)
- Bearer tokens (`Bearer ey...`)
- GitHub tokens (`ghp_...`, `gho_...`)
- OpenAI keys (`sk-...`)
- AWS access keys (`AKIA...`)

### Redaction of Saved Artifacts

- `prompt.md`, `response.md`, `diff.patch` scanned before writing to disk
- `events.jsonl` contains metadata only — never prompt content or responses
- `validator.log` scanned post-capture (best-effort)

### Honest Limits

- Novel secret formats won't be caught
- Base64-encoded or binary secrets are invisible to regex
- `.env.example` may trigger false positives
- Configurable via `.openforgeconfig` ignore patterns

## Validator Execution

### Environment Sanitization

Validators run as subprocesses with a sanitized environment. Only these variables pass through:

```
PATH  HOME  LANG  LC_ALL  LC_CTYPE  PWD  PYTHONPATH  TMPDIR
```

Dangerous prefixes are stripped: `AWS_`, `AZURE_`, `OPENAI_`, `ANTHROPIC_`, `GITHUB_`, `SECRET`, `PASSWORD`, `TOKEN`, `KEY`.

### Execution Model

- `subprocess.run(shell=True, cwd=<project>)`
- `stdin` closed (no interactive input)
- Timeout enforced (default 300s per validator)
- stdout + stderr captured to log files

### Honest Limits

- No process isolation beyond subprocess boundaries
- No network restriction enforcement in v1 (advisory flag only)
- Validators can read any file within `--cwd`
- Validator commands come from the PRD — trusted author model applies

## Prompt Injection Mitigation

- Repo file content is included as clearly delimited data sections, not instruction text
- Task descriptions from PRD are trusted (PRD author is the trust boundary)
- Agent responses are treated as untrusted data — not re-injected as instructions in v1
- Review findings (v1.1) will be validated against Pydantic schema before reuse
