# PRD: Multi Stage Test

## Objective
Test multi-stage parsing.

## Scope
### In Scope
- Feature A

## Routing
```yaml routing
aliases:
  local:
    agent: openforge-local
    fallback: openforge-cloud
    context: 8192
  cloud:
    agent: openforge-cloud
```

## Phase: scaffold
```yaml phase:scaffold
stage: 1
executor: cloud
validator: "echo ok"
```
- [ ] Setup project
  ```yaml task:setup-project
  id: setup-project
  produces: [src/]
  ```

## Phase: implement
```yaml phase:implement
stage: 2
executor: local
validator: "npm test"
```
- [ ] Build feature
  ```yaml task:build-feature
  id: build-feature
  reads: [src/]
  produces: [src/feature.ts, tests/feature.test.ts]
  ```

## Stage Validators
```yaml stage-validators
1: "echo stage1"
2: "npm test"
```

## Acceptance Criteria
- Tests pass
