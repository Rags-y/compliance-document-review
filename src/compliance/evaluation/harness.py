
import json
from pathlib import Path

from compliance.evaluation.disclosure_checker import evaluate_disclosure


def evaluate_disclosure_cases(fixture_path: str | Path) -> dict:
    """Evaluate fixture cases and summarize expected versus actual status."""
    path = Path(fixture_path)
    cases = json.loads(path.read_text(encoding="utf-8-sig"))

    results = []

    for case in cases:
        for disclosure in case["required_disclosures"]:
            evaluation = evaluate_disclosure(
                case["document_text"],
                disclosure["required_phrases"],
            )
            actual_status = evaluation["status"].value

            results.append(
                {
                    "case_id": case["case_id"],
                    "disclosure_id": disclosure["disclosure_id"],
                    "expected_status": case["expected_status"],
                    "actual_status": actual_status,
                    "found_phrases": evaluation["found_phrases"],
                    "missing_phrases": evaluation["missing_phrases"],
                    "passed": actual_status == case["expected_status"],
                }
            )

    total = len(results)
    passed = sum(result["passed"] for result in results)

    return {
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": passed / total if total else 0.0,
        "results": results,
    }
