# PRD: Duplicate Block

## Objective
Test duplicate detection.

## Scope
### In Scope
- Item

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
- [ ] Task one
  ```yaml task:task-one
  id: task-one
  produces: [src/a.ts]
  ```

## Phase: setup
```yaml phase:setup
stage: 2
executor: cloud
```
- [ ] Task two
  ```yaml task:task-two
  id: task-two
  produces: [src/b.ts]
  ```
