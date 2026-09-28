import type { Complaint } from "../api/types";

export function ComplaintResult({ complaint }: { complaint: Complaint }) {
  return (
    <section className="result-panel" aria-live="polite">
      <p className="eyebrow">Received</p>
      <h2>Your complaint is in the queue</h2>
      <div className="result-grid">
        <div><span>Category</span><strong>{complaint.category}</strong></div>
        <div><span>Priority</span><strong className={`priority-${complaint.priority}`}>{complaint.priority}</strong></div>
        <div><span>Status</span><strong>{complaint.status.replace("_", " ")}</strong></div>
        <div><span>Provider</span><strong>{complaint.triaged_by ?? "pending"}</strong></div>
      </div>
      {complaint.ai_summary && <p className="summary">“{complaint.ai_summary}”</p>}
    </section>
  );
}
