
from pathlib import Path

from compliance.inspection.inspector import MockComplianceInspector
from compliance.inspection.rule_retriever import MockRuleRetriever


RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "compliance"
    / "mock_rules.json"
)


def test_inspector_returns_structured_findings():
    retriever = MockRuleRetriever(RULES_PATH)
    inspector = MockComplianceInspector(retriever)

    result = inspector.inspect(
        "We guarantee an 18% annual return without any market risk."
    )

    assert result.flags
    flag = result.flags[0]

    assert flag.passage
    assert flag.rule_id
    assert flag.reason
    assert flag.severity
    assert flag.rule_id in {
        rule.rule_id for rule in retriever.rules
    }


def test_inspector_returns_empty_result_for_unmatched_text():
    retriever = MockRuleRetriever(RULES_PATH)
    inspector = MockComplianceInspector(retriever)

    result = inspector.inspect(
        "The document describes the office location and meeting room."
    )

    assert result.flags == ()
