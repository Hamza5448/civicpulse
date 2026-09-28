import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { useState } from "react";

import { ErrorBoundary } from "./components/ErrorBoundary";
import { DashboardPage } from "./pages/DashboardPage";
import { StatsPage } from "./pages/StatsPage";
import { SubmitPage } from "./pages/SubmitPage";
import "./styles.css";

export function App() {
  const [view, setView] = useState<"submit" | "dashboard" | "stats">("submit");
  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#submit" onClick={() => setView("submit")}>Civic<span>Pulse</span></a>
        <nav className="nav-tabs" aria-label="Primary navigation">
          {(["submit", "dashboard", "stats"] as const).map((tab) => <button key={tab} type="button" aria-current={view === tab ? "page" : undefined} onClick={() => setView(tab)}>{tab === "submit" ? "Submit" : tab === "dashboard" ? "Dashboard" : "Stats"}</button>)}
        </nav>
      </header>
      <main className="main-content">
        <section className="hero"><div><p className="eyebrow">Municipal signal desk</p><h1>Small reports. Clearer action.</h1></div><p className="hero-copy">A calmer way to send civic issues to the people who can move them forward.</p></section>
        {view === "submit" && <SubmitPage />}
        {view === "dashboard" && <DashboardPage />}
        {view === "stats" && <StatsPage />}
      </main>
    </div>
  );
}

const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <ErrorBoundary><App /></ErrorBoundary>
    </StrictMode>,
  );
}
