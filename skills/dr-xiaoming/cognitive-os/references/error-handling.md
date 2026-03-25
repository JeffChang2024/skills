# Error Handling & Self-Correction

## Error Type Handlers

### Tool Failure
- Alternative tool available → switch to alternative
- No alternative → inform user: "Tool X failed, but based on existing info and logic, here's my judgment…"

### Source Conflict
- Do NOT hide — transparently present: "Source A says X, Source B says Y. I lean toward X because…"

### User Intent Shifted
- Abandon original plan immediately
- Update task list
- Confirm new direction with user

### Quality Gate Failed
- Caused by insufficient info → supplementary search
- Caused by logic error → re-reason from scratch
- Then regenerate

### Context Overflow
- Compress with priority retention:
  - **Keep**: Key decision points, core facts, final conclusions
  - **Discard**: Intermediate process, abandoned alternatives, chat noise
