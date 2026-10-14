
import pytest

from compliance.inspection.review import (
    HumanReviewWorkflow,
    ReviewRecord,
    ReviewStatus,
)


def test_new_review_starts_pending():
    record = ReviewRecord()

    assert record.status == ReviewStatus.PENDING_REVIEW
    assert record.reviewer_id is None


def test_human_can_approve():
    workflow = HumanReviewWorkflow()

    result = workflow.decide(
        ReviewRecord(),
        ReviewStatus.APPROVED,
        reviewer_id="reviewer-1",
        comment="Reviewed and approved.",
    )

    assert result.status == ReviewStatus.APPROVED
    assert result.reviewer_id == "reviewer-1"


def test_human_can_reject():
    result = HumanReviewWorkflow().decide(
        ReviewRecord(),
        ReviewStatus.REJECTED,
        reviewer_id="reviewer-2",
    )

    assert result.status == ReviewStatus.REJECTED


def test_missing_reviewer_id_is_rejected():
    with pytest.raises(ValueError, match="reviewer ID"):
        HumanReviewWorkflow().decide(
            ReviewRecord(),
            ReviewStatus.APPROVED,
            reviewer_id=" ",
        )


def test_ai_cannot_submit_pending_as_final_decision():
    with pytest.raises(ValueError, match="APPROVED or REJECTED"):
        HumanReviewWorkflow().decide(
            ReviewRecord(),
            ReviewStatus.PENDING_REVIEW,
            reviewer_id="reviewer-1",
        )


def test_final_decision_cannot_be_overwritten():
    workflow = HumanReviewWorkflow()
    approved = workflow.decide(
        ReviewRecord(),
        ReviewStatus.APPROVED,
        reviewer_id="reviewer-1",
    )

    with pytest.raises(ValueError, match="already been recorded"):
        workflow.decide(
            approved,
            ReviewStatus.REJECTED,
            reviewer_id="reviewer-2",
        )
