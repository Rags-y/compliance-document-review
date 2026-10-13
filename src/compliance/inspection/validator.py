
from dataclasses import dataclass

from compliance.inspection.models import (
    ComplianceFlag,
    InspectionResult,
)
from compliance.inspection.rule_retriever import RuleRetriever


@dataclass(frozen=True)
class ValidatedComplianceFlag:
    """A compliance finding grounded in the source document."""

    passage: str
    rule_id: str
    reason: str
    severity: str
    start: int
    end: int


@dataclass(frozen=True)
class ValidatedInspectionResult:
    """Inspection results after grounding validation."""

    flags: tuple[ValidatedComplianceFlag, ...]
    rejected_count: int


class InspectionValidator:
    """Reject findings that cannot be grounded in rules and source text."""

    def __init__(self, rule_retriever: RuleRetriever):
        self.rule_retriever = rule_retriever

    def validate(
        self,
        result: InspectionResult,
        source_text: str,
    ) -> ValidatedInspectionResult:
        accepted = []
        rejected_count = 0

        for flag in result.flags:
            rule = self.rule_retriever.get_by_id(flag.rule_id)

            if rule is None or not flag.passage:
                rejected_count += 1
                continue

            start = source_text.find(flag.passage)

            if start == -1:
                rejected_count += 1
                continue

            accepted.append(
                ValidatedComplianceFlag(
                    passage=flag.passage,
                    rule_id=flag.rule_id,
                    reason=flag.reason,
                    severity=rule.severity,
                    start=start,
                    end=start + len(flag.passage),
                )
            )

        return ValidatedInspectionResult(
            flags=tuple(accepted),
            rejected_count=rejected_count,
        )
