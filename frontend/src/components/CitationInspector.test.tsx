import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CitationInspector } from "./CitationInspector";

afterEach(cleanup);

describe("CitationInspector", () => {
  const citation = {
    source_id: "S1",
    document_id: "doc",
    chunk_id: "chunk",
    title: "KYC Manual",
    source: "kyc.md",
    version: "2026.3",
    section: "Standard evidence",
    page_number: 4,
    excerpt: "A photo identity document is required.",
  };

  it("keeps analyst inspection focused on evidence", () => {
    render(<CitationInspector citation={citation} onClose={vi.fn()} />);

    expect(screen.getByRole("tab", { name: "evidence" })).toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: "details" })).not.toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: "context" })).not.toBeInTheDocument();
  });

  it("adds document details for compliance without retrieval context", () => {
    render(<CitationInspector citation={citation} onClose={vi.fn()} showDetails />);

    expect(screen.getByRole("tab", { name: "details" })).toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: "context" })).not.toBeInTheDocument();
  });

  it("shows source location and all retrieval component scores", () => {
    const onClose = vi.fn();
    render(
      <CitationInspector
        citation={citation}
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
