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

    def create_token(self, entity_type: str) -> str:
        prefix = self.TOKEN_PREFIXES.get(entity_type, entity_type)

        self._counters[prefix] = self._counters.get(prefix, 0) + 1

        return f"[{prefix}_{self._counters[prefix]}]"

    def map_entities(self, entities: list[PIIEntity]) -> dict[str, str]:
        """Assign tokens and return token -> original-value mapping."""

        mapping: dict[str, str] = {}

        for entity in entities:
            if entity.token is None:
                entity.token = self.create_token(entity.entity_type)

            mapping[entity.token] = entity.value

        return mapping