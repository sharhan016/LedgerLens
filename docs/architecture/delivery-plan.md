# Delivery plan

## Product outcome

LedgerLens will be a browser-demonstrable, production-style banking RAG platform whose
answers can be traced back to authorized source passages. The build is organized as
nine independently verified Vertex tasks. A dependent task cannot begin until Vertex
has recorded passing evidence for its prerequisites.

| Task | Verifiable outcome | Depends on |
| --- | --- | --- |
| T-01 | Runnable repository, API shell, browser shell, and local infrastructure | — |
| T-02 | Tenant-aware persistence, authentication, and RBAC | T-01 |
| T-03 | Traceable ingestion of a synthetic banking corpus | T-02 |
| T-04 | Authorized dense + keyword retrieval, RRF, and reranking | T-03 |
| T-05 | Grounded, cited answers through configurable LLM providers | T-04 |
| T-06 | Governed SQL/API routing and retrieval validation | T-05 |
| T-07 | Conversations, semantic cache, audit, telemetry, and evaluation | T-05 |
| T-08 | Complete responsive browser demonstration experience | T-06, T-07 |
| T-09 | Containerized end-to-end proof, hardening, and demo runbook | T-08 |

The canonical task criteria, checks, lifecycle state, and evidence receipts live in
`.vertex/project.json`. This document explains the product sequence; it does not replace
the executable ledger.

## Verification policy

Each task owns `scripts/verify/NN-*.sh`. A task check must exercise its observable
acceptance criteria, must not rewrite source files, and must pass through `vertex verify`
before dependents are started. Failed or interrupted attempts remain in the evidence
history. Architectural decisions and known limitations are updated with the work they
describe, never retroactively at the end.

## Explicit non-goals for the foundation

- No fake chat responses, retrieval results, ingestion progress, or evaluation scores.
- No production identity provider before the tenant/RBAC task defines the boundary.
- No Kubernetes, cloud-specific deployment, distributed workers, or provider matrix
  before the core local product works.
- No real customer or bank-confidential data.
- No Vertex code or runtime dependency inside LedgerLens.

