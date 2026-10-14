
import pytest

from compliance.inspection.output_parser import (
    InspectionOutputError,
    parse_inspection_output,
)


def test_parse_valid_inspection_output():
    result = parse_inspection_output(
        {
            "flags": [
                {
                    "passage": "guaranteed returns",
                    "rule_id": "GUAR-05",
                    "reason": "Potentially misleading guarantee.",
                    "severity": "high",
                }
            ],
            "prompt_version": "v1",
            "model_id": "mock-inspector",
        }
    )

    assert len(result.flags) == 1
    assert result.flags[0].rule_id == "GUAR-05"
    assert result.model_id == "mock-inspector"


def test_parse_json_string():
    result = parse_inspection_output('{"flags": []}')

    assert result.flags == ()


def test_malformed_json_is_rejected():
    with pytest.raises(InspectionOutputError):
        parse_inspection_output('{"flags": [')


def test_missing_flags_is_rejected():
    with pytest.raises(InspectionOutputError):
        parse_inspection_output({"findings": []})


def test_invalid_flag_field_is_rejected():
    with pytest.raises(InspectionOutputError):
        parse_inspection_output(
            {
                "flags": [
                    {
                        "passage": "guarantee",
                        "rule_id": "GUAR-05",
                        "reason": "",
                        "severity": "high",
                    }
                ]
            }
        )


def test_non_object_json_is_rejected():
    with pytest.raises(InspectionOutputError):
        parse_inspection_output("[]")
