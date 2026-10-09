
import re

from compliance.inspection.models import DocumentSection


class DocumentSectioner:
    """Split text into paragraphs while preserving source offsets."""

    def section(self, text: str) -> list[DocumentSection]:
        sections = []

        # Match non-empty paragraphs without changing their source text.
        for index, match in enumerate(
            re.finditer(r"\S.*?(?=\n\s*\n|\Z)", text, re.DOTALL),
            start=1,
        ):
            start, end = match.span()
            sections.append(
                DocumentSection(
                    section_id=f"section-{index:03d}",
                    text=text[start:end],
                    start=start,
                    end=end,
                )
            )

        return sections