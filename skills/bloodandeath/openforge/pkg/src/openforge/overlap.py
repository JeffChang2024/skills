from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openforge.schemas.prd import ForgePRD


def normalize_path(p: str) -> str:
    raw = p.strip()
    is_subtree = raw.endswith("/")
    parts: list[str] = []

    for segment in raw.replace("\\", "/").split("/"):
        if segment in {"", "."}:
            continue
        parts.append(segment)

    normalized = "/".join(parts)
    if is_subtree and normalized:
        normalized = f"{normalized}/"
    return normalized


def paths_overlap(a: str, b: str) -> bool:
    left = normalize_path(a)
    right = normalize_path(b)

    if left == right:
        return True

    left_subtree = left.endswith("/")
    right_subtree = right.endswith("/")

    if left_subtree and right.startswith(left):
        return True
    if right_subtree and left.startswith(right):
        return True
    if left_subtree and right_subtree:
        return left.startswith(right) or right.startswith(left)
    return False


def validate_overlap(prd: ForgePRD) -> list[str]:
    errors: list[str] = []
    phases_by_stage: dict[int, list[tuple[str, list[str]]]] = {}

    for phase in prd.phases:
        produces: list[str] = []
        for task in phase.tasks:
            produces.extend(task.config.produces)
        phases_by_stage.setdefault(phase.config.stage, []).append((phase.id, produces))

    for stage, phase_claims in sorted(phases_by_stage.items()):
        for index, (left_phase, left_paths) in enumerate(phase_claims):
            for right_phase, right_paths in phase_claims[index + 1 :]:
                for left_path in left_paths:
                    for right_path in right_paths:
                        if paths_overlap(left_path, right_path):
                            message = (
                                f"stage {stage} overlap between phase '{left_phase}' "
                                f"({left_path}) and phase '{right_phase}' ({right_path})"
                            )
                            errors.append(message)

    return errors
