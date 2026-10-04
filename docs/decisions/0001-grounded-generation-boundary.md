# 0001: Keep generation provider-neutral and validate its citations

- Status: accepted
- Date: 2026-10-04

## Context

LedgerLens must work with OpenAI-compatible hosted APIs, OpenRouter, and practical local
servers without spreading provider-specific payloads through retrieval or API code. Model
output is not evidence by itself: a fluent answer may cite an unknown source or make a
claim that is not supported by its cited passage.

## Decision

Generation receives a typed request containing only the authorized, bounded, labeled
context produced after retrieval. Providers implement one interface and return an answer,
model identity, and cited source identifiers. The OpenAI-compatible adapter is configured
by environment; OpenRouter adds only its attribution headers, and local OpenAI-compatible
servers need no separate implementation.

Answers pass through a deterministic validator. It rejects unknown citation identifiers,
measures citation coverage and lexical support per factual sentence, reports unsupported
claims, and exposes a bounded confidence signal. These signals are diagnostic—not a
probability that the answer is true. When retrieval returns no evidence, the service does
not call an LLM and explicitly reports that no authorized source material was found.

## Consequences

- Provider changes do not alter retrieval or response contracts.
- The browser can inspect sources, passages, component scores, query transformations,
  grounding diagnostics, and stage latency.
- Lexical support is conservative and cannot establish semantic entailment; evaluation and
  stronger verification can be added without changing the provider boundary.
- Provider credentials remain environment configuration and never enter prompts, logs, or
  committed files.

