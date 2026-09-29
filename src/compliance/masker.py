from .detector import PIIDetector
from .mapper import TokenMapper
from .models import MaskingResult


class PIIMasker:
    """Detect PII and replace it with safe tokens."""

    def __init__(
        self,
        detector: PIIDetector | None = None,
        mapper: TokenMapper | None = None,
    ):
        self.detector = detector or PIIDetector()
        self.mapper = mapper or TokenMapper()

    def mask(self, text: str) -> MaskingResult:
        entities = self.detector.detect(text)

        mapping = self.mapper.map_entities(entities)

        masked_text = text

        # Replace from right to left so character offsets remain valid.
        for entity in reversed(entities):
            if entity.token is None:
                raise RuntimeError("PII entity has no token.")

            masked_text = (
                masked_text[:entity.start]
                + entity.token
                + masked_text[entity.end:]
            )

        return MaskingResult(
            masked_text=masked_text,
            entities=entities,
            mapping=mapping,
        )