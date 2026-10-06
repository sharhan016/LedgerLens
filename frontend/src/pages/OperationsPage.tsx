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

  const totalRequests = data?.metrics.reduce((sum, metric) => sum + metric.count, 0) ?? 0;
  const weightedLatency = data?.metrics.reduce((sum, metric) => sum + metric.average_latency_ms * metric.count, 0) ?? 0;
  const averageLatency = totalRequests ? weightedLatency / totalRequests : 0;
  const maximumLatency = data?.metrics.reduce((maximum, metric) => Math.max(maximum, metric.maximum_latency_ms), 0) ?? 0;
  const errorCount = data?.metrics.filter((metric) => metric.status_code >= 400).reduce((sum, metric) => sum + metric.count, 0) ?? 0;

  return (
    <div className="content-page">
      <div className="page-heading">
        <div><span>04 / Operations</span><h1>System pulse.</h1></div>
        <p>Operational telemetry records bounded routes, statuses, counts, and latency. Questions, answers, tokens, and document content are excluded.</p>
      </div>
      {error ? <div className="permission-panel"><strong>Operations access unavailable</strong><p>{error}</p></div> : data ? (
        <>
          <div className="privacy-line"><span>Content policy</span><strong>{data.content_policy}</strong></div>
          <section className="operations-summary" aria-label="Operational summary">
            <article><span>Total requests</span><strong>{totalRequests}</strong><small>Recorded API calls</small></article>
            <article><span>Average latency</span><strong>{averageLatency.toFixed(1)}<em> ms</em></strong><small>Weighted across requests</small></article>
            <article><span>Peak latency</span><strong>{maximumLatency.toFixed(1)}<em> ms</em></strong><small>Slowest recorded route</small></article>
            <article className={errorCount ? "attention" : "healthy"}><span>Errors</span><strong>{errorCount}</strong><small>{errorCount ? "Requires review" : "No failing requests"}</small></article>
          </section>
          <div className="route-ledger-heading"><strong>Route ledger</strong><span>{data.metrics.length} route states</span></div>
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
