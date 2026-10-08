"""Persist and load finalized chunks for retrieval."""

import json
from pathlib import Path

from src.models.chunk import Chunk


class IndexStore:
    """Persist finalized chunks, and load them again later."""

    def save(self, chunks: list[Chunk], path: Path) -> None:
        """Save finalized chunks as JSON at the provided path."""

        path.parent.mkdir(parents=True, exist_ok=True)
        serialized_chunks = [
            chunk.model_dump()
            for chunk in chunks
        ]
        with path.open("w", encoding="utf-8") as file:
            json.dump(
                serialized_chunks,
                file,
                indent=2,
                ensure_ascii=False,
                )

    def load(self, path: Path) -> list[Chunk]:
        """Load finalized JSON chunks and return validated Chunk objects."""

        with path.open("r", encoding="utf-8") as file:
            loaded_data = json.load(file)

        chunks: list[Chunk] = []

        for chunk_data in loaded_data:
            chunk = Chunk.model_validate(chunk_data)
            chunks.append(chunk)

        return chunks
