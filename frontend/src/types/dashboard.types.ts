export interface DashboardStats {
  organizations_count: number;
  projects_total: number;
  projects_active: number;
  projects_completed: number;
  deliverables_total: number;
  deliverables_pending: number;
  deliverables_approved: number;
  deliverables_changes_requested: number;
  invoices_total_amount: string;
  invoices_paid_amount: string;
  invoices_pending_amount: string;
}
