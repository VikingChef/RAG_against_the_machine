"""Coordinates single-query and dataset retrieval workflows."""

from src.output.output_builder import OutputBuilder
from src.retrieval.retriever import Retriever
from src.models.query import Query
from src.models.search_result import SearchResult
from src.models.evaluation_models import RagDataset
from src.models.evaluation_models import StudentSearchResults
from src.models.evaluation_models import MinimalSearchResults


class SearchPipeline:
    """Manages search workflows using a retriever and output builder."""

    def __init__(
        self,
        retriever: Retriever,
        output_builder: OutputBuilder,
    ) -> None:
        """Initialize the pipeline with its retriever and output builder."""

        self.retriever = retriever
        self.output_builder = output_builder

    def search(
        self,
        query: Query,
    ) -> list[SearchResult]:
        """Search for one query and return the ranked results."""

        results = self.retriever.search(query)

        return results

    def search_dataset(
        self,
        dataset: RagDataset,
        k: int,
    ) -> StudentSearchResults:
        """Search a dataset and build evaluator-facing search results."""

        search_results: list[MinimalSearchResults] = []

        for question in dataset.rag_questions:
            query = Query(
                text=question.question,
                k=k,
            )

            retrieved_results = self.search(query)

            converted_result = self.output_builder.build_search_result(
                question_id=question.question_id,
                question=question.question,
                results=retrieved_results,
            )

            search_results.append(converted_result)

        return self.output_builder.build_search_results(
            results=search_results,
            k=k,
        )
