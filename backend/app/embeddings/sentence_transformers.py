import asyncio
from functools import partial


class MissingMLDependencyError(RuntimeError):
    pass


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str, *, dimensions: int = 384) -> None:
        self._model_name = model_name
        self._dimensions = dimensions
        self._model = None

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def _load_model(self):  # type: ignore[no-untyped-def]
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                raise MissingMLDependencyError(
                    "install LedgerLens with the 'ml' extra to use local embeddings"
                ) from error
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def _embed_sync(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        result = vectors.tolist()
        if any(len(vector) != self._dimensions for vector in result):
            raise ValueError(
                f"embedding model dimensions do not match configured {self._dimensions}"
            )
        return result

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(self._embed_sync, texts))

