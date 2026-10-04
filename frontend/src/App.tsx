import { CapabilityLedger } from "./components/CapabilityLedger";
import { useSystemStatus } from "./hooks/useSystemStatus";
import "./styles.css";

const plannedCapabilities = [
  { name: "API foundation", status: "ready" as const, vertex_task: "T-01" },
  { name: "Tenant security", status: "ready" as const, vertex_task: "T-02" },
  { name: "Document ingestion", status: "ready" as const, vertex_task: "T-03" },
  { name: "Hybrid retrieval", status: "ready" as const, vertex_task: "T-04" },
  { name: "Grounded answers", status: "planned" as const, vertex_task: "T-05" },
];

export default function App() {
  const { data, error, loading } = useSystemStatus();
  const capabilities = data?.capabilities ?? plannedCapabilities;

  return (
    <main>
      <header className="topbar">
        <a className="wordmark" href="#top" aria-label="LedgerLens home">
          <span className="wordmark-mark">LL</span>
          <span>LedgerLens</span>
        </a>
        <div className="system-pulse" aria-live="polite">
          <span className={error ? "pulse error" : "pulse"} />
          {loading ? "Contacting API" : error ? "API offline" : "Foundation online"}
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Evidence-led banking knowledge</p>
          <h1>
            Answers are easy.
            <span>Proof is the product.</span>
          </h1>
          <p className="lede">
            LedgerLens is being built to retrieve policy knowledge within authorization
            boundaries, show its sources, and make every generated claim inspectable.
          </p>
          <div className="hero-meta">
            <div>
              <span>Environment</span>
              <strong>{data?.environment ?? "development"}</strong>
            </div>
            <div>
              <span>Release</span>
              <strong>{data?.release ?? "0.1.0"}</strong>
            </div>
            <div>
              <span>Current gate</span>
              <strong>T-01</strong>
            </div>
          </div>
        </div>

        <aside className="evidence-card" aria-label="Design principle">
          <div className="card-label">Operating principle · 01</div>
          <blockquote>
            “A response is not complete until the reader can inspect why it exists.”
          </blockquote>
          <div className="citation-line">
            <span>Source</span>
            <span>LedgerLens architecture record</span>
          </div>
          <div className="citation-line">
            <span>Status</span>
            <span>Foundation established</span>
          </div>
        </aside>
      </section>

      {error && (
        <div className="notice" role="status">
          <strong>API connection unavailable.</strong> Showing the checked-in delivery ledger.
          Start the backend at port 8000 to see live readiness.
        </div>
      )}

      <CapabilityLedger capabilities={capabilities} />

      <footer>
        <span>Synthetic banking data only</span>
        <span>Authorization before retrieval</span>
        <span>Citations before confidence</span>
      </footer>
    </main>
  );
}
