from pydantic import BaseModel


class InvoiceCreate(BaseModel):
    title: str
    amount: str  # str at HTTP boundary; handler converts to Decimal


class InvoiceResponse(BaseModel):
    id: str
    title: str
    amount: str  # str(invoice.amount) — avoids float precision loss in JSON
    org_id: str
    tenant_id: str
    status: str
    created_at: str
    paid_at: str | None
