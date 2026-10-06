"""Build BM25 indexes from finalized chunks."""

from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from src.models.chunk import Chunk
from src.retrieval.retrieval_utils import RetrievalTokenizer


class BM25Builder:
    """Build BM25 indexes from finalized chunks."""

    def __init__(
        self,
        tokenizer: RetrievalTokenizer,
    ) -> None:
        """Initialize the builder with a retrieval tokenizer."""

        self.tokenizer = tokenizer

    def build(
        self,
        chunks: list[Chunk],
    ) -> BM25Okapi:
        """Build a BM25 index from finalized chunks."""

        if not chunks:
            raise ValueError("Can't build BM25 index from an empty chunk list")

        tokenized_corpus: list[list[str]] = []

        for chunk in chunks:
            chunk_tokens = self.tokenizer.tokenize(chunk.text)
            tokenized_corpus.append(chunk_tokens)
        bm25_index = BM25Okapi(tokenized_corpus)

        return bm25_index
