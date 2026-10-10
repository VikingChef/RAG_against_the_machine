"""Build model-facing context from retrieved search results."""

from src.models.context_result import ContextResult
from src.models.search_result import SearchResult


class ContextBuilder:
    """Format retrieved search results into model-facing context."""

    def build(
        self,
        results: list[SearchResult],
    ) -> ContextResult:
        """Build model-facing context from ordered search results."""

        context_blocks: list[str] = []

        for result in results:
            context_block = (
                f"File: {result.chunk.file_path}\n"
                f"Characters: {result.chunk.first_character_index}-"
                f"{result.chunk.last_character_index}\n\n"
                f"{result.chunk.text}"
            )
            context_blocks.append(context_block)

        context_text = "\n\n---\n\n".join(context_blocks)

        return ContextResult(
            context_text=context_text,
            selected_results=results,
        )
