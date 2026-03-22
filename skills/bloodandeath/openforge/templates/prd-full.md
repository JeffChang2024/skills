# PRD: <project title>

## Objective
<describe the primary outcome this run should achieve>

## Problem
<describe the current gap, pain, or risk>

## Scope
### In Scope
- <in-scope area 1>
- <in-scope area 2>
- <in-scope area 3>

### Out of Scope
- <out-of-scope area 1>
- <out-of-scope area 2>

## Routing
```yaml routing
aliases:
  scaffold-cloud:
    agent: openforge-cloud
    fallback: openforge-cloud-fallback
    context: 64000
  implementation-local:
    agent: openforge-local
    fallback: openforge-cloud
    context: 16000
  review-review:
    agent: openforge-review
    fallback: openforge-cheap
    context: 64000
```

## Phase: scaffold
```yaml phase:scaffold
stage: 1
executor: scaffold-cloud
validator: "<stage 1 phase validator command>"
validator_timeout: 300
```
- [ ] <describe task here>
  ```yaml task:scaffold-task-1
  id: scaffold-task-1
  reads: [docs/, package.json]
  produces: [src/, tests/]
  ```
- [ ] <describe task here>
  ```yaml task:scaffold-task-2
  id: scaffold-task-2
  reads: [src/, tests/]
  produces: [src/bootstrap.ts, tests/bootstrap.test.ts]
  ```

## Phase: implementation
```yaml phase:implementation
stage: 2
executor: implementation-local
validator: "<stage 2 phase validator command>"
validator_timeout: 600
```
- [ ] <describe task here>
  ```yaml task:implementation-task-1
  id: implementation-task-1
  reads: [src/, docs/spec.md]
  produces: [src/feature.ts, tests/feature.test.ts]
  ```
- [ ] <describe task here>
  ```yaml task:implementation-task-2
  id: implementation-task-2
  reads: [src/feature.ts, tests/feature.test.ts]
  produces: [src/integration.ts, tests/integration.test.ts]
  ```

## Phase: review
```yaml phase:review
stage: 3
executor: review-review
validator: "<stage 3 phase validator command>"
validator_timeout: 300
```
- [ ] <describe task here>
  ```yaml task:review-task-1
  id: review-task-1
  reads: [src/, tests/, docs/]
  produces: [reports/review-findings.md]
  ```

## Stage Validators
```yaml stage-validators
1: "<validate scaffold stage>"
2: "<validate implementation stage>"
3: "<validate review stage>"
```

## Acceptance Criteria
- <describe measurable acceptance criterion 1>
- <describe measurable acceptance criterion 2>
- <describe measurable acceptance criterion 3>
