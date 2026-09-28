import { useState } from "react";

import { ComplaintForm } from "../components/ComplaintForm";
import { ComplaintResult } from "../components/ComplaintResult";
import type { Complaint } from "../api/types";

export function SubmitPage() {
  const [created, setCreated] = useState<Complaint | null>(null);
  return <div className="page-grid"><ComplaintForm onCreated={setCreated} />{created ? <ComplaintResult complaint={created} /> : <aside className="aside-note"><span className="note-number">01</span><h3>One clear signal can move a whole street forward.</h3><p>Your report is triaged by the backend and placed in the operations queue.</p></aside>}</div>;
}
