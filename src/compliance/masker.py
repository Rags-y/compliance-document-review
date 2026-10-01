from .detector import PIIDetector
from .mapper import TokenMapper
from .mapping_store import MappingStore
from .models import MaskingResult


class PIIMasker:
    """Detect PII, replace it with safe tokens, and optionally store mappings."""

    def __init__(
        self,
        detector: PIIDetector | None = None,
        mapper: TokenMapper | None = None,
        mapping_store: MappingStore | None = None,
    ):
        self.detector = detector or PIIDetector()
        self.mapper = mapper or TokenMapper()
        self.mapping_store = mapping_store

    def mask(
        self,
        text: str,
        document_id: str | None = None,
    ) -> MaskingResult:
        entities = self.detector.detect(text)

        mapping = self.mapper.map_entities(entities)

        if document_id is not None:
            if self.mapping_store is None:
                raise ValueError(
                    "A MappingStore is required when document_id is provided."
                )

            self.mapping_store.save(document_id, mapping)

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