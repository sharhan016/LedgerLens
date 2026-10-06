# Hostinger VPS deployment

This document describes the prepared deployment contract for
`https://ledgerlens.sharhan.dev`. It does not record a VPS address, credential, private
key, or certificate. Repository preparation does not deploy the application or change
Cloudflare DNS.

The implementation follows Hostinger's official
[Deploy to Hostinger VPS action](https://github.com/hostinger/deploy-on-vps) and its
[shared Traefik network model](https://www.hostinger.com/support/connecting-multiple-docker-compose-projects-using-traefik-in-hostinger-docker-manager/).

## Runtime contract

`docker-compose.production.yml` defines three services:

| Service | Build or image | Internal port | Health | Public | Persistence |
| --- | --- | ---: | --- | --- | --- |
| `frontend` | Multi-stage React build, Nginx runtime | 80 | Nginx proxies `/health/ready` | Through Traefik only | None |
| `backend` | `backend/Dockerfile` | 8000 | Database-backed `/health/ready` | No | None |
| `db` | `pgvector/pgvector:pg16` | 5432 | `pg_isready` | No | `ledgerlens_postgres` volume |

Only `frontend` joins the external Traefik network. Backend and PostgreSQL are reachable
only on the Compose application network. The production Compose file has no host `ports`
mappings.

The existing `docker-compose.yml` remains the local demo contract, including ports 5173,
8000, and 5432. Continue to use `docker compose up --build` locally.

## Public routing and TLS

Hostinger's Traefik project must exist before LedgerLens is deployed. Its shared external
Docker network is expected to be named `traefik-proxy`; set the `TRAEFIK_NETWORK`
repository variable if the actual network has a different name.

The frontend labels configure:

- router name `ledgerlens`;
- host rule `Host("ledgerlens.sharhan.dev")`;
- `websecure` entrypoint;
- TLS with the `letsencrypt` certificate resolver;
- Nginx container port 80 as the upstream service.

Traefik owns host ports 80 and 443. LedgerLens does not bind either port.

The React build uses an empty `VITE_API_BASE_URL`, so browser requests are same-origin:

```text
https://ledgerlens.sharhan.dev/api/...
```

Nginx proxies `/api/` and `/health/` to `backend:8000`. No deployed browser request points
to localhost. Container health checks may use localhost inside their own network namespace.

## Environment modes

The prepared workflow defaults to `LEDGERLENS_ENV=showcase`. This mode is suitable only
for the public synthetic portfolio demonstration: it enables the synthetic personas,
deterministic ML adapters, extractive non-LLM answers, and idempotent synthetic seed.
No customer or institution data may be loaded into that deployment.

`LEDGERLENS_ENV=production` preserves the stricter application checks. Production rejects:

- placeholder JWT secrets;
- demo authentication;
- deterministic demo embedding/reranking;
- demo extractive generation.

A true production deployment therefore requires a real identity/login integration before
the current browser UI is usable. It also requires `LEDGERLENS_INSTALL_ML=true`,
`LEDGERLENS_ML_MODE=sentence_transformers`, and a real generation provider. This is an
explicit product limitation, not something the deployment workflow bypasses.

## GitHub configuration

Create a protected GitHub environment named `production` if approval gates are desired.
The workflow runs backend tests, frontend tests/build, a localhost-artifact check, and
Compose validation before the deployment job.

Required Actions secrets:

| Secret | Purpose |
| --- | --- |
| `HOSTINGER_API_KEY` | Authenticates Hostinger's official deployment action |
| `POSTGRES_PASSWORD` | Initializes and authenticates PostgreSQL; use a strong URL-safe value |
| `LEDGERLENS_JWT_SECRET` | Signs access tokens; use at least 32 random characters |

Optional Actions secret:

| Secret | Purpose |
| --- | --- |
| `LEDGERLENS_LLM_API_KEY` | Required by OpenRouter or another configured remote provider |

Required Actions variable:

| Variable | Purpose |
| --- | --- |
| `HOSTINGER_VM_ID` | Numeric Hostinger virtual-machine identifier |

Optional Actions variables and workflow defaults:

| Variable | Default | Notes |
| --- | --- | --- |
| `TRAEFIK_NETWORK` | `traefik-proxy` | Must match the network created by Hostinger's Traefik project |
| `LEDGERLENS_ENV` | `showcase` | Use `production` only after replacing all demo adapters and identity |
| `LEDGERLENS_ML_MODE` | `deterministic_demo` | Production value: `sentence_transformers` |
| `LEDGERLENS_INSTALL_ML` | `false` | Must be `true` for Sentence Transformers/CrossEncoder |
| `LEDGERLENS_LLM_PROVIDER` | `demo_extractive` | Production: `openrouter`, `openai_compatible`, or `local_openai` |
| `LEDGERLENS_LLM_BASE_URL` | `https://openrouter.ai/api/v1` | Provider endpoint |
| `LEDGERLENS_LLM_MODEL` | `openai/gpt-4o-mini` | Provider model identifier |
| `LEDGERLENS_DEMO_AUTH_ENABLED` | `true` | Must be `false` in production |
| `LEDGERLENS_DEMO_SEED_ENABLED` | `true` | Loads the synthetic corpus idempotently |
| `LEDGERLENS_REGULATORY_API_MODE` | `fixture` | Set `live` only with a real HTTPS service |
| `LEDGERLENS_REGULATORY_API_URL` | empty | Required for live regulatory mode |

The deployment fixes CORS to `https://ledgerlens.sharhan.dev`, disables API documentation,
and uses the existing issuer, audience, embedding dimensions, cache settings, and fixture
paths unless explicitly overridden in the Compose file.

Do not commit a `.env` file. The Hostinger action supplies deployment values to the Compose
project from GitHub Secrets and Variables.

For a private GitHub repository, follow the Hostinger action documentation to configure a
repository deploy key. Do not store a private key in this repository.

## Database lifecycle

The `pgvector/pgvector:pg16` image supplies PostgreSQL 16 and the vector extension. On each
backend start, `backend/scripts/start.sh` runs:

```text
alembic upgrade head
```

Migration `0001` executes `CREATE EXTENSION IF NOT EXISTS vector`. The backend waits for the
database health check before migration, and the frontend waits for backend readiness.

When demo seeding is enabled, the startup script then runs the existing idempotent synthetic
bootstrap. Existing tenant/source/version records are skipped.

The named `ledgerlens_postgres` volume survives container restart and normal Compose
recreation. Do not use `docker compose down --volumes`, delete the volume, or delete the
Docker Manager project with its storage when preserving data matters.

Application containers and in-memory request metrics are ephemeral. Uploaded documents,
conversations, audit events, and semantic-cache entries live in PostgreSQL and therefore
use the persistent volume.

## First deployment checklist

These are manual future actions; none were performed during repository preparation.

1. Provision a Hostinger VPS using the current Docker template.
2. Install Hostinger's Traefik project template in Docker Manager.
3. Confirm the external network name and `websecure`/`letsencrypt` identifiers match the
   production Compose labels.
4. In Cloudflare, create an `A` record named `ledgerlens` pointing to the VPS public IPv4.
   Use DNS-only mode for initial certificate issuance unless the chosen Traefik/Cloudflare
   setup is already verified.
5. Add the required GitHub Secrets and `HOSTINGER_VM_ID` variable listed above.
6. Confirm the repository visibility/deploy-key requirement.
7. Push to `main` or manually run **Verify and deploy to Hostinger**.
8. Wait for all three containers to become healthy in Hostinger Docker Manager.
9. Confirm `https://ledgerlens.sharhan.dev/health/ready` returns `status: ok`.
10. Open the site and exercise login, retrieval, citations, and a container restart.
11. If Cloudflare was initially DNS-only, enable proxying only after HTTPS and application
    health are confirmed.

## Inspecting health and logs

Use Hostinger Docker Manager to inspect project status and container logs. Expected layers:

- PostgreSQL healthy: `pg_isready` succeeds.
- Backend healthy: `/health/ready` executes `SELECT 1` successfully.
- Frontend healthy: Nginx reaches backend readiness through its internal proxy.
- Public healthy: Traefik serves the same readiness URL over HTTPS.

`/health/live` proves only that the FastAPI process is running. `/health/ready` proves the
process can reach PostgreSQL.

## Updating and rollback

Updates are deployed after a verified push to `main`. Alembic migrations run automatically
and must remain forward-compatible with the running release.

For an application rollback, revert the faulty Git commit on `main` and let the workflow
redeploy the previous application definition. Review migrations before rollback: the
startup process upgrades schemas but does not automatically downgrade them. Back up the
PostgreSQL volume before any release containing a destructive migration.

Do not remove the named volume during an application rollback.

## Pre-deployment blockers

Before the first deployment, the operator must still provide:

- a Hostinger VPS and official Traefik project;
- the confirmed Traefik external-network and resolver names;
- GitHub Secrets and `HOSTINGER_VM_ID`;
- the Cloudflare DNS record;
- a decision to run the synthetic `showcase` mode or complete real identity/provider setup
  for strict `production` mode.
