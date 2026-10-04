import type { CapabilityStatus } from "../types/system";

type Props = {
  capabilities: CapabilityStatus[];
};

export function CapabilityLedger({ capabilities }: Props) {
  return (
    <section className="ledger" aria-labelledby="ledger-title">
      <div className="section-heading">
        <span>Build ledger</span>
        <h2 id="ledger-title">Capability record</h2>
      </div>
      <div className="ledger-list">
        {capabilities.map((capability, index) => (
          <article className="ledger-row" key={capability.vertex_task}>
            <span className="ledger-index">{String(index + 1).padStart(2, "0")}</span>
            <div>
              <h3>{capability.name}</h3>
              <p>{capability.vertex_task} · evidence-gated increment</p>
            </div>
            <span className={`status-chip ${capability.status}`}>{capability.status}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

