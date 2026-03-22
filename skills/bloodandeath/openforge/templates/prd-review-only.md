# PRD: <review title>

## Objective
<describe the review objective>

## Problem
<describe why this review is needed>

## Scope
### In Scope
- <paths or systems to review>

### Out of Scope
- <paths or systems not to review>

## Routing
```yaml routing
aliases:
  review-review:
    agent: openforge-review
    fallback: openforge-cheap
    context: 64000
```

## Phase: review
```yaml phase:review
stage: 1
executor: review-review
validator: "<optional review validator command>"
validator_timeout: 300
```
- [ ] <describe task here>
  ```yaml task:review-existing-code
  id: review-existing-code
  reads: [src/, tests/, docs/]
  produces: [reports/review-findings.md]
  ```

## Stage Validators
```yaml stage-validators
1: "<optional stage validator command>"
```

## Acceptance Criteria
- <review findings are written to the declared report path>
- <all critical issues found in scope are documented>
