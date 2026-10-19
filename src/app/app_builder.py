"""Build configured application pipelines and wire their dependencies."""

from pathlib import Path

from src.retrieval.retriever import Retriever
from src.config.config import Config
from src.indexing.corpus_loader import CorpusLoader
from src.indexing.python_chunker import PythonChunker
from src.indexing.text_chunker import TextChunker
from src.indexing.index_store import IndexStore
from src.indexing.indexer import Indexer
from src.pipeline.index_pipeline import IndexPipeline
from src.indexing.bm25_builder import BM25Builder
from src.retrieval.retrieval_utils import RetrievalTokenizer
from src.output.output_builder import OutputBuilder
from src.pipeline.search_pipeline import SearchPipeline
from src.retrieval.retriever_factory import RetrieverFactory
from src.generation.model_manager import ModelManager
from src.pipeline.answer_pipeline import AnswerPipeline
from src.generation.generator import Generator
from src.context.token_budget import TokenBudget
from src.context.context_builder import ContextBuilder
from src.prompting.prompt_builder import PromptBuilder


class AppBuilder:
    """Build configured application pipelines and their dependencies."""

    def __init__(self, config: Config) -> None:
        """Initialize the builder with application configuration."""

        self.config = config

    def build_index_pipeline(self) -> IndexPipeline:
        """Build the indexing pipeline."""
        corpus_loader = CorpusLoader(
            self.config.allowed_extensions
        )
        python_chunker = PythonChunker(
            self.config.max_chunk_size
        )
        text_chunker = TextChunker(
            self.config.max_chunk_size,
            self.config.text_chunk_overlap,
        )
        index_store = IndexStore()

        indexer = Indexer(
            corpus_loader,
            python_chunker,
            text_chunker,
            index_store,
        )

        return IndexPipeline(
            indexer
        )

    def _build_retriever(
        self,
        index_path: Path,
    ) -> Retriever:
        """Build a retriever from persisted index data."""

        index_store = IndexStore()
        tokenizer = RetrievalTokenizer()

        bm25_builder = BM25Builder(
            tokenizer
        )
        retriever_factory = RetrieverFactory(
            index_store,
            bm25_builder,
            tokenizer,
        )

        return retriever_factory.create(
            index_path
        )

    def build_search_pipeline(
        self,
        index_path: Path,
    ) -> SearchPipeline:
        """Build a search pipeline from a persisted index."""

        retriever = self._build_retriever(
            index_path
        )
        output_builder = OutputBuilder()

        return SearchPipeline(
            retriever,
            output_builder,
        )

    def build_answer_pipeline(
        self,
        index_path: Path,
    ) -> AnswerPipeline:
        """Build an answer pipeline from a persisted index."""

        retriever = self._build_retriever(
            index_path
        )

        model_manager = ModelManager(
            self.config.model_name
        )

        generator = Generator(
            model_manager,
            self.config.max_new_tokens,
        )

        token_budget = TokenBudget(
            model_manager.tokenizer,
            self.config.total_context_tokens,
            self.config.max_new_tokens,
        )

        context_builder = ContextBuilder()

        prompt_builder = PromptBuilder()

        output_builder = OutputBuilder()

        return AnswerPipeline(
            retriever,
            context_builder,
            prompt_builder,
            model_manager,
            token_budget,
            generator,
            output_builder,
        )
