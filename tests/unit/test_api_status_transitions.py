import pytest

from services.api.app.domain import ReportStatus, is_allowed_transition

SUBMITTED = ReportStatus.SUBMITTED
UNDER_REVIEW = ReportStatus.UNDER_REVIEW
RESOLVED = ReportStatus.RESOLVED


@pytest.mark.parametrize(
    ("current", "target"), [(SUBMITTED, UNDER_REVIEW), (UNDER_REVIEW, RESOLVED)]
)
def test_forward_single_step_is_allowed(
    current: ReportStatus, target: ReportStatus
) -> None:
    assert is_allowed_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (SUBMITTED, RESOLVED),
        (UNDER_REVIEW, SUBMITTED),
        (RESOLVED, UNDER_REVIEW),
        (RESOLVED, SUBMITTED),
        (SUBMITTED, SUBMITTED),
        (RESOLVED, RESOLVED),
    ],
)
def test_other_transitions_are_rejected(
    current: ReportStatus, target: ReportStatus
) -> None:
    assert not is_allowed_transition(current, target)
