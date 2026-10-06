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
  const [classification, setClassification] = useState("internal");
  const [accessPreset, setAccessPreset] = useState("analyst,compliance,admin");
  const [status, setStatus] = useState<string | null>(null);
  const canIngest = session?.user.role === "compliance" || session?.user.role === "admin";
  const isAdmin = session?.user.role === "admin";

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
        classification: isAdmin ? classification : "internal",
        allowedRoles: isAdmin ? accessPreset : "analyst,compliance,admin",
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
        <aside className={`ingestion-desk ${isAdmin ? "admin-governance" : ""}`}>
          <span className="section-label">{isAdmin ? "Governance controls" : "Ingestion desk"}</span>
          <h2>{isAdmin ? "Add and classify knowledge" : canIngest ? "Add governed knowledge" : "Read-only access"}</h2>
          {canIngest ? (
            <form onSubmit={(event) => void submit(event)}>
              <label htmlFor="policy-file">Policy file<input accept=".md,.txt,.pdf" id="policy-file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} type="file" /></label>
              <label htmlFor="document-title">Document title<input id="document-title" onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Retail KYC Manual" value={title} /></label>
              <label htmlFor="document-version">Version<input id="document-version" onChange={(event) => setVersion(event.target.value)} value={version} /></label>
              {isAdmin ? (
                <div className="governance-fields">
                  <label htmlFor="document-classification">Classification<select id="document-classification" onChange={(event) => setClassification(event.target.value)} value={classification}><option value="internal">Internal</option><option value="restricted">Restricted</option><option value="confidential">Confidential</option></select></label>
                  <label htmlFor="document-visibility">Visible to<select id="document-visibility" onChange={(event) => setAccessPreset(event.target.value)} value={accessPreset}><option value="viewer,analyst,compliance,admin">All authorized users</option><option value="analyst,compliance,admin">Policy staff</option><option value="compliance,admin">Compliance and Admin</option><option value="admin">Admin only</option></select></label>
                </div>
              ) : <p className="access-preset"><strong>Access preset</strong><span>Policy staff · Analyst, Compliance and Admin</span></p>}
              <button disabled={!file || !title} type="submit">Ingest, chunk & index</button>
              {status && <p className="ingestion-status" role="status">{status}</p>}
            </form>
          ) : <p>Your Analyst role can inspect authorized sources but cannot change document content, classification, or visibility.</p>}
          <div className="format-note"><strong>Accepted</strong><span>Markdown · Text · PDF</span><strong>Limit</strong><span>10 MB per file</span></div>
        </aside>
      </div>
    </div>
  );
}
