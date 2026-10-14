
from dataclasses import dataclass
from enum import Enum


class ReviewStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ReviewRecord:
    """Human-review state, separate from AI inspection findings."""

    status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    reviewer_id: str | None = None
    comment: str = ""


class HumanReviewWorkflow:
    """Record an explicit human review decision."""

    def decide(
        self,
        record: ReviewRecord,
        decision: ReviewStatus,
        reviewer_id: str,
        comment: str = "",
    ) -> ReviewRecord:
        if record.status != ReviewStatus.PENDING_REVIEW:
            raise ValueError(
                "A final review decision has already been recorded."
            )

        if decision not in (
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
        ):
            raise ValueError(
                "A reviewer must choose APPROVED or REJECTED."
            )

        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            raise ValueError("A reviewer ID is required.")

        return ReviewRecord(
            status=decision,
            reviewer_id=reviewer_id.strip(),
            comment=comment.strip(),
        )
