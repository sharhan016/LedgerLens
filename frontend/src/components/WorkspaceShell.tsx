import type { ReactNode } from "react";

import { useAuth } from "../hooks/useAuth";
import { useSystemStatus } from "../hooks/useSystemStatus";

export type WorkspaceView = "assistant" | "knowledge" | "evaluation" | "operations";

const navigation: Array<{ id: WorkspaceView; label: string; index: string }> = [
  { id: "assistant", label: "Ask LedgerLens", index: "01" },
  { id: "knowledge", label: "Knowledge base", index: "02" },
  { id: "evaluation", label: "Evaluation", index: "03" },
  { id: "operations", label: "Operations", index: "04" },
];

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

  return (
    <main className="workspace">
      <aside className="rail">
        <button className="rail-brand" onClick={() => onNavigate("assistant")} type="button">
          LL
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
              <strong>{item.label}</strong>
            </button>
          ))}
        </nav>
        <div className="rail-foot">
          <div className="api-state">
            <span className={error ? "state-dot error" : "state-dot"} />
            {data ? "API online" : error ? "API offline" : "Checking"}
          </div>
          <button className="logout-button" onClick={logout} type="button">End session</button>
        </div>
      </aside>
      <section className="workspace-main">
        <header className="workspace-header">
          <div>
            <span className="workspace-kicker">Northstar Union Bank</span>
            <strong>Knowledge evidence desk</strong>
          </div>
          <div className="operator">
            <span>{session?.display_name}</span>
            <small>{session?.user.role} · synthetic tenant</small>
          </div>
        </header>
        {children}
      </section>
    </main>
  );
}

