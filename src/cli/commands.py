"""Expose indexing, retrieval, answering, and evaluation as CLI commands."""

from pathlib import Path

from src.app.app_builder import AppBuilder
from src.config.config import Config
from src.datasets.dataset_loader import DatasetLoader
from src.datasets.dataset_writer import DataSetWriter
from src.models.evaluation_models import AnsweredQuestion, StudentSearchResults
from src.models.query import Query
from src.output.output_builder import OutputBuilder


class Commands:
    """Provide the commands exposed through Python Fire."""

    def __init__(self) -> None:
        """Initialize the CLI with conventional project paths."""

        self.corpus_root = Path("data/raw")
        self.index_path = Path("data/processed/chunks.json")

    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the raw corpus using the requested maximum chunk size."""

        if max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be positive")

        builder = AppBuilder(Config(max_chunk_size=max_chunk_size))
        chunks = builder.build_index_pipeline().run(
            self.corpus_root, self.index_path
        )

        print(f"Indexed {len(chunks)} chunks into {self.index_path}")

    def search(self, query: str, k: int = 10) -> None:
        """Print ranked source locations for a single query."""

        pipeline = AppBuilder(Config()).build_search_pipeline(self.index_path)
        results = pipeline.search(Query(text=query, k=k))
        output_builder = OutputBuilder()

        for result in results:
            source = output_builder.build_source(result)
            print(source.model_dump_json())

    def search_dataset(
        self,
        dataset_path: str,
        k: int = 10,
        save_directory: str = "outputs",
    ) -> None:
        """Retrieve sources for a dataset and save evaluator-facing JSON."""

        dataset = DatasetLoader().load(Path(dataset_path))
        pipeline = AppBuilder(Config()).build_search_pipeline(self.index_path)
        results = pipeline.search_dataset(dataset, k)
        destination = Path(save_directory)
        destination.mkdir(parents=True, exist_ok=True)
        output_path = destination / "student_search_results.json"
        DataSetWriter().write(results, output_path)
        print(f"Saved search results to {output_path}")

    def answer(self, query: str, k: int = 10) -> None:
        """Retrieve sources and print a generated answer."""
        pipeline = AppBuilder(Config()).build_answer_pipeline(self.index_path)
        result = pipeline.answer(Query(text=query, k=k))
        print(result.answer)

    def answer_dataset(
        self,
        student_search_results_path: str,
        save_directory: str = "outputs",
    ) -> None:
        """Answer using earlier retrieved sources, without searching again."""

        search_results = DatasetLoader().load_search_results(
            Path(student_search_results_path)
        )
        pipeline = AppBuilder(Config()).build_answer_pipeline(self.index_path)
        answers = pipeline.answer_dataset(search_results)
        destination = Path(save_directory)
        destination.mkdir(parents=True, exist_ok=True)
        output_path = destination / "student_search_results_and_answer.json"
        DataSetWriter().write(answers, output_path)
        print(f"Saved answers to {output_path}")

    def evaluate(
        self,
        student_search_results_path: str,
        dataset_path: str,
    ) -> None:
        """Report source-level recall at k for questions with gold sources."""

        predictions: StudentSearchResults = (
            DatasetLoader().load_search_results(
                Path(student_search_results_path)
            )
        )
        dataset = DatasetLoader().load(Path(dataset_path))

        gold_by_id = {
            question.question_id: question
            for question in dataset.rag_questions
            if isinstance(question, AnsweredQuestion)
        }
        scores: list[float] = []

        for prediction in predictions.search_results:
            gold = gold_by_id.get(prediction.question_id)

            if gold is None or not gold.sources:
                continue

            expected = {
                (source.file_path, source.first_character_index,
                 source.last_character_index)
                for source in gold.sources
            }

            retrieved = {
                (source.file_path, source.first_character_index,
                 source.last_character_index)
                for source in prediction.retrieved_sources[:predictions.k]
            }

            scores.append(len(expected & retrieved) / len(expected))

        if not scores:
            print("No comparable questions with reference sources found.")
            return

        recall = sum(scores) / len(scores)

        print(f"Source recall@{predictions.k}: {recall:.2%} "
              f"({len(scores)} evaluated questions)")
