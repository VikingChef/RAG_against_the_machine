"""Build evaluator-facing output models from internal application results."""

from src.models.evaluation_models import (
    MinimalAnswer,
    MinimalSearchResults,
    MinimalSource,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)
from src.models.search_result import SearchResult


class OutputBuilder:
    """Build evaluator-facing output models."""

    def build_source(
        self,
        result: SearchResult,
    ) -> MinimalSource:
        """Build a minimal source from one retrieval result."""

        return MinimalSource(
            file_path=result.chunk.file_path,
            first_character_index=result.chunk.first_character_index,
            last_character_index=result.chunk.last_character_index,
        )

    def build_search_result(
        self,
        question_id: str,
        question: str,
        results: list[SearchResult],
    ) -> MinimalSearchResults:
        """Build evaluator-facing search results for one question."""

        retrieved_sources: list[MinimalSource] = []

        for result in results:
            source = self.build_source(result)

            retrieved_sources.append(source)

        return MinimalSearchResults(
            question_id=question_id,
            question=question,
            retrieved_sources=retrieved_sources,
        )

    def build_search_results(
        self,
        results: list[MinimalSearchResults],
        k: int,
    ) -> StudentSearchResults:
        """Build evaluator-facing search results for a dataset."""

        return StudentSearchResults(
            search_results=results,
            k=k,
        )

    def build_answer(
        self,
        search_result: MinimalSearchResults,
        answer: str,
    ) -> MinimalAnswer:
        """Build an evaluator-facing answer for one question."""

        return MinimalAnswer(
            question_id=search_result.question_id,
            question=search_result.question,
            retrieved_sources=search_result.retrieved_sources,
            answer=answer,
        )

    def build_answers(
        self,
        answers: list[MinimalAnswer],
        k: int,
    ) -> StudentSearchResultsAndAnswer:
        """Build evaluator-facing answers for a dataset."""

        return StudentSearchResultsAndAnswer(
            search_results=answers,
            k=k,
        )
