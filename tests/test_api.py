from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["privacy_layer"] == "enabled"


def test_mask_endpoint_masks_pii():
    response = client.post(
        "/mask",
        json={
            "document_id": "api-test-001",
            "text": (
                "Investment Agreement for Jane Smith "
                "(SSN: 987-65-4321, Account #AC-99120)."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == "api-test-001"

    masked_text = data["masked_text"]

    assert "Jane Smith" not in masked_text
    assert "987-65-4321" not in masked_text
    assert "AC-99120" not in masked_text

    assert "[CLIENT_1]" in masked_text
    assert "[SSN_1]" in masked_text
    assert "[ACCOUNT_1]" in masked_text


def test_simulate_ai_never_receives_raw_pii():
    response = client.post(
        "/simulate-ai",
        json={
            "document_id": "api-test-002",
            "text": (
                "Review Jane Smith's account AC-99120. "
                "Her SSN is 987-65-4321."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    outbound_prompt = data["outbound_ai_payload"]["prompt"]

    assert "Jane Smith" not in outbound_prompt
    assert "AC-99120" not in outbound_prompt
    assert "987-65-4321" not in outbound_prompt

    assert "[CLIENT_1]" in outbound_prompt
    assert "[ACCOUNT_1]" in outbound_prompt
    assert "[SSN_1]" in outbound_prompt

    assert data["privacy_check"]["raw_pii_sent"] is False
    assert data["privacy_check"]["mapping_kept_server_side"] is True


def test_unmask_endpoint_restores_pii():
    document_id = "api-test-003"

    mask_response = client.post(
        "/mask",
        json={
            "document_id": document_id,
            "text": (
                "Agreement for Jane Smith. "
                "SSN: 987-65-4321."
            ),
        },
    )

    assert mask_response.status_code == 200

    masked_text = mask_response.json()["masked_text"]

    unmask_response = client.post(
        "/unmask",
        json={
            "document_id": document_id,
            "text": masked_text,
        },
    )

    assert unmask_response.status_code == 200

    restored_text = unmask_response.json()["unmasked_text"]

    assert restored_text == (
        "Agreement for Jane Smith. "
        "SSN: 987-65-4321."
    )


def test_unmask_unknown_document_returns_404():
    response = client.post(
        "/unmask",
        json={
            "document_id": "does-not-exist",
            "text": "Hello [CLIENT_1].",
        },
    )

    assert response.status_code == 404