import type { components } from "./schema";

export type Category = components["schemas"]["Category"];
export type Priority = components["schemas"]["Priority"];
export type ComplaintStatus = components["schemas"]["ComplaintStatus"];
export type ComplaintCreate = components["schemas"]["ComplaintCreate"];
export type Complaint = components["schemas"]["ComplaintResponse"];
export type ComplaintListResponse = components["schemas"]["ComplaintListResponse"];
export type StatsResponse = components["schemas"]["StatsResponse"];

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly retryAfter?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
