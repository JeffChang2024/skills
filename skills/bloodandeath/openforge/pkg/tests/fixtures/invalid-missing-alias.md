# PRD: Missing Alias

## Objective
Test missing alias detection.

## Scope
### In Scope
- Item

## Routing
```yaml routing
aliases:
  cloud:
    agent: openforge-cloud
```

## Phase: broken
```yaml phase:broken
stage: 1
executor: local
```
- [ ] Some task
  ```yaml task:some-task
  id: some-task
  produces: [src/a.ts]
  ```
