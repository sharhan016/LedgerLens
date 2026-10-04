import type { Citation, Passage } from "../types/api";

export function CitationInspector({
  citation,
  passage,
  onClose,
}: {
  citation: Citation;
  passage?: Passage;
  onClose: () => void;
}) {
  return (
    <aside className="citation-inspector" aria-label="Citation evidence" aria-live="polite">
      <div className="inspector-head">
        <span>{citation.source_id} · source evidence</span>
        <button aria-label="Close citation inspector" onClick={onClose} type="button">×</button>
      </div>
      <h2>{citation.title}</h2>
      <dl className="source-facts">
        <div><dt>File</dt><dd>{citation.source}</dd></div>
        <div><dt>Version</dt><dd>{citation.version}</dd></div>
        <div><dt>Location</dt><dd>{citation.page_number ? `Page ${citation.page_number}` : citation.section ?? "—"}</dd></div>
        <div><dt>Channel</dt><dd>{passage?.retrieval_channel ?? "document"}</dd></div>
      </dl>
      <blockquote>{citation.excerpt}</blockquote>
      {passage && (
        <div className="score-ledger">
          <h3>Retrieval record</h3>
          {[
            ["Dense", passage.dense_score],
            ["Keyword", passage.keyword_score],
            ["RRF", passage.rrf_score],
            ["Rerank", passage.rerank_score],
          ].map(([label, value]) => (
            <div key={label as string}>
              <span>{label}</span>
              <strong>{typeof value === "number" ? value.toFixed(4) : "—"}</strong>
            </div>
          ))}
          <p>Validation · {passage.validation_status}</p>
        </div>
      )}
    </aside>
  );
}

