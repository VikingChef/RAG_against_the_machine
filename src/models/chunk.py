"""Define and validate the core Chunk model used by indexing and retrieval."""

from pydantic import BaseModel, Field, model_validator


class Chunk(BaseModel):
    """Represent the core object created by indexing
    and consumed by retrieval.
    """
    file_path: str
    text: str
    first_character_index: int = Field(ge=0)
    last_character_index: int = Field(ge=0)
    file_type: str
    chunk_type: str

    @model_validator(mode="after")
    def validate_indexes(self):
        if self.last_character_index < self.first_character_index:
            raise ValueError(
                "last_character_index must be >= first_character_index"
            )
        return self
