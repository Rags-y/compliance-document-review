from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_inspect_reports_present_disclosure():
    response = client.post(
        "/inspect",
        json={
            "text": (
                "Investments involve market risk "
                "and possible loss of principal."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["disclosures"]
    result = data["disclosures"][0]

    assert result["disclosure_id"] == "RISK-DISC-01"
    assert result["status"] == "PRESENT"
    assert result["found_phrases"] == [
        "market risk",
        "loss of principal",
    ]
    assert result["missing_phrases"] == []
    assert result["mock"] is True
    assert data["review"]["status"] == "PENDING_REVIEW"


def test_inspect_reports_missing_disclosure():
    response = client.post(
        "/inspect",
        json={"text": "Our investment product targets long-term growth."},
    )

    assert response.status_code == 200
    result = response.json()["disclosures"][0]

    assert result["status"] == "MISSING"
    assert result["found_phrases"] == []
    assert result["missing_phrases"] == [
        "market risk",
        "loss of principal",
    ]


def test_inspect_reports_ambiguous_disclosure():
    response = client.post(
        "/inspect",
        json={"text": "Investments involve market risk."},
    )

    assert response.status_code == 200
    result = response.json()["disclosures"][0]

    assert result["status"] == "AMBIGUOUS"
    assert result["found_phrases"] == ["market risk"]
    assert result["missing_phrases"] == ["loss of principal"]


def test_disclosure_check_does_not_bypass_human_review():
    response = client.post(
        "/inspect",
        json={
            "text": (
                "Investments involve market risk "
                "and possible loss of principal."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["review"]["status"] == "PENDING_REVIEW"
    assert data["review"]["final_decision_by_ai"] is False
