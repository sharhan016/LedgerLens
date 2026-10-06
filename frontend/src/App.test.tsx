import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { AuthProvider } from "./hooks/useAuth";
import type { DemoSession, Role } from "./types/api";

function sessionFor(role: Role): DemoSession {
  const names: Record<Role, string> = {
    viewer: "Vikram Iyer",
    analyst: "Asha Rao",
    compliance: "Mira Fernandes",
    admin: "Dev Malhotra",
  };
  return {
  access_token: "token",
  token_type: "bearer",
  user: { user_id: "user", tenant_id: "tenant", role },
  display_name: names[role],
  tenant_name: "Northstar Union Bank · Synthetic",
  demo_auth: true,
  };
}

const session = sessionFor("compliance");

function stubWorkspaceRequests() {
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/api/v1/system/status")) {
      return new Response(JSON.stringify({
        application: "LedgerLens", environment: "test", release: "0.1.0",
        status: "foundation_ready", capabilities: [],
      }), { status: 200 });
    }
    if (url.endsWith("/api/v1/conversations")) return new Response("[]", { status: 200 });
    if (url.endsWith("/api/v1/documents")) {
      return new Response(JSON.stringify([{
        id: "doc-1", title: "Premium Savings Policy", source_type: "policy",
        version: "2026.2", status: "ready",
      }]), { status: 200 });
    }
    return new Response(JSON.stringify({ detail: "Unexpected request" }), { status: 500 });
  }));
}

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

describe("LedgerLens workspace", () => {
  it("loads an authenticated workspace and navigates to real knowledge data", async () => {
    localStorage.setItem("ledgerlens.demo-session", JSON.stringify(session));
    stubWorkspaceRequests();

    render(<AuthProvider><App /></AuthProvider>);

    expect(await screen.findByText("Knowledge Assistant")).toBeInTheDocument();
    expect(screen.getByText("Mira Fernandes")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "End session" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Knowledge base/ }));
    expect(await screen.findByText("Premium Savings Policy")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("API online")).toBeInTheDocument());
  });

  it.each([
    { role: "analyst" as const, evaluation: false, operations: false },
    { role: "compliance" as const, evaluation: true, operations: false },
    { role: "admin" as const, evaluation: true, operations: true },
  ])("shows only authorized navigation for $role", async ({ role, evaluation, operations }) => {
    localStorage.setItem("ledgerlens.demo-session", JSON.stringify(sessionFor(role)));
    stubWorkspaceRequests();

    render(<AuthProvider><App /></AuthProvider>);

    expect(await screen.findByRole("button", { name: /Ask LedgerLens/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Knowledge base/ })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Evaluation/ }) !== null).toBe(evaluation);
    expect(screen.queryByRole("button", { name: /Operations/ }) !== null).toBe(operations);
  });
});
