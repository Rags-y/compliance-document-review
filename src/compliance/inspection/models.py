
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