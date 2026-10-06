# LedgerLens

LedgerLens is a production-style, multi-tenant banking knowledge assistant built around
inspectable retrieval. It ingests a fictional policy corpus, combines pgvector similarity
with PostgreSQL full-text search, applies reciprocal-rank fusion and reranking, enforces
tenant and role filters in the query, and returns cited answers with the underlying
passages, scores, route, confidence, and latency record.

The adjacent Vertex Harness coordinates development and stores local verification
receipts. LedgerLens remains standalone: Vertex is not copied into this repository and is
not a runtime dependency. `.vertex/` is intentionally ignored by Git.

## Run the synthetic demo

Prerequisites are Docker with Compose v2. No real customer or institution data is used.

```console
cp .env.example .env
docker compose up --build
```

Open `http://localhost:5173`, then choose Asha (analyst), Mira (compliance), or Dev
(administrator). The first container start applies all migrations and idempotently loads
the eight synthetic policies, three demo identities, and a small product-metrics ledger.
The API is available at `http://localhost:8000`; readiness is database-backed at
`/health/ready`.

The Compose demo deliberately defaults to two clearly identified offline adapters:

- `deterministic_demo` embeddings/reranking keep a first run small and repeatable.
- `demo-extractive-not-llm` produces cited extractive answers without calling a model.

They are demo-only and rejected when `LEDGERLENS_ENV=production`. To exercise the real
local ML path, set `LEDGERLENS_INSTALL_ML=true` and
`LEDGERLENS_ML_MODE=sentence_transformers`, then rebuild. To use an actual generator,
set `LEDGERLENS_LLM_PROVIDER` to `local_openai`, `openai_compatible`, or `openrouter` and
configure the URL, model, and key in `.env`. Sentence Transformers and the cross-encoder
remain the default outside the container demo.

Stop the stack with `docker compose down`. Add `--volumes` only when you intentionally want
to erase the local demo database.

## Develop and verify

Python 3.11+, Node.js 22+, npm 10+, and `uv` are required for host development.

```console
make install
make test-backend
make test-web
make build-web
make verify
```

Run the API and web workspace separately with `make dev-api` and `make dev-web`. The
integrated verification runs linting, backend and frontend tests, migration compilation,
the retrieval evaluation dataset, a production web build, container contract checks, and
the Playwright browser journey.

## Architecture and safety

- FastAPI, Pydantic, SQLAlchemy async, Alembic, PostgreSQL, and pgvector form the service.
- React, TypeScript, and Vite provide the responsive evidence workspace.
- JWT principals carry tenant and role; database retrieval applies both filters before
  ranking and orchestration validates them again fail-closed.
- OpenAI-compatible, OpenRouter, and local OpenAI-style generation share one provider
  boundary. Answers without authorized evidence do not call a provider.
- Audit records retain hashes, routes, counts, and grounding outcomes—not raw questions.
- Semantic cache keys include tenant, role, knowledge version, evidence fingerprint, and
  expiry.

See [system architecture](docs/architecture/system-overview.md),
[delivery plan](docs/architecture/delivery-plan.md), and the
[demo runbook](docs/demo/runbook.md).

## Deployment preparation

The repository includes a Hostinger-oriented production Compose contract and a gated
GitHub Actions workflow for `ledgerlens.sharhan.dev`. They keep PostgreSQL and FastAPI off
public host ports, route same-origin `/api/` traffic through the frontend, and let the
existing host-networked Traefik discover that frontend through Docker labels.

No VPS or DNS changes are made by repository setup. Before enabling deployment, follow the
[Hostinger deployment guide](docs/deployment/hostinger.md) to verify the existing VPS
Traefik project, configure the Cloudflare record, GitHub Secrets, VM ID, environment mode,
and first-run checks.
