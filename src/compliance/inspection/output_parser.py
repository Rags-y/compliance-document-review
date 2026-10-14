
import json

from compliance.inspection.models import (
    ComplianceFlag,
    InspectionResult,
)


class InspectionOutputError(ValueError):
    """Raised when inspection output does not match the expected schema."""


def parse_inspection_output(
    payload: str | dict,
) -> InspectionResult:
    """Parse and validate the structure of inspection output.

    This validates the data shape, not whether findings are factually
    grounded. Pass the result through InspectionValidator afterward.
    """
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise InspectionOutputError(
                "Inspection output is not valid JSON."
            ) from exc
    elif isinstance(payload, dict):
        data = payload
    else:
        raise InspectionOutputError(
            "Inspection output must be a JSON string or object."
        )

    if not isinstance(data, dict):
        raise InspectionOutputError(
            "Inspection output must be a JSON object."
        )

    raw_flags = data.get("flags")
    if not isinstance(raw_flags, list):
        raise InspectionOutputError(
            "'flags' must be a list."
        )

    flags = []

    for index, item in enumerate(raw_flags):
        if not isinstance(item, dict):
            raise InspectionOutputError(
                f"Flag {index} must be an object."
            )

        values = {}
        for field in ("passage", "rule_id", "reason", "severity"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                raise InspectionOutputError(
                    f"Flag {index} has an invalid '{field}' field."
                )
            values[field] = value.strip()

        flags.append(ComplianceFlag(**values))

    prompt_version = data.get("prompt_version", "v1")
    model_id = data.get("model_id", "unknown")

    if not isinstance(prompt_version, str) or not prompt_version.strip():
        raise InspectionOutputError(
            "'prompt_version' must be a non-empty string."
        )

    if not isinstance(model_id, str) or not model_id.strip():
        raise InspectionOutputError(
            "'model_id' must be a non-empty string."
        )

    return InspectionResult(
        flags=tuple(flags),
        prompt_version=prompt_version,
        model_id=model_id,
    )
