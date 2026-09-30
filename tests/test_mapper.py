from compliance.mapper import TokenMapper
from compliance.models import PIIEntity


def test_creates_tokens():
    mapper = TokenMapper()
    token1 = mapper.create_token("SSN")
    token2 = mapper.create_token("SSN")
    token3 = mapper.create_token("EMAIL")

    assert token1 == "[SSN_1]"
    assert token2 == "[SSN_2]"
    assert token3 == "[EMAIL_1]"


def test_maps_entities():
    mapper = TokenMapper()

    entities = [
        PIIEntity(
            entity_type="SSN",
            value="987-65-4321",
            start=0,
            end=11,
        ),
        PIIEntity(
            entity_type="EMAIL",
            value="jane@example.com",
            start=20,
            end=37,
        ),
    ]

    mapping = mapper.map_entities(entities)

    assert mapping == {
        "[SSN_1]": "987-65-4321",
        "[EMAIL_1]": "jane@example.com",
    }

    assert entities[0].token == "[SSN_1]"
    assert entities[1].token == "[EMAIL_1]"


def test_reuses_token_for_same_value():
    mapper = TokenMapper()

    entities = [
        PIIEntity(
            entity_type="PERSON",
            value="Jane Smith",
            start=0,
            end=10,
        ),
        PIIEntity(
            entity_type="PERSON",
            value="Jane Smith",
            start=20,
            end=30,
        ),
    ]

    mapping = mapper.map_entities(entities)

    assert entities[0].token == "[CLIENT_1]"
    assert entities[1].token == "[CLIENT_1]"
    assert mapping == {
        "[CLIENT_1]": "Jane Smith",
    }