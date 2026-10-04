import { chromium } from "../../frontend/node_modules/@playwright/test/index.mjs";

const screenshot = "/tmp/ledgerlens-workspace.png";

function jsonResponse(route, payload, status = 200) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(payload) });
}

async function handleApi(route) {
  const url = route.request().url();
  if (url.endsWith("/api/v1/system/status")) {
    return jsonResponse(route, { application: "LedgerLens", environment: "demo", release: "0.1.0", status: "foundation_ready", capabilities: [] });
  }
  if (url.endsWith("/api/v1/auth/demo-login")) {
    return jsonResponse(route, { access_token: "demo-token", token_type: "bearer", user: { user_id: "11111111-1111-1111-1111-111111111111", tenant_id: "22222222-2222-2222-2222-222222222222", role: "compliance" }, display_name: "Mira Fernandes", tenant_name: "Northstar Union Bank · Synthetic", demo_auth: true });
  }
  if (url.endsWith("/api/v1/conversations")) return jsonResponse(route, []);
  if (url.endsWith("/api/v1/assistant/ask")) {
    return jsonResponse(route, { answer: "The Premium Savings Account requires an average monthly balance of INR 25,000 [S1].", model: "demo-grounded-model", citations: [{ source_id: "S1", document_id: "33333333-3333-3333-3333-333333333333", chunk_id: "44444444-4444-4444-4444-444444444444", title: "Premium Savings Account Policy", source: "premium-savings-policy.md", version: "2026.2", section: "Balance requirement", page_number: null, excerpt: "The account requires an average monthly balance of INR 25,000." }], passages: [{ chunk_id: "44444444-4444-4444-4444-444444444444", title: "Premium Savings Account Policy", source: "premium-savings-policy.md", content: "The account requires an average monthly balance of INR 25,000.", section: "Balance requirement", page_number: null, dense_score: 0.91, keyword_score: 0.84, rrf_score: 0.032, rerank_score: 0.98, retrieval_channel: "hybrid", validation_status: "authorized" }], grounding: { grounded: true, citation_coverage: 1, lexical_support: 1, confidence: 0.97, unsupported_claims: [], invalid_citations: [] }, query_trace: { original_query: "What is the minimum balance?", retrieval_query: "What is the minimum balance?", intent: "fact", route: "hybrid_knowledge", transformations: [], routing_reason: "Question is answered from authorized document knowledge.", selected_sources: ["documents"] }, latency_ms: { planning: 1, retrieval: 42, generation: 120, validation: 2, operations: 3, total: 168 }, conversation_id: "55555555-5555-5555-5555-555555555555", cache_hit: false });
  }
  if (url.endsWith("/api/v1/documents")) {
    return jsonResponse(route, [{ id: "33333333-3333-3333-3333-333333333333", title: "Premium Savings Account Policy", source_type: "policy", version: "2026.2", status: "ready" }]);
  }
  if (url.endsWith("/api/v1/evaluation/summary")) {
    return jsonResponse(route, { dataset: "banking-rag-v1.jsonl", cases: 8, recall_at_3: 1, answer_term_coverage: 1, status: "passing", per_case: [{ id: "BAL-001", expected_source: "premium-savings-policy.md", top_3: ["premium-savings-policy.md"], retrieved: true, answer_term_coverage: 1 }] });
  }
  if (url.endsWith("/api/v1/operations/metrics")) {
    return jsonResponse(route, { content_policy: "paths, status codes, counts, and latency only", metrics: [{ method: "POST", route: "/api/v1/assistant/ask", status_code: 200, count: 4, average_latency_ms: 168, maximum_latency_ms: 212 }] });
  }
  return jsonResponse(route, { detail: "Unhandled smoke-test route" }, 500);
}

const consoleErrors = [];
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
await page.route("**/api/v1/**", handleApi);
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});

await page.goto("http://127.0.0.1:5173", { waitUntil: "networkidle" });
await page.getByRole("button", { name: /Mira Fernandes/ }).click();
await page.getByLabel("Question for the authorized knowledge base").fill("What is the minimum balance?");
await page.getByRole("button", { name: "Generate cited answer" }).click();
await page.getByText("The Premium Savings Account requires").waitFor();
await page.getByRole("button", { name: /S1 Premium Savings Account Policy/ }).click();
await page.getByText("Retrieval record").waitFor();
await page.screenshot({ path: screenshot, fullPage: true });
await page.getByRole("button", { name: "Close citation inspector" }).click();
await page.getByRole("button", { name: "02 Knowledge base" }).click();
await page.getByText("Premium Savings Account Policy").waitFor();
await page.getByRole("button", { name: "03 Evaluation" }).click();
await page.getByText("Recall @ 3").waitFor();
await page.getByRole("button", { name: "04 Operations" }).click();
await page.getByText("System pulse.").waitFor();
await page.setViewportSize({ width: 390, height: 844 });
await page.reload({ waitUntil: "networkidle" });
if (await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)) {
  throw new Error("Mobile layout has horizontal overflow");
}
if (consoleErrors.length) throw new Error(`Browser console errors: ${consoleErrors.join("\n")}`);
await browser.close();
console.log(`workspace browser smoke passed; screenshot: ${screenshot}`);
