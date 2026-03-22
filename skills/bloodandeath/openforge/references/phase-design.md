# Phase Design Reference

> **Audience:** AI agents and developers decomposing work into OpenForge phases and tasks.
> **Goal:** Turn fuzzy project intent into a staged plan that agents can execute without
> stepping on each other, losing context, or hiding failure.

---

## 1. First Principle

A good OpenForge PRD does **not** mirror your org chart or your Jira board.
It mirrors the **dependency graph of safe execution**.

Split work into phases only when the split improves one of these:
- correctness
- validator signal quality
- scope isolation
- model fit
- recovery after failure

If a split does not buy you one of those, it is probably ceremony.

---

## 2. Mental Model

OpenForge has four planning layers:

1. **Objective** — What final outcome matters?
2. **Phase** — A dependency boundary with one executor and one validator policy
3. **Task** — A concrete unit of work inside a phase
4. **Stage** — The execution ordering layer that groups phases by sequence

### 2.1 Phase vs stage

These are related, but not identical.

- **Phase** = named work packet with executor and tasks
- **Stage** = integer ordering key

Multiple phases may share a stage number, but then their output claims must not overlap.
This is useful when you want peer workstreams that can conceptually progress together.

---

## 3. When to Split Phases

Split phases when any of the following is true.

### 3.1 Different executor quality is needed

Example:
- `scaffold` wants a large-context cloud model
- `implementation` can use a cheaper local model
- `review` needs a high-judgment review model

```yaml
phase:scaffold      -> executor: scaffold-cloud
phase:implementation -> executor: impl-local
phase:review        -> executor: review-review
```

That is a clean split because model fit changes by phase.

### 3.2 Validation signal changes materially

If one part is validated by lint/typecheck and another requires integration tests,
split them.

Bad:
- single phase with validator `npm run lint && npm run test && npm run e2e`

Better:
- scaffold → validator `tsc --noEmit`
- implementation → validator `npm test`
- integration → validator `npm run e2e`

Why? Because when it fails, you know *which layer failed*.

### 3.3 Output ownership changes

Split phases when different parts of the repo should be owned separately.

Example:
- `frontend-shell` claims `web/`
- `backend-api` claims `api/`

If both are stage 2 and their claims do not overlap, that is a valid split.

### 3.4 The task needs a checkpoint before continuing

Use a phase boundary when later work becomes expensive unless earlier work is proven sound.

Example:
1. create DB schema
2. validate migrations and ORM models
3. only then build service layer

### 3.5 Human review should happen before proceeding

Even though v1 is sequential and mostly autonomous, phase boundaries are the right place
for manual review pauses or resumable checkpoints.

---

## 4. When *Not* to Split Phases

Do **not** split phases just because:
- there are multiple files involved
- a phase has more than one task
- you want prettier section names
- you are trying to reproduce team ownership boundaries in documentation

Bad over-splitting example:
- `create-types`
- `create-controller`
- `create-tests`
- `wire-routes`

If all four use the same executor, same validator, and same code area, that is probably
one implementation phase with four tasks.

---

## 5. Stage Ordering Rules

Stage numbers are integers `>= 1`.
OpenForge executes lower stages before higher stages.

### 5.1 Recommended ordering pattern

For most software projects:
- Stage 1 → scaffold / groundwork
- Stage 2 → implementation
- Stage 3 → integration / polish
- Stage 4 → review / audit

You do **not** need contiguous numbers, but use them anyway. Human readability matters.

### 5.2 Same-stage multi-phase rules

If multiple phases share the same stage:
- every task in those phases must declare `produces`
- `produces` claims must not overlap across same-stage phases
- validators should be independent or cheap enough to isolate failures cleanly

Good:

```yaml
## Phase: frontend-shell
stage: 2
produces: web/

## Phase: backend-api
stage: 2
produces: api/
```

Bad:

```yaml
## Phase: ui
stage: 2
produces: src/

## Phase: api
stage: 2
produces: src/server/
```

That overlaps and validation will fail.

### 5.3 Cross-stage overlap is allowed

This is important.
A later stage may modify files created by an earlier stage.

Example:
- Stage 1 scaffold creates `src/routes.ts`
- Stage 2 implementation updates `src/routes.ts`
- Stage 3 review reads it and writes `reports/review.md`

That is normal.

---

## 6. Choosing Executors Per Phase

OpenForge phase design works best when executor choice is intentional.

### 6.1 Scaffold phases

Use when:
- project structure is incomplete
- conventions need to be established
- many files need to be created coherently

Preferred executor:
- `cloud` for new systems or broad repo changes
- `local` only if the scaffold pattern is very familiar and repetitive

Prompt tier goal:
- broad context
- strong convention-following
- fewer weird omissions

### 6.2 Implementation phases

Use when:
- the structure already exists
- tasks are bounded and file-local enough to be surgical

Preferred executor:
- `local` first for cost control
- fallback to `cloud` for harder tasks or repeated failures

Prompt tier goal:
- minimal drift
- direct code changes
- narrow `produces`

### 6.3 Review phases

Use when:
- you want findings, not code
- you need critique, not generation
- the deliverable is a report or checklist

Preferred executor:
- `review`
- optional fallback to `cheap` only for lightweight audits or low-stakes triage

Prompt tier goal:
- explicit non-coding behavior
- surface risks and missing edge cases

### 6.4 Cheap support phases

Use when:
- a task is extraction, inventory, summarization, or classification
- paying cloud/review rates would be wasteful

Examples:
- enumerate TODO markers
- summarize API endpoints
- list test files missing coverage
- extract migration names from a directory

---

## 7. Task Design Inside a Phase

Tasks are where most PRDs quietly succeed or fail.

### 7.1 Good task properties

A good task is:
- concrete
- verifiable
- narrow in file ownership
- independent enough to retry cleanly
- obvious about what changed if it fails

Bad task text:
- "Improve auth"

Better:
- "Implement JWT verification middleware and add unit tests for invalid, expired, and valid tokens"

### 7.2 Task count guideline

A practical target:
- **1–5 tasks per phase** for most repos

More than 5 tasks often means:
- the phase is too broad
- the decomposition is too fine-grained
- validation will be muddy

### 7.3 Reads vs produces discipline

`reads` should include only what the agent truly needs.
`produces` should include every file or subtree it may legitimately change.

Good:

```yaml
reads: [src/auth/, docs/jwt-spec.md]
produces: [src/middleware/jwt.ts, tests/middleware/jwt.test.ts]
```

Bad:

```yaml
reads: [src/]
produces: [src/]
```

That is legal, but lazy. Broad claims reduce scope protection and increase prompt noise.

### 7.4 Checklist text matters

Remember that the Markdown checklist line becomes part of the task prompt.
The YAML block does not replace it; it complements it.

Write task text like an instruction, not a title fragment.

Bad:
- [ ] Auth middleware

Better:
- [ ] Implement JWT auth middleware and reject malformed, expired, and wrong-audience tokens

---

## 8. Validator Design

Validators are the enforcement layer that turns “looks plausible” into “actually works.”

### 8.1 Per-phase validators

Use phase validators for checks tightly coupled to that phase’s output.

Examples:
- scaffold → `tsc --noEmit`
- backend implementation → `pytest tests/api/test_auth.py`
- frontend implementation → `pnpm vitest src/components/LoginForm.test.tsx`

### 8.2 Stage validators

Use stage validators for broader guarantees once all phases in a stage complete.

Examples:
- stage 2 → `npm test`
- stage 3 → `npm run e2e`
- stage 4 → `python scripts/check_release_readiness.py`

### 8.3 Good validator properties

A good validator is:
- deterministic
- local to the repo
- fast enough to run repeatedly
- specific enough to identify what failed
- low-side-effect or side-effect-free

### 8.4 Anti-pattern validator examples

Avoid validators that:
- deploy to production
- mutate remote systems
- seed databases in non-disposable environments
- depend on fragile external services unless that is the point of the stage

Bad:

```yaml
validator: "npm run deploy"
```

Better:

```yaml
validator: "npm run build && npm run test"
```

### 8.5 Timeout tuning

Use higher `validator_timeout` for:
- integration suites
- end-to-end tests
- language toolchains with long cold starts

Use lower timeouts for:
- lint
- typecheck
- formatting checks

Examples:

```yaml
validator: "ruff check ."
validator_timeout: 60
```

```yaml
validator: "npm run e2e"
validator_timeout: 900
```

---

## 9. Common Phase Patterns

### 9.1 Scaffold → Implement → Review

This is the default pattern for most product changes.

**Stage 1: scaffold**
- create directories, interfaces, base wiring
- validate compilation or structure

**Stage 2: implement**
- add behavior, tests, edge handling
- validate with focused test suite

**Stage 3: review**
- produce findings report
- optional manual checkpoint before fixes

Use this when the feature is new and architecture matters.

### 9.2 Frontend → Backend → Integration

Use when UX and API are distinct but eventually must meet.

**Stage 1: backend-foundation**
- schema, routes, handlers, unit tests

**Stage 2: frontend-shell**
- components, view state, client hooks

**Stage 3: integration**
- end-to-end wiring, API contracts, user flows

Good when you can keep `web/` and `api/` ownership separate early, then bind later.

### 9.3 Schema → Service → API

Useful for data-centric systems.

**Stage 1: schema**
- migrations, models, generated types

**Stage 2: service**
- business logic, transactions, guards

**Stage 3: api**
- handlers, serialization, request validation

This sequence avoids API code being built against unstable storage structures.

### 9.4 Triage → Remediation → Review

Use for quality or security work.

**Stage 1: triage-cheap**
- inventory findings or hotspots

**Stage 2: remediation**
- patch specific issues

**Stage 3: review-review**
- verify the fixes and remaining risks

### 9.5 Review-only PRD

Sometimes you should not implement anything at all.
Use a single review phase when the goal is assessment.

Example outputs:
- `reports/security-audit.md`
- `reports/perf-findings.md`
- `reports/migration-readiness.md`

This pattern is already represented in `templates/prd-review-only.md`.

---

## 10. Anti-Patterns to Avoid

### 10.1 The giant everything phase

```yaml
## Phase: do-all-the-things
stage: 1
executor: cloud
validator: "npm run lint && npm test && npm run e2e"
```

Why it fails:
- too much context
- unclear failure source
- hard to resume intelligently
- expensive retries

### 10.2 The microscopic phase explosion

Ten tiny phases each with one trivial task and the same executor/validator is not design.
It is paperwork.

### 10.3 Broad lazy path claims

```yaml
produces: [src/, tests/, docs/]
```

If the task only touches one middleware and one test, claim those files instead.
Broad claims weaken security and make no-op detection less informative.

### 10.4 Review phase that secretly codes

If your review task says “evaluate correctness” but `produces` includes `src/`, you are
mixing roles. Review phases should usually produce reports, not implementation.

### 10.5 Validator mismatch

Do not validate scaffold with an end-to-end suite unless the scaffold is supposed to produce
a running product. Match validator scope to phase responsibility.

### 10.6 Cross-cutting task text with narrow path claims

Bad:

```yaml
- [ ] Refactor the authentication architecture across the application
  produces: [src/auth.ts]
```

The text promises a broad change; the claims allow a tiny one. That mismatch almost
invites scope violations.

### 10.7 Hidden dependency ordering

If task B depends on files from task A, but both sit in separate same-stage phases with no
validator/checkpoint between them, you have encoded an unstated dependency.
Split into later stage or one phase.

---

## 11. Example Decomposition Walkthrough

Suppose the objective is: **add tenant-aware API rate limiting**.

### Weak decomposition

```markdown
## Phase: implementation
stage: 1
executor: impl-local
- [ ] Add rate limiting everywhere
```

This is too vague. It hides data design, middleware behavior, config shape, and testing.

### Better decomposition

```markdown
## Phase: scaffold
```yaml phase:scaffold
stage: 1
executor: scaffold-cloud
validator: "npm run lint && tsc --noEmit"
```
- [ ] Define rate-limit config types and middleware entry point
  ```yaml task:scaffold-rate-limit
  id: scaffold-rate-limit
  reads: [src/config/, src/middleware/]
  produces: [src/config/rateLimit.ts, src/middleware/rateLimit.ts]
  ```

## Phase: implementation
```yaml phase:implementation
stage: 2
executor: impl-local
validator: "npm test -- rateLimit"
validator_timeout: 300
```
- [ ] Implement tenant-aware token bucket logic and unit tests
  ```yaml task:impl-token-bucket
  id: impl-token-bucket
  reads: [src/config/rateLimit.ts, src/middleware/rateLimit.ts]
  produces: [src/services/rateLimiter.ts, tests/services/rateLimiter.test.ts]
  ```
- [ ] Wire middleware into API routes and add integration tests
  ```yaml task:impl-wire-rate-limit
  id: impl-wire-rate-limit
  reads: [src/middleware/rateLimit.ts, src/routes/, src/services/rateLimiter.ts]
  produces: [src/middleware/rateLimit.ts, src/routes/api.ts,
             tests/integration/rateLimit.test.ts]
  ```

## Phase: review
```yaml phase:review
stage: 3
executor: review-review
```
- [ ] Review rate limiting for tenant bypasses and denial-of-service edge cases
  ```yaml task:review-rate-limit
  id: review-rate-limit
  reads: [src/, tests/]
  produces: [reports/rate-limit-review.md]
  ```
```

Why this works:
- scaffold establishes shape first
- implementation is concrete and testable
- review is evaluative and report-based
- validators align with phase responsibility

---

## 12. Design Heuristics You Can Reuse

When drafting a phase plan, ask:

1. **Does this phase have one clear job?**
2. **Would one validator meaningfully tell me if it succeeded?**
3. **Is the chosen executor actually the best model tier for this kind of work?**
4. **Are the produced paths narrow enough to enforce scope?**
5. **If this phase fails three times, will I know what to change?**
6. **Could a later stage safely depend on this output?**
7. **Am I splitting because of real dependency boundaries, or just aesthetics?**

If several answers are weak, redesign the phase layout before running.

---

## 13. Recommended Defaults

If you do not know how to decompose a normal feature PRD, start here:

- **Phase 1: scaffold**
  - executor: cloud
  - validator: lint/typecheck
- **Phase 2: implementation**
  - executor: local with cloud fallback
  - validator: focused tests
- **Phase 3: review**
  - executor: review
  - output: findings report

That pattern is not always optimal, but it is a reliable baseline.
