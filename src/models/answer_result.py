from pydantic import BaseModel

from src.models.search_result import SearchResult


class AnswerResult(BaseModel):
    """Represent a generated answer and the retrieval information
    used to produce it.
    """

    answer: str
    search_results: list[SearchResult]
