from .mapping_store import MappingStore


class PIIUnmasker:
    """Restore masked PII using a document-specific mapping."""

    def __init__(self, mapping_store: MappingStore):
        self.mapping_store = mapping_store

    def unmask(self, text: str, document_id: str) -> str:
        mapping = self.mapping_store.get(document_id)

        unmasked_text = text

        for token, original_value in mapping.items():
            unmasked_text = unmasked_text.replace(
                token,
                original_value,
            )

        return unmasked_text