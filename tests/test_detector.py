from compliance.detector import PIIDetector


def test_detects_ssn():
    detector = PIIDetector()
    text = "Client SSN: 987-65-4321"
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "SSN"
    assert entities[0].value == "987-65-4321"


def test_detects_email():
    detector = PIIDetector()
    text = "Contact: jane.smith@example.com"
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "EMAIL"


def test_detects_phone():
    detector = PIIDetector()
    text = "Phone: +1 555-123-4567"
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "PHONE"


def test_detects_account_number():
    detector = PIIDetector()
    text = "Account: #AC-99120"
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "ACCOUNT"


def test_detects_dollar_amount():
    detector = PIIDetector()
    text = "Investment amount: $250,000"
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "DOLLAR_AMOUNT"


def test_does_not_flag_s_and_p_500():
    detector = PIIDetector()
    text = "The S&P 500 is a market index."
    entities = detector.detect(text)

    assert entities == []


def test_detects_person_name():
    detector = PIIDetector()
    text = "Investment Agreement for Jane Smith."
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "PERSON"
    assert entities[0].value == "Jane Smith"


def test_does_not_flag_common_title_as_person_name():
    detector = PIIDetector()
    text = "Investment Agreement for the client."
    entities = detector.detect(text)

    assert entities == []


def test_does_not_flag_s_and_p_500_as_person_name():
    detector = PIIDetector()
    text = "The S&P 500 is a market index."
    entities = detector.detect(text)

    assert entities == []


def test_detects_address():
    detector = PIIDetector()
    text = "Client address: 123 Main Street, New York, NY 10001"
    entities = detector.detect(text)

    assert len(entities) == 1
    assert entities[0].entity_type == "ADDRESS"
    assert entities[0].value == "123 Main Street, New York, NY 10001"


def test_does_not_flag_normal_sentence_as_address():
    detector = PIIDetector()
    text = "The client reviewed the investment agreement."
    entities = detector.detect(text)

    assert entities == []