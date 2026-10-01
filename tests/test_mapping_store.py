from compliance.mapping_store import MappingStore


def test_saves_and_retrieves_mapping(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))

    mapping = {
        "[CLIENT_1]": "Jane Smith",
        "[SSN_1]": "987-65-4321",
    }

    store.save("document-001", mapping)

    result = store.get("document-001")

    assert result == mapping


def test_different_documents_have_separate_mappings(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))

    store.save(
        "document-001",
        {"[CLIENT_1]": "Jane Smith"},
    )

    store.save(
        "document-002",
        {"[CLIENT_1]": "John Smith"},
    )

    assert store.get("document-001") == {
        "[CLIENT_1]": "Jane Smith",
    }

    assert store.get("document-002") == {
        "[CLIENT_1]": "John Smith",
    }


def test_missing_document_raises_error(tmp_path):
    store = MappingStore(storage_dir=str(tmp_path))

    try:
        store.get("missing-document")
        assert False
    except KeyError:
        assert True