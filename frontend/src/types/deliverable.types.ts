export enum DeliverableStatus {
  PENDING = "PENDING",
  APPROVED = "APPROVED",
  CHANGES_REQUESTED = "CHANGES_REQUESTED",
}

export interface Deliverable {
  id: string;
  title: string;
  url_link: string;
  project_id: string;
  tenant_id: string;
  status: DeliverableStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateDeliverableDto {
  title: string;
  url_link: string;
}
