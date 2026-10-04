import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { getMetrics } from "../services/api";
import type { OperationsMetrics } from "../types/api";

export function OperationsPage() {
  const { session } = useAuth();
  const [data, setData] = useState<OperationsMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    getMetrics(session.access_token).then(setData).catch((reason) => {
      setError(reason instanceof Error ? reason.message : "Metrics unavailable");
    });
  }, [session]);

  return (
    <div className="content-page">
      <div className="page-heading">
        <div><span>04 / Operations</span><h1>System pulse.</h1></div>
        <p>Operational telemetry records bounded routes, statuses, counts, and latency. Questions, answers, tokens, and document content are excluded.</p>
      </div>
      {error ? <div className="permission-panel"><strong>Operations access unavailable</strong><p>{error}</p></div> : data ? (
        <>
          <div className="privacy-line"><span>Content policy</span><strong>{data.content_policy}</strong></div>
          <section className="operations-grid">
            {data.metrics.map((metric) => (
              <article key={`${metric.method}-${metric.route}-${metric.status_code}`}>
                <div><span>{metric.method}</span><span>{metric.status_code}</span></div>
                <h2>{metric.route}</h2>
                <dl><div><dt>Requests</dt><dd>{metric.count}</dd></div><div><dt>Average</dt><dd>{metric.average_latency_ms.toFixed(1)} ms</dd></div><div><dt>Peak</dt><dd>{metric.maximum_latency_ms.toFixed(1)} ms</dd></div></dl>
              </article>
            ))}
          </section>
        </>
      ) : <div className="loading-field">Reading protected telemetry…</div>}
    </div>
  );
}

