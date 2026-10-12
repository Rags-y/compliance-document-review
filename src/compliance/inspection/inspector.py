
import re

from compliance.inspection.models import (
    ComplianceFlag,
    InspectionResult,
)
from compliance.inspection.rule_retriever import RuleRetriever


class MockComplianceInspector:
    """Generate structured findings using configured mock rules."""

    def __init__(self, rule_retriever: RuleRetriever):
        self.rule_retriever = rule_retriever

    def inspect(self, text: str) -> InspectionResult:
        flags = []

        for rule in self.rule_retriever.retrieve_for_text(text):
            for keyword in rule.keywords:
                match = re.search(re.escape(keyword), text, re.IGNORECASE)
                if not match:
                    continue

                passage = match.group(0)
                flags.append(
                    ComplianceFlag(
                        passage=passage,
                        rule_id=rule.rule_id,
                        reason=(
                            f"The document contains wording related to "
                            f"'{rule.title}'. Review it against the rule."
                        ),
                        severity=rule.severity,
                    )
                )
                break

        return InspectionResult(flags=tuple(flags))
