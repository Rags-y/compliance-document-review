import re

from .models import PIIEntity


class PIIDetector:
    """Detect common PII patterns using regex and heuristics."""

    PATTERNS = {
        "SSN": re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        ),
        "EMAIL": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "PHONE": re.compile(
            r"(?<!\d)(?:\+1[-.\s]?)?"
            r"(?:\(?\d{3}\)?[-.\s]?)"
            r"\d{3}[-.\s]?\d{4}(?!\d)"
        ),
        "ACCOUNT": re.compile(
            r"(?i)(?<!\w)(?:#\s*)?(?:AC|ACCOUNT)[-_ ]?\d{4,}(?!\w)"
        ),
        "DOLLAR_AMOUNT": re.compile(
            r"(?<!\w)\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?!\w)"
        ),
    }

    def detect(self, text: str) -> list[PIIEntity]:
        entities: list[PIIEntity] = []

        for entity_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                entities.append(
                    PIIEntity(
                        entity_type=entity_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                    )
                )

        return self._resolve_overlaps(entities)

    @staticmethod
    def _resolve_overlaps(
        entities: list[PIIEntity],
    ) -> list[PIIEntity]:
        """Keep non-overlapping entities, preferring longer spans."""

        entities = sorted(
            entities,
            key=lambda entity: (
                -(entity.end - entity.start),
                entity.start,
            ),
        )

        selected: list[PIIEntity] = []

        for entity in entities:
            overlaps = any(
                entity.start < existing.end
                and entity.end > existing.start
                for existing in selected
            )

            if not overlaps:
                selected.append(entity)

        return sorted(selected, key=lambda entity: entity.start)