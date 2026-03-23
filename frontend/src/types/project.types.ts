export enum ProjectStatus {
  ACTIVE = "ACTIVE",
  COMPLETED = "COMPLETED",
}

export interface Project {
  id: string;
  name: string;
  description: string;
  org_id: string;
  tenant_id: string;
  status: ProjectStatus;
  created_at: string;
}

export interface CreateProjectDto {
  name: string;
  description: string;
  org_id: string;
}
