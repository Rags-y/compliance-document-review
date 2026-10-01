from compliance.masker import PIIMasker
from compliance.mapping_store import MappingStore


def test_masks_pii():
    masker = PIIMasker()

    text = (
        "Client Jane Smith has SSN 987-65-4321 "
        "and email jane.smith@example.com."
    )

    result = masker.mask(text)

    assert "[CLIENT_1]" in result.masked_text
    assert "[SSN_1]" in result.masked_text
    assert "[EMAIL_1]" in result.masked_text

    assert "Jane Smith" not in result.masked_text
    assert "987-65-4321" not in result.masked_text
    assert "jane.smith@example.com" not in result.masked_text

    assert result.mapping["[CLIENT_1]"] == "Jane Smith"
    assert result.mapping["[SSN_1]"] == "987-65-4321"
    assert result.mapping["[EMAIL_1]"] == "jane.smith@example.com"


def test_clean_text_is_unchanged():
    masker = PIIMasker()

    text = "The S&P 500 is a market index."

    result = masker.mask(text)

    assert result.masked_text == text
    assert result.entities == []
    assert result.mapping == {}


def test_reuses_token_for_repeated_person_name():
    masker = PIIMasker()

    text = (
        "Investment Agreement for Jane Smith. "
        "Jane Smith is the client."
    )

    result = masker.mask(text)

    assert result.masked_text == (
        "Investment Agreement for [CLIENT_1]. "
        "[CLIENT_1] is the client."
    )

    assert result.mapping == {
        "[CLIENT_1]": "Jane Smith",
    }


def test_masks_address():
    masker = PIIMasker()

    text = "Client address: 123 Main Street, New York, NY 10001"

    result = masker.mask(text)

    assert result.masked_text == "Client address: [ADDRESS_1]"
    assert result.mapping == {
        "[ADDRESS_1]": "123 Main Street, New York, NY 10001",
    }


def test_masking_stores_mapping_by_document_id(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))
    masker = PIIMasker(mapping_store=store)

    text = "Client Jane Smith has SSN 987-65-4321."

    result = masker.mask(
        text,
        document_id="document-001",
    )

    assert result.masked_text == (
        "Client [CLIENT_1] has SSN [SSN_1]."
    )

    stored_mapping = store.get("document-001")

    assert stored_mapping == {
        "[CLIENT_1]": "Jane Smith",
        "[SSN_1]": "987-65-4321",
    }