import { useState } from "react";

type Group = "auth" | "query" | "retrieve" | "answer" | "observe";

type NodeDetail = {
  id: string;
  step: string;
  title: string;
  group: Group;
  what: string;
  why: string;
  input: string;
  output: string;
  technology: string;
  safeguard: string;
};

const nodes: NodeDetail[] = [
  { id: "question", step: "01", title: "User question", group: "auth", what: "Receives the natural-language question from the Assistant workspace.", why: "The original wording must remain available to the answer provider.", input: "Question string", output: "Authenticated assistant request", technology: "React → POST /api/v1/assistant/ask", safeguard: "The request cannot supply its own tenant or role." },
  { id: "principal", step: "02", title: "JWT principal", group: "auth", what: "Resolves user, tenant, role, and permissions from the bearer token.", why: "Every later data operation needs a trusted security context.", input: "Authorization: Bearer JWT", output: "Principal { user_id, tenant_id, role }", technology: "FastAPI authentication dependency", safeguard: "Invalid or absent credentials fail before assistant processing." },
  { id: "permission", step: "03", title: "Permission check", group: "auth", what: "Requires documents:read before retrieval can begin.", why: "Evidence access is a server-side capability, not a UI state.", input: "Principal + required permission", output: "Allowed request or 403", technology: "Permission.DOCUMENTS_READ", safeguard: "The check runs on every protected request." },
  { id: "normalize", step: "04", title: "Query normalization", group: "query", what: "Collapses whitespace and rejects retrieval queries shorter than three characters.", why: "Dense and keyword retrieval need the same stable query form.", input: "Planner retrieval_query", output: "Normalized query", technology: "HybridRetrievalOrchestrator", safeguard: "Normalization does not replace the original question used for generation." },
  { id: "planner", step: "05", title: "Deterministic planner", group: "query", what: "Classifies intent, expands known banking terms, and selects a retrieval route.", why: "Some questions need governed documents plus structured or regulatory sources.", input: "Original question", output: "intent + route + retrieval_query", technology: "RuleBasedQueryPlanner", safeguard: "The chosen route is returned in the trace and written to audit." },
  { id: "dense", step: "06A", title: "Dense retrieval", group: "retrieve", what: "Ranks semantically similar chunks using the embedded query.", why: "Semantic similarity catches paraphrases and related policy language.", input: "384d vector + tenant + role", output: "Up to 30 candidates", technology: "PostgreSQL + pgvector", safeguard: "tenant_id and allowed_roles filter before ranking." },
  { id: "keyword", step: "06B", title: "Keyword retrieval", group: "retrieve", what: "Ranks exact policy terminology with PostgreSQL full-text search.", why: "Names, identifiers, and regulated phrases benefit from lexical matching.", input: "Normalized query + tenant + role", output: "Up to 30 candidates", technology: "PostgreSQL FTS", safeguard: "The same tenant and role predicates apply independently." },
  { id: "rrf", step: "07", title: "RRF fusion", group: "retrieve", what: "Combines independently ranked dense and keyword results using 1 / (60 + rank).", why: "Rank fusion avoids comparing incompatible raw score scales.", input: "Authorized dense + keyword rankings", output: "One fused candidate order", technology: "Reciprocal Rank Fusion · constant 60", safeguard: "Only candidates passing the authorization guard are fused." },
  { id: "rerank", step: "08", title: "Reranking", group: "retrieve", what: "Scores query–passage relevance again after fusion.", why: "A second relevance pass improves the evidence order.", input: "Query + fused candidates", output: "Relevance-scored candidates", technology: "cross-encoder/ms-marco-MiniLM-L-6-v2; token-overlap demo fallback", safeguard: "Demo mode remains deterministic and reproducible." },
  { id: "evidence", step: "09", title: "Evidence selection", group: "retrieve", what: "Selects at most eight passages and labels them S1–S8.", why: "A bounded context keeps provenance inspectable.", input: "Reranked candidates", output: "Context + source metadata", technology: "RoutedRetrievalOrchestrator + ContextBuilder", safeguard: "Supplemental SQL/API results are deduplicated and validated." },
  { id: "authorization", step: "10", title: "Authorized evidence", group: "auth", what: "Rechecks tenant, role, content, and source integrity after retrieval.", why: "New adapters must not weaken the access invariant.", input: "Candidate passages", output: "Fail-closed authorized set", technology: "RetrievalValidator", safeguard: "Defense in depth after database-level filtering." },
  { id: "cache", step: "11", title: "Semantic cache", group: "answer", what: "Looks for a reusable generation only after the evidence set is known.", why: "A cached answer must correspond to the same authorized context.", input: "Query vector + knowledge version + context fingerprint", output: "Cached generation or miss", technology: "PostgreSQL pgvector · 0.92 threshold · 60-minute TTL", safeguard: "Scoped by tenant, role, provider, knowledge version, evidence fingerprint, and expiry." },
  { id: "generator", step: "12", title: "Generator", group: "answer", what: "Composes an answer from labeled evidence or uses the deterministic extractive provider.", why: "The model writes the response; it does not choose authorization.", input: "Original question + S1–S8 context", output: "Answer + cited source IDs", technology: "DemoExtractiveProvider or OpenAI-compatible provider", safeguard: "LLM mode uses temperature 0 and evidence-only instructions." },
  { id: "grounding", step: "13", title: "Grounding validator", group: "answer", what: "Checks citation validity, claim coverage, lexical support, and retrieval quality.", why: "Fluency alone does not establish that an answer is supported.", input: "Generation + ContextSource records", output: "grounded + confidence + unsupported claims", technology: "Deterministic lexical grounding; not semantic entailment", safeguard: "Invalid citations or unsupported claims make the answer ungrounded." },
  { id: "answer", step: "14", title: "Cited answer", group: "answer", what: "Returns the answer, citations, passages, scores, route trace, and latency.", why: "A technical reviewer can inspect how the answer was produced.", input: "Validated generation", output: "AssistantResponse", technology: "FastAPI schema + React evidence inspector", safeguard: "No evidence produces an explicit abstention response." },
  { id: "audit", step: "15", title: "Conversation + audit", group: "observe", what: "Persists the exchange and an audit event after validation.", why: "Answer history and governance need durable evidence.", input: "Question, answer, route, grounding, cache state", output: "Conversation + audit_event", technology: "PostgreSQL", safeguard: "Audit stores the question SHA-256 rather than the raw question." },
  { id: "telemetry", step: "16", title: "Telemetry", group: "observe", what: "Records route-level status, count, and latency information.", why: "Operators need health signals without user content.", input: "HTTP request lifecycle", output: "Operational metrics", technology: "FastAPI observability middleware", safeguard: "No questions, answers, tokens, or document content are recorded." },
];

const ingestion = [
  ["Sources", "PDF / Markdown / TXT", "Documents enter with a SHA-256 source identity."],
  ["Parser", "Format-aware parsing", "PDF pages, Markdown headings, and text provenance are retained."],
  ["Boundary", "UTF-8-safe 512 KiB", "Processing boundary—not an embedding chunk size."],
  ["Chunk", "180 / 30 / 150 words", "Maximum / overlap / step; never crosses a source segment."],
  ["Embed", "384-dimensional vector", "all-MiniLM-L6-v2 or deterministic demo vectors."],
  ["Persist", "PostgreSQL + pgvector", "Text, vector, source, version, tenant, and roles."],
];

function Mark() { return <span className="architecture-console-mark" aria-hidden="true">LL</span>; }

function DiagramNode({ item, selected, onSelect }: { item: NodeDetail; selected: boolean; onSelect: (item: NodeDetail) => void }) {
  return <button className={`architecture-diagram-node group-${item.group}${selected ? " selected" : ""}`} aria-pressed={selected} onClick={() => onSelect(item)}>
    <small>{item.step}</small><strong>{item.title}</strong>
  </button>;
}

function DetailPanel({ item }: { item: NodeDetail }) {
  return <aside className="architecture-node-detail" aria-live="polite">
    <header><span>{item.step} / {item.group}</span><h3>{item.title}</h3></header>
    <div className="architecture-detail-fields">
      <div><small>What it does</small><p>{item.what}</p></div><div><small>Why it exists</small><p>{item.why}</p></div>
      <div><small>Input</small><p>{item.input}</p></div><div><small>Output</small><p>{item.output}</p></div>
      <div><small>Implementation</small><p>{item.technology}</p></div><div><small>Decision / safeguard</small><p>{item.safeguard}</p></div>
    </div>
  </aside>;
}

export function ArchitecturePage() {
  const [selectedId, setSelectedId] = useState("rrf");
  const selected = nodes.find((node) => node.id === selectedId) ?? nodes[0];
  const select = (node: NodeDetail) => setSelectedId(node.id);

  return <main className="architecture-console">
    <header className="architecture-console-nav">
      <a href="/" className="architecture-console-wordmark" aria-label="LedgerLens home"><Mark /><span>LedgerLens</span></a>
      <span className="architecture-console-path">/ architecture / ai systems</span>
      <a href="/" className="architecture-console-exit">Workspace <span>↗</span></a>
    </header>

    <section className="architecture-console-intro" aria-labelledby="architecture-title">
      <div><p className="architecture-console-kicker">System walkthrough · implementation map</p><h1 id="architecture-title">How a question becomes a cited answer</h1><p>Click any node to inspect its boundary, data contract, implementation, and safeguard. This map follows the real request lifecycle from JWT principal to persisted audit.</p></div>
      <dl><div><dt>Evidence context</dt><dd>S1–S8</dd></div><div><dt>Candidate pool</dt><dd>30 + 30</dd></div><div><dt>RRF constant</dt><dd>60</dd></div><div><dt>Vector width</dt><dd>384d</dd></div></dl>
    </section>

    <section className="architecture-console-section" aria-labelledby="overview-title">
      <div className="architecture-console-heading"><span>01 / System overview</span><h2 id="overview-title">Question lifecycle</h2><p>The split lane is dense and keyword retrieval. Colors identify authentication, query planning, retrieval, answer generation, and observability.</p></div>
      <div className="architecture-overview-diagram" aria-label="Interactive question lifecycle architecture diagram">
        <div className="architecture-diagram-row primary-row">
          {nodes.slice(0, 5).map((item, index) => <div className="architecture-node-wrap" key={item.id}><DiagramNode item={item} selected={selected.id === item.id} onSelect={select} />{index < 4 && <i aria-hidden="true">→</i>}</div>)}
        </div>
        <div className="architecture-split-label"><span>parallel authorized retrieval</span></div>
        <div className="architecture-retrieval-branch">
          <div className="architecture-parallel-nodes"><DiagramNode item={nodes[5]} selected={selected.id === "dense"} onSelect={select} /><DiagramNode item={nodes[6]} selected={selected.id === "keyword"} onSelect={select} /></div>
          <i aria-hidden="true">⇢</i>
          {nodes.slice(7).map((item, index, list) => <div className="architecture-node-wrap" key={item.id}><DiagramNode item={item} selected={selected.id === item.id} onSelect={select} />{index < list.length - 1 && <i aria-hidden="true">→</i>}</div>)}
        </div>
      </div>
      <DetailPanel item={selected} />
      <div className="architecture-legend"><span><i className="legend-auth" /> auth</span><span><i className="legend-query" /> planning</span><span><i className="legend-retrieve" /> retrieval</span><span><i className="legend-answer" /> answer</span><span><i className="legend-observe" /> observability</span></div>
    </section>

    <section className="architecture-console-section dark" aria-labelledby="ingestion-title">
      <div className="architecture-console-heading"><span>02 / Ingestion pipeline</span><h2 id="ingestion-title">Documents become governed chunks</h2><p>Ingestion preserves provenance, creates bounded semantic units, embeds them, and persists authorization metadata with the vector.</p></div>
      <div className="architecture-ingestion-diagram">{ingestion.map(([label, title, text], index) => <div className="architecture-ingestion-wrap" key={label}><details><summary><small>{label}</small><strong>{title}</strong></summary><p>{text}</p></details>{index < ingestion.length - 1 && <i aria-hidden="true">→</i>}</div>)}</div>
      <div className="architecture-fact-strip"><span><b>512 KiB</b> UTF-8 source safety boundary</span><span><b>180 / 30 / 150</b> max / overlap / step</span><span><b>Never crosses</b> source segments</span></div>
    </section>

    <section className="architecture-console-section" aria-labelledby="retrieval-title">
      <div className="architecture-console-heading"><span>03 / Query & retrieval</span><h2 id="retrieval-title">Two signals, one ranked context</h2><p>The planner can add structured SQL and regulatory sources; the routed orchestrator then deduplicates, validates, reranks, and selects.</p></div>
      <div className="architecture-linear-diagram retrieval-detail">
        <button onClick={() => select(nodes[4])}><b>Planner</b><small>4 deterministic routes</small></button><i>→</i>
        <div><button onClick={() => select(nodes[5])}><b>Dense</b><small>pgvector · top 30</small></button><button onClick={() => select(nodes[6])}><b>Keyword</b><small>FTS · top 30</small></button></div><i>→</i>
        <button onClick={() => select(nodes[7])}><b>RRF</b><small>Σ 1/(60 + rank)</small></button><i>→</i><button onClick={() => select(nodes[8])}><b>Rerank</b><small>CrossEncoder / demo</small></button><i>→</i><button onClick={() => select(nodes[9])}><b>Evidence</b><small>S1–S8</small></button>
      </div>
      <p className="architecture-route-strip"><b>Routes</b> hybrid_knowledge <span>·</span> hybrid_sql <span>·</span> hybrid_api <span>·</span> hybrid_sql_api</p>
    </section>

    <section className="architecture-console-section answer-section" aria-labelledby="answer-title">
      <div className="architecture-console-heading"><span>04 / Answer pipeline</span><h2 id="answer-title">The model is downstream of evidence</h2><p>The LLM is called only when authorized evidence exists and there is no valid semantic-cache hit.</p></div>
      <div className="architecture-linear-diagram answer-detail"><button onClick={() => select(nodes[10])}><b>Authorized</b><small>evidence set</small></button><i>→</i><button onClick={() => select(nodes[11])}><b>Cache</b><small>role scoped</small></button><i>→</i><button onClick={() => select(nodes[12])}><b>Generator</b><small>demo or LLM</small></button><i>→</i><button onClick={() => select(nodes[13])}><b>Grounding</b><small>lexical validator</small></button><i>→</i><button onClick={() => select(nodes[14])}><b>Cited answer</b><small>passages + trace</small></button></div>
      <div className="architecture-fail-path"><span>FAIL-CLOSED PATH</span><strong>No authorized evidence</strong><p>“I could not find authorized source material for this question.” The generator is not called.</p></div>
    </section>

    <section className="architecture-console-section dark" aria-labelledby="security-title">
      <div className="architecture-console-heading"><span>05 / Security & authorization</span><h2 id="security-title">Access control is a retrieval invariant</h2><p>Evidence is filtered where it is queried, validated again after adapters return, and isolated again in semantic caching.</p></div>
      <div className="architecture-security-grid"><article><small>01 / database boundary</small><h3>Tenant + allowed role</h3><p>Dense and keyword SQL apply tenant_id and allowed_roles before ranking.</p></article><article><small>02 / orchestration boundary</small><h3>Fail-closed validation</h3><p>Tenant, role, non-empty content, and source are checked after retrieval.</p></article><article><small>03 / cache boundary</small><h3>Role-scoped reuse</h3><p>Tenant, role, knowledge version, provider, evidence fingerprint, and expiry scope every hit.</p></article></div>
    </section>

    <section className="architecture-console-section" aria-labelledby="infrastructure-title">
      <div className="architecture-console-heading"><span>06 / Runtime & infrastructure</span><h2 id="infrastructure-title">Components around the model</h2><p>Model providers are replaceable. Evidence, permissions, response contracts, and validation remain stable.</p></div>
      <div className="architecture-infrastructure"><article><b>Frontend</b><small>React</small><p>Role-aware workspace, questions, citations, and evidence inspector.</p></article><article><b>FastAPI</b><small>Application boundary</small><p>Auth, ingestion, retrieval, assistant, evaluation, and operations APIs.</p></article><article><b>PostgreSQL + pgvector</b><small>System of record</small><p>Documents, chunks, vectors, cache, conversations, and audit.</p></article><article><b>External providers</b><small>Optional adapters</small><p>OpenAI-compatible LLM and regulatory API/fixtures.</p></article><article><b>Evaluation</b><small>Checked-in benchmark</small><p>Versioned cases executed against the synthetic banking corpus.</p></article></div>
    </section>

    <section className="architecture-console-section evaluation-section" aria-labelledby="evaluation-title">
      <div className="architecture-console-heading"><span>07 / Evaluation</span><h2 id="evaluation-title">Deterministic retrieval benchmark</h2><p>These metrics test the checked-in corpus and retrieval expectations. They do not claim to measure open-ended LLM answer quality.</p></div>
      <div className="architecture-evaluation-grid"><div><small>Dataset</small><strong>banking-rag-v1.jsonl</strong><span>8 checked-in cases</span></div><div><small>Recall@3</small><strong>100%</strong><span>Reference run · threshold 87.5%</span></div><div><small>Answer-term coverage</small><strong>100%</strong><span>Reference run · threshold 95%</span></div></div>
      <p className="architecture-evaluation-note">The benchmark uses deterministic lexical document ranking. The live assistant separately evaluates citation validity and lexical claim support after generation.</p>
    </section>

    <footer className="architecture-console-footer"><a href="/"><Mark /> LedgerLens</a><span>Implementation-aligned AI architecture</span><a href="/">Return to workspace ↗</a></footer>
  </main>;
}
