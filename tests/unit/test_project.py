"""Unit tests for the Project aggregate."""

import uuid

import pytest

from src.domain.project.errors import InvalidProjectNameError
from src.domain.project.events import ProjectCreated
from src.domain.project.project import Project, ProjectStatus
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


def _make_project(name: str = "My Project", description: str = "") -> Project:
    return Project.create(
        name=name,
        description=description,
        org_id=OrganizationId.generate(),
        tenant_id=TenantId(str(uuid.uuid4())),
        owner_id=str(uuid.uuid4()),
    )


def test_create_emits_project_created_event():
    project = _make_project()
    events = project.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], ProjectCreated)


def test_create_event_contains_correct_data():
    org_id = OrganizationId.generate()
    tenant_id = TenantId(str(uuid.uuid4()))
    owner_id = str(uuid.uuid4())
    project = Project.create(
        name="Test Project",
        description="",
        org_id=org_id,
        tenant_id=tenant_id,
        owner_id=owner_id,
    )
    events = project.pull_domain_events()
    event = events[0]
    assert event.project_id == project.id.value
    assert event.name == "Test Project"
    assert event.org_id == org_id.value
    assert event.tenant_id == tenant_id.value
    assert event.owner_id == owner_id


def test_name_empty_raises_error():
    with pytest.raises(InvalidProjectNameError):
        _make_project(name="")


def test_name_one_char_raises_error():
    with pytest.raises(InvalidProjectNameError):
        _make_project(name="X")


def test_name_100_chars_is_valid():
    project = _make_project(name="A" * 100)
    assert project.name == "A" * 100


def test_name_101_chars_raises_error():
    with pytest.raises(InvalidProjectNameError):
        _make_project(name="A" * 101)


def test_default_status_is_active():
    project = _make_project()
    assert project.status is ProjectStatus.ACTIVE


def test_org_id_and_tenant_id_assigned_correctly():
    org_id = OrganizationId.generate()
    tenant_id = TenantId(str(uuid.uuid4()))
    project = Project.create(
        name="Project",
        description="",
        org_id=org_id,
        tenant_id=tenant_id,
        owner_id=str(uuid.uuid4()),
    )
    assert project.org_id == org_id
    assert project.tenant_id == tenant_id


def test_project_id_generate_produces_valid_uuid():
    pid = ProjectId.generate()
    parsed = uuid.UUID(pid.value)
    assert str(parsed) == pid.value
