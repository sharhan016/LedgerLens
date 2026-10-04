import re

from app.ingestion.cleaning import clean_content
from app.ingestion.domain import PreparedChunk, SourceSegment

TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def estimate_tokens(content: str) -> int:
    return len(TOKEN_PATTERN.findall(content))


class SectionAwareChunker:
    def __init__(self, *, max_words: int = 180, overlap_words: int = 30) -> None:
        if max_words < 20:
            raise ValueError("max_words must be at least 20")
        if overlap_words < 0 or overlap_words >= max_words:
            raise ValueError("overlap_words must be between zero and max_words")
        self._max_words = max_words
        self._step = max_words - overlap_words

    def chunk(self, segments: tuple[SourceSegment, ...]) -> tuple[PreparedChunk, ...]:
        chunks: list[PreparedChunk] = []
        for segment in segments:
            cleaned = clean_content(segment.content)
            words = cleaned.split()
            for start in range(0, len(words), self._step):
                window = words[start : start + self._max_words]
                if not window:
                    continue
                content = " ".join(window)
                chunks.append(
                    PreparedChunk(
                        ordinal=len(chunks),
                        content=content,
                        token_count=estimate_tokens(content),
                        section=segment.section,
                        page_number=segment.page_number,
                        embedding=None,
                    )
                )
                if start + self._max_words >= len(words):
                    break
        if not chunks:
            raise ValueError("document contains no content after cleaning")
        return tuple(chunks)
