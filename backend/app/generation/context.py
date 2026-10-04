from app.generation.domain import ContextSource
from app.retrieval.domain import RetrievalCandidate


class ContextBuilder:
    def __init__(self, max_characters: int = 14_000) -> None:
        self._max_characters = max_characters

    def build(
        self, candidates: list[RetrievalCandidate]
    ) -> tuple[str, tuple[ContextSource, ...]]:
        blocks: list[str] = []
        sources: list[ContextSource] = []
        used = 0
        for index, candidate in enumerate(candidates, start=1):
            source_id = f"S{index}"
            location = (
                f"page {candidate.page_number}"
                if candidate.page_number is not None
                else candidate.section or "location unavailable"
            )
            header = (
                f"[{source_id}] {candidate.title} | {candidate.source} | "
                f"version {candidate.version} | {location}"
            )
            available = self._max_characters - used - len(header) - 2
            if available <= 0:
                break
            content = candidate.content[:available]
            block = f"{header}\n{content}"
            blocks.append(block)
            used += len(block) + 2
            sources.append(
                ContextSource(
                    source_id=source_id,
                    chunk_id=str(candidate.chunk_id),
                    document_id=str(candidate.document_id),
                    title=candidate.title,
                    source=candidate.source,
                    version=candidate.version,
                    content=content,
                    section=candidate.section,
                    page_number=candidate.page_number,
                )
            )
        return "\n\n".join(blocks), tuple(sources)

