import { useState, type FormEvent } from "react";

import { createComplaint } from "../api/client";
import type { Complaint } from "../api/types";
import { ApiError } from "../api/types";

interface Props {
  onCreated: (complaint: Complaint) => void;
}

export function ComplaintForm({ onCreated }: Props) {
  const [text, setText] = useState("");
  const [location, setLocation] = useState("");
  const [contact, setContact] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (text.trim().length < 10) {
      setError("Please describe the complaint in at least 10 characters.");
      return;
    }
    if (location.trim().length < 3) {
      setError("Please provide a location.");
      return;
    }
    setSubmitting(true);
    try {
      const complaint = await createComplaint({
        text: text.trim(),
        location: location.trim(),
        ...(contact.trim() ? { reporter_contact: contact.trim() } : {}),
      });
      onCreated(complaint);
      setText("");
      setLocation("");
      setContact("");
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.status === 429 ? `${caught.message} Try again in ${caught.retryAfter ?? "a moment"}.` : caught.message);
      } else {
        setError("Submission failed. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="form-panel" onSubmit={submit} noValidate>
      <div className="section-heading">
        <p className="eyebrow">New signal</p>
        <h2>Tell us what needs attention</h2>
        <p>Describe the issue plainly. The system will triage it for the operations team.</p>
      </div>
      <label htmlFor="complaint-text">
        Complaint
        <textarea id="complaint-text" value={text} onChange={(event) => setText(event.target.value)} placeholder="What happened?" minLength={10} maxLength={2000} required />
        <span className="field-hint">{text.length}/2000</span>
      </label>
      <label htmlFor="complaint-location">
        Location
        <input id="complaint-location" value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Street, block, or landmark" minLength={3} maxLength={200} required />
      </label>
      <label htmlFor="complaint-contact">
        Contact <span className="optional">optional</span>
        <input id="complaint-contact" value={contact} onChange={(event) => setContact(event.target.value)} placeholder="Phone or email" maxLength={255} />
      </label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? "Triage in progress..." : "Submit complaint"}
      </button>
    </form>
  );
}
