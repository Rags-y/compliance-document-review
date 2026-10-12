
from dataclasses import dataclass


@dataclass(frozen=True)
class ComplianceRule:
    rule_id: str
    title: str
    description: str
    keywords: tuple[str, ...]
    severity: str
    mock: bool = True


@dataclass(frozen=True)
class DocumentSection:
    section_id: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class ComplianceFlag:
    """A structured compliance finding produced by the inspection agent."""

    passage: str
    rule_id: str
    reason: str
    severity: str


@dataclass(frozen=True)
class InspectionResult:
    """Structured findings for a single document inspection."""

    flags: tuple[ComplianceFlag, ...]
    prompt_version: str = "v1"
    model_id: str = "mock-inspector"
