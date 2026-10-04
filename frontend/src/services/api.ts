import type {
  AssistantAnswer,
  ConversationSummary,
  DemoSession,
  DocumentSummary,
  EvaluationSummary,
  OperationsMetrics,
  Role,
} from "../types/api";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(payload?.detail ?? `Request failed with ${response.status}`, response.status);
  }
  return response.json() as Promise<T>;
}

export function demoLogin(persona: Role): Promise<DemoSession> {
  return request("/api/v1/auth/demo-login", {
    method: "POST",
    body: JSON.stringify({ persona }),
  });
}

export function askAssistant(
  token: string,
  question: string,
  conversationId?: string,
): Promise<AssistantAnswer> {
  return request(
    "/api/v1/assistant/ask",
    {
      method: "POST",
      body: JSON.stringify({ question, conversation_id: conversationId ?? null }),
    },
    token,
  );
}

export function listConversations(token: string): Promise<ConversationSummary[]> {
  return request("/api/v1/conversations", {}, token);
}

export function listDocuments(token: string): Promise<DocumentSummary[]> {
  return request("/api/v1/documents", {}, token);
}

export function getEvaluation(token: string): Promise<EvaluationSummary> {
  return request("/api/v1/evaluation/summary", {}, token);
}

export function getMetrics(token: string): Promise<OperationsMetrics> {
  return request("/api/v1/operations/metrics", {}, token);
}

export async function ingestDocument(
  token: string,
  file: File,
  fields: { title: string; version: string; classification: string },
): Promise<{ document_id: string; status: string; chunks: unknown[] }> {
  const body = new FormData();
  body.set("file", file);
  body.set("title", fields.title);
  body.set("version", fields.version);
  body.set("classification", fields.classification);
  body.set("source_type", "policy");
  return request("/api/v1/ingestion/documents", { method: "POST", body }, token);
}

