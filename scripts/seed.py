"""Seed script — populates the DB with demo data using handlers directly.

Usage:
    uv run python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def seed() -> None:
    # ── 1. Register mappers in FK-dependency order ───────────────────
    from src.infrastructure.persistence.sqlalchemy.mappers.tenant_mapper import (
        start_mappers as start_tenant_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.user_mapper import (
        start_mappers as start_user_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.refresh_token_mapper import (
        start_mappers as start_refresh_token_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.organization_mapper import (
        start_mappers as start_organization_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.invitation_mapper import (
        start_mappers as start_invitation_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.project_mapper import (
        start_mappers as start_project_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.deliverable_mapper import (
        start_mappers as start_deliverable_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.invoice_mapper import (
        start_mappers as start_invoice_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.conversation_mapper import (
        start_mappers as start_conversation_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.message_mapper import (
        start_mappers as start_message_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.document_mapper import (
        start_mappers as start_document_mappers,
    )

    start_tenant_mappers()
    start_user_mappers()
    start_refresh_token_mappers()
    start_organization_mappers()
    start_invitation_mappers()
    start_project_mappers()
    start_deliverable_mappers()
    start_invoice_mappers()
    start_conversation_mappers()
    start_message_mappers()
    start_document_mappers()

    # ── 2. Create tables ─────────────────────────────────────────────
    from src.infrastructure.persistence.sqlalchemy.database import engine, metadata

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    # ── 3. Import handlers + commands ────────────────────────────────
    from src.infrastructure.config.container import (
        get_create_tenant_handler,
        get_register_user_handler,
        get_create_organization_handler,
        get_invite_member_handler,
        get_accept_invitation_handler,
        get_create_project_handler,
        get_submit_deliverable_handler,
        get_approve_deliverable_handler,
        get_request_changes_handler,
        get_issue_invoice_handler,
        get_mark_invoice_paid_handler,
        get_create_conversation_handler,
        get_send_message_handler,
    )
    from src.application.create_tenant.command import CreateTenantCommand
    from src.application.register_user.command import RegisterUserCommand
    from src.application.create_organization.command import CreateOrganizationCommand
    from src.application.invite_member.command import InviteMemberCommand
    from src.application.accept_invitation.command import AcceptInvitationCommand
    from src.application.create_project.command import CreateProjectCommand
    from src.application.submit_deliverable.command import SubmitDeliverableCommand
    from src.application.approve_deliverable.command import ApproveDeliverableCommand
    from src.application.request_changes.command import RequestChangesCommand
    from src.application.issue_invoice.command import IssueInvoiceCommand
    from src.application.mark_invoice_paid.command import MarkInvoicePaidCommand
    from src.application.create_conversation.command import CreateConversationCommand
    from src.application.send_message.command import SendMessageCommand

    # ── 4. Create tenant ─────────────────────────────────────────────
    print("Creating tenant...")
    tenant = await get_create_tenant_handler().handle(
        CreateTenantCommand(name="Demo", slug="demo")
    )
    tid = tenant.id.value
    print(f"  Tenant: {tid}")

    # ── 5. Create users ──────────────────────────────────────────────
    print("Creating users...")
    # RegisterUserHandler returns str (user_id), not domain object
    owner_id = await get_register_user_handler().handle(
        RegisterUserCommand(
            email="owner@kairos.dev",
            name="Ana García",
            password="password123",
            tenant_id=tid,
            app_name="Kairos",
        )
    )
    print(f"  Owner: {owner_id} (owner@kairos.dev)")

    member_id = await get_register_user_handler().handle(
        RegisterUserCommand(
            email="dev@kairos.dev",
            name="Carlos López",
            password="password123",
            tenant_id=tid,
            app_name="Kairos",
        )
    )
    print(f"  Member: {member_id} (dev@kairos.dev)")

    # ── 6. Create organization ───────────────────────────────────────
    print("Creating organization...")
    org = await get_create_organization_handler().handle(
        CreateOrganizationCommand(
            name="Agencia Creativa",
            slug="agencia-creativa",
            owner_id=owner_id,
            tenant_id=tid,
        )
    )
    org_id = org.id.value
    print(f"  Org: {org_id} (agencia-creativa)")

    # ── 7. Invite + accept member ────────────────────────────────────
    print("Inviting member...")
    invitation = await get_invite_member_handler().handle(
        InviteMemberCommand(
            org_id=org_id,
            inviter_id=owner_id,
            invitee_email="dev@kairos.dev",
            role="MEMBER",
            tenant_id=tid,
        )
    )
    inv_id = invitation.id.value
    print(f"  Invitation: {inv_id}")

    print("Accepting invitation...")
    await get_accept_invitation_handler().handle(
        AcceptInvitationCommand(
            invitation_id=inv_id,
            user_id=member_id,
            tenant_id=tid,
        )
    )
    print("  Accepted!")

    # ── 8. Create projects ───────────────────────────────────────────
    print("Creating projects...")
    proj1 = await get_create_project_handler().handle(
        CreateProjectCommand(
            name="Rediseño Web Q1",
            description="Rediseño completo del sitio web corporativo",
            org_id=org_id,
            owner_id=owner_id,
            tenant_id=tid,
        )
    )
    p1_id = proj1.id.value
    print(f"  Project 1: {p1_id} (Rediseño Web Q1)")

    proj2 = await get_create_project_handler().handle(
        CreateProjectCommand(
            name="App Mobile v2",
            description="Segunda versión de la aplicación móvil",
            org_id=org_id,
            owner_id=owner_id,
            tenant_id=tid,
        )
    )
    p2_id = proj2.id.value
    print(f"  Project 2: {p2_id} (App Mobile v2)")

    # ── 9. Create deliverables ───────────────────────────────────────
    print("Creating deliverables...")
    # Project 1: 3 deliverables (1 APPROVED, 1 PENDING, 1 CHANGES_REQUESTED)
    d1 = await get_submit_deliverable_handler().handle(
        SubmitDeliverableCommand(
            title="Wireframes Homepage",
            url_link="https://figma.com/wireframes-homepage",
            project_id=p1_id,
            submitter_id=owner_id,
            tenant_id=tid,
        )
    )
    await get_approve_deliverable_handler().handle(
        ApproveDeliverableCommand(
            deliverable_id=d1.id.value,
            approver_id=owner_id,
            tenant_id=tid,
        )
    )
    print("  Deliverable 1: Wireframes Homepage (APPROVED)")

    await get_submit_deliverable_handler().handle(
        SubmitDeliverableCommand(
            title="Diseño UI Responsivo",
            url_link="https://figma.com/ui-responsivo",
            project_id=p1_id,
            submitter_id=member_id,
            tenant_id=tid,
        )
    )
    print("  Deliverable 2: Diseño UI Responsivo (PENDING)")

    d3 = await get_submit_deliverable_handler().handle(
        SubmitDeliverableCommand(
            title="Prototipo Interactivo",
            url_link="https://figma.com/prototipo",
            project_id=p1_id,
            submitter_id=member_id,
            tenant_id=tid,
        )
    )
    await get_request_changes_handler().handle(
        RequestChangesCommand(
            deliverable_id=d3.id.value,
            reviewer_id=owner_id,
            tenant_id=tid,
        )
    )
    print("  Deliverable 3: Prototipo Interactivo (CHANGES_REQUESTED)")

    # Project 2: 2 deliverables (both PENDING)
    await get_submit_deliverable_handler().handle(
        SubmitDeliverableCommand(
            title="Arquitectura Mobile",
            url_link="https://notion.so/arch-mobile",
            project_id=p2_id,
            submitter_id=owner_id,
            tenant_id=tid,
        )
    )
    print("  Deliverable 4: Arquitectura Mobile (PENDING)")

    await get_submit_deliverable_handler().handle(
        SubmitDeliverableCommand(
            title="Diseño UI Mobile",
            url_link="https://figma.com/ui-mobile",
            project_id=p2_id,
            submitter_id=member_id,
            tenant_id=tid,
        )
    )
    print("  Deliverable 5: Diseño UI Mobile (PENDING)")

    # ── 10. Create invoices ──────────────────────────────────────────
    print("Creating invoices...")
    inv_paid = await get_issue_invoice_handler().handle(
        IssueInvoiceCommand(
            title="Diseño UI - Enero",
            amount="2500.00",
            org_id=org_id,
            issuer_id=owner_id,
            tenant_id=tid,
        )
    )
    await get_mark_invoice_paid_handler().handle(
        MarkInvoicePaidCommand(
            invoice_id=inv_paid.id.value,
            requester_id=owner_id,
            tenant_id=tid,
        )
    )
    print("  Invoice 1: Diseño UI - Enero $2,500.00 (PAID)")

    await get_issue_invoice_handler().handle(
        IssueInvoiceCommand(
            title="Desarrollo - Febrero",
            amount="4000.00",
            org_id=org_id,
            issuer_id=owner_id,
            tenant_id=tid,
        )
    )
    print("  Invoice 2: Desarrollo - Febrero $4,000.00 (SENT)")

    await get_issue_invoice_handler().handle(
        IssueInvoiceCommand(
            title="Consultoría - Marzo",
            amount="1500.00",
            org_id=org_id,
            issuer_id=owner_id,
            tenant_id=tid,
        )
    )
    print("  Invoice 3: Consultoría - Marzo $1,500.00 (DRAFT)")

    # ── 11. Create conversations + messages ──────────────────────────
    print("Creating conversations...")
    # Org conversation
    org_conv = await get_create_conversation_handler().handle(
        CreateConversationCommand(org_id=org_id)
    )
    oc_id = org_conv.id.value
    print(f"  Org conversation: {oc_id}")

    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=oc_id,
            sender_id=owner_id,
            content="¡Bienvenidos al canal de la agencia! Aquí coordinaremos todo.",
        )
    )
    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=oc_id,
            sender_id=member_id,
            content="Perfecto, gracias Ana. Tengo listo el primer entregable del proyecto web.",
        )
    )
    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=oc_id,
            sender_id=owner_id,
            content="Genial Carlos, lo reviso hoy y te dejo feedback.",
        )
    )

    # Project 1 conversation
    p1_conv = await get_create_conversation_handler().handle(
        CreateConversationCommand(org_id=org_id, project_id=p1_id)
    )
    pc1_id = p1_conv.id.value
    print(f"  Project 1 conversation: {pc1_id}")

    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=pc1_id,
            sender_id=owner_id,
            content="Acabo de aprobar los wireframes. Podemos avanzar con el diseño UI.",
        )
    )
    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=pc1_id,
            sender_id=member_id,
            content="Perfecto, ya tengo avanzado el diseño responsivo. Lo subo hoy.",
        )
    )

    # Project 2 conversation
    p2_conv = await get_create_conversation_handler().handle(
        CreateConversationCommand(org_id=org_id, project_id=p2_id)
    )
    pc2_id = p2_conv.id.value
    print(f"  Project 2 conversation: {pc2_id}")

    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=pc2_id,
            sender_id=member_id,
            content="Subí la arquitectura del proyecto mobile. Necesito feedback antes de empezar el diseño.",
        )
    )
    await get_send_message_handler().handle(
        SendMessageCommand(
            conversation_id=pc2_id,
            sender_id=owner_id,
            content="Lo reviso mañana temprano. Se ve bien a primera vista.",
        )
    )

    # ── Done ─────────────────────────────────────────────────────────
    print("\n[OK] Seed complete!")
    print("  Login with: owner@kairos.dev / password123")
    print("  Or with:    dev@kairos.dev / password123")
    print("  Workspace slug: demo")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
