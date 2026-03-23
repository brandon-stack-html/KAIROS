"""Unit tests for the Organization aggregate — pure domain logic, no DB."""

from datetime import UTC, datetime, timedelta

import pytest

from src.domain.organization.errors import (
    CannotRemoveLastOwnerError,
    InsufficientRoleError,
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
    MemberAlreadyExistsError,
)
from src.domain.organization.invitation import Invitation
from src.domain.organization.organization import Organization
from src.domain.shared.invitation_id import InvitationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserEmail, UserId


def make_tenant_id() -> TenantId:
    return TenantId.generate()


def make_user_id() -> UserId:
    return UserId.generate()


def make_org(owner_id: UserId | None = None) -> tuple[Organization, UserId]:
    if owner_id is None:
        owner_id = make_user_id()
    org = Organization.create(
        name="Acme Corp",
        slug="acme-corp",
        owner_id=owner_id,
        tenant_id=make_tenant_id(),
    )
    return org, owner_id


class TestOrganizationCreate:
    def test_create_adds_owner_as_owner_role(self):
        org, owner_id = make_org()
        assert len(org.memberships) == 1
        m = org.memberships[0]
        assert m.user_id == owner_id
        assert m.role is Role.OWNER

    def test_create_emits_organization_created_event(self):
        org, owner_id = make_org()
        events = org.pull_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "OrganizationCreated"


class TestAddMember:
    def test_member_cannot_invite(self):
        org, owner_id = make_org()
        member_id = make_user_id()
        org.add_member(inviter_id=owner_id, user_id=member_id, role=Role.MEMBER)
        org.pull_domain_events()  # clear events

        new_user_id = make_user_id()
        with pytest.raises(InsufficientRoleError):
            org.add_member(inviter_id=member_id, user_id=new_user_id, role=Role.MEMBER)

    def test_same_user_cannot_be_member_twice(self):
        org, owner_id = make_org()
        member_id = make_user_id()
        org.add_member(inviter_id=owner_id, user_id=member_id, role=Role.MEMBER)

        with pytest.raises(MemberAlreadyExistsError):
            org.add_member(inviter_id=owner_id, user_id=member_id, role=Role.MEMBER)

    def test_admin_can_invite(self):
        org, owner_id = make_org()
        admin_id = make_user_id()
        org.add_member(inviter_id=owner_id, user_id=admin_id, role=Role.ADMIN)

        new_user_id = make_user_id()
        org.add_member(inviter_id=admin_id, user_id=new_user_id, role=Role.MEMBER)
        assert len(org.memberships) == 3


class TestRemoveMember:
    def test_cannot_remove_last_owner(self):
        org, owner_id = make_org()
        with pytest.raises(CannotRemoveLastOwnerError):
            org.remove_member(remover_id=owner_id, user_id=owner_id)

    def test_owner_can_remove_member(self):
        org, owner_id = make_org()
        member_id = make_user_id()
        org.add_member(inviter_id=owner_id, user_id=member_id, role=Role.MEMBER)
        assert len(org.memberships) == 2

        org.remove_member(remover_id=owner_id, user_id=member_id)
        assert len(org.memberships) == 1


class TestChangeMemberRole:
    def test_cannot_demote_last_owner(self):
        org, owner_id = make_org()
        with pytest.raises(CannotRemoveLastOwnerError):
            org.change_member_role(
                changer_id=owner_id,
                user_id=owner_id,
                new_role=Role.ADMIN,
            )

    def test_member_cannot_change_roles(self):
        org, owner_id = make_org()
        member_id = make_user_id()
        org.add_member(inviter_id=owner_id, user_id=member_id, role=Role.MEMBER)

        with pytest.raises(InsufficientRoleError):
            org.change_member_role(
                changer_id=member_id,
                user_id=owner_id,
                new_role=Role.MEMBER,
            )


class TestInvitation:
    def test_expired_invitation_cannot_be_accepted(self):
        inv = Invitation(
            id=InvitationId.generate(),
            org_id="some-org-id",
            invitee_email=UserEmail("alice@example.com"),
            inviter_id=make_user_id(),
            role=Role.MEMBER,
            expires_at=datetime.now(UTC) - timedelta(days=1),  # already expired
        )
        with pytest.raises(InvitationExpiredError):
            inv.accept()

    def test_already_accepted_invitation_cannot_be_accepted_again(self):
        inv = Invitation.create(
            org_id="some-org-id",
            invitee_email=UserEmail("bob@example.com"),
            inviter_id=make_user_id(),
            role=Role.MEMBER,
        )
        inv.accept()
        with pytest.raises(InvitationAlreadyAcceptedError):
            inv.accept()
