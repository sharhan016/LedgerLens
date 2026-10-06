import { useState } from "react";

import type { AssistantAnswer, Citation, Passage } from "../types/api";

type InspectorTab = "evidence" | "details" | "context";

export function CitationInspector({ citation, passage, queryTrace, latencyMs, showDiagnostics = false, onClose }: {
  citation: Citation;
  passage?: Passage;
  queryTrace?: AssistantAnswer["query_trace"];
  latencyMs?: Record<string, number>;
  showDiagnostics?: boolean;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<InspectorTab>("evidence");
  const tabs: InspectorTab[] = showDiagnostics ? ["evidence", "details", "context"] : ["evidence", "details"];

  return (
    <aside className="citation-inspector" aria-label="Citation evidence" aria-live="polite">
      <div className="inspector-head">
        <div className="inspector-tabs" role="tablist" aria-label="Source inspection">
          {tabs.map((item) => <button aria-selected={tab === item} className={tab === item ? "active" : ""} key={item} onClick={() => setTab(item)} role="tab" type="button">{item}</button>)}
        </div>
        <button aria-label="Close citation inspector" onClick={onClose} type="button">×</button>
      </div>

      <div className="inspector-document">
        <span className="document-glyph" aria-hidden="true">▤</span>
        <div><h2>{citation.title}</h2><span className="authorization-chip">Authorized</span><small>{citation.version}</small></div>
      </div>

      {tab === "evidence" && (
        <div className="inspector-panel" role="tabpanel">
          <h3>Relevant passage</h3>
          <p className="passage-location">{citation.page_number ? `Page ${citation.page_number}` : citation.section ?? "Document passage"}{citation.section && citation.page_number ? ` · ${citation.section}` : ""}</p>
          <blockquote>{citation.excerpt}</blockquote>
          <p className="validation-line"><span>Validation</span><strong>{passage?.validation_status ?? "authorized"}</strong></p>
        </div>
      )}

      {tab === "details" && (
        <div className="inspector-panel" role="tabpanel">
          <h3>Document details</h3>
          <dl className="source-facts">
            <div><dt>Source</dt><dd>{citation.source}</dd></div><div><dt>Version</dt><dd>{citation.version}</dd></div><div><dt>Section</dt><dd>{citation.section ?? "—"}</dd></div><div><dt>Page</dt><dd>{citation.page_number ?? "—"}</dd></div><div><dt>Channel</dt><dd>{passage?.retrieval_channel ?? "document"}</dd></div>
          </dl>
        </div>
      )}

      {tab === "context" && showDiagnostics && (
        <div className="inspector-panel" role="tabpanel">
          <h3>Retrieval context</h3>
          {passage && <div className="score-ledger">{[["Dense similarity", passage.dense_score], ["Keyword match", passage.keyword_score], ["RRF score", passage.rrf_score], ["Reranker score", passage.rerank_score]].map(([label, value]) => <div key={label as string}><span>{label}</span><strong>{typeof value === "number" ? value.toFixed(4) : "—"}</strong></div>)}</div>}
          {queryTrace && <dl className="source-facts"><div><dt>Route</dt><dd>{queryTrace.route}</dd></div><div><dt>Intent</dt><dd>{queryTrace.intent}</dd></div><div><dt>Reason</dt><dd>{queryTrace.routing_reason}</dd></div></dl>}
          {latencyMs?.total !== undefined && <p className="validation-line"><span>Total latency</span><strong>{latencyMs.total.toFixed(0)} ms</strong></p>}
        </div>
      )}
    </aside>
  );
}
