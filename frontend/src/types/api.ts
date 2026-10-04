export type Role = "viewer" | "analyst" | "compliance" | "admin";

export type DemoSession = {
  access_token: string;
  token_type: "bearer";
  user: { user_id: string; tenant_id: string; role: Role };
  display_name: string;
  tenant_name: string;
  demo_auth: true;
};

export type Citation = {
  source_id: string;
  document_id: string;
  chunk_id: string;
  title: string;
  source: string;
  version: string;
  section: string | null;
  page_number: number | null;
  excerpt: string;
};

export type Passage = {
  chunk_id: string;
  title: string;
  source: string;
  content: string;
  section: string | null;
  page_number: number | null;
  dense_score: number | null;
  keyword_score: number | null;
  rrf_score: number;
  rerank_score: number | null;
  retrieval_channel: string;
  validation_status: string;
};

export type AssistantAnswer = {
  answer: string;
  model: string;
  citations: Citation[];
  passages: Passage[];
  grounding: {
    grounded: boolean;
    citation_coverage: number;
    lexical_support: number;
    confidence: number;
    unsupported_claims: string[];
    invalid_citations: string[];
  };
  query_trace: {
    original_query: string;
    retrieval_query: string;
    intent: string;
    route: string;
    transformations: string[];
    routing_reason: string;
    selected_sources: string[];
  };
  latency_ms: Record<string, number>;
  conversation_id: string | null;
  cache_hit: boolean;
};

export type ConversationSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type DocumentSummary = {
  id: string;
  title: string;
  source_type: string;
  version: string;
  status: string;
};

export type EvaluationSummary = {
  dataset: string;
  cases: number;
  recall_at_3: number;
  answer_term_coverage: number;
  status: string;
  per_case: Array<{
    id: string;
    expected_source: string;
    top_3: string[];
    retrieved: boolean;
    answer_term_coverage: number;
  }>;
};

export type OperationsMetrics = {
  content_policy: string;
  metrics: Array<{
    method: string;
    route: string;
    status_code: number;
    count: number;
    average_latency_ms: number;
    maximum_latency_ms: number;
  }>;
};

