"""Unit tests for the Deliverable aggregate."""

import uuid

import pytest

from src.domain.deliverable.deliverable import Deliverable, DeliverableStatus
from src.domain.deliverable.errors import (
    DeliverableAlreadyReviewedError,
    InvalidDeliverableTitleError,
)
from src.domain.deliverable.events import (
    ChangesRequested,
    DeliverableApproved,
    DeliverableSubmitted,
)
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


def _make_deliverable(
    title: str = "My Design", url: str = "https://figma.com/file/abc"
) -> Deliverable:
    return Deliverable.create(
        title=title,
        url_link=url,
        project_id=ProjectId.generate(),
        tenant_id=TenantId(str(uuid.uuid4())),
        submitted_by=str(uuid.uuid4()),
    )


def test_create_emits_deliverable_submitted():
    d = _make_deliverable()
    events = d.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], DeliverableSubmitted)


def test_title_empty_raises_error():
    with pytest.raises(InvalidDeliverableTitleError):
        _make_deliverable(title="")


def test_title_one_char_raises_error():
    with pytest.raises(InvalidDeliverableTitleError):
        _make_deliverable(title="X")


def test_default_status_is_pending():
    d = _make_deliverable()
    assert d.status is DeliverableStatus.PENDING


def test_approve_changes_status_and_emits_event():
    d = _make_deliverable()
    d.pull_domain_events()  # clear create event
    approver_id = str(uuid.uuid4())
    d.approve(approver_id)
    assert d.status is DeliverableStatus.APPROVED
    events = d.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], DeliverableApproved)
    assert events[0].approved_by == approver_id


def test_approve_already_approved_raises_error():
    d = _make_deliverable()
    d.approve(str(uuid.uuid4()))
    with pytest.raises(DeliverableAlreadyReviewedError):
        d.approve(str(uuid.uuid4()))


def test_request_changes_changes_status_and_emits_event():
    d = _make_deliverable()
    d.pull_domain_events()  # clear create event
    reviewer_id = str(uuid.uuid4())
    d.request_changes(reviewer_id)
    assert d.status is DeliverableStatus.CHANGES_REQUESTED
    events = d.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], ChangesRequested)
    assert events[0].reviewed_by == reviewer_id


def test_request_changes_already_reviewed_raises_error():
    d = _make_deliverable()
    d.request_changes(str(uuid.uuid4()))
    with pytest.raises(DeliverableAlreadyReviewedError):
        d.request_changes(str(uuid.uuid4()))
