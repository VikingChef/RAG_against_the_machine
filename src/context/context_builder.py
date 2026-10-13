"""Build model-facing context from selected chunks."""

from src.models.chunk import Chunk
from src.models.context_result import ContextResult


class ContextBuilder:
    """Format selected chunks into model-facing context."""

    def build(
        self,
        chunks: list[Chunk],
    ) -> ContextResult:
        """Build model-facing context from ordered chunks."""

        context_blocks: list[str] = []

        for chunk in chunks:
            context_block = (
                f"File: {chunk.file_path}\n"
                f"Characters: {chunk.first_character_index}-"
                f"{chunk.last_character_index}\n\n"
                f"{chunk.text}"
            )
            context_blocks.append(context_block)

        context_text = "\n\n---\n\n".join(context_blocks)

        return ContextResult(
            context_text=context_text,
            selected_chunks=chunks,
        )
