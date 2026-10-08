# Compliance Document Review — PII Security & Masking Service

A privacy-first PII masking layer for an AI-powered compliance document review system.

This project implements the Service 1 — PII Security & Masking Service from the larger Compliance Document Review architecture.

The service ensures that sensitive personally identifiable information (PII) is detected and replaced with safe document-scoped tokens before document content is sent to an external AI/LLM service.


## Overview

The intended compliance review architecture is:

```text
Raw Document
     |
     v
PII Masking & Security Layer
     |
     v
Masked Document
     |
     v
AI / LLM Service
     |
     v
Compliance Analysis
     |
     v
Human Review
     |
     v
Unmask / Rehydrate for Authorized UI


The current implementation focuses on the PII Security & Masking Layer.
The main security principle is:
Raw PII should never be included in outbound AI payloads.
```

## Features

Detect common PII using regex and heuristics
Replace detected PII with safe tokens
Maintain stable tokens for repeated PII within a document
Store original PII mappings server-side
Restore original PII when authorized using the document ID
Mask content before LLM requests
Mask content before embedding requests
Verify serialized outbound AI payloads contain no raw PII
Document-specific token mapping
FastAPI REST API
Swagger/OpenAPI documentation
Adversarial PII security tests
API integration tests
Clean non-PII text passes through unchanged
Supported PII Types

The current detector supports:

PII Type	Example	Replacement
Person name	Jane Smith	[CLIENT_1]
SSN	987-65-4321	[SSN_1]
Email	jane.smith@example.com	[EMAIL_1]
Phone	+1 555-123-4567	[PHONE_1]
Account number	AC-99120	[ACCOUNT_1]
Address	Address: 123 Main Street, New York, NY 10001	[ADDRESS_1]
Dollar amount	$250,000	[AMOUNT_1]

The detector intentionally uses conservative patterns to reduce false positives.

Example
Input
Investment Agreement for Jane Smith
(SSN: 987-65-4321, Account #AC-99120).

We guarantee Jane Smith an 18% annual return
on investment without any market risk.
Masked output
Investment Agreement for [CLIENT_1]
(SSN: [SSN_1], Account [ACCOUNT_1]).

We guarantee [CLIENT_1] an 18% annual return
on investment without any market risk.
Server-side mapping
[CLIENT_1]  -> Jane Smith
[SSN_1]     -> 987-65-4321
[ACCOUNT_1] -> AC-99120

The mapping is stored server-side and is not included in the outbound AI payload.

## Project Structure

compliance-document-review/
│
├── src/
│   └── compliance/
│       ├── __init__.py
│       ├── models.py
│       ├── detector.py
│       ├── masker.py
│       ├── mapper.py
│       ├── mapping_store.py
│       ├── unmasker.py
│       └── interceptor.py
│
├── tests/
│   ├── test_detector.py
│   ├── test_masker.py
│   ├── test_mapper.py
│   ├── test_mapping_store.py
│   ├── test_unmasker.py
│   ├── test_interceptor.py
│   ├── test_security.py
│   ├── test_adversarial_pii.py
│   └── test_api.py
│
├── fixtures/
│   ├── sample_pii.txt
│   └── sample_clean.txt
│
├── data/
│   └── mappings/
│
├── docs/
│   └── MASKER_LIMITATIONS.md
│
├── app.py
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore

## Core Components

PIIDetector

Detects PII using regex and conservative heuristics.

Document
   |
   v
PIIDetector
   |
   v
PIIEntity objects

Each detected entity contains:

entity type
original value
start offset
end offset
assigned token
TokenMapper

Creates document-scoped tokens.

For example:

Jane Smith -> [CLIENT_1]
Jane Smith -> [CLIENT_1]

Repeated occurrences of the same PII value within the same masking operation reuse the same token.

Different documents receive their own token numbering.

MappingStore

Stores mappings using the document ID:

document_id
     |
     v
server-side mapping

Example:

data/mappings/investment-agreement-demo.json

Mapping files contain sensitive information and are excluded from Git through .gitignore.

PIIMasker

Coordinates:

Detector
   +
Token Mapper
   +
Mapping Store

and produces:

MaskingResult
├── masked_text
├── entities
└── mapping


PIIUnmasker

Restores the original values using the document-specific mapping.

[CLIENT_1]
    |
    v
Jane Smith


MaskedLlmClient

Provides the privacy boundary for downstream AI operations.

It exposes:

complete()
embed()

Both methods mask the input before passing it to the downstream client.

Conceptually:

Application
     |
     v
MaskedLlmClient
     |
     v
PIIMasker
     |
     v
Masked payload
     |
     v
External AI service


## FastAPI Demo

The project includes a FastAPI demonstration application.

Start the server with:

uvicorn app:app --reload

Open the Swagger interface:

http://127.0.0.1:8000/docs
API Endpoints
GET /

Health check.

Example response:

{
  "service": "Compliance Document Review",
  "status": "running",
  "privacy_layer": "enabled"
}
POST /mask

Masks PII in a document.

Example request:

{
  "document_id": "investment-agreement-demo",
  "text": "Investment Agreement for Jane Smith (SSN: 987-65-4321, Account #AC-99120)."
}

Example response:

{
  "document_id": "investment-agreement-demo",
  "masked_text": "Investment Agreement for [CLIENT_1] (SSN: [SSN_1], Account [ACCOUNT_1]).",
  "detected_entities": [
    {
      "type": "PERSON",
      "token": "[CLIENT_1]"
    },
    {
      "type": "SSN",
      "token": "[SSN_1]"
    },
    {
      "type": "ACCOUNT",
      "token": "[ACCOUNT_1]"
    }
  ]
}

POST /simulate-ai

Simulates the payload that would be sent to an external AI service.

Example:

{
  "document_id": "investment-agreement-demo",
  "text": "Review Jane Smith's account AC-99120. Her SSN is 987-65-4321."
}

The simulated outbound payload contains:

{
  "prompt": "Review [CLIENT_1]'s account [ACCOUNT_1]. Her SSN is [SSN_1]."
}

The API also reports:

{
  "raw_pii_sent": false,
  "mapping_kept_server_side": true
}

POST /unmask

Restores original PII using the document-specific mapping.

Example:

{
  "document_id": "investment-agreement-demo",
  "text": "Agreement for [CLIENT_1]. SSN: [SSN_1]."
}

The response contains the restored text.

## Testing

The project uses pytest.

Run the complete test suite:

pytest -q

Current test status:

41 passed

The tests cover:

PII detection
PII masking
token mapping
document-specific mappings
mapping persistence
unmasking
LLM interception
embedding interception
serialized outbound payload security
adversarial PII cases
API endpoints
clean/non-PII text
error handling
Security Validation

One of the key acceptance criteria is that raw PII must not appear in an outbound AI request.

The test suite verifies that serialized outbound payloads do not contain values such as:

Jane Smith
987-65-4321
AC-99120
jane.smith@example.com

while safe tokens such as:

[CLIENT_1]
[SSN_1]
[ACCOUNT_1]
[EMAIL_1]

remain available to the AI system.

## Adversarial Testing

The project includes security-oriented tests for:

multiple PII types
repeated PII
safe financial terms
normal business text
clean documents
contextual person-name detection
masking multiple entities
preventing accidental replacement of non-PII terms

For example, financial terminology such as:

S&P 500

should remain unchanged.

Privacy Boundary

The system separates:

Data sent to AI
Masked document

from:

Data retained by the server
Token -> Original PII

The mapping is never intentionally included in the AI payload.

This creates a clear privacy boundary between the application server and downstream AI services.

## Known Limitations

The current implementation is intentionally focused on a practical PII masking milestone.

Current limitations include:

Detection is regex/heuristic based.
Person-name detection is conservative.
Address detection currently targets a specific address format.
Detection is not equivalent to a full NER-based PII system.
Mapping storage is file-based for the current prototype.
Mapping files require appropriate production access controls and encryption.
PDF/DOCX ingestion is not implemented in this service milestone.
The compliance rule engine and compliance inspection agent are separate future services.
The current API demonstrates the privacy boundary but does not connect to a production LLM provider.

See:

docs/MASKER_LIMITATIONS.md

for additional detector limitations.

## Running the Project

1. Create and activate a virtual environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
2. Install dependencies
pip install -r requirements.txt
3. Run tests
pytest -q
4. Start the API
uvicorn app:app --reload
5. Open Swagger
http://127.0.0.1:8000/docs
## Future Architecture

The larger system can build on this privacy layer:

                  ┌──────────────────────────┐
                  │      Raw Document        │
                  └────────────┬─────────────┘
                               │
                               v
                  ┌──────────────────────────┐
                  │ Service 1                │
                  │ PII Masking & Security   │
                  └────────────┬─────────────┘
                               │
                         Masked Document
                               │
                               v
                  ┌──────────────────────────┐
                  │ Service 2                │
                  │ AI Compliance Inspection │
                  └────────────┬─────────────┘
                               │
                               v
                  ┌──────────────────────────┐
                  │ Service 3                │
                  │ Rules / Absence / Eval   │
                  └────────────┬─────────────┘
                               │
                               v
                  ┌──────────────────────────┐
                  │ Human Officer Review     │
                  └──────────────────────────┘

The current repository provides the privacy foundation required before sensitive document content is exposed to downstream AI systems.

## Author
Raghav Kumar
