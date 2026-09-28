import { useEffect, useState } from "react";

import { getStats } from "../api/client";
import type { StatsResponse } from "../api/types";

export function StatsPanel() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [cacheStatus, setCacheStatus] = useState("UNKNOWN");
  const [error, setError] = useState("");
  useEffect(() => {
    getStats().then((result) => { setStats(result.data); setCacheStatus(result.cacheStatus); }).catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load statistics."));
  }, []);
  if (error) return <section className="dashboard-panel"><p className="form-error" role="alert">{error}</p></section>;
  if (!stats) return <section className="dashboard-panel"><p className="loading-state">Loading statistics...</p></section>;
  return <section className="dashboard-panel stats-panel"><div className="section-heading row-heading"><div><p className="eyebrow">Pulse check</p><h2>What residents are reporting</h2></div><span className={`cache-badge cache-${cacheStatus.toLowerCase()}`}>Cache {cacheStatus}</span></div><div className="stats-columns"><div><h3>By category</h3>{Object.entries(stats.by_category).map(([key, value]) => <div className="stat-line" key={key}><span>{key}</span><strong>{value}</strong></div>)}</div><div><h3>By priority</h3>{Object.entries(stats.by_priority).map(([key, value]) => <div className="stat-line" key={key}><span>{key}</span><strong>{value}</strong></div>)}</div></div></section>;
}
