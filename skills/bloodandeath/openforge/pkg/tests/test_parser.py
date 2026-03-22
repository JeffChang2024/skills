from __future__ import annotations

from pathlib import Path

import pytest

from openforge.overlap import normalize_path
from openforge.parser import ParseError, parse_prd, validate_overlap

_FIXTURES = Path(__file__).parent / "fixtures"
_TEMPLATES = Path(__file__).resolve().parents[2] / "templates"


def test_parse_valid_simple() -> None:
    prd = parse_prd(_FIXTURES / "valid-simple.md")

    assert prd.title == "Simple Test"
    assert prd.objective == "Test basic parsing."
    assert set(prd.routing.aliases) == {"cloud"}
    assert len(prd.phases) == 1
    assert prd.phases[0].id == "setup"
    assert [task.id for task in prd.phases[0].tasks] == ["first-task", "second-task"]
    assert prd.phases[0].tasks[0].text == "First task"


def test_parse_valid_multi_stage() -> None:
    prd = parse_prd(_FIXTURES / "valid-multi-stage.md")

    assert [phase.config.stage for phase in prd.phases] == [1, 2]
    assert prd.phases[0].config.validator == "echo ok"
    assert prd.phases[1].config.executor == "local"
    assert prd.stage_validators == {1: "echo stage1", 2: "npm test"}
    assert prd.acceptance_criteria == ["Tests pass"]


def test_invalid_missing_alias() -> None:
    with pytest.raises(ParseError, match="local"):
        parse_prd(_FIXTURES / "invalid-missing-alias.md")


def test_invalid_duplicate_block() -> None:
    with pytest.raises(ParseError, match="duplicate"):
        parse_prd(_FIXTURES / "invalid-duplicate-block.md")


def test_validate_overlap() -> None:
    prd = parse_prd(_FIXTURES / "invalid-overlap.md", lenient=True)

    errors = validate_overlap(prd)

    assert errors
    assert "alpha" in errors[0]
    assert "beta" in errors[0]


def test_no_overlap_different_stages() -> None:
    prd = parse_prd(_FIXTURES / "valid-multi-stage.md")

    assert validate_overlap(prd) == []


@pytest.mark.parametrize(
    "template_name",
    ["prd-simple.md", "prd-full.md", "prd-review-only.md"],
)
def test_templates_parse_successfully(template_name: str) -> None:
    prd = parse_prd(_TEMPLATES / template_name, lenient=True)

    assert prd.title
    assert prd.phases


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("./src//auth/./models", "src/auth/models"),
        ("src///auth/", "src/auth/"),
        ("./tests/./unit//", "tests/unit/"),
        ("file.txt", "file.txt"),
    ],
)
def test_path_normalization(raw: str, expected: str) -> None:
    assert normalize_path(raw) == expected
