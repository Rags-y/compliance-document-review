from .masker import PIIMasker


class MaskedLlmClient:
    """Privacy-safe wrapper around an LLM/embedding client."""

    def __init__(self, client, masker: PIIMasker | None = None):
        self.client = client
        self.masker = masker or PIIMasker()

    def complete(self, prompt: str, document_id: str):
        """Mask the prompt before sending it to the LLM client."""

        result = self.masker.mask(
            prompt,
            document_id=document_id,
        )

        return self.client.complete(result.masked_text)

    def embed(self, text: str, document_id: str):
        """Mask text before sending it to the embedding client."""

        result = self.masker.mask(
            text,
            document_id=document_id,
        )

        return self.client.embed(result.masked_text)