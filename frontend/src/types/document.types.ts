export interface Document {
  id: string;
  org_id: string;
  project_id: string | null;
  uploaded_by: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  storage_path: string;
  created_at: string;
}
