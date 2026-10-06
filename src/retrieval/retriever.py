"""Retrieve and rank chunks using BM25."""

from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from src.models.chunk import Chunk
from src.models.query import Query
from src.models.search_result import SearchResult
from src.retrieval.retrieval_utils import RetrievalTokenizer


class Retriever:
    """Search a prepared BM25 index and return ranked chunk results."""

    def __init__(
        self,
        bm25_index: BM25Okapi,
        chunks: list[Chunk],
        tokenizer: RetrievalTokenizer,
    ) -> None:
        """Initialize retriever with its BM25 index, chunks, and tokenizer."""

        self.bm25_index = bm25_index
        self.chunks = chunks
        self.tokenizer = tokenizer

    def search(
        self,
        query: Query,
    ) -> list[SearchResult]:
        """Search the BM25 index for the query and return the top results."""

        query_tokens = self.tokenizer.tokenize(query.text)
        bm25_scores = self.bm25_index.get_scores(query_tokens)

        scored_chunks: list[tuple[Chunk, float]] = []

        for chunk, score in zip(self.chunks, bm25_scores):
            scored_chunks.append((chunk, score))

        sorted_scored_chunks = sorted(
            scored_chunks,
            key=lambda item: item[1],
            reverse=True,
        )

        top_scored_chunks = sorted_scored_chunks[:query.k]

        results: list[SearchResult] = []

        for rank, (chunk, score) in enumerate(top_scored_chunks, start=1):
            result = SearchResult(
                chunk=chunk,
                score=score,
                rank=rank,
            )
            results.append(result)

        return results
