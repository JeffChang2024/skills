# Official Repro Guidance

Use this reference when the task needs current official guidance instead of folklore.

## PyTorch reproducibility

Use the PyTorch reproducibility note as the ground truth for deterministic debug loops.

Borrow these rules:

- seed Python, NumPy, and Torch
- set DataLoader worker seeds explicitly
- disable `cudnn.benchmark` during debugging
- use deterministic algorithms only when you need repeatable investigation or regression checks

Source:
- https://docs.pytorch.org/docs/stable/notes/randomness.html

## Albumentations segmentation handling

Use Albumentations guidance whenever masks move with images.

Borrow these rules:

- spatial transforms must hit image and mask together
- image-only transforms must stay image-only
- masks should use nearest-neighbor interpolation
- review transformed previews instead of assuming transform safety

Source:
- https://albumentations.ai/docs/3-basic-usage/semantic-segmentation/

## MLflow tracking

Treat MLflow as the minimum bar for what a serious run should preserve.

Capture at least:

- params
- metrics over time
- artifacts
- environment notes
- run purpose

Source:
- https://mlflow.org/docs/latest/ml/tracking/quickstart/

## DVC pipeline discipline

Use DVC concepts when the repo has many data and training steps but weak provenance.

Borrow these habits even without installing DVC:

- named stages
- declared inputs and outputs
- versioned params and metrics
- experiment comparison from saved artifacts, not memory

Source:
- https://dvc.org/doc/start/data-pipelines/data-pipelines
