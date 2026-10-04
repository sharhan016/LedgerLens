import { useEffect, useState } from "react";

import { CitationInspector } from "../components/CitationInspector";
import { useAuth } from "../hooks/useAuth";
import { askAssistant, listConversations } from "../services/api";
import type { AssistantAnswer, Citation, ConversationSummary } from "../types/api";

const prompts = [
  "What is the minimum balance for Premium Savings?",
  "What happens when periodic KYC verification fails?",
  "Compare Gold and Classic credit card eligibility.",
];

export function AssistantPage() {
  const { session } = useAuth();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AssistantAnswer | null>(null);
  const [selected, setSelected] = useState<Citation | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    listConversations(session.access_token).then(setConversations).catch(() => setConversations([]));
  }, [session, answer]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!session || !question.trim()) return;
    setLoading(true);
    setError(null);
    setSelected(null);
    try {
      const result = await askAssistant(session.access_token, question, conversationId);
      setAnswer(result);
      setConversationId(result.conversation_id ?? undefined);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The assistant request failed");
    } finally {
      setLoading(false);
    }
  }

  const selectedPassage = selected
    ? answer?.passages.find((passage) => passage.chunk_id === selected.chunk_id)
    : undefined;

  return (
    <div className={selected ? "assistant-layout inspector-open" : "assistant-layout"}>
      <aside className="conversation-rail">
        <div className="panel-title">
          <span>Conversation ledger</span>
          <button onClick={() => { setConversationId(undefined); setAnswer(null); }} type="button">＋ New</button>
        </div>
        {conversations.length ? conversations.map((conversation) => (
          <button
            className={conversationId === conversation.id ? "conversation active" : "conversation"}
            key={conversation.id}
            onClick={() => setConversationId(conversation.id)}
            type="button"
          >
            <strong>{conversation.title}</strong>
            <span>{new Date(conversation.updated_at).toLocaleDateString()}</span>
          </button>
        )) : <p className="empty-note">Your verified answers will collect here.</p>}
      </aside>

      <section className="ask-stage">
        <div className="page-heading">
          <div><span>01 / Assistant</span><h1>Ask against the record.</h1></div>
          <p>Answers are generated only after authorized retrieval. Open any citation to inspect the passage and ranking evidence.</p>
        </div>

        {!answer && (
          <div className="prompt-starters">
            {prompts.map((prompt) => (
              <button key={prompt} onClick={() => setQuestion(prompt)} type="button">{prompt}<span>↗</span></button>
            ))}
          </div>
        )}

        {answer && (
          <article className="answer-sheet" aria-live="polite">
            <div className="answer-meta">
              <span className={answer.grounding.grounded ? "grounded" : "review"}>
                {answer.grounding.grounded ? "Grounded" : "Review required"}
              </span>
              <span>Confidence {(answer.grounding.confidence * 100).toFixed(0)}%</span>
              <span>{answer.cache_hit ? "Semantic cache" : answer.model}</span>
              <span>{answer.latency_ms.total.toFixed(0)} ms</span>
            </div>
            <h2>{question}</h2>
            <p className="answer-copy">{answer.answer}</p>
            <div className="citation-row" aria-label="Answer citations">
              {answer.citations.map((citation) => (
                <button key={citation.source_id} onClick={() => setSelected(citation)} type="button">
                  <span>{citation.source_id}</span>
                  <strong>{citation.title}</strong>
                  <small>{citation.section ?? `Page ${citation.page_number}`}</small>
                </button>
              ))}
            </div>
            <details className="trace-panel">
              <summary>Why this answer</summary>
              <div className="trace-grid">
                <div><span>Route</span><strong>{answer.query_trace.route}</strong><p>{answer.query_trace.routing_reason}</p></div>
                <div><span>Sources selected</span><strong>{answer.query_trace.selected_sources.join(" · ")}</strong><p>{answer.query_trace.retrieval_query}</p></div>
                <div><span>Citation coverage</span><strong>{(answer.grounding.citation_coverage * 100).toFixed(0)}%</strong><p>Lexical support {(answer.grounding.lexical_support * 100).toFixed(0)}%</p></div>
              </div>
            </details>
          </article>
        )}

        <form className="question-box" onSubmit={(event) => void submit(event)}>
          <label htmlFor="question">Question for the authorized knowledge base</label>
          <textarea
            id="question"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about a product, policy, procedure, or regulatory bulletin…"
            rows={3}
            value={question}
          />
          <div>
            <span>{question.length}/2000</span>
            <button disabled={loading || question.trim().length < 3} type="submit">
              {loading ? "Tracing evidence…" : "Generate cited answer"}
            </button>
          </div>
          {error && <p className="form-error" role="alert">{error}</p>}
        </form>
      </section>

      {selected && (
        <CitationInspector citation={selected} passage={selectedPassage} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}

