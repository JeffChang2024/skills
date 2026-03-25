# OpenClaw Browser Lane

Use this reference when the workflow depends on a real browser session for Colab, Kaggle, Gemini, ChatGPT, or another notebook-like UI.

## The Reliable Pattern

1. Start or validate the gateway.
2. Start the browser profile and wait for a usable CDP endpoint.
3. Attach with Playwright over CDP.
4. Select the right page by URL, not by tab order.
5. Create a bounded notebook action:
   - inject a temporary cell
   - run until a marker or timeout
   - pull artifacts locally
   - delete the temporary cell if possible
6. Save screenshots and machine-readable outputs.
7. Fail hard if the session is not actually attached or the requested mode is unavailable.

## What To Preserve

- browser profile alias
- sanitized session alias plus attach result
- target URL
- requested mode and actual mode
- screenshots
- output JSON or CSV
- local artifact paths
- timeout used
- browser run card path

## Sanitization Boundary

Keep raw CDP URLs, websocket endpoints, and private profile names out of durable public-facing artifacts.

If a local debug session needs that information, keep it in ephemeral scratch logs only. The durable record should preserve aliases, attach state, screenshots, artifacts, and the final outcome.

## Failure Modes Seen In Practice

- gateway healthy but browser attach fails
- websocket connects but CDP actions time out
- notebook page exists but `window.colab` internals are not ready
- browser LLM page loads but the requested model or mode is unavailable
- long browser jobs hang without a clear completion signal

## Guardrails

- never assume a page is ready because it is visible
- use a URL match and explicit readiness probe
- use a hard timeout for every long browser action
- use a success marker in notebook output when possible
- prefer downloading artifacts through the notebook proxy over screenshot-only evidence
- if a model selector like Gemini Pro is unavailable, stop and record that explicitly

## Colab and Notebook-Specific Tactics

- smoke-test with a short run before a full training launch
- set the accelerator explicitly when the runtime type matters
- check notebook idleness before injecting a new cell
- collect the final training artifacts back to local disk
- capture at least two screenshots when human review depends on the browser lane

## Role In The Decision Stack

Browser automation is a hypothesis or execution lane. It is not the promotion authority.

Promotion should still depend on local or synced artifacts:

- benchmark snapshots
- evaluation summaries
- run cards
- side-by-side visual boards
