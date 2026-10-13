"""Coordinate retrieval, context building, prompting, and answer generation."""

from src.context.context_builder import ContextBuilder
from src.context.token_budget import TokenBudget
from src.generation.generator import Generator
from src.generation.model_manager import ModelManager
from src.models.answer_result import AnswerResult
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
        fitted_prompt = self._build_fitting_prompt(
            query,
            search_results,
        )

        if fitted_prompt is None:
            return AnswerResult(
                answer=(
                    "The query is too large to fit within the model "
                    "context window."
                ),
                search_results=[],
            )

        context, formatted_prompt = fitted_prompt
        answer_text = self.generator.generate(formatted_prompt)

        return AnswerResult(
            answer=answer_text,
            search_results=context.selected_results,
        )

    def _build_fitting_prompt(
        self,
        query: Query,
        search_results: list[SearchResult],
    ) -> tuple[ContextResult, str] | None:
        """Build the largest model prompt that fits the token budget."""
        selected_results = search_results[:]

        while True:
            context = self.context_builder.build(selected_results)
            prompt_string = self.prompt_builder.build(
                query,
                context,
            )
            formatted_prompt = self.model_manager.format_prompt(
                prompt_string,
            )

            if self.token_budget.fits(formatted_prompt):
                return context, formatted_prompt

            if not selected_results:
                return None

            selected_results = selected_results[:-1]
