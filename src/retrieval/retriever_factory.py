"""Assemble a ready retriever from persisted index data."""

from pathlib import Path

from src.indexing.index_store import IndexStore
from src.indexing.bm25_builder import BM25Builder
from src.retrieval.retriever import Retriever
from src.retrieval.retrieval_utils import RetrievalTokenizer


class RetrieverFactory:
    """Build a ready Retriever from persisted index data."""

    def __init__(
        self,
        index_store: IndexStore,
        bm25_builder: BM25Builder,
        tokenizer: RetrievalTokenizer,
    ) -> None:
        """Initialize factory with dependencies needed to build retrievers."""

        self.index_store = index_store
        self.bm25_builder = bm25_builder
        self.tokenizer = tokenizer

    def create(
        self,
        index_path: Path,
    ) -> Retriever:
        """Create a Retriever from persisted index data."""

        chunks = self.index_store.load(index_path)
        bm25_index = self.bm25_builder.build(chunks)

        retriever = Retriever(
            bm25_index=bm25_index,
            chunks=chunks,
            tokenizer=self.tokenizer,
        )

        return retriever
