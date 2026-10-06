import { useEffect, useState } from "react";

import { CitationInspector } from "../components/CitationInspector";
import { LedgerLensMark } from "../components/LedgerLensMark";
import { useAuth } from "../hooks/useAuth";
import { askAssistant, listConversations } from "../services/api";
import type { AssistantAnswer, Citation, ConversationSummary } from "../types/api";

const prompts = [
  "What is the minimum balance for Premium Savings?",
  "What happens when periodic KYC verification fails?",
  "Compare Gold and Classic credit card eligibility.",
  "What documents are required for a home loan application?",
];

export function AssistantPage() {
  const { session } = useAuth();
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [answer, setAnswer] = useState<AssistantAnswer | null>(null);
  const [selected, setSelected] = useState<Citation | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [historyOpen, setHistoryOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session) return;
    listConversations(session.access_token).then(setConversations).catch(() => setConversations([]));
  }, [session, answer]);

  function startNewConversation() {
    setConversationId(undefined);
    setQuestion("");
    setSubmittedQuestion("");
    setAnswer(null);
    setSelected(null);
    setHistoryOpen(false);
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const nextQuestion = question.trim();
    if (!session || !nextQuestion) return;
    setLoading(true);
    setError(null);
    setSelected(null);
    setSubmittedQuestion(nextQuestion);
    try {
      const result = await askAssistant(session.access_token, nextQuestion, conversationId);
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
  const showDiagnostics = session?.user.role === "admin";

  return (
    <div className={selected ? "assistant-workbench inspector-open" : "assistant-workbench"}>
      <section className="assistant-canvas">
        <header className="assistant-titlebar">
          <div>
            <span>01 / Assistant</span>
            <h1>Knowledge Assistant</h1>
            <p>Search policies, procedures, products and regulatory guidance.</p>
          </div>
          <div className="assistant-actions">
            <button onClick={startNewConversation} type="button"><span aria-hidden="true">＋</span> New chat</button>
            <button aria-expanded={historyOpen} onClick={() => setHistoryOpen((open) => !open)} type="button"><span aria-hidden="true">◷</span> Chat history</button>
          </div>
        </header>

        {historyOpen && (
          <aside className="assistant-history" aria-label="Chat history">
            <div><strong>Conversation history</strong><button aria-label="Close chat history" onClick={() => setHistoryOpen(false)} type="button">×</button></div>
            {conversations.length ? conversations.map((conversation) => (
              <button className={conversationId === conversation.id ? "active" : ""} key={conversation.id} onClick={() => { setConversationId(conversation.id); setHistoryOpen(false); }} type="button">
                <strong>{conversation.title}</strong><span>{new Date(conversation.updated_at).toLocaleDateString()}</span>
              </button>
            )) : <p>No saved conversations yet.</p>}
          </aside>
        )}

        <form className="assistant-composer" onSubmit={(event) => void submit(event)}>
          <label htmlFor="question">Question for the authorized knowledge base</label>
          <textarea id="question" maxLength={2000} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a question about a policy, product, procedure or regulation…" rows={3} value={question} />
          <div className="composer-controls">
            <div><span>Northstar Union Bank</span><span>{session?.user.role === "analyst" ? "Standard policy library" : "Authorized policy library"}</span></div>
            <span>{question.length}/2000</span>
            <button disabled={loading || question.trim().length < 3} type="submit">{loading ? "Tracing evidence…" : "Ask"}<span aria-hidden="true">↵</span></button>
          </div>
          {error && <p className="form-error" role="alert">{error}</p>}
        </form>

        {!answer && (
          <section className="assistant-suggestions" aria-labelledby="suggested-questions">
            <h2 id="suggested-questions"><span aria-hidden="true">✦</span> Suggested questions</h2>
            <div>{prompts.map((prompt) => <button key={prompt} onClick={() => setQuestion(prompt)} type="button">{prompt}<span aria-hidden="true">→</span></button>)}</div>
          </section>
        )}

        {answer && (
          <section className="conversation-stream" aria-live="polite">
            <article className="message message-user">
              <span className="message-avatar">{session?.display_name.split(" ").map((part) => part[0]).join("")}</span>
              <div><header><strong>You</strong><span>Just now</span></header><p>{submittedQuestion}</p></div>
            </article>
            <article className="message message-assistant">
              <LedgerLensMark compact />
              <div className="assistant-response">
                <header><div><strong>LedgerLens</strong><span>{answer.latency_ms.total.toFixed(0)} ms</span></div><span className={answer.grounding.grounded ? "answer-state grounded" : "answer-state review"}>{answer.grounding.grounded ? "● Grounded answer" : "● Review required"}</span></header>
                <p className="answer-copy">{answer.answer}</p>
                <div className="response-facts"><span>Confidence {(answer.grounding.confidence * 100).toFixed(0)}%</span><span>{answer.cache_hit ? "Semantic cache" : answer.model}</span><span>{answer.query_trace.route}</span></div>
                <div className="source-heading"><strong>Sources ({answer.citations.length})</strong><span>Select a source to inspect its evidence</span></div>
                <div className="assistant-sources" aria-label="Answer sources">
                  {answer.citations.map((citation) => (
                    <button className={selected?.chunk_id === citation.chunk_id ? "active" : ""} key={citation.source_id} onClick={() => setSelected(citation)} type="button">
                      <span>{citation.source_id}</span><strong>{citation.title}</strong><small>{citation.version} · {citation.section ?? `Page ${citation.page_number}`}</small><em>View passage →</em>
                    </button>
                  ))}
                </div>
              </div>
            </article>
          </section>
        )}
      </section>

      {selected && answer && <CitationInspector citation={selected} latencyMs={answer.latency_ms} onClose={() => setSelected(null)} passage={selectedPassage} queryTrace={answer.query_trace} showDiagnostics={showDiagnostics} />}
    </div>
  );
}
