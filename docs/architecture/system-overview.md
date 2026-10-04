# System architecture

## Boundaries

```text
Browser (React)
      │ JSON/HTTP
FastAPI application
      ├── identity and authorization
      ├── ingestion and document lifecycle
      ├── query understanding and routing
      ├── retrieval orchestration
      │     ├── pgvector dense retrieval
      │     ├── PostgreSQL full-text retrieval
      │     ├── governed SQL retrieval
      │     └── typed API adapters
      ├── RRF, reranking, and context construction
      ├── provider-neutral LLM generation
      ├── citation and grounding validation
      └── audit, metrics, cache, and evaluation
                    │
          PostgreSQL + pgvector
```

The API is the authorization boundary. Tenant and role filters are applied in repository
and retrieval queries; the browser is not trusted to enforce access. Retrieval strategies
implement narrow interfaces so dense, keyword, SQL, and API results can be tested in
isolation before orchestration.

## Initial runtime

The foundation runs as three local services: a Vite React web application, a FastAPI API,
and PostgreSQL with pgvector. The current API exposes only readiness information. Product
capabilities appear only after their Vertex task is implemented and verified.

## Evolution rules

1. Keep transport schemas separate from persistence models and domain services.
2. Keep provider-specific LLM and embedding code behind typed interfaces.
3. Persist source/version/location/authorization metadata through every ingestion and
   retrieval stage.
4. Treat citations and grounding as validated output, not presentation decoration.
5. Prefer deterministic test doubles at boundaries while preserving real local-model and
   PostgreSQL implementations for integration proof.
6. Record latency and audit events without logging secrets or unrestricted document text.

