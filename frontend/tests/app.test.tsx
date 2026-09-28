import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/main";

const fetchMock = vi.fn();

function complaint(overrides: Record<string, unknown> = {}) {
  return {
    id: "complaint-1",
    text: "Burst water main flooding Street 12",
    location: "Street 12",
    reporter_contact: null,
    category: "water",
    priority: "high",
    status: "open",
    ai_summary: "Burst water main flooding Street 12",
    triaged_by: "rules",
    triage_latency_ms: 1,
    created_at: "2026-09-28T00:00:00Z",
    updated_at: "2026-09-28T00:00:00Z",
    ...overrides,
  };
}

function response(body: unknown, status = 200, headers: HeadersInit = {}) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", ...headers } });
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("CivicPulse frontend workflows", () => {
  it("validates the complaint form before making a request", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(screen.getByRole("alert")).toHaveTextContent("at least 10 characters");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("submits a complaint and renders the triage result", async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValueOnce(response(complaint(), 201));
    render(<App />);
    await user.type(screen.getByPlaceholderText("What happened?"), "Burst water main flooding Street 12");
    await user.type(screen.getByPlaceholderText("Street, block, or landmark"), "Street 12");
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(await screen.findByText("Your complaint is in the queue")).toBeInTheDocument();
    expect(screen.getByText("rules")).toBeInTheDocument();
  });

  it("shows a submitting state while the request is pending", async () => {
    const user = userEvent.setup();
    fetchMock.mockReturnValueOnce(new Promise(() => undefined));
    render(<App />);
    await user.type(screen.getByPlaceholderText("What happened?"), "Burst water main flooding Street 12");
    await user.type(screen.getByPlaceholderText("Street, block, or landmark"), "Street 12");
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(screen.getByRole("button", { name: "Triage in progress..." })).toBeDisabled();
  });

  it("surfaces rate-limit errors from the backend", async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValueOnce(response({ detail: "Complaint submission rate limit exceeded" }, 429, { "Retry-After": "12" }));
    render(<App />);
    await user.type(screen.getByPlaceholderText("What happened?"), "Burst water main flooding Street 12");
    await user.type(screen.getByPlaceholderText("Street, block, or landmark"), "Street 12");
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Try again in 12");
  });

  it("loads dashboard filters and surfaces the server 409 message", async () => {
    const user = userEvent.setup();
    fetchMock
      .mockResolvedValueOnce(response({ items: [complaint()], total: 1, page: 1, page_size: 6 }))
      .mockResolvedValueOnce(response({ detail: "Invalid status transition: resolved -> open" }, 409));
    render(<App />);
    await user.click(screen.getByRole("button", { name: "Dashboard" }));
    expect(await screen.findByText("Burst water main flooding Street 12")).toBeInTheDocument();
    await user.selectOptions(screen.getByRole("combobox", { name: `Status for complaint-1` }), "resolved");
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid status transition: resolved -> open");
  });

  it("renders stats and the X-Cache response header", async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValueOnce(response({ by_category: { water: 3 }, by_priority: { high: 1 } }, 200, { "X-Cache": "HIT" }));
    render(<App />);
    await user.click(screen.getByRole("button", { name: "Stats" }));
    expect(await screen.findByText("Cache HIT")).toBeInTheDocument();
    expect(screen.getByText("water")).toBeInTheDocument();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/stats", expect.anything()));
  });
});
