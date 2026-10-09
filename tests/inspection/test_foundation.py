
from pathlib import Path

from compliance.inspection.rule_retriever import MockRuleRetriever
from compliance.inspection.sectioner import DocumentSectioner


ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = ROOT / "fixtures" / "compliance" / "mock_rules.json"


def test_sectioner_preserves_exact_text_and_offsets():
    text = "First paragraph.\n\nSecond paragraph with details."

    sections = DocumentSectioner().section(text)

    assert len(sections) == 2

    for section in sections:
        assert text[section.start:section.end] == section.text

    assert sections[0].text == "First paragraph."
    assert sections[1].text == "Second paragraph with details."


def test_sectioner_handles_empty_text():
    assert DocumentSectioner().section("") == []
    assert DocumentSectioner().section(" \n\n ") == []


def test_mock_rules_load_ten_unique_ids():
    retriever = MockRuleRetriever(RULES_PATH)

    assert len(retriever.rules) == 10
    assert len({rule.rule_id for rule in retriever.rules}) == 10
    assert all(rule.mock for rule in retriever.rules)


def test_rule_lookup_returns_matching_rule():
    retriever = MockRuleRetriever(RULES_PATH)

    rule = retriever.get_by_id("FINRA-2210")

    assert rule is not None
    assert rule.title == "Fair and balanced communications"
    assert retriever.get_by_id("UNKNOWN-RULE") is None


def test_retrieval_finds_guarantee_and_risk_rules():
    retriever = MockRuleRetriever(RULES_PATH)

    text = (
        "We guarantee [CLIENT_1] an 18% annual return "
        "without any market risk."
    )

    matched_ids = {
        rule.rule_id for rule in retriever.retrieve_for_text(text)
    }

    assert "FINRA-2210" in matched_ids
    assert "RISK-03" in matched_ids
    assert "GUAR-05" in matched_ids
    assert "RET-02" in matched_ids