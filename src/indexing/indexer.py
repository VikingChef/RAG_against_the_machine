"""Coordinates corpus loading, chunking, and index persistence."""

from pathlib import Path

from src.models.chunk import Chunk
from src.indexing.corpus_loader import CorpusLoader
from src.indexing.python_chunker import PythonChunker
from src.indexing.text_chunker import TextChunker
from src.indexing.index_store import IndexStore


class Indexer:
    """Orchestrates corpus loading, chunking, and persistence."""

    def __init__(
        self,
        corpus_loader: CorpusLoader,
        python_chunker: PythonChunker,
        text_chunker: TextChunker,
        index_store: IndexStore,
    ) -> None:
        """Initialize the indexer with its workflow collaborators."""

        self.corpus_loader = corpus_loader
        self.python_chunker = python_chunker
        self.text_chunker = text_chunker
        self.index_store = index_store

    def index(
        self,
        corpus_root: Path,
        index_path: Path,
    ) -> list[Chunk]:
        """Load, chunk, persist, and return finalized corpus chunks."""

        source_files = self.corpus_loader.load(corpus_root)

        chunks: list[Chunk] = []

        for source_file in source_files:
            if source_file.file_type == ".py":
                file_chunks = self.python_chunker.chunk(source_file)
            else:
                file_chunks = self.text_chunker.chunk(source_file)
            chunks.extend(file_chunks)

        self.index_store.save(
            chunks=chunks,
            path=index_path,
            )

        return chunks
