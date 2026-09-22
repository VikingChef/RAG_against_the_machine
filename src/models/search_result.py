from pydantic import BaseModel, Field

from src.models.chunk import Chunk

class SearchResult(BaseModel):
    """Represent one retrieved chunk, its match score, and its rank."""

    chunk: Chunk
    score: float
    rank: int = Field(ge=1)
