from compliance.mapping_store import MappingStore
from compliance.masker import PIIMasker
from compliance.unmasker import PIIUnmasker


def test_unmasks_document_specific_tokens(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))

    store.save(
        "document-001",
        {
            "[CLIENT_1]": "Jane Smith",
            "[SSN_1]": "987-65-4321",
        },
    )

    unmasker = PIIUnmasker(store)

    masked_text = (
        "Client [CLIENT_1] has SSN [SSN_1]."
    )

    result = unmasker.unmask(
        masked_text,
        "document-001",
    )

    assert result == (
        "Client Jane Smith has SSN 987-65-4321."
    )


def test_does_not_use_another_documents_mapping(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))

    store.save(
        "document-001",
        {"[CLIENT_1]": "Jane Smith"},
    )

    store.save(
        "document-002",
        {"[CLIENT_1]": "John Smith"},
    )

    unmasker = PIIUnmasker(store)

    result = unmasker.unmask(
        "Hello [CLIENT_1].",
        "document-002",
    )

    assert result == "Hello John Smith."
    from compliance.masker import PIIMasker


def test_mask_then_unmask_round_trip(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))

    masker = PIIMasker(mapping_store=store)
    unmasker = PIIUnmasker(store)

    original_text = (
        "Investment Agreement for Jane Smith. "
        "SSN: 987-65-4321."
    )

    masked_result = masker.mask(
        original_text,
        document_id="document-001",
    )

    assert masked_result.masked_text == (
        "Investment Agreement for [CLIENT_1]. "
        "SSN: [SSN_1]."
    )

    restored_text = unmasker.unmask(
        masked_result.masked_text,
        "document-001",
    )

    assert restored_text == original_text