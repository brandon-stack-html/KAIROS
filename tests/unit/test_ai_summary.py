"""Unit tests for GenerateClientUpdateHandler."""

import uuid
from datetime import UTC, datetime

import pytest

from src.application.generate_client_update.command import GenerateClientUpdateCommand
from src.application.generate_client_update.handler import GenerateClientUpdateHandler
from src.domain.project.errors import ProjectNotFoundError
from src.domain.project.project import Project, ProjectStatus
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId
from src.infrastructure.persistence.in_memory.ai_service import InMemoryAiService

# ── Minimal test doubles ──────────────────────────────────────────────────────


class _FakeProjectRepo:
    def __init__(self, project=None):
        self._project = project

    async def find_by_id(self, *args, **kwargs):
        return self._project

    async def save(self, *args): ...


class _FakeDeliverableRepo:
    def __init__(self, deliverables=None):
        self._deliverables = deliverables or []

    async def find_by_project(self, *args, **kwargs):
        return self._deliverables


class _FakeUoW:
    def __init__(self, project=None, deliverables=None):
        self.projects = _FakeProjectRepo(project)
        self.deliverables = _FakeDeliverableRepo(deliverables)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def _make_project(tenant_id: str) -> Project:
    return Project(
        id=ProjectId.generate(),
        name="Mi Proyecto Web",
        description="Rediseño completo del sitio",
        org_id=OrganizationId.generate(),
        tenant_id=TenantId(tenant_id),
        status=ProjectStatus.ACTIVE,
        created_at=datetime.now(UTC),
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_handler_calls_ai_service_with_project_name_and_deliverables():
    """Handler passes project name and deliverables to the AI service."""
    tenant_id = str(uuid.uuid4())
    project = _make_project(tenant_id)
    ai_service = InMemoryAiService()

    handler = GenerateClientUpdateHandler(
        uow=_FakeUoW(project=project, deliverables=[]),
        ai_service=ai_service,
    )
    result = await handler.handle(
        GenerateClientUpdateCommand(project_id=project.id.value, tenant_id=tenant_id)
    )

    assert len(ai_service.calls) == 1
    assert ai_service.calls[0]["project_name"] == "Mi Proyecto Web"
    assert ai_service.calls[0]["deliverables"] == []
    assert "Mi Proyecto Web" in result


@pytest.mark.asyncio
async def test_handler_raises_project_not_found_when_project_missing():
    """Handler raises ProjectNotFoundError when project does not exist."""
    tenant_id = str(uuid.uuid4())
    ai_service = InMemoryAiService()

    handler = GenerateClientUpdateHandler(
        uow=_FakeUoW(project=None),
        ai_service=ai_service,
    )

    with pytest.raises(ProjectNotFoundError):
        await handler.handle(
            GenerateClientUpdateCommand(
                project_id=str(uuid.uuid4()),
                tenant_id=tenant_id,
            )
        )
