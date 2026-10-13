"""Represent model-facing context and the chunks selected for it."""

from pydantic import BaseModel

from src.models.chunk import Chunk


class ContextResult(BaseModel):
    """Represent formatted context and the chunks included in it."""

    context_text: str
    selected_chunks: list[Chunk]
