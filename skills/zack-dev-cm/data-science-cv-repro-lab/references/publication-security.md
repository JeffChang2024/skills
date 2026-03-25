# Publication Security

Use this reference before publishing the skill to OpenClaw or ClawHub.

## ClawHub fact

ClawHub is public. Published skills and their `SKILL.md` content are visible to everyone.

Source:
- https://docs.openclaw.ai/tools/clawhub

## What must not ship

- secrets, tokens, API keys, passwords
- private browser profile names
- raw CDP URLs or websocket endpoints
- private notebook URLs
- internal hostnames or VM names
- absolute local filesystem paths
- private dataset slugs or customer identifiers
- GitHub topics, ClawHub tags, changelog text, or release notes that expose customer names or private infra terms
- command examples that embed credentials in flags

## OpenClaw-specific safety rules

- Keep secrets out of prompts and logs.
- Treat third-party skills as untrusted code.
- Prefer sandboxed runs for risky tools.
- Keep skill config secrets in `skills.entries.*.env` or `apiKey`, not in the skill files.

Source:
- https://docs.openclaw.ai/tools/skills

## Review checklist

1. Search for absolute paths.
2. Search for usernames, profile names, and internal URLs.
3. Search for notebook ids and dataset ids that are not intended to be public.
4. Search for raw CDP URLs, websocket endpoints, and browser attach dumps.
5. Search for token-like strings and secret-shaped env vars.
6. Ensure bundled scripts do not combine env harvesting with network exfiltration.
7. Ensure the skill uses `{baseDir}` for bundled file references.
8. Review publish metadata, tags, topics, and changelog text for internal names or customer terms.
9. If private specialization is still needed, keep it in a local override skill instead of the public bundle.

## Practical review step

Use your local audit tooling to scan for absolute paths, localhost URLs, websocket endpoints, tokens, and secret-shaped strings before publishing.
