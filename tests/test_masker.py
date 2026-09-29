from compliance.masker import PIIMasker


def test_masks_pii():
    masker = PIIMasker()

    text = (
        "Client Jane Smith has SSN 987-65-4321 "
        "and email jane.smith@example.com."
    )

    result = masker.mask(text)

    assert "[SSN_1]" in result.masked_text
    assert "[EMAIL_1]" in result.masked_text

    assert "987-65-4321" not in result.masked_text
    assert "jane.smith@example.com" not in result.masked_text

    assert result.mapping["[SSN_1]"] == "987-65-4321"
    assert result.mapping["[EMAIL_1]"] == "jane.smith@example.com"


def test_clean_text_is_unchanged():
    masker = PIIMasker()

    text = "The S&P 500 is a market index."

    result = masker.mask(text)

    assert result.masked_text == text
    assert result.entities == []
    assert result.mapping == {}