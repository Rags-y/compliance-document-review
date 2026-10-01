import json
from pathlib import Path


class MappingStore:
    """Server-side store for document-specific PII mappings."""

    def __init__(self, storage_dir: str = "data/mappings"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, document_id: str, mapping: dict[str, str]) -> None:
        path = self._get_path(document_id)

        path.write_text(
            json.dumps(mapping, indent=2),
            encoding="utf-8",
        )

    def get(self, document_id: str) -> dict[str, str]:
        path = self._get_path(document_id)

        if not path.exists():
            raise KeyError(f"No mapping found for document: {document_id}")

        return json.loads(path.read_text(encoding="utf-8"))

    def _get_path(self, document_id: str) -> Path:
        safe_document_id = "".join(
            character
            for character in document_id
            if character.isalnum() or character in ("-", "_")
        )

        if not safe_document_id:
            raise ValueError("Invalid document ID.")

        return self.storage_dir / f"{safe_document_id}.json"