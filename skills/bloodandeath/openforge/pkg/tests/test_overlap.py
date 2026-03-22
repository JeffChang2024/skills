from __future__ import annotations

from openforge.overlap import normalize_path, paths_overlap


def test_paths_overlap_exact_match() -> None:
    assert paths_overlap("src/auth/models.py", "./src//auth/models.py")


def test_paths_overlap_subtree_and_exact() -> None:
    assert paths_overlap("src/auth/", "src/auth/models/user.ts")


def test_paths_overlap_subtree_prefixes() -> None:
    assert paths_overlap("src/auth/", "src/auth/models/")


def test_paths_do_not_overlap() -> None:
    assert not paths_overlap("src/auth/", "src/payments/")


def test_normalize_path_preserves_subtree_marker() -> None:
    assert normalize_path("./src//") == "src/"
