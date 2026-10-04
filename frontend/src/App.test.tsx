import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { AuthProvider } from "./hooks/useAuth";
import type { DemoSession } from "./types/api";

const session: DemoSession = {
  access_token: "token",
  token_type: "bearer",
  user: { user_id: "user", tenant_id: "tenant", role: "compliance" },
  display_name: "Mira Fernandes",
  tenant_name: "Northstar Union Bank · Synthetic",
  demo_auth: true,
};

afterEach(() => {
  localStorage.clear();
  vi.unstubAllGlobals();
});

describe("LedgerLens workspace", () => {
  it("loads an authenticated workspace and navigates to real knowledge data", async () => {
    localStorage.setItem("ledgerlens.demo-session", JSON.stringify(session));
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/api/v1/system/status")) {
        return new Response(JSON.stringify({
          application: "LedgerLens", environment: "test", release: "0.1.0",
          status: "foundation_ready", capabilities: [],
        }), { status: 200 });
      }
      if (url.endsWith("/api/v1/conversations")) {
        return new Response("[]", { status: 200 });
      }
      if (url.endsWith("/api/v1/documents")) {
        return new Response(JSON.stringify([{
          id: "doc-1", title: "Premium Savings Policy", source_type: "policy",
          version: "2026.2", status: "ready",
        }]), { status: 200 });
      }
      return new Response(JSON.stringify({ detail: "Unexpected request" }), { status: 500 });
    }));

    render(<AuthProvider><App /></AuthProvider>);

    expect(await screen.findByText("Ask against the record.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Knowledge base/ }));
    expect(await screen.findByText("Premium Savings Policy")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("API online")).toBeInTheDocument());
  });
});

