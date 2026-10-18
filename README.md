# Compliance Document Review

A Python-based compliance document review demo that combines PII masking, rule-based compliance inspection, disclosure checks, and human review in a FastAPI application.

## Overview

The project demonstrates a privacy-aware workflow for reviewing financial documents. It replaces detected personally identifiable information (PII) with tokens, inspects the masked text for potential compliance concerns, checks required disclosures, and allows a human reviewer to approve or reject a document.

### Core services

**1. PII Masking and Privacy Layer**
- Detects supported PII categories, including names, SSNs, email addresses, phone numbers, account identifiers, and dollar amounts.
- Replaces detected values with tokens such as `[CLIENT_1]` and `[EMAIL_1]`.
- Maintains the original-value mapping on the server side.
- Supports restoration of original values through an unmasking endpoint.
- Provides a simulated outbound AI payload to demonstrate the intended privacy boundary.

**2. Compliance Inspection**
- Inspects masked text using mock compliance rules.
- Returns structured findings containing the matched passage, rule ID, reason, severity, and character offsets.
- Validates inspection findings and reports rejected findings.
- Checks configured disclosure requirements and identifies found and missing phrases.

**3. Disclosure Evaluation and Human Review**
- Evaluates disclosure presence using configurable required phrases.
- Classifies disclosure checks as `PRESENT`, `MISSING`, or `AMBIGUOUS`.
- Creates a pending review record for inspected documents.
- Allows a human reviewer to approve or reject a document and record a comment.
- Keeps the final review decision separate from the automated inspection output.

## Workflow

1. Submit a document for inspection.
2. Mask detected PII and retain its mapping on the server.
3. Inspect the masked text against mock compliance rules.
4. Evaluate required disclosures.
5. Create a `PENDING_REVIEW` record.
6. Have a reviewer approve or reject the document.
7. Restore original values when authorized and needed.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- Pytest
- JSON-based mock compliance rules and evaluation fixtures

## Project Setup

### Requirements

- Python 3.13 or a compatible Python version
- pip
- PowerShell on Windows (commands below use PowerShell)

### Installation

Clone or open the project repository, then navigate to its root directory:

```powershell
cd path\to\compliance-document-review
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Configure the Python import path:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

Start the API server:

```powershell
uvicorn app:app --reload
```

The API will be available at:

- Base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Keep the server running while making API requests.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check service health |
| POST | `/mask` | Mask detected PII in text |
| POST | `/unmask` | Restore original values using the document mapping |
| POST | `/simulate-ai` | Generate a simulated AI payload from masked text |
| POST | `/inspect` | Run compliance inspection and disclosure checks |
| GET | `/review/{document_id}` | Retrieve the current review record |
| POST | `/review/{document_id}` | Submit a human review decision |

### Example request bodies

**Mask text — `POST /mask`**

```json
{
  "text": "Investment agreement for Jane Smith. Email: jane.smith@example.com"
}
```

**Simulate outbound AI payload — `POST /simulate-ai`**

```json
{
  "document_id": "YOUR_DOCUMENT_ID",
  "text": "Investment agreement for Jane Smith."
}
```

**Inspect a document — `POST /inspect`**

```json
{
  "text": "We guarantee an 18% annual return without any market risk."
}
```

**Unmask text — `POST /unmask`**

```json
{
  "document_id": "YOUR_DOCUMENT_ID",
  "text": "Investment agreement for [CLIENT_1]. Email: [EMAIL_1]"
}
```

**Submit a human review — `POST /review/{document_id}`**

```json
{
  "decision": "REJECTED",
  "reviewer_id": "demo-reviewer",
  "comment": "Potentially misleading return claim; further review required."
}
```

Valid review decisions are `PENDING_REVIEW`, `APPROVED`, and `REJECTED`. Use `APPROVED` or `REJECTED` when submitting a final reviewer decision.

Refer to `/docs` for the complete request schemas and response structures.

## Running Tests

Set the source path before running tests:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m pytest -q
```

### Verified results

- Automated test suite: **80 passed**
- Disclosure evaluation: **3 passed, 0 failed**
- Disclosure fixture accuracy: **100% (3 of 3 cases)**

Run the disclosure evaluation independently:

```powershell
python -c "from compliance.evaluation.harness import evaluate_disclosure_cases; import json; r = evaluate_disclosure_cases('fixtures/compliance/disclosure_cases.json'); print(json.dumps({k:v for k,v in r.items() if k != 'results'}, indent=2))"
```

The disclosure evaluation uses a small set of predefined JSON fixtures. Its accuracy result applies only to those cases; it is not a measurement of overall regulatory compliance accuracy.

## Sample Data

The `fixtures/` directory contains sample documents and mock compliance data used for development and testing.

- `sample_pii.txt` — sample financial document containing PII and potentially problematic financial claims.
- `sample_clean.txt` — sample text with general financial-risk statements.
- `compliance/required_disclosures.json` — configured disclosure requirements.
- `compliance/disclosure_cases.json` — expected outcomes for disclosure evaluation.
- `compliance/mock_rules.json` — mock rules used for compliance inspection.

## Important Limitations

- **Mock inspection:** compliance findings are generated using mock rules and inspection components. They are not authoritative legal or regulatory determinations.
- **Simulated AI integration:** `/simulate-ai` demonstrates a masked outbound payload; it does not call an external AI service.
- **Detection limitations:** PII detection is limited to the patterns and categories supported by the implementation. Undetected sensitive information may remain in text.
- **In-memory state:** original-value mappings and review records are held in application memory. Restarting the server may clear them.
- **Evaluation scope:** the included disclosure evaluation uses only three predefined cases and does not establish production readiness.
- **Production hardening:** persistent storage, authentication, authorization, audit logging, stronger privacy controls, and broader testing would be needed before handling real sensitive documents.

## Project Goal

The goal is to demonstrate a modular compliance review workflow that separates PII masking, automated inspection, disclosure evaluation, and human decision-making while keeping original-value mappings on the server side.

## Author
Raghav Kumar
