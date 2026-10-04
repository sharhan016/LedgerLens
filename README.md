# LedgerLens

LedgerLens is a production-style, multi-tenant banking knowledge assistant. It is
designed to ingest synthetic policy documents and produce inspectable, grounded answers
through hybrid retrieval, authorization-aware context construction, citations, and
evaluation.

The repository is intentionally standalone. The adjacent Vertex Harness coordinates
development and records verification evidence, but it is not copied into the application
and is never a runtime dependency.

## Current state

The active increment is the runnable project foundation:

- FastAPI exposes liveness, readiness, and system-status endpoints.
- React and Vite provide an honest system-readiness browser shell.
- Docker Compose declares the web, API, and PostgreSQL/pgvector services.
- Later capabilities are tracked as dependency-gated Vertex tasks in
  `.vertex/project.json`; the browser does not pretend those capabilities exist yet.

See [the delivery plan](docs/architecture/delivery-plan.md) and
[the system architecture](docs/architecture/system-overview.md).

## Prerequisites

- Python 3.11+
- Node.js 22+
- npm 10+
- Docker with the Compose v2 plugin (for the complete local stack)
- `uv` for the recommended backend workflow

The default `make install` includes the `ml` extra used by the real local Sentence
Transformers embedding and cross-encoder reranking adapters. Model weights are downloaded
by those libraries on first use and cached outside the repository.

## Local setup

```console
cp .env.example .env
make install
make dev-api
```

In another terminal:

```console
make dev-web
```

Open `http://localhost:5173`. The API is served at `http://localhost:8000`.

To run the containerized stack after installing Docker Compose v2:

```console
docker compose up --build
```

## Verification

```console
make verify-foundation
```

The same command is registered as the executable Vertex check for task `T-01`.
Vertex records the command, source fingerprint, output, and result in its repository
ledger rather than trusting a manual completion claim.

## Synthetic data only

LedgerLens must never contain real customer financial data. All demo policies, accounts,
transactions, and identities introduced in later phases will be fictional and visibly
labelled as synthetic.
