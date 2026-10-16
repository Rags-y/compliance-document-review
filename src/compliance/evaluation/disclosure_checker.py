
from enum import Enum
from typing import Iterable


class DisclosureStatus(str, Enum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    AMBIGUOUS = "AMBIGUOUS"


def evaluate_disclosure(
    document_text: str,
    required_phrases: Iterable[str],
) -> dict:
    """Evaluate required phrases and return status plus phrase-level details."""
    phrases = list(required_phrases)

    if not phrases or any(
        not isinstance(phrase, str) or not phrase.strip()
        for phrase in phrases
    ):
        raise ValueError("Required phrases must contain non-empty strings.")

    normalized_text = document_text.casefold()
    found_phrases = [
        phrase for phrase in phrases
        if phrase.casefold() in normalized_text
    ]
    missing_phrases = [
        phrase for phrase in phrases
        if phrase.casefold() not in normalized_text
    ]

    if not missing_phrases:
        status = DisclosureStatus.PRESENT
    elif not found_phrases:
        status = DisclosureStatus.MISSING
    else:
        status = DisclosureStatus.AMBIGUOUS

    return {
        "status": status,
        "found_phrases": found_phrases,
        "missing_phrases": missing_phrases,
    }


def check_disclosure(
    document_text: str,
    required_phrases: Iterable[str],
) -> DisclosureStatus:
    """Return only the disclosure status for backward compatibility."""
    return evaluate_disclosure(document_text, required_phrases)["status"]
