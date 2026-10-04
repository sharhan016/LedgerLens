from dataclasses import replace

from app.retrieval.domain import RetrievalCandidate


def reciprocal_rank_fusion(
    dense: list[RetrievalCandidate],
    keyword: list[RetrievalCandidate],
    *,
    constant: int = 60,
) -> list[RetrievalCandidate]:
    if constant <= 0:
        raise ValueError("RRF constant must be positive")
    merged: dict[object, RetrievalCandidate] = {}
    contributions: dict[object, float] = {}

    for channel, candidates in (("dense", dense), ("keyword", keyword)):
        for rank, candidate in enumerate(candidates, start=1):
            score = candidate.dense_score if channel == "dense" else candidate.keyword_score
            ranked = candidate.with_rank(channel=channel, rank=rank, score=score or 0.0)
            existing = merged.get(candidate.chunk_id)
            if existing is not None:
                ranked = replace(
                    existing,
                    dense_rank=ranked.dense_rank or existing.dense_rank,
                    dense_score=(
                        ranked.dense_score
                        if ranked.dense_rank is not None
                        else existing.dense_score
                    ),
                    keyword_rank=ranked.keyword_rank or existing.keyword_rank,
                    keyword_score=(
                        ranked.keyword_score
                        if ranked.keyword_rank is not None
                        else existing.keyword_score
                    ),
                )
            merged[candidate.chunk_id] = ranked
            contributions[candidate.chunk_id] = contributions.get(candidate.chunk_id, 0.0) + (
                1.0 / (constant + rank)
            )

    fused = [replace(item, rrf_score=contributions[item.chunk_id]) for item in merged.values()]
    return sorted(fused, key=lambda item: item.rrf_score, reverse=True)

