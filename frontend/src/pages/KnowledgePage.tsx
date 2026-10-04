import { useEffect, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { ingestDocument, listDocuments } from "../services/api";
import type { DocumentSummary } from "../types/api";

export function KnowledgePage() {
  const { session } = useAuth();
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [version, setVersion] = useState("2026.1");
  const [status, setStatus] = useState<string | null>(null);
  const canIngest = session?.user.role === "compliance" || session?.user.role === "admin";

  function refresh() {
    if (!session) return;
    listDocuments(session.access_token).then(setDocuments).catch(() => setDocuments([]));
  }

  useEffect(refresh, [session]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!session || !file || !title) return;
    setStatus("Parsing and indexing…");
    try {
      const result = await ingestDocument(session.access_token, file, {
        title,
        version,
        classification: "internal",
      });
      setStatus(`Ready · ${result.chunks.length} chunks · ${result.document_id.slice(0, 8)}`);
      setFile(null);
      setTitle("");
      refresh();
    } catch (reason) {
      setStatus(reason instanceof Error ? reason.message : "Ingestion failed");
    }
  }

  return (
    <div className="content-page">
      <div className="page-heading">
        <div><span>02 / Knowledge base</span><h1>Source register.</h1></div>
        <p>Every document retains its tenant, version, source, visibility, location, and ingestion status through retrieval.</p>
      </div>
      <div className="knowledge-grid">
        <section className="document-register">
          <div className="register-head"><span>{documents.length} authorized documents</span><span>Status</span></div>
          {documents.length ? documents.map((document, index) => (
            <article key={document.id}>
              <span className="row-number">{String(index + 1).padStart(2, "0")}</span>
              <div><h2>{document.title}</h2><p>{document.source_type} · version {document.version}</p></div>
              <span className={`document-status ${document.status}`}>{document.status}</span>
            </article>
          )) : <div className="register-empty">No documents are visible for this persona yet.</div>}
        </section>
        <aside className="ingestion-desk">
          <span className="section-label">Ingestion desk</span>
          <h2>{canIngest ? "Add governed knowledge" : "Read-only access"}</h2>
          {canIngest ? (
            <form onSubmit={(event) => void submit(event)}>
              <label>Policy file<input accept=".md,.txt,.pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} type="file" /></label>
              <label>Document title<input onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Retail KYC Manual" value={title} /></label>
              <label>Version<input onChange={(event) => setVersion(event.target.value)} value={version} /></label>
              <button disabled={!file || !title} type="submit">Ingest, chunk & index</button>
              {status && <p className="ingestion-status" role="status">{status}</p>}
            </form>
          ) : <p>Your analyst role can inspect authorized sources but cannot change the knowledge base.</p>}
          <div className="format-note"><strong>Accepted</strong><span>Markdown · Text · PDF</span><strong>Limit</strong><span>10 MB per file</span></div>
        </aside>
      </div>
    </div>
  );
}

