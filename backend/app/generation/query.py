import re
from dataclasses import dataclass
from enum import StrEnum


class QueryIntent(StrEnum):
    FACT = "fact"
    COMPARISON = "comparison"
    LATEST_POLICY = "latest_policy"


@dataclass(frozen=True, slots=True)
class QueryPlan:
    original_query: str
    retrieval_query: str
    intent: QueryIntent
    route: str
    transformations: tuple[str, ...]


class RuleBasedQueryPlanner:
    synonyms = {
        r"\bkyc\b": "know your customer KYC",
        r"\baml\b": "anti money laundering AML",
        r"\bfee\b": "fee charge pricing",
    }

    def plan(self, query: str) -> QueryPlan:
        normalized = " ".join(query.strip().split())
        lowered = normalized.lower()
        if any(token in lowered for token in ("compare", "difference", "versus", " vs ")):
            intent = QueryIntent.COMPARISON
        elif any(token in lowered for token in ("latest", "current policy", "most recent")):
            intent = QueryIntent.LATEST_POLICY
        else:
            intent = QueryIntent.FACT
        rewritten = normalized
        transformations: list[str] = []
        for pattern, replacement in self.synonyms.items():
            if re.search(pattern, rewritten, flags=re.IGNORECASE):
                rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
                label = pattern.replace("\\b", "")
                transformations.append(f"expanded:{label}")
        return QueryPlan(
            original_query=normalized,
            retrieval_query=rewritten,
            intent=intent,
            route="hybrid_knowledge",
            transformations=tuple(transformations),
        )
