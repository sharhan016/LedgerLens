# LedgerLens demo runbook

## Before the demonstration

1. Copy `.env.example` to `.env` and replace the development JWT secret.
2. Start `docker compose up --build` and wait until the API reports healthy.
3. Open `http://localhost:5173` in a private browser window.
4. Confirm the header says **Synthetic environment · no customer data**.

The first boot can take longer when `LEDGERLENS_ML_MODE=sentence_transformers` because
model weights are downloaded. The default Compose mode is offline and deterministic.

## Suggested journey

1. Enter as **Mira Fernandes / compliance**.
2. Ask: “What is the minimum balance requirement for the Premium Savings Account?”
3. Open citation **S1** and point out source, version, section, hybrid scores, rerank score,
   and the authorization validation marker.
4. Visit **Knowledge base** to show the ingested policy versions.
5. Visit **Evaluation** to show retrieval recall and answer-term coverage.
6. Visit **Operations** to show content-safe route, status, count, and latency telemetry.
7. End the session, enter as another persona, and explain that tenant and role predicates
   are applied before ranking; the orchestration layer validates results again.

## Real-provider mode

For the portfolio demonstration with real local ML, set:

```dotenv
LEDGERLENS_ML_MODE=sentence_transformers
LEDGERLENS_INSTALL_ML=true
LEDGERLENS_LLM_PROVIDER=local_openai
LEDGERLENS_LLM_BASE_URL=http://host.docker.internal:11434/v1
LEDGERLENS_LLM_MODEL=qwen2.5:7b-instruct
```

Start the compatible model server before LedgerLens. OpenAI-compatible and OpenRouter
providers use the same boundary. Provider failures surface as failures; the application
does not silently invent an answer.

## Troubleshooting

- `/health/live` proves the API process is running; `/health/ready` additionally proves
  PostgreSQL is reachable.
- If no documents appear, inspect backend startup output for the migration and synthetic
  seed steps. Both are idempotent and safe to rerun.
- If the real ML path cannot download weights, use the documented deterministic demo mode
  and state clearly that it is a demo adapter.
- Never load customer records into this repository or the demo tenant.
