import type {
  Category,
  Complaint,
  ComplaintCreate,
  ComplaintListResponse,
  ComplaintStatus,
  Priority,
  StatsResponse,
} from "./types";
import { ApiError } from "./types";

const apiBaseUrl = (window.__CIVICPULSE_CONFIG__?.apiBaseUrl ?? "/api").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<{ data: T; response: Response }> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  const body = (await response.json().catch(() => ({}))) as { detail?: unknown };
  if (!response.ok) {
    const detail = body.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => (typeof item === "object" && item && "msg" in item ? item.msg : "Invalid input")).join("; ")
      : typeof detail === "string"
        ? detail
        : "The request could not be completed.";
    throw new ApiError(message, response.status, response.headers.get("Retry-After") ?? undefined);
  }
  return { data: body as T, response };
}

export function createComplaint(payload: ComplaintCreate): Promise<Complaint> {
  return request<Complaint>("/complaints", { method: "POST", body: JSON.stringify(payload) }).then(
    ({ data }) => data,
  );
}

export interface ComplaintFilters {
  category?: Category;
  priority?: Priority;
  status?: ComplaintStatus;
  page?: number;
  pageSize?: number;
}

export function listComplaints(filters: ComplaintFilters = {}): Promise<ComplaintListResponse> {
  const params = new URLSearchParams();
  if (filters.category) params.set("category", filters.category);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.status) params.set("status", filters.status);
  params.set("page", String(filters.page ?? 1));
  params.set("page_size", String(filters.pageSize ?? 10));
  return request<ComplaintListResponse>(`/complaints?${params}`).then(({ data }) => data);
}

export function updateComplaintStatus(id: string, status: ComplaintStatus): Promise<Complaint> {
  return request<Complaint>(`/complaints/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  }).then(({ data }) => data);
}

export function getStats(): Promise<{ data: StatsResponse; cacheStatus: string }> {
  return request<StatsResponse>("/stats").then(({ data, response }) => ({
    data,
    cacheStatus: response.headers.get("X-Cache") ?? "UNKNOWN",
  }));
}
