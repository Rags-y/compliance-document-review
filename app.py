
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from compliance.evaluation.disclosure_checker import evaluate_disclosure
from compliance.inspection.inspector import MockComplianceInspector
from compliance.inspection.review import (
    HumanReviewWorkflow,
    ReviewRecord,
    ReviewStatus,
)
from compliance.inspection.rule_retriever import MockRuleRetriever
from compliance.inspection.validator import InspectionValidator
from compliance.mapping_store import MappingStore
from compliance.masker import PIIMasker
from compliance.mapper import TokenMapper
from compliance.unmasker import PIIUnmasker


app = FastAPI(
    title="Compliance Document Review",
    description="PII-safe compliance document review demo.",
    version="0.3.0",
)

mapping_store = MappingStore()
unmasker = PIIUnmasker(mapping_store=mapping_store)

BASE_DIR = Path(__file__).resolve().parent

RULES_PATH = BASE_DIR / "fixtures" / "compliance" / "mock_rules.json"
DISCLOSURE_REQUIREMENTS_PATH = (
    BASE_DIR / "fixtures" / "compliance" / "required_disclosures.json"
)

rule_retriever = MockRuleRetriever(RULES_PATH)
inspector = MockComplianceInspector(rule_retriever)
validator = InspectionValidator(rule_retriever)
review_workflow = HumanReviewWorkflow()

review_records: dict[str, ReviewRecord] = {}
review_lock = Lock()


class MaskRequest(BaseModel):
    text: str
    document_id: str | None = None


class UnmaskRequest(BaseModel):
    document_id: str
    text: str


class SimulateAiRequest(BaseModel):
    document_id: str
    text: str


class InspectRequest(BaseModel):
    text: str
    document_id: str | None = None


class ReviewRequest(BaseModel):
    decision: ReviewStatus
    reviewer_id: str = Field(min_length=1, max_length=200)
    comment: str = Field(default="", max_length=2000)


def create_masker() -> PIIMasker:
    """Create a fresh masker so token numbering is document-scoped."""
    return PIIMasker(
        mapper=TokenMapper(),
        mapping_store=mapping_store,
    )


def load_disclosure_requirements() -> list[dict]:
    """Load the configured mock disclosure requirements."""
    requirements = json.loads(
        DISCLOSURE_REQUIREMENTS_PATH.read_text(encoding="utf-8-sig")
    )

    if not isinstance(requirements, list):
        raise ValueError("Disclosure requirements must be a JSON list.")

    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ValueError("Each disclosure requirement must be a JSON object.")

        if not isinstance(requirement.get("disclosure_id"), str):
            raise ValueError("Each disclosure must have a string disclosure_id.")

        if not isinstance(requirement.get("description"), str):
            raise ValueError("Each disclosure must have a string description.")

        phrases = requirement.get("required_phrases")
        if (
            not isinstance(phrases, list)
            or not phrases
            or any(not isinstance(phrase, str) or not phrase.strip()
                   for phrase in phrases)
        ):
            raise ValueError(
                "Each disclosure must contain non-empty required phrases."
            )

    return requirements


@app.get("/")
def health_check():
    return {
        "service": "Compliance Document Review",
        "status": "running",
        "privacy_layer": "enabled",
    }


@app.post("/mask")
def mask_document(request: MaskRequest):
    document_id = request.document_id or str(uuid4())
    masker = create_masker()

    result = masker.mask(request.text, document_id=document_id)

    return {
        "document_id": document_id,
        "masked_text": result.masked_text,
        "detected_entities": [
            {"type": entity.entity_type, "token": entity.token}
            for entity in result.entities
        ],
    }


@app.post("/unmask")
def unmask_document(request: UnmaskRequest):
    try:
        restored_text = unmasker.unmask(
            request.text,
            request.document_id,
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="No mapping found for this document.",
        )

    return {
        "document_id": request.document_id,
        "unmasked_text": restored_text,
    }


@app.post("/simulate-ai")
def simulate_ai(request: SimulateAiRequest):
    try:
        masker = create_masker()
        result = masker.mask(
            request.text,
            document_id=request.document_id,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to prepare the masked AI payload.",
        )

    return {
        "document_id": request.document_id,
        "outbound_ai_payload": {"prompt": result.masked_text},
        "privacy_check": {
            "raw_pii_sent": False,
            "mapping_kept_server_side": True,
        },
    }


@app.post("/inspect")
def inspect_document(request: InspectRequest):
    document_id = request.document_id or str(uuid4())

    try:
        masked_result = create_masker().mask(
            request.text,
            document_id=document_id,
        )
        masked_text = masked_result.masked_text

        # Existing mock inspection and validation run on masked text.
        inspection = inspector.inspect(masked_text)
        validated = validator.validate(inspection, masked_text)

        # Evaluate configured mock disclosures against masked text.
        disclosures = []

        for requirement in load_disclosure_requirements():
            evaluation = evaluate_disclosure(
                masked_text,
                requirement["required_phrases"],
            )

            disclosures.append(
                {
                    "disclosure_id": requirement["disclosure_id"],
                    "description": requirement["description"],
                    "status": evaluation["status"].value,
                    "found_phrases": evaluation["found_phrases"],
                    "missing_phrases": evaluation["missing_phrases"],
                    "mock": requirement.get("mock", True),
                }
            )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Document inspection failed.",
        )

    with review_lock:
        review_records.setdefault(document_id, ReviewRecord())

    return {
        "document_id": document_id,
        "masked_text": masked_text,
        "findings": [
            {
                "passage": flag.passage,
                "rule_id": flag.rule_id,
                "reason": flag.reason,
                "severity": flag.severity,
                "start": flag.start,
                "end": flag.end,
            }
            for flag in validated.flags
        ],
        "rejected_findings": validated.rejected_count,
        "disclosures": disclosures,
        "review": {
            "status": ReviewStatus.PENDING_REVIEW.value,
            "final_decision_by_ai": False,
        },
        "privacy_check": {
            "raw_pii_sent_to_inspector": False,
            "mapping_kept_server_side": True,
        },
    }


@app.get("/review/{document_id}")
def get_review(document_id: str):
    with review_lock:
        record = review_records.get(document_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="No review record found for this document.",
        )

    return {
        "document_id": document_id,
        "status": record.status.value,
        "reviewer_id": record.reviewer_id,
        "comment": record.comment,
    }


@app.post("/review/{document_id}")
def submit_review(document_id: str, request: ReviewRequest):
    with review_lock:
        record = review_records.get(document_id)

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="No review record found for this document.",
            )

        try:
            updated = review_workflow.decide(
                record=record,
                decision=request.decision,
                reviewer_id=request.reviewer_id,
                comment=request.comment,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        review_records[document_id] = updated

    return {
        "document_id": document_id,
        "status": updated.status.value,
        "reviewer_id": updated.reviewer_id,
        "comment": updated.comment,
    }
