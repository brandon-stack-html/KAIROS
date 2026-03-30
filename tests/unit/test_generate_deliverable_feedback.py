"""Unit tests for GenerateDeliverableFeedbackHandler."""

import pytest

from src.application.generate_deliverable_feedback.command import (
    GenerateDeliverableFeedbackCommand,
)
from src.application.generate_deliverable_feedback.handler import (
    GenerateDeliverableFeedbackHandler,
)
from src.domain.deliverable.deliverable import Deliverable, DeliverableStatus
from src.domain.deliverable.errors import DeliverableNotFoundError
from src.domain.project.project import Project
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId
from src.infrastructure.persistence.in_memory.ai_service import InMemoryAiService
from uuid import uuid4


class FakeDeliverableRepo:
    def __init__(self, deliverable: Deliverable | None = None):
        self._deliverable = deliverable

    async def find_by_id(self, deliverable_id, tenant_id):
        return self._deliverable

    async def save(self, deliverable):
        pass

    async def find_by_project(self, project_id, tenant_id):
        return []

    async def find_by_tenant(self, tenant_id):
        return []


class FakeProjectRepo:
    def __init__(self, project: Project | None = None):
        self._project = project

    async def find_by_id(self, project_id, tenant_id):
        return self._project

    async def save(self, project):
        pass

    async def find_by_org(self, org_id, tenant_id):
        return []

    async def find_by_tenant(self, tenant_id):
        return []


class FakeOrgRepo:
    async def find_by_id(self, org_id, tenant_id):
        return None

    async def save(self, org):
        pass


class FakeUoW:
    def __init__(
        self,
        deliverable: Deliverable | None = None,
        project: Project | None = None,
    ):
        self.deliverables = FakeDeliverableRepo(deliverable)
        self.projects = FakeProjectRepo(project)
        self.organizations = FakeOrgRepo()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass


def make_deliverable(
    title: str = "Design Mock-ups",
    url: str = "https://figma.com/file/abc123",
) -> Deliverable:
    """Create a test deliverable."""
    return Deliverable.create(
        title=title,
        url_link=url,
        project_id=ProjectId.generate(),
        tenant_id=TenantId.generate(),
        submitted_by=str(uuid4()),
    )


def make_project(name: str = "Q1 Redesign") -> Project:
    """Create a test project."""
    return Project.create(
        name=name,
        description="Test project",
        org_id=OrganizationId.generate(),
        tenant_id=TenantId.generate(),
        owner_id=str(uuid4()),
    )


def make_command(
    deliverable_id: str = "d1",
    feedback_text: str = "Logo is too big, colors are off",
) -> GenerateDeliverableFeedbackCommand:
    """Create a test command."""
    return GenerateDeliverableFeedbackCommand(
        deliverable_id=deliverable_id,
        feedback_text=feedback_text,
        reviewer_id=str(uuid4()),
        tenant_id=str(uuid4()),
    )


class TestGenerateDeliverableFeedbackHandler:
    """Unit tests for GenerateDeliverableFeedbackHandler."""

    @pytest.mark.asyncio
    async def test_returns_ai_response(self):
        """Should return the AI-generated feedback."""
        # Arrange
        ai = InMemoryAiService()
        ai.response = '{"items":[{"what":"fix logo","priority":"high","suggestion":"resize to 120px"}],"summary":"resize logo"}'

        deliverable = make_deliverable()
        project = make_project()
        uow = FakeUoW(deliverable=deliverable, project=project)
        handler = GenerateDeliverableFeedbackHandler(uow, ai)
        command = make_command()

        # Act
        result = await handler.handle(command)

        # Assert
        assert "items" in result
        assert "high" in result
        assert len(ai.calls) == 1
        assert "prompt" in ai.calls[0]

    @pytest.mark.asyncio
    async def test_raises_not_found_when_deliverable_missing(self):
        """Should raise DeliverableNotFoundError if deliverable does not exist."""
        # Arrange
        ai = InMemoryAiService()
        uow = FakeUoW(deliverable=None, project=make_project())
        handler = GenerateDeliverableFeedbackHandler(uow, ai)
        command = make_command()

        # Act & Assert
        with pytest.raises(DeliverableNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_includes_feedback_text_in_prompt(self):
        """Should include the feedback text in the prompt sent to AI."""
        # Arrange
        ai = InMemoryAiService()
        ai.response = '{"items":[],"summary":"test"}'

        feedback_text = "The design doesn't match the brand guidelines"
        deliverable = make_deliverable()
        project = make_project()
        uow = FakeUoW(deliverable=deliverable, project=project)
        handler = GenerateDeliverableFeedbackHandler(uow, ai)
        command = make_command(feedback_text=feedback_text)

        # Act
        await handler.handle(command)

        # Assert
        assert len(ai.calls) == 1
        prompt = ai.calls[0]["prompt"]
        assert feedback_text in prompt
        assert deliverable.title in prompt
        assert deliverable.url_link in prompt
        assert project.name in prompt
