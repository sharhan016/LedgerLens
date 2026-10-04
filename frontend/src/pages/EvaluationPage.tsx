import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { getEvaluation } from "../services/api";
import type { EvaluationSummary } from "../types/api";

export function EvaluationPage() {
  const { session } = useAuth();
  const [report, setReport] = useState<EvaluationSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    getEvaluation(session.access_token).then(setReport).catch((reason) => {
      setError(reason instanceof Error ? reason.message : "Evaluation unavailable");
    });
  }, [session]);

  return (
    <div className="content-page">
      <div className="page-heading">
        <div><span>03 / Evaluation</span><h1>Trust, measured.</h1></div>
        <p>The checked-in question set is executed against the synthetic banking corpus. These are repeatable retrieval signals, not decorative scores.</p>
      </div>
      {error ? <div className="permission-panel"><strong>Evaluation access unavailable</strong><p>{error}</p></div> : report ? (
        <>
          <div className="metric-marquee">
            <div><span>Recall @ 3</span><strong>{(report.recall_at_3 * 100).toFixed(0)}%</strong><small>Expected policy appears in top three</small></div>
            <div><span>Answer terms</span><strong>{(report.answer_term_coverage * 100).toFixed(0)}%</strong><small>Reference facts present in source</small></div>
            <div><span>Dataset</span><strong>{report.cases}</strong><small>{report.dataset}</small></div>
            <div className="stamp"><span>{report.status}</span></div>
          </div>
          <section className="evaluation-table">
            <div className="evaluation-row header"><span>Case</span><span>Expected evidence</span><span>Top result</span><span>Result</span></div>
            {report.per_case.map((item) => (
              <div className="evaluation-row" key={item.id}>
                <strong>{item.id}</strong><span>{item.expected_source}</span><span>{item.top_3[0]}</span><span className={item.retrieved ? "pass" : "fail"}>{item.retrieved ? "pass" : "review"}</span>
              </div>
            ))}
          </section>
        </>
      ) : <div className="loading-field">Running deterministic benchmark…</div>}
    </div>
  );
}

