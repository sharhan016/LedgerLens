import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CitationInspector } from "./CitationInspector";

describe("CitationInspector", () => {
  it("shows source location and all retrieval component scores", () => {
    const onClose = vi.fn();
    render(
      <CitationInspector
        citation={{
          source_id: "S1",
          document_id: "doc",
          chunk_id: "chunk",
          title: "KYC Manual",
          source: "kyc.md",
          version: "2026.3",
          section: "Standard evidence",
          page_number: 4,
          excerpt: "A photo identity document is required.",
        }}
        onClose={onClose}
        showDiagnostics
        passage={{
          chunk_id: "chunk",
          title: "KYC Manual",
          source: "kyc.md",
          content: "A photo identity document is required.",
          section: "Standard evidence",
          page_number: 4,
          dense_score: 0.91,
          keyword_score: 0.82,
          rrf_score: 0.032,
          rerank_score: 0.97,
          retrieval_channel: "hybrid",
          validation_status: "authorized",
        }}
      />,
    );

    expect(screen.getByText(/Page 4/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "context" }));
    expect(screen.getByText("0.9700")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Close citation inspector" }));
    expect(onClose).toHaveBeenCalledOnce();
  });
});
