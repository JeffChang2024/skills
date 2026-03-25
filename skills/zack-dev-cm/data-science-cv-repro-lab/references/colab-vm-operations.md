# Colab And VM Operations

Use this reference when the workflow depends on Google Colab GPUs or a custom GPU VM.

## Google Colab GPU Management

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

### Colab artifact discipline

Keep one export root such as:

- `/content/export`
- `/kaggle/working/export`

The bundled `init_cv_artifact_manifest.py` helper can create `artifact_manifest.json` for that export root.

Write at least:

- `dataset_manifest.json`
- `run_context.json`
- `browser_run_card.json` when a browser lane was used
- `artifact_manifest.json`
- `metrics.csv` or `metrics.json`
- `train_strategy.json`
- one preview image
- one final checkpoint or checkpoint pointer

### Colab browser evidence

When browser automation is part of the task, preserve:

- runtime type selected
- notebook URL
- sanitized browser alias
- screenshots
- marker or completion signal
- local artifact pull results

### Colab decision rule

Do not let a successful browser run stand in for a successful model run.

A Colab pass is only complete when:

- the runtime was correct
- the smoke cell passed
- the export bundle exists
- the bundle was pulled locally
- the candidate was added to the run card

## Custom GPU VM Management

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

The bundled `init_cv_vm_bootstrap_manifest.py` helper provides a starting schema for that file.

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

### Artifact sync

Do not leave the only copy of a useful candidate on the VM.

Sync back:

- dataset manifest
- candidate run card
- rendered run summary
- summary json
- history csv
- checkpoint path or exported model
- benchmark snapshot
- preview boards

### VM decision rule

Do not promote directly from live VM state.

Promotion should happen only after the synced artifacts have been reviewed locally or from a trusted artifact store.

### Shutdown

When the work is complete:

- stop the training session
- flush remaining artifacts
- stop the VM automatically if policy allows
- record the final state in the run card
