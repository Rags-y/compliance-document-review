from compliance.detector import PIIDetector
from compliance.masker import PIIMasker


def test_detects_multiple_pii_types():
    detector = PIIDetector()

    text = (
        "Client Jane Smith, SSN 987-65-4321, "
        "email jane.smith@example.com, "
        "phone +1 555-123-4567, "
        "account AC-99120, "
        "investment $250,000."
    )

    entities = detector.detect(text)

    entity_types = [entity.entity_type for entity in entities]

    assert "PERSON" in entity_types
    assert "SSN" in entity_types
    assert "EMAIL" in entity_types
    assert "PHONE" in entity_types
    assert "ACCOUNT" in entity_types
    assert "DOLLAR_AMOUNT" in entity_types


def test_masks_multiple_pii_types():
    masker = PIIMasker()

    text = (
        "Client Jane Smith, SSN 987-65-4321, "
        "email jane.smith@example.com, "
        "account AC-99120."
    )

    result = masker.mask(text)

    assert "Jane Smith" not in result.masked_text
    assert "987-65-4321" not in result.masked_text
    assert "jane.smith@example.com" not in result.masked_text
    assert "AC-99120" not in result.masked_text

    assert "[CLIENT_1]" in result.masked_text
    assert "[SSN_1]" in result.masked_text
    assert "[EMAIL_1]" in result.masked_text
    assert "[ACCOUNT_1]" in result.masked_text


def test_safe_financial_terms_are_not_flagged():
    detector = PIIDetector()

    text = (
        "The S&P 500 increased by 2%. "
        "The Dow Jones Industrial Average also increased."
    )

    entities = detector.detect(text)

    assert entities == []


def test_normal_business_text_is_not_flagged():
    detector = PIIDetector()

    text = (
        "The company reviewed its investment strategy "
        "and updated its compliance procedures."
    )

    entities = detector.detect(text)

    assert entities == []


def test_masking_does_not_change_safe_text():
    masker = PIIMasker()

    text = (
        "The S&P 500 is a market index. "
        "The company follows FINRA compliance procedures."
    )

    result = masker.mask(text)

    assert result.masked_text == text
    assert result.entities == []
    assert result.mapping == {}


def test_repeated_pii_uses_same_token():
    masker = PIIMasker()

    text = (
        "Jane Smith is the client. "
        "The agreement was signed by Jane Smith."
    )

    result = masker.mask(text)

    assert result.masked_text == (
        "[CLIENT_1] is the client. "
        "The agreement was signed by [CLIENT_1]."
    )

    assert result.mapping == {
        "[CLIENT_1]": "Jane Smith",
    }