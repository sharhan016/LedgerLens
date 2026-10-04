import io
from pathlib import Path
from typing import Protocol

from pypdf import PdfReader

from app.ingestion.domain import IngestionSource, SourceSegment


class UnsupportedDocumentError(ValueError):
    pass


class DocumentParser(Protocol):
    extensions: frozenset[str]

    def parse(self, source: IngestionSource) -> tuple[SourceSegment, ...]: ...


class MarkdownParser:
    extensions = frozenset({".md", ".markdown"})

    def parse(self, source: IngestionSource) -> tuple[SourceSegment, ...]:
        text = source.content.decode("utf-8")
        lines = text.splitlines()
        segments: list[SourceSegment] = []
        section: str | None = None
        content: list[str] = []
        in_frontmatter = bool(lines and lines[0].strip() == "---")

        for line in lines[1:] if in_frontmatter else lines:
            if in_frontmatter:
                if line.strip() == "---":
                    in_frontmatter = False
                continue
            if line.startswith("#"):
                if content:
                    segments.append(SourceSegment("\n".join(content), section=section))
                    content = []
                section = line.lstrip("#").strip()
            else:
                content.append(line)
        if content:
            segments.append(SourceSegment("\n".join(content), section=section))
        return tuple(segment for segment in segments if segment.content.strip())


class TextParser:
    extensions = frozenset({".txt"})

    def parse(self, source: IngestionSource) -> tuple[SourceSegment, ...]:
        return (SourceSegment(source.content.decode("utf-8")),)


class PdfParser:
    extensions = frozenset({".pdf"})

    def parse(self, source: IngestionSource) -> tuple[SourceSegment, ...]:
        reader = PdfReader(io.BytesIO(source.content))
        return tuple(
            SourceSegment(page.extract_text() or "", page_number=index)
            for index, page in enumerate(reader.pages, start=1)
            if (page.extract_text() or "").strip()
        )


class ParserRegistry:
    def __init__(self, parsers: tuple[DocumentParser, ...] | None = None) -> None:
        self._parsers = parsers or (MarkdownParser(), TextParser(), PdfParser())

    @property
    def supported_extensions(self) -> frozenset[str]:
        return frozenset(extension for parser in self._parsers for extension in parser.extensions)

    def parse(self, source: IngestionSource) -> tuple[SourceSegment, ...]:
        extension = Path(source.filename).suffix.lower()
        parser = next(
            (candidate for candidate in self._parsers if extension in candidate.extensions), None
        )
        if parser is None:
            supported = ", ".join(sorted(self.supported_extensions))
            raise UnsupportedDocumentError(f"unsupported document type; expected one of {supported}")
        segments = parser.parse(source)
        if not segments:
            raise ValueError("document contains no extractable text")
        return segments

