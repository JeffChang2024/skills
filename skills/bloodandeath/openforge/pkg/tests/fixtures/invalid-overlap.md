# PRD: Overlap Test

## Objective
Test overlap detection.

## Scope
### In Scope
- Item

## Routing
```yaml routing
aliases:
  cloud:
    agent: openforge-cloud
  local:
    agent: openforge-local
```

## Phase: alpha
```yaml phase:alpha
stage: 1
executor: cloud
```
- [ ] Write files
  ```yaml task:write-files
  id: write-files
  produces: [src/auth/]
  ```

## Phase: beta
```yaml phase:beta
stage: 1
executor: local
```
- [ ] More files
  ```yaml task:more-files
  id: more-files
  produces: [src/auth/models/user.ts]
  ```
