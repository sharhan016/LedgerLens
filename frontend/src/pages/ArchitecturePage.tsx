const ingestionSteps = [
  { number: "01", title: "Parse", detail: "PDF pages, Markdown sections, or plain text become source segments with provenance intact." },
  { number: "02", title: "Bound", detail: "Segments are split at a UTF-8-safe 512 KiB processing boundary before semantic chunking." },
  { number: "03", title: "Chunk", detail: "Section-aware windows cap at 180 words, overlap by 30, and advance by 150 words." },
  { number: "04", title: "Embed", detail: "Each semantic chunk becomes a 384-dimensional vector while retaining tenant and role metadata." },
  { number: "05", title: "Persist", detail: "Text, vector, source, version, tenant, and allowed roles are stored together in PostgreSQL." },
];

const retrievalStages = [
  ["Plan", "Rules classify the question and select knowledge, SQL, regulatory API, or a combined route."],
  ["Retrieve", "Dense pgvector similarity and PostgreSQL keyword search each produce an authorized candidate list."],
  ["Fuse", "Reciprocal Rank Fusion combines ranks with 1 / (60 + rank), avoiding incompatible score scales."],
  ["Rerank", "A cross-encoder scores query–passage relevance; the deterministic demo uses token overlap."],
  ["Select", "At most eight passages enter the answer context, each carrying a stable source label."],
];

const safeguards = [
  { label: "Before ranking", value: "Tenant + role filters", copy: "Unauthorized chunks are removed in the database queries—not hidden after retrieval." },
  { label: "After retrieval", value: "Fail-closed validation", copy: "Every candidate is checked again for tenant, role, content, and source integrity." },
  { label: "During generation", value: "Evidence-only prompt", copy: "The model receives selected passages and must attach a source marker to factual claims." },
  { label: "After generation", value: "Grounding validator", copy: "Citation validity, claim coverage, lexical support, and retrieval quality determine confidence." },
  { label: "Across requests", value: "Role-scoped cache", copy: "Cached answers are isolated by tenant, role, knowledge version, provider, and context fingerprint." },
  { label: "In telemetry", value: "Content-minimized audit", copy: "LedgerLens records a question hash and system facts—not raw questions, answers, or document text." },
];

function BrandMark() {
  return <span className="architecture-mark" aria-hidden="true">LL</span>;
}

export function ArchitecturePage() {
  return (
    <main className="architecture-page">
      <header className="architecture-nav">
        <a className="architecture-wordmark" href="/" aria-label="LedgerLens home">
          <BrandMark />
          <span>LedgerLens</span>
        </a>
        <span className="architecture-nav-label"><i /> AI system architecture</span>
        <a className="architecture-return" href="/">Return to workspace <span aria-hidden="true">↗</span></a>
      </header>

      <section className="architecture-hero" aria-labelledby="architecture-title">
        <div className="architecture-hero-copy">
          <p className="architecture-eyebrow">Technical field note · 01</p>
          <h1 id="architecture-title">From source byte<br />to cited answer.</h1>
          <p className="architecture-deck">
            LedgerLens is a role-aware retrieval system for bank policy knowledge. It turns governed documents into
            searchable evidence, routes each question to the right sources, and tests every generated claim against
            the passages the user is allowed to see.
          </p>
        </div>
        <div className="architecture-system-card" aria-label="System summary">
          <div className="architecture-orbit" aria-hidden="true">
            <span className="architecture-orbit-core">RAG</span>
            <i className="orbit-node node-a" /><i className="orbit-node node-b" /><i className="orbit-node node-c" />
          </div>
          <dl>
            <div><dt>Vector store</dt><dd>PostgreSQL + pgvector</dd></div>
            <div><dt>Embedding width</dt><dd>384 dimensions</dd></div>
            <div><dt>Retrieval</dt><dd>Dense + keyword</dd></div>
            <div><dt>Answer contract</dt><dd>Cited + validated</dd></div>
          </dl>
        </div>
      </section>

      <section className="architecture-section architecture-ingestion" aria-labelledby="ingestion-title">
        <div className="architecture-section-intro">
          <p className="architecture-eyebrow">01 / Ingestion</p>
          <h2 id="ingestion-title">Structure before similarity.</h2>
          <p>Large files are made safe to process first. Smaller semantic windows are created second. Those are deliberately separate boundaries.</p>
        </div>
        <ol className="architecture-pipeline">
          {ingestionSteps.map((step) => (
            <li key={step.number}>
              <span>{step.number}</span>
              <div><h3>{step.title}</h3><p>{step.detail}</p></div>
            </li>
          ))}
        </ol>
        <aside className="architecture-boundary-note">
          <strong>512 KiB is not an embedding chunk.</strong>
          <p>It is a source-segment safety boundary measured in UTF-8 bytes. Semantic chunks remain no larger than 180 words and never cross a source segment.</p>
        </aside>
        <div className="architecture-parser-grid">
          <article><span>.PDF</span><h3>Page-aware</h3><p>pypdf extracts page text and preserves one-based page numbers for citations.</p></article>
          <article><span>.MD</span><h3>Section-aware</h3><p>Frontmatter is removed and heading boundaries are retained as section metadata.</p></article>
          <article><span>.TXT</span><h3>Source-aware</h3><p>Plain text enters as one source segment before byte-safe splitting and cleaning.</p></article>
        </div>
      </section>

      <section className="architecture-section architecture-retrieval" aria-labelledby="retrieval-title">
        <div className="architecture-section-intro architecture-on-dark">
          <p className="architecture-eyebrow">02 / Retrieval</p>
          <h2 id="retrieval-title">Two searches.<br />One evidence order.</h2>
          <p>The query is normalized and embedded once. Dense meaning and exact language are searched independently, authorized independently, then fused.</p>
        </div>
        <div className="architecture-retrieval-map">
          <div className="architecture-query-node"><small>Input</small><strong>Normalized question</strong></div>
          <div className="architecture-search-lanes">
            <article><span>Dense lane</span><strong>pgvector cosine similarity</strong><small>Top 30 candidates</small></article>
            <article><span>Keyword lane</span><strong>PostgreSQL text search</strong><small>Top 30 candidates</small></article>
          </div>
          <div className="architecture-fusion-node"><small>Fusion constant · 60</small><strong>RRF score = Σ 1 / (60 + rank)</strong></div>
          <div className="architecture-output-node"><small>Context budget</small><strong>8 reranked passages</strong></div>
        </div>
        <ol className="architecture-stage-list">
          {retrievalStages.map(([title, copy], index) => (
            <li key={title}><span>0{index + 1}</span><h3>{title}</h3><p>{copy}</p></li>
          ))}
        </ol>
        <p className="architecture-route-note">
          <strong>Available routes</strong> hybrid knowledge · knowledge + SQL · knowledge + regulatory API · knowledge + SQL + API
        </p>
      </section>

      <section className="architecture-section architecture-generation" aria-labelledby="generation-title">
        <div className="architecture-section-intro">
          <p className="architecture-eyebrow">03 / Answering</p>
          <h2 id="generation-title">Generation is not the final judge.</h2>
          <p>LedgerLens treats a fluent answer as a draft until its citations and claims survive a deterministic grounding check.</p>
        </div>
        <div className="architecture-answer-flow" aria-label="Grounded answer flow">
          <article><span>01</span><h3>Build context</h3><p>Selected evidence is labeled S1–S8 with source metadata.</p></article>
          <div className="architecture-flow-arrow" aria-hidden="true">→</div>
          <article><span>02</span><h3>Generate</h3><p>Temperature 0. Every factual sentence must carry a [S#] citation.</p></article>
          <div className="architecture-flow-arrow" aria-hidden="true">→</div>
          <article><span>03</span><h3>Validate</h3><p>Claims, citation coverage, lexical support, and retrieval quality are scored.</p></article>
        </div>
        <div className="architecture-confidence">
          <div>
            <p className="architecture-eyebrow">Confidence composition</p>
            <strong>0.45</strong><span>citation coverage</span>
            <strong>0.35</strong><span>lexical support</span>
            <strong>0.20</strong><span>retrieval quality</span>
          </div>
          <blockquote>
            “No authorized evidence” is a valid answer state. The assistant is designed to abstain instead of filling a gap from model memory.
          </blockquote>
        </div>
      </section>

      <section className="architecture-section architecture-safeguards" aria-labelledby="safeguards-title">
        <div className="architecture-section-intro architecture-on-dark">
          <p className="architecture-eyebrow">04 / AI safeguards</p>
          <h2 id="safeguards-title">Authorization travels with the evidence.</h2>
          <p>Access control is part of retrieval, caching, generation context, and observability—not a presentation-layer filter.</p>
        </div>
        <div className="architecture-safeguard-grid">
          {safeguards.map((item) => (
            <article key={item.label}><small>{item.label}</small><h3>{item.value}</h3><p>{item.copy}</p></article>
          ))}
        </div>
      </section>

      <section className="architecture-section architecture-modes" aria-labelledby="modes-title">
        <div className="architecture-section-intro">
          <p className="architecture-eyebrow">05 / Runtime modes</p>
          <h2 id="modes-title">Reproducible locally. Replaceable in production.</h2>
        </div>
        <div className="architecture-mode-table" role="table" aria-label="AI runtime modes">
          <div className="architecture-table-row architecture-table-head" role="row"><span role="columnheader">Stage</span><span role="columnheader">Deterministic demo</span><span role="columnheader">ML / LLM mode</span></div>
          <div className="architecture-table-row" role="row"><strong role="cell">Embedding</strong><span role="cell">Normalized hash vector</span><span role="cell">all-MiniLM-L6-v2 · 384d</span></div>
          <div className="architecture-table-row" role="row"><strong role="cell">Reranking</strong><span role="cell">Token overlap</span><span role="cell">ms-marco-MiniLM-L-6-v2</span></div>
          <div className="architecture-table-row" role="row"><strong role="cell">Answering</strong><span role="cell">Extractive, non-LLM</span><span role="cell">OpenAI-compatible JSON response</span></div>
          <div className="architecture-table-row" role="row"><strong role="cell">Contract</strong><span role="cell">Same citations + validation</span><span role="cell">Same citations + validation</span></div>
        </div>
      </section>

      <section className="architecture-section architecture-evaluation" aria-labelledby="evaluation-title">
        <div>
          <p className="architecture-eyebrow">06 / Evaluation</p>
          <h2 id="evaluation-title">Measured against a checked-in banking benchmark.</h2>
        </div>
        <div className="architecture-metrics">
          <article><strong>Recall@3</strong><p>Did an expected source appear in the first three retrieved results?</p></article>
          <article><strong>Answer-term coverage</strong><p>Did the grounded answer contain the expected domain terms?</p></article>
          <article><strong>Role-restricted cases</strong><p>Does the same question expose only evidence allowed for the active persona?</p></article>
        </div>
      </section>

      <footer className="architecture-footer">
        <a className="architecture-wordmark" href="/"><BrandMark /><span>LedgerLens</span></a>
        <p>AI architecture · implementation-aligned</p>
        <a href="/">Enter workspace <span aria-hidden="true">→</span></a>
      </footer>
    </main>
  );
}
