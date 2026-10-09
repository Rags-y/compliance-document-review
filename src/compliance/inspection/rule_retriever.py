
import json
from pathlib import Path
from typing import Protocol

from compliance.inspection.models import ComplianceRule


class RuleRetriever(Protocol):
    """Interface that future rule retrieval implementations must follow."""

    def get_by_id(self, rule_id: str) -> ComplianceRule | None:
        ...

    def retrieve_for_text(self, text: str) -> list[ComplianceRule]:
        ...


class MockRuleRetriever:
    """Load development rules from a local JSON fixture."""

    def __init__(self, rules_path: str | Path):
        self.rules_path = Path(rules_path)
        raw_rules = json.loads(
            self.rules_path.read_text(encoding="utf-8")
        )

        self.rules = [
            ComplianceRule(
                rule_id=item["rule_id"],
                title=item["title"],
                description=item["description"],
                keywords=tuple(item["keywords"]),
                severity=item["severity"],
                mock=item.get("mock", True),
            )
            for item in raw_rules
        ]

        self._rules_by_id = {
            rule.rule_id: rule for rule in self.rules
        }

        if len(self._rules_by_id) != len(self.rules):
            raise ValueError("Duplicate compliance rule IDs found.")

    def get_by_id(self, rule_id: str) -> ComplianceRule | None:
        return self._rules_by_id.get(rule_id)

    def retrieve_for_text(self, text: str) -> list[ComplianceRule]:
        """Return rules whose configured keywords appear in the text."""
        lowered_text = text.casefold()

        return [
            rule
            for rule in self.rules
            if any(
                keyword.casefold() in lowered_text
                for keyword in rule.keywords
            )
        ]