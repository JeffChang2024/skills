# Agentic Research Patterns

Use this reference when the task is bigger than one training run and needs a research loop, not only a script.

## `autoresearch` Patterns Worth Reusing

The useful idea from `karpathy/autoresearch` is not "let the agent wander". It is controlled decomposition:

- one topic per workspace
- separate planning from searching
- separate searching from writing
- preserve a journal so later turns can resume from evidence instead of memory
- add a reviewer pass before accepting the final result

Source:
- https://github.com/karpathy/autoresearch

## CV Adaptation

Map those ideas onto DS and CV work like this:

### Role split

Even in a single-agent workflow, keep these roles conceptually separate:

- planner
- executor
- reviewer
- promoter

That separation prevents one bad run from turning straight into a promotion decision.

### Topic file

Write the product question, benchmark set, and promotion gate before experimentation starts.

### Plan directory

Keep a short plan with:

- hypothesis
- expected win surface
- expected failure mode
- stop condition

### Search and read equivalents

For CV, "search" usually means:

- inspecting repo scripts
- locating previous run cards
- checking dataset manifests
- comparing checkpoints
- finding prior benchmark artifacts

For browser tasks, include:

- target URL
- browser profile alias
- browser session alias
- required attachments
- success marker
- artifact pull list

### Collection layer

Preserve machine-readable evidence:

- dataset manifests
- metrics CSV or JSON
- screenshots
- preview grids
- benchmark snapshots
- browser run cards
- run summaries
- run cards

### Review layer

Require a review pass before promotion:

- did the candidate beat the baseline on the same cases
- did the browser lane actually run, or only partially attach
- did the long run stay healthy
- did the downstream render or service keep parity

## Minimum Folder Shape

For a non-trivial CV investigation, create:

- `README.md`
- `research.md`
- `plan.md`
- `journal.md`
- `evidence.md`
- `promotion.md`

Use the bundled scaffold script when you want this structure quickly.

## Run Card Pattern

For every serious candidate, keep one machine-readable run card that joins:

- dataset identity
- source commits
- browser lane state
- training lane state
- benchmark outputs
- decision

The bundled `init_cv_run_card.py` script gives a starting schema for that file.

When browser execution matters, pair it with:

- `init_cv_browser_run_card.py` for notebook or browser evidence
- `init_cv_dataset_manifest.py` for the shared dataset identity
- `render_cv_run_summary.py` for the markdown summary derived from the run card
- `init_cv_artifact_manifest.py` for the export bundle contents
- `init_cv_vm_bootstrap_manifest.py` for long-run VM launch metadata
