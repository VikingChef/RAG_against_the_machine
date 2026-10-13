"""Expose the indexing workflow through a pipeline interface."""

from pathlib import Path

from src.indexing.indexer import Indexer
from src.models.chunk import Chunk


class IndexPipeline:
    """Run the corpus indexing workflow."""

    def __init__(
        self,
        indexer: Indexer,
    ) -> None:
        """Initialize the pipeline with its indexer."""

        self.indexer = indexer

    def run(
        self,
        corpus_root: Path,
        index_path: Path,
    ) -> list[Chunk]:
        """Run indexing for a corpus and return the finalized chunks."""

        chunks = self.indexer.index(corpus_root, index_path)

        return chunks
