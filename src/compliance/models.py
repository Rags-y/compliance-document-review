from dataclasses import dataclass


@dataclass
class PIIEntity:
    entity_type: str
    value: str
    start: int
    end: int
    token: str | None = None


@dataclass
class MaskingResult:
    masked_text: str
    entities: list[PIIEntity]
    mapping: dict[str, str]