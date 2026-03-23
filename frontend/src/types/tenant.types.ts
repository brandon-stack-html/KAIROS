export interface Tenant {
  id: string;
  name: string;
  slug: string;
}

export interface CreateTenantDto {
  name: string;
  slug: string;
}
