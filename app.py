from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from compliance.mapping_store import MappingStore
from compliance.masker import PIIMasker
from compliance.mapper import TokenMapper
from compliance.unmasker import PIIUnmasker


app = FastAPI(
    title="Compliance Document Review",
    description="PII-safe compliance document review demo.",
    version="0.1.0",
)

mapping_store = MappingStore()
unmasker = PIIUnmasker(mapping_store=mapping_store)


class MaskRequest(BaseModel):
    text: str
    document_id: str | None = None


class UnmaskRequest(BaseModel):
    document_id: str
    text: str


class SimulateAiRequest(BaseModel):
    document_id: str
    text: str


def create_masker() -> PIIMasker:
    """Create a fresh masker so token numbering is document-scoped."""
    return PIIMasker(
        mapper=TokenMapper(),
        mapping_store=mapping_store,
    )


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

    result = masker.mask(
        request.text,
        document_id=document_id,
    )

    return {
        "document_id": document_id,
        "masked_text": result.masked_text,
        "detected_entities": [
            {
                "type": entity.entity_type,
                "token": entity.token,
            }
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
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    # This represents the payload that would be sent
    # to an external AI service.
    ai_payload = {
        "prompt": result.masked_text,
    }

    return {
        "document_id": request.document_id,
        "outbound_ai_payload": ai_payload,
        "privacy_check": {
            "raw_pii_sent": False,
            "mapping_kept_server_side": True,
        },
    }