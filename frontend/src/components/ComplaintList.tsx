import { useEffect, useState } from "react";

import { listComplaints, updateComplaintStatus, type ComplaintFilters } from "../api/client";
import type { Category, Complaint, ComplaintStatus, Priority } from "../api/types";
import { ApiError } from "../api/types";

const categories: Category[] = ["water", "electricity", "sanitation", "roads", "streetlights", "other"];
const priorities: Priority[] = ["high", "normal", "low"];
const statuses: ComplaintStatus[] = ["open", "in_progress", "resolved", "rejected"];

export function ComplaintList() {
  const [items, setItems] = useState<Complaint[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<ComplaintFilters>({ pageSize: 6 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusError, setStatusError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    listComplaints({ ...filters, page })
      .then((result) => {
        if (active) { setItems(result.items); setTotal(result.total); setError(""); }
      })
      .catch((caught) => { if (active) setError(caught instanceof Error ? caught.message : "Could not load complaints."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [filters, page]);

  function changeFilter(key: keyof ComplaintFilters, value: string) {
    setPage(1);
    setFilters((current) => ({ ...current, [key]: value || undefined }));
  }

  async function changeStatus(complaint: Complaint, value: ComplaintStatus) {
    setStatusError("");
    try {
      const updated = await updateComplaintStatus(complaint.id, value);
      setItems((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch (caught) {
      setStatusError(caught instanceof ApiError ? caught.message : "Status update failed.");
    }
  }

  const pageCount = Math.max(1, Math.ceil(total / (filters.pageSize ?? 6)));
  return (
    <section className="dashboard-panel">
      <div className="section-heading row-heading">
        <div><p className="eyebrow">Operations view</p><h2>Complaint queue</h2></div>
        <span className="count-label">{total} total</span>
      </div>
      <div className="filters" aria-label="Complaint filters">
        <select aria-label="Category filter" value={filters.category ?? ""} onChange={(event) => changeFilter("category", event.target.value)}><option value="">All categories</option>{categories.map((value) => <option key={value} value={value}>{value}</option>)}</select>
        <select aria-label="Priority filter" value={filters.priority ?? ""} onChange={(event) => changeFilter("priority", event.target.value)}><option value="">All priorities</option>{priorities.map((value) => <option key={value} value={value}>{value}</option>)}</select>
        <select aria-label="Status filter" value={filters.status ?? ""} onChange={(event) => changeFilter("status", event.target.value)}><option value="">All statuses</option>{statuses.map((value) => <option key={value} value={value}>{value.replace("_", " ")}</option>)}</select>
      </div>
      {statusError && <p className="form-error" role="alert">{statusError}</p>}
      {loading && <p className="loading-state">Loading the queue...</p>}
      {!loading && error && <p className="form-error" role="alert">{error}</p>}
      {!loading && !error && items.length === 0 && <p className="empty-state">No complaints match these filters.</p>}
      {!loading && !error && items.length > 0 && <div className="complaint-table">{items.map((complaint) => <article className="complaint-row" key={complaint.id}><div><span className="row-category">{complaint.category} · {complaint.priority}</span><h3>{complaint.text}</h3><p>{complaint.location}</p></div><label className="status-control">Status<select aria-label={`Status for ${complaint.id}`} value={complaint.status} onChange={(event) => changeStatus(complaint, event.target.value as ComplaintStatus)}>{statuses.map((value) => <option key={value} value={value}>{value.replace("_", " ")}</option>)}</select></label></article>)}</div>}
      <div className="pagination"><button type="button" disabled={page <= 1 || loading} onClick={() => setPage((current) => current - 1)}>Previous</button><span>Page {page} of {pageCount}</span><button type="button" disabled={page >= pageCount || loading} onClick={() => setPage((current) => current + 1)}>Next</button></div>
    </section>
  );
}
