# Colab And VM Operations

Use this reference when the SOTA workflow depends on Google Colab GPUs, Kaggle notebooks, or a custom GPU VM.

## Google Colab and notebook GPU management

### Required operating pattern

1. Open the target notebook through a stable URL.
2. Select the accelerator explicitly.
3. Run a smoke cell before any expensive training.
4. Export artifacts to one stable directory.
5. Pull the artifact manifest and previews back locally.

### Colab smoke checklist

Before a long run, verify from inside the notebook:

- Python version
- GPU presence
- CUDA visibility to the framework
- dataset mount or download success
- write access to the export directory

Minimum smoke checks:

- `nvidia-smi`
- `torch.cuda.is_available()` or framework equivalent
- one tiny batch through the dataloader
- one tiny forward pass

### Artifact discipline

Keep one export root such as:

- `/content/export`
- `/kaggle/working/export`

Write at least:

- campaign or program json
- candidate or candidate-card json
- browser run card when a GUI lane was used
- artifact manifest
- metrics CSV or JSON
- one preview image
- one final checkpoint or checkpoint pointer

### Decision rule

Do not let a successful browser run stand in for a successful model run.

A notebook pass is only complete when:

- the runtime was correct
- the smoke cell passed
- the export bundle exists
- the bundle was pulled locally
- the candidate was added to the program evidence

## Custom GPU VM management

### Bootstrap

Every long-run VM job should start with a machine-readable bootstrap manifest:

- git commit
- dataset id plus manifest hash
- command line
- output root
- model family
- threshold or loss settings
- GPU type
- start time

### Liveness

Do not rely on PID existence alone.

Use at least one of:

- heartbeat file
- session json
- tmux session plus heartbeat
- supervisor status
- epoch-progress polling

### Health policy

Track:

- epoch progression
- best metric so far
- GPU utilization
- GPU memory
- heartbeat age
- log freshness

A healthy long run should have explicit stall and failure rules.

### Recovery

When a run goes unhealthy, the workflow should define one of:

- kill and relaunch
- kill and fall back to a tiny debug run
- sync artifacts and stop the VM
- hold the VM for human review

### Promotion rule

Do not promote directly from live VM state.

Promotion should happen only after the synced artifacts have been reviewed locally or from a trusted artifact store.
