import time
from dataclasses import dataclass

from app.generation.context import ContextBuilder
from app.generation.domain import ContextSource, GenerationRequest, GroundingReport, LLMGeneration
from app.generation.grounding import GroundingValidator
from app.generation.providers import LLMProvider
from app.generation.query import QueryPlan, RuleBasedQueryPlanner
from app.retrieval.domain import RetrievalCandidate
from app.retrieval.orchestrator import HybridRetrievalOrchestrator
from app.security.principal import Principal


@dataclass(frozen=True, slots=True)
class AssistantResult:
    answer: str
    model: str
    plan: QueryPlan
    sources: tuple[ContextSource, ...]
    passages: tuple[RetrievalCandidate, ...]
    grounding: GroundingReport
    latency_ms: dict[str, float]


class AssistantService:
    def __init__(
        self,
        *,
        retrieval: HybridRetrievalOrchestrator,
        provider: LLMProvider,
        planner: RuleBasedQueryPlanner | None = None,
        context_builder: ContextBuilder | None = None,
        validator: GroundingValidator | None = None,
    ) -> None:
        self._retrieval = retrieval
        self._provider = provider
        self._planner = planner or RuleBasedQueryPlanner()
        self._context_builder = context_builder or ContextBuilder()
        self._validator = validator or GroundingValidator()

    async def answer(self, principal: Principal, question: str) -> AssistantResult:
        started = time.perf_counter()
        plan = self._planner.plan(question)
        planned = time.perf_counter()
        passages = await self._retrieval.search(principal, plan.retrieval_query)
        retrieved = time.perf_counter()
        context, sources = self._context_builder.build(passages)
        if not sources:
            generation_answer = "I could not find authorized source material for this question."
            generation = LLMGeneration(generation_answer, (), "no-evidence")
        else:
            generation = await self._provider.generate(
                GenerationRequest(
                    question=plan.original_query,
                    context=context,
                    sources=sources,
                    intent=plan.intent.value,
                )
            )
        generated = time.perf_counter()
        retrieval_quality = (
            sum((item.rerank_score or 0.0) for item in passages) / len(passages)
            if passages
            else 0.0
        )
        grounding = self._validator.validate(
            generation,
            sources,
            retrieval_quality=max(0.0, min(1.0, retrieval_quality)),
        )
        finished = time.perf_counter()
        return AssistantResult(
            answer=generation.answer,
            model=generation.model,
            plan=plan,
            sources=sources,
            passages=tuple(passages),
            grounding=grounding,
            latency_ms={
                "planning": round((planned - started) * 1000, 3),
                "retrieval": round((retrieved - planned) * 1000, 3),
                "generation": round((generated - retrieved) * 1000, 3),
                "validation": round((finished - generated) * 1000, 3),
                "total": round((finished - started) * 1000, 3),
            },
        )
