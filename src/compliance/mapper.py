from .models import PIIEntity


class TokenMapper:
    """Create stable tokens for PII entities within a document."""

    TOKEN_PREFIXES = {
        "PERSON": "CLIENT",
        "SSN": "SSN",
        "EMAIL": "EMAIL",
        "PHONE": "PHONE",
        "ACCOUNT": "ACCOUNT",
        "ADDRESS": "ADDRESS",
        "DOLLAR_AMOUNT": "AMOUNT",
    }

    def __init__(self):
        self._counters: dict[str, int] = {}
        self._value_to_token: dict[tuple[str, str], str] = {}

    def create_token(self, entity_type: str) -> str:
        prefix = self.TOKEN_PREFIXES.get(entity_type, entity_type)

        self._counters[prefix] = self._counters.get(prefix, 0) + 1

        return f"[{prefix}_{self._counters[prefix]}]"

    def map_entities(self, entities: list[PIIEntity]) -> dict[str, str]:
        """Assign stable tokens and return token -> original-value mapping."""

        mapping: dict[str, str] = {}

        for entity in entities:
            key = (entity.entity_type, entity.value)

            if entity.token is None:
                if key in self._value_to_token:
                    entity.token = self._value_to_token[key]
                else:
                    entity.token = self.create_token(entity.entity_type)
                    self._value_to_token[key] = entity.token

            mapping[entity.token] = entity.value

        return mapping