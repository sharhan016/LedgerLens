import { useAuth } from "../hooks/useAuth";
import type { Role } from "../types/api";

const personas: Array<{ role: Role; name: string; remit: string; code: string }> = [
  { role: "analyst", name: "Asha Rao", remit: "Policy research & customer guidance", code: "AN" },
  { role: "compliance", name: "Mira Fernandes", remit: "Restricted policy & audit review", code: "CO" },
  { role: "admin", name: "Dev Malhotra", remit: "Knowledge operations & ingestion", code: "AD" },
];

export function LoginPage() {
  const { login, loading, error } = useAuth();

  return (
    <main className="login-page">
      <header className="login-header">
        <div className="wordmark">
          <span className="wordmark-mark">LL</span>
          <span>LedgerLens</span>
        </div>
        <span className="demo-ribbon">Synthetic environment · no customer data</span>
      </header>
      <section className="login-hero">
        <div>
          <p className="eyebrow">Authorization comes first</p>
          <h1>
            Enter the evidence
            <em> room.</em>
          </h1>
          <p className="lede">
            Choose a synthetic persona to inspect how the same banking knowledge behaves
            across role boundaries. Every answer keeps its sources, scores, routing, and
            grounding record attached.
          </p>
        </div>
        <div className="persona-stack" aria-label="Demo personas">
          {personas.map((persona, index) => (
            <button
              className="persona-card"
              disabled={loading}
              key={persona.role}
              onClick={() => void login(persona.role)}
              style={{ "--delay": `${index * 90}ms` } as React.CSSProperties}
              type="button"
            >
              <span className="persona-code">{persona.code}</span>
              <span>
                <strong>{persona.name}</strong>
                <small>{persona.remit}</small>
              </span>
              <span className="persona-role">{persona.role}</span>
              <span className="arrow" aria-hidden="true">↗</span>
            </button>
          ))}
          {error && <p className="form-error" role="alert">{error}</p>}
        </div>
      </section>
      <footer className="login-footer">
        <span>Northstar Union Bank / fictional</span>
        <span>Inspectable retrieval · cited generation · evidence ledger</span>
      </footer>
    </main>
  );
}

