# Public Safety

Use this reference before sharing or publishing SOTA-agent artifacts.

## What must not ship

- secrets, tokens, API keys, cookies, passwords
- private datasets, hidden benchmark ids, or customer names
- internal experiment URLs
- raw notebook links
- raw CDP URLs, websocket endpoints, or browser profile names
- absolute local filesystem paths
- private model registry locations
- unpublished paper PDFs or copyrighted attachments you do not have the right to redistribute

## Public-safe defaults

- keep artifact references sanitized by default
- prefer benchmark ids over local paths
- prefer paper titles and public URLs over private folders or local PDF paths
- prefer summary tables over raw debug dumps

## Review checklist

1. Search for secrets and secret-shaped env vars.
2. Search for absolute paths and raw notebook URLs.
3. Search for customer names, dataset slugs, or hidden benchmark identifiers.
4. Confirm the promoted score is tied to the right benchmark and not to an internal-only evaluation surface.
5. Review the changelog and summary text for private names or infra terms.

## Practical audit commands

```bash
rg -n "/Users/|/home/|localhost|127\\.0\\.0\\.1|token|api[_-]?key|secret|password|cookie|ws://|wss://" ./skill/sota-agent
python3 -m py_compile ./skill/sota-agent/scripts/*.py
```
