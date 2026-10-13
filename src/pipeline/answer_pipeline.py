"""Coordinate retrieval, context building, prompting, and answer generation."""

from src.context.context_builder import ContextBuilder
from src.context.token_budget import TokenBudget
from src.generation.generator import Generator
from src.generation.model_manager import ModelManager
from src.models.answer_result import AnswerResult
from src.models.chunk import Chunk
from src.models.context_result import ContextResult
from src.models.query import Query
from src.models.search_result import SearchResult
from src.prompting.prompt_builder import PromptBuilder
from src.retrieval.retriever import Retriever


class AnswerPipeline:
    """Run the complete answer-generation pipeline for a query."""

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        prompt_builder: PromptBuilder,
        model_manager: ModelManager,
        token_budget: TokenBudget,
        generator: Generator,
    ) -> None:
        """Initialize the pipeline with its shared services."""
        self.retriever = retriever
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.model_manager = model_manager
        self.token_budget = token_budget
        self.generator = generator

    def answer(self, query: Query) -> AnswerResult:
        """Retrieve sources and generate an answer for a query."""
        search_results = self.retriever.search(query)

        return self.answer_from_results(
            query,
            search_results,
        )

    def answer_from_results(
        self,
        query: Query,
        search_results: list[SearchResult],
    ) -> AnswerResult:
        """Generate an answer from already retrieved search results."""
        chunks = [
            result.chunk
            for result in search_results
        ]

        answer_text, selected_count = self._generate_from_chunks(
            query,
            chunks,
        )

        return AnswerResult(
            answer=answer_text,
            search_results=search_results[:selected_count],
        )

    def _generate_from_chunks(
        self,
        query: Query,
        chunks: list[Chunk],
    ) -> tuple[str, int]:
        """Generate an answer from ordered chunks within the token budget."""
        fitted_prompt = self._build_fitting_prompt(
            query,
            chunks,
        )

        if fitted_prompt is None:
            return (
                "The query is too large to fit within the model "
                "context window.",
                0,
            )

        context, formatted_prompt = fitted_prompt
        answer_text = self.generator.generate(formatted_prompt)

        return answer_text, len(context.selected_chunks)

    def _build_fitting_prompt(
        self,
        query: Query,
        chunks: list[Chunk],
    ) -> tuple[ContextResult, str] | None:
        """Build the largest model prompt that fits the token budget."""
        selected_chunks = chunks[:]

        while True:
            context = self.context_builder.build(selected_chunks)
            prompt_string = self.prompt_builder.build(
                query,
                context,
            )
            formatted_prompt = self.model_manager.format_prompt(
                prompt_string,
            )

            if self.token_budget.fits(formatted_prompt):
                return context, formatted_prompt

            if not selected_chunks:
                return None

            selected_chunks = selected_chunks[:-1]
