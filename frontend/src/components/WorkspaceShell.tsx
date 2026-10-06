import type { ReactNode } from "react";

import { LedgerLensMark } from "./LedgerLensMark";
import { workspaceNavigationFor, type WorkspaceView } from "../config/workspaceAccess";
import { useAuth } from "../hooks/useAuth";
import { useSystemStatus } from "../hooks/useSystemStatus";

export type { WorkspaceView } from "../config/workspaceAccess";

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
  const navigation = workspaceNavigationFor(role);

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
              <strong>{item.label}<small>{item.descriptor}</small></strong>
            </button>
          ))}
        </nav>
        <div className="rail-foot">
          <div className="rail-status">
            <span className={error ? "state-dot error" : "state-dot"} />
            <span><strong>{data ? "API online" : error ? "API offline" : "Checking systems"}</strong><small>{data ? "All systems operational" : error ? "Service unavailable" : "Reading service status"}</small></span>
          </div>
          <div className="rail-identity">
            <span className="operator-badge">{roleDetail.initials}</span>
            <span className="operator-copy"><strong>{session?.display_name}</strong><small>{roleDetail.label}</small></span>
            <button aria-label="End session" onClick={logout} type="button">›</button>
          </div>
        </div>
      </aside>
      <section className="workspace-main">
        <header className="workspace-header">
          <div>
            <span className="workspace-kicker">Northstar Union Bank / {active}</span>
            <strong>{viewDetail.label}</strong>
          </div>
          <div className="tenant-chip">
            <span aria-hidden="true">▥</span>
            <span><strong>Northstar Union Bank</strong><small>Demo environment</small></span>
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
