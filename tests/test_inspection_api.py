
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_inspect_document_returns_findings_and_pending_review():
    response = client.post(
        "/inspect",
        json={
            "text": (
                "We guarantee an 18% annual return on investment "
                "without any market risk."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["document_id"]
    assert data["review"]["status"] == "PENDING_REVIEW"
    assert data["review"]["final_decision_by_ai"] is False
    assert data["privacy_check"]["raw_pii_sent_to_inspector"] is False
    assert data["privacy_check"]["mapping_kept_server_side"] is True

    assert len(data["findings"]) > 0

    for finding in data["findings"]:
        assert finding["passage"]
        assert finding["rule_id"]
        assert finding["severity"]
        assert finding["start"] >= 0
        assert finding["end"] > finding["start"]


def test_review_can_be_approved_and_retrieved():
    inspect_response = client.post(
        "/inspect",
        json={"text": "We guarantee a guaranteed return."},
    )

    assert inspect_response.status_code == 200
    document_id = inspect_response.json()["document_id"]

    review_response = client.post(
        f"/review/{document_id}",
        json={
            "decision": "APPROVED",
            "reviewer_id": "test-reviewer",
            "comment": "Reviewed in automated test.",
        },
    )

    assert review_response.status_code == 200
    assert review_response.json()["status"] == "APPROVED"

    get_response = client.get(f"/review/{document_id}")

    assert get_response.status_code == 200
    assert get_response.json()["reviewer_id"] == "test-reviewer"
    assert get_response.json()["comment"] == "Reviewed in automated test."


def test_review_cannot_be_submitted_for_unknown_document():
    response = client.post(
        "/review/unknown-document-id",
        json={
            "decision": "APPROVED",
            "reviewer_id": "test-reviewer",
            "comment": "Should not be accepted.",
        },
    )

    assert response.status_code == 404


def test_final_review_decision_cannot_be_overwritten():
    inspect_response = client.post(
        "/inspect",
        json={"text": "The investment has no market risk."},
    )
    document_id = inspect_response.json()["document_id"]

    first_review = client.post(
        f"/review/{document_id}",
        json={
            "decision": "APPROVED",
            "reviewer_id": "reviewer-one",
            "comment": "Initial decision.",
        },
    )
    assert first_review.status_code == 200

    second_review = client.post(
        f"/review/{document_id}",
        json={
            "decision": "REJECTED",
            "reviewer_id": "reviewer-two",
            "comment": "Attempt to overwrite.",
        },
    )

    assert second_review.status_code == 400

    final_response = client.get(f"/review/{document_id}")
    assert final_response.status_code == 200
    assert final_response.json()["status"] == "APPROVED"
    assert final_response.json()["reviewer_id"] == "reviewer-one"
