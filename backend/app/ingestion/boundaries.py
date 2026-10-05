from app.ingestion.cleaning import clean_content
from app.ingestion.domain import SourceSegment

DEFAULT_PROCESSING_SEGMENT_BYTES = 512 * 1024


class Utf8ProcessingBoundary:
    """Split cleaned source segments into UTF-8-safe processing units."""

    def __init__(self, *, max_bytes: int = DEFAULT_PROCESSING_SEGMENT_BYTES) -> None:
        if max_bytes < 4:
            raise ValueError("max_bytes must be at least 4 to hold any UTF-8 code point")
        self._max_bytes = max_bytes

    def split(self, segments: tuple[SourceSegment, ...]) -> tuple[SourceSegment, ...]:
        bounded: list[SourceSegment] = []
        for segment in segments:
            content = clean_content(segment.content)
            encoded = content.encode("utf-8")
            start = 0

            while start < len(encoded):
                end = min(start + self._max_bytes, len(encoded))
                while end < len(encoded) and encoded[end] & 0b1100_0000 == 0b1000_0000:
                    end -= 1

                bounded.append(
                    SourceSegment(
                        encoded[start:end].decode("utf-8"),
                        section=segment.section,
                        page_number=segment.page_number,
                    )
                )
                start = end

        return tuple(bounded)
