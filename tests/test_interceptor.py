import json

from compliance.interceptor import MaskedLlmClient
from compliance.mapping_store import MappingStore
from compliance.masker import PIIMasker


class FakeAiClient:
    def __init__(self):
        self.completed_prompts = []
        self.embedded_texts = []

    def complete(self, prompt):
        self.completed_prompts.append(prompt)
        return "AI response"

    def embed(self, text):
        self.embedded_texts.append(text)
        return [0.1, 0.2, 0.3]


def test_complete_sends_masked_prompt(tmp_path):
    client = FakeAiClient()
    store = MappingStore(storage_dir=str(tmp_path))
    masker = PIIMasker(mapping_store=store)
    masked_client = MaskedLlmClient(client, masker)

    prompt = (
        "Review the agreement for Jane Smith. "
        "Her SSN is 987-65-4321."
    )

    result = masked_client.complete(
        prompt,
        document_id="document-001",
    )

    assert result == "AI response"

    assert client.completed_prompts == [
        "Review the agreement for [CLIENT_1]. "
        "Her SSN is [SSN_1]."
    ]

    assert "Jane Smith" not in client.completed_prompts[0]
    assert "987-65-4321" not in client.completed_prompts[0]


def test_embed_sends_masked_text(tmp_path):
    client = FakeAiClient()
    store = MappingStore(storage_dir=str(tmp_path))
    masker = PIIMasker(mapping_store=store)
    masked_client = MaskedLlmClient(client, masker)

    text = (
        "Investment Agreement for Jane Smith. "
        "SSN: 987-65-4321."
    )

    result = masked_client.embed(
        text,
        document_id="document-001",
    )

    assert result == [0.1, 0.2, 0.3]

    assert client.embedded_texts == [
        "Investment Agreement for [CLIENT_1]. "
        "SSN: [SSN_1]."
    ]

    assert "Jane Smith" not in client.embedded_texts[0]
    assert "987-65-4321" not in client.embedded_texts[0]


def test_clean_text_passes_through_unchanged(tmp_path):
    client = FakeAiClient()
    store = MappingStore(storage_dir=str(tmp_path))
    masker = PIIMasker(mapping_store=store)
    masked_client = MaskedLlmClient(client, masker)

    text = "The S&P 500 is a market index."

    masked_client.complete(
        text,
        document_id="document-002",
    )

    assert client.completed_prompts == [
        "The S&P 500 is a market index."
    ]


def test_serialized_outbound_request_contains_no_raw_pii(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))
    masker = PIIMasker(mapping_store=store)

    client = FakeAiClient()
    masked_client = MaskedLlmClient(client, masker)

    prompt = (
        "Review Jane Smith's account AC-99120. "
        "Her SSN is 987-65-4321 and email is "
        "jane.smith@example.com."
    )

    masked_client.complete(
        prompt,
        document_id="document-003",
    )

    outbound_payload = {
        "model": "mock-model",
        "prompt": client.completed_prompts[0],
    }

    serialized_request = json.dumps(
        outbound_payload
    ).encode("utf-8")

    assert b"Jane Smith" not in serialized_request
    assert b"987-65-4321" not in serialized_request
    assert b"AC-99120" not in serialized_request
    assert b"jane.smith@example.com" not in serialized_request

    assert b"[CLIENT_1]" in serialized_request
    assert b"[SSN_1]" in serialized_request
    assert b"[ACCOUNT_1]" in serialized_request
    assert b"[EMAIL_1]" in serialized_request


def test_mapping_stays_server_side(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))
    masker = PIIMasker(mapping_store=store)

    client = FakeAiClient()
    masked_client = MaskedLlmClient(client, masker)

    prompt = (
        "Review Jane Smith's account AC-99120. "
        "Her SSN is 987-65-4321."
    )

    masked_client.complete(
        prompt,
        document_id="document-004",
    )

    outbound_prompt = client.completed_prompts[0]

    stored_mapping = store.get("document-004")

    # AI client receives masked content only.
    assert "[CLIENT_1]" in outbound_prompt
    assert "[ACCOUNT_1]" in outbound_prompt
    assert "[SSN_1]" in outbound_prompt

    assert "Jane Smith" not in outbound_prompt
    assert "AC-99120" not in outbound_prompt
    assert "987-65-4321" not in outbound_prompt

    # Original values remain available only in server-side storage.
    assert stored_mapping == {
        "[CLIENT_1]": "Jane Smith",
        "[ACCOUNT_1]": "AC-99120",
        "[SSN_1]": "987-65-4321",
    }