import type { ReactNode } from "react";

import { LedgerLensMark } from "./LedgerLensMark";
import { useAuth } from "../hooks/useAuth";
import { useSystemStatus } from "../hooks/useSystemStatus";

export type WorkspaceView = "assistant" | "knowledge" | "evaluation" | "operations";

const navigation: Array<{ id: WorkspaceView; label: string; index: string }> = [
  { id: "assistant", label: "Ask LedgerLens", index: "01" },
  { id: "knowledge", label: "Knowledge base", index: "02" },
  { id: "evaluation", label: "Evaluation", index: "03" },
  { id: "operations", label: "Operations", index: "04" },
];

const viewDetails: Record<WorkspaceView, { label: string; descriptor: string }> = {
  assistant: { label: "Evidence desk", descriptor: "Ask · retrieve · verify" },
  knowledge: { label: "Source register", descriptor: "Ingest · classify · govern" },
  evaluation: { label: "Trust benchmark", descriptor: "Measure · compare · review" },
  operations: { label: "System ledger", descriptor: "Observe · protect · account" },
};

const roleDetails = {
  analyst: { initials: "AN", label: "Policy analyst", access: "Standard policy library" },
  compliance: { initials: "CO", label: "Compliance officer", access: "Restricted policies + audit traces" },
  admin: { initials: "KA", label: "Knowledge admin", access: "Ingestion + system settings" },
  viewer: { initials: "VI", label: "Viewer", access: "Read-only policy access" },
};

export function WorkspaceShell({
  active,
  onNavigate,
  children,
}: {
  active: WorkspaceView;
  onNavigate: (view: WorkspaceView) => void;
  children: ReactNode;
}) {
  const { session, logout } = useAuth();
  const { data, error } = useSystemStatus();
  const role = session?.user.role ?? "viewer";
  const roleDetail = roleDetails[role];
  const viewDetail = viewDetails[active];

  return (
    <main className={`workspace brand-workspace role-${role}`}>
      <aside className="rail">
        <button className="rail-brand" onClick={() => onNavigate("assistant")} type="button" aria-label="Open evidence desk">
          <LedgerLensMark compact />
          <span>LedgerLens</span>
        </button>
        <nav aria-label="Workspace navigation">
          {navigation.map((item) => (
            <button
              className={active === item.id ? "nav-item active" : "nav-item"}
              key={item.id}
              onClick={() => onNavigate(item.id)}
              type="button"
            >
              <span>{item.index}</span>
              <strong>{item.label}<small>{viewDetails[item.id].descriptor}</small></strong>
            </button>
          ))}
        </nav>
        <div className="rail-foot">
          <div className="api-state">
            <span className={error ? "state-dot error" : "state-dot"} />
            {data ? "API online" : error ? "API offline" : "Checking"}
          </div>
          <button className="logout-button" onClick={logout} type="button">End session <span>↗</span></button>
        </div>
      </aside>
      <section className="workspace-main">
        <header className="workspace-header">
          <div>
            <span className="workspace-kicker">Northstar Union Bank / {active}</span>
            <strong>{viewDetail.label}</strong>
          </div>
          <div className="operator">
            <span className="operator-badge">{roleDetail.initials}</span>
            <span className="operator-copy"><strong>{session?.display_name}</strong><small>{roleDetail.label} · Demo environment</small></span>
          </div>
        </header>
        <div className="workspace-context" role="status">
          <span>Active access</span>
          <strong>{roleDetail.access}</strong>
          <small>Policy · Proof · Provenance</small>
        </div>
        {children}
      </section>
    </main>
  );
}
