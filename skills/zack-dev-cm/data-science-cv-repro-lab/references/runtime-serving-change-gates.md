# Runtime And Serving Change Gates

Use this reference when a CV release changes export format, runtime thresholds, service packaging, or deployment shape rather than core model weights.

## Separate The Three Surfaces

Treat these as distinct checks:

1. Semantic surface
   - checkpoint or model quality on the fixed benchmark set
2. Runtime surface
   - exported model, service latency, memory, warm-start behavior, and health checks
3. Product surface
   - the actual user-facing output, overlay, API payload, or UI state

Do not let a semantic win hide a runtime regression. Do not let a latency win hide a product-surface regression.

## Default Gate Order

1. Smoke the exported artifact locally.
2. Compare runtime or staged-service behavior against the trusted baseline.
3. Run the exact product-surface review for the release surface.
4. Promote only if all required surfaces pass.

## What To Record

- candidate id and baseline id
- exported artifact path or image digest
- runtime environment or service revision
- latency and error-rate summary
- product-surface screenshots or outputs
- rollback target

## Hold Conditions

- staged candidate changes the output format or overlay semantics
- runtime gains require threshold changes that regress the user-facing surface
- service or container health is unstable even when semantic metrics look good
- rollback target is unclear

## Promotion Discipline

- benchmark first
- staged-service check second
- product-surface gate last
- generate one promotion bundle that references all three surfaces before the decision
