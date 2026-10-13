"""Resolve saved source locations to indexed chunks."""

from src.errors.application_errors import SourceChunkNotFoundError
from src.models.chunk import Chunk
from src.models.evaluation_models import MinimalSource


def resolve_sources(
    sources: list[MinimalSource],
    chunks: list[Chunk],
) -> list[Chunk]:
    """Resolve saved source locations to their indexed chunks."""

    resolved_chunks: list[Chunk] = []

    for source in sources:
        matched_chunk = None

        for chunk in chunks:
            if (
                source.file_path == chunk.file_path
                and source.first_character_index == chunk.first_character_index
                and source.last_character_index == chunk.last_character_index
            ):
                matched_chunk = chunk
                break

        if matched_chunk is None:
            raise SourceChunkNotFoundError(
                source.file_path,
                source.first_character_index,
                source.last_character_index,
            )

        resolved_chunks.append(matched_chunk)

    return resolved_chunks
