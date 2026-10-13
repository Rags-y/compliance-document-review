
from pathlib import Path

from compliance.inspection.inspector import MockComplianceInspector
from compliance.inspection.models import (
    ComplianceFlag,
    InspectionResult,
)
from compliance.inspection.rule_retriever import MockRuleRetriever
from compliance.inspection.validator import InspectionValidator


RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "compliance"
    / "mock_rules.json"
)


def setup_validator():
    retriever = MockRuleRetriever(RULES_PATH)
    return retriever, InspectionValidator(retriever)


def test_valid_finding_has_exact_offsets():
    source = "Intro. We guarantee an 18% annual return. End."
    retriever, validator = setup_validator()
    result = MockComplianceInspector(retriever).inspect(source)

    validated = validator.validate(result, source)

    assert validated.flags
    flag = validated.flags[0]
    assert source[flag.start:flag.end] == flag.passage
    assert flag.start == source.find(flag.passage)
    assert flag.end == flag.start + len(flag.passage)
    assert flag.severity == retriever.get_by_id(flag.rule_id).severity


def test_unknown_rule_is_rejected():
    _, validator = setup_validator()
    result = InspectionResult(
        flags=(
            ComplianceFlag(
                passage="guarantee",
                rule_id="UNKNOWN-999",
                reason="Unknown rule",
                severity="high",
            ),
        )
    )

    validated = validator.validate(result, "We guarantee returns.")

    assert validated.flags == ()
    assert validated.rejected_count == 1


def test_unquoted_source_text_is_rejected():
    _, validator = setup_validator()
    result = InspectionResult(
        flags=(
            ComplianceFlag(
                passage="This exact passage is not in the document.",
                rule_id="GUAR-05",
                reason="Unsupported claim",
                severity="high",
            ),
        )
    )

    validated = validator.validate(result, "We guarantee returns.")

    assert validated.flags == ()
    assert validated.rejected_count == 1


def test_multiple_occurrences_use_first_exact_match():
    _, validator = setup_validator()
    source = "Risk noted. Risk reviewed."
    result = InspectionResult(
        flags=(
            ComplianceFlag(
                passage="Risk",
                rule_id="RISK-03",
                reason="Risk wording",
                severity="medium",
            ),
        )
    )

    validated = validator.validate(result, source)

    assert len(validated.flags) == 1
    assert validated.flags[0].start == source.find("Risk")
    assert validated.flags[0].end == source.find("Risk") + len("Risk")
