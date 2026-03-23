export enum InvoiceStatus {
  DRAFT = "DRAFT",
  SENT = "SENT",
  PAID = "PAID",
}

export interface Invoice {
  id: string;
  title: string;
  amount: string;
  org_id: string;
  tenant_id: string;
  status: InvoiceStatus;
  created_at: string;
  paid_at: string | null;
}

export interface CreateInvoiceDto {
  title: string;
  amount: string;
}
