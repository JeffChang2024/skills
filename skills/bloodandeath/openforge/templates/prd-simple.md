# PRD: Simple Test

## Objective
Test basic parsing.

## Scope
### In Scope
- Item one

## Routing
```yaml routing
aliases:
  cloud:
    agent: openforge-cloud
```

## Phase: setup
```yaml phase:setup
stage: 1
executor: cloud
```
- [ ] First task
  ```yaml task:first-task
  id: first-task
  produces: [src/a.ts]
  ```
- [ ] Second task
  ```yaml task:second-task
  id: second-task
  produces: [src/b.ts]
  ```
