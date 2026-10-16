import json
from pathlib import Path

import pytest

from compliance.evaluation.disclosure_checker import (
    DisclosureStatus,
    check_disclosure,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "compliance"
    / "disclosure_cases.json"
)


@pytest.mark.parametrize(
    "case",
    json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig")),
    ids=lambda case: case["case_id"],
)
def test_disclosure_cases(case):
    disclosure = case["required_disclosures"][0]

    result = check_disclosure(
        case["document_text"],
        disclosure["required_phrases"],
    )

    assert result.value == case["expected_status"]


def test_phrase_matching_is_case_insensitive():
    result = check_disclosure(
        "Investments involve MARKET RISK and LOSS OF PRINCIPAL.",
        ["market risk", "loss of principal"],
    )

    assert result == DisclosureStatus.PRESENT


def test_partial_disclosure_is_ambiguous():
    result = check_disclosure(
        "Investments involve market risk.",
        ["market risk", "loss of principal"],
    )

    assert result == DisclosureStatus.AMBIGUOUS


def test_empty_required_phrases_raise_error():
    with pytest.raises(ValueError):
        check_disclosure("Some document text.", [])

from compliance.evaluation.disclosure_checker import evaluate_disclosure


def test_evaluation_reports_found_and_missing_phrases():
    result = evaluate_disclosure(
        "Investments involve market risk.",
        ["market risk", "loss of principal"],
    )

    assert result["status"] == DisclosureStatus.AMBIGUOUS
    assert result["found_phrases"] == ["market risk"]
    assert result["missing_phrases"] == ["loss of principal"]


def test_evaluation_rejects_non_string_phrases():
    with pytest.raises(ValueError):
        evaluate_disclosure("Some text.", ["valid phrase", None])
