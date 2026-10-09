"""Define the result produced by context construction."""

from pydantic import BaseModel

from src.models.search_result import SearchResult


class ContextResult(BaseModel):
    """Represent the output of context construction."""

    context_text: str
    selected_results: list[SearchResult]
