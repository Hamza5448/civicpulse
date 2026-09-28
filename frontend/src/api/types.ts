export type Category =
  | "water"
  | "electricity"
  | "sanitation"
  | "roads"
  | "streetlights"
  | "other";
export type Priority = "high" | "normal" | "low";
export type ComplaintStatus = "open" | "in_progress" | "resolved" | "rejected";

export interface ComplaintCreate {
  text: string;
  location: string;
  reporter_contact?: string;
}

export interface Complaint {
  id: string;
  text: string;
  location: string;
  reporter_contact: string | null;
  category: Category;
  priority: Priority;
  status: ComplaintStatus;
  ai_summary: string | null;
  triaged_by: string | null;
  triage_latency_ms: number | null;
  created_at: string;
  updated_at: string;
}

export interface ComplaintListResponse {
  items: Complaint[];
  total: number;
  page: number;
  page_size: number;
}

export interface StatsResponse {
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
}

export interface ApiErrorPayload {
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }>;
}

export class ApiError extends Error {
  status: number;
  retryAfter?: string;

  constructor(message: string, status: number, retryAfter?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryAfter = retryAfter;
  }
}
