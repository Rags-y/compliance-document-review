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
        "ADDRESS": re.compile(
    r"(?i)(?<=address:\s)"
    r"\d+\s+[A-Za-z0-9.\- ]+\s+"
    r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr)"
    r",\s*[A-Za-z .'-]+,\s*[A-Z]{2}\s+\d{5}"
),
        "DOLLAR_AMOUNT": re.compile(
            r"(?<!\w)\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?!\w)"
        ),
       "PERSON": re.compile(
    r"(?:(?i:for|name|client|review)\s*[:\-]?\s*"
    r"|(?i:mr|mrs|ms|miss|dr)\.?\s+)"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
    r"(?:'s)?"
),
    }

    def detect(self, text: str) -> list[PIIEntity]:
        entities: list[PIIEntity] = []

        for entity_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group()

                if entity_type == "PERSON":
                    value = match.group(1)
                    start = match.start(1)
                    end = match.end(1)
                else:
                    start = match.start()
                    end = match.end()

                entities.append(
                    PIIEntity(
                        entity_type=entity_type,
                        value=value,
                        start=start,
                        end=end,
                    )
                )

        # Detect repeated occurrences of person names already identified.
        person_names = {
            entity.value
            for entity in entities
            if entity.entity_type == "PERSON"
        }

        for person_name in person_names:
            for match in re.finditer(
                rf"(?<![A-Za-z]){re.escape(person_name)}(?![A-Za-z])",
                text,
            ):
                already_detected = any(
                    entity.entity_type == "PERSON"
                    and entity.start == match.start()
                    and entity.end == match.end()
                    for entity in entities
                )

                if not already_detected:
                    entities.append(
                        PIIEntity(
                            entity_type="PERSON",
                            value=person_name,
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